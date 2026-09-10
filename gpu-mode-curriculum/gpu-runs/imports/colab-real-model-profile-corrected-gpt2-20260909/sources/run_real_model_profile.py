#!/usr/bin/env python3
"""Paired GPT-2 generation measurements and separately captured CUDA profiles."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import statistics
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import run_real_model_fused_paged_decode as decode
from run_real_model_sdpa_backend import MODEL_REVISION, PROMPTS

ROOT = Path(__file__).resolve().parent


def category(name):
    lower = name.lower()
    if 'scaled_dot_product' in lower or 'softmax' in lower or 'paged' in lower:
        return 'attention'
    if any(x in lower for x in ('addmm', 'bmm', 'matmul', 'aten::mm')):
        return 'matrix_multiply'
    if any(x in lower for x in ('copy', 'aten::cat', 'contiguous', 'clone', '_to_copy')):
        return 'movement'
    if any(x in lower for x in ('empty', 'resize', 'alloc', 'free')):
        return 'allocation'
    if any(x in lower for x in ('synchronize', 'nonzero', 'item', '_local_scalar')):
        return 'host_device_coordination'
    return 'other'


def timed(model, encoded):
    torch.cuda.synchronize()
    start_event, end_event = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    start = time.perf_counter_ns()
    start_event.record()
    tokens = decode.native_decode(model, encoded)
    end_event.record()
    torch.cuda.synchronize()
    return {'wall_ms': (time.perf_counter_ns() - start) / 1e6,
            'cuda_event_ms': start_event.elapsed_time(end_event)}, tokens


def capture(model, encoded, path):
    torch.cuda.synchronize()
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
                                            torch.profiler.ProfilerActivity.CUDA],
                                record_shapes=True) as profiler:
        with torch.profiler.record_function('gpt2_complete_generation'):
            tokens = decode.native_decode(model, encoded)
            torch.cuda.synchronize()
    profiler.export_chrome_trace(str(path))
    compressed = path.with_suffix('.json.gz')
    with path.open('rb') as source, gzip.open(compressed, 'wb') as dest:
        shutil.copyfileobj(source, dest)
    operators = []
    totals = {}
    for event in profiler.key_averages():
        row = {'name': event.key, 'count': event.count,
               'self_cpu_us': event.self_cpu_time_total,
               'self_device_us': getattr(event, 'self_device_time_total', 0.0),
               'category': category(event.key)}
        operators.append(row)
        group = totals.setdefault(row['category'], {'self_cpu_us': 0.0, 'self_device_us': 0.0, 'count': 0})
        for key in group:
            group[key] += row[key]
    return {'trace': compressed.name, 'trace_sha256': hashlib.sha256(compressed.read_bytes()).hexdigest(),
            'operators': sorted(operators, key=lambda r: r['self_device_us'], reverse=True),
            'categories': totals,
            'scope': 'Separate instrumented generation; self times are attribution, not additive wall-time components.'}, tokens


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'reports')
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--max-new-tokens', type=int, default=32)
    args = parser.parse_args()
    if args.repeats < 3 or args.max_new_tokens < 1:
        parser.error('at least three repeats and a positive token count required')
    if not torch.cuda.is_available():
        raise SystemExit('CUDA required; no GPU result fabricated')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    decode.MAX_NEW_TOKENS = args.max_new_tokens
    tokenizer = AutoTokenizer.from_pretrained(decode.MODEL_ID, revision=MODEL_REVISION, padding_side='left')
    tokenizer.pad_token = tokenizer.eos_token
    encoded = tokenizer(list(PROMPTS), padding=True, return_tensors='pt').to('cuda')
    model = AutoModelForCausalLM.from_pretrained(decode.MODEL_ID, revision=MODEL_REVISION,
            attn_implementation='eager', use_safetensors=True).to('cuda').eval()
    original_attention = decode.gpt2_modeling.eager_attention_forward
    with torch.inference_mode():
        reference = model.generate(**encoded, do_sample=False, max_new_tokens=args.max_new_tokens,
                                   eos_token_id=None, pad_token_id=tokenizer.pad_token_id)[:, -args.max_new_tokens:]
    individual_parity = all(torch.equal(decode.native_decode(model, tokenizer([prompt], return_tensors='pt').to('cuda'))[0], reference[i])
                            for i, prompt in enumerate(PROMPTS))
    module = decode.build_extension()
    rows = {}
    try:
        for variant in ('eager', 'sdpa', 'paged', 'persistent'):
            decode.gpt2_modeling.eager_attention_forward = original_attention
            if hasattr(model, '_reset_fused_decode_state'):
                del model._reset_fused_decode_state
            model.config._attn_implementation = 'sdpa' if variant == 'sdpa' else 'eager'
            if variant == 'paged':
                decode.install_fused_attention(model, module)
            elif variant == 'persistent':
                decode.install_persistent_fused_attention(model, module)
            timed(model, encoded)  # compile/warm up outside all measurements
            torch.cuda.reset_peak_memory_stats()
            samples = []
            parity = True
            for _ in range(args.repeats):
                sample, tokens = timed(model, encoded)
                samples.append(sample)
                parity = parity and bool(torch.equal(reference, tokens))
            peak = torch.cuda.max_memory_allocated()
            profile, tokens = capture(model, encoded, args.output_dir / f'real-model-profile-{variant}.json')
            parity = parity and bool(torch.equal(reference, tokens))
            rows[variant] = {'samples': samples, 'wall_ms_median': statistics.median(s['wall_ms'] for s in samples),
                             'cuda_event_ms_median': statistics.median(s['cuda_event_ms'] for s in samples),
                             'output_parity': parity, 'peak_memory_allocated_bytes': peak,
                             'attention_backend': model.config._attn_implementation,
                             'generated_token_ids': tokens.tolist(), 'profile': profile}
            print(json.dumps({'variant': variant, 'parity': parity, 'wall_ms_median': rows[variant]['wall_ms_median']}), flush=True)
    finally:
        decode.gpt2_modeling.eager_attention_forward = original_attention
    for row in rows.values():
        row['latency_over_eager_ratio'] = row['wall_ms_median'] / rows['eager']['wall_ms_median']
    accepted = individual_parity and all(row['output_parity'] and any(op['self_device_us'] > 0 for op in row['profile']['operators']) for row in rows.values())
    report = {'schema_version': 'real-model-profile-v0.1', 'evidence_kind': 'measured_gpu',
              'gpu_execution_accepted': accepted, 'batch_vs_individual_output_parity': individual_parity,
              'model_id': decode.MODEL_ID, 'model_revision': MODEL_REVISION, 'tokenizer_revision': MODEL_REVISION,
              'device_name': torch.cuda.get_device_name(), 'dtype': str(model.dtype),
              'runtime': {'torch': torch.__version__, 'transformers': __import__('transformers').__version__, 'cuda': torch.version.cuda},
              'command': [sys.executable, *sys.argv],
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), Path(decode.__file__), ROOT / 'run_real_model_sdpa_backend.py')},
              'protocol': {'prompts': list(PROMPTS), 'prompt_token_counts': encoded['attention_mask'].sum(-1).tolist(),
                           'max_new_tokens': args.max_new_tokens, 'repeats': args.repeats, 'warmups': 1,
                           'order': list(rows), 'timing': 'Complete generation with CUDA synchronization; profiler capture separate from timings',
                           'limitation': 'Fixed-order variant blocks; timing drift is not controlled by interleaving'},
              'reference_token_ids': reference.tolist(), 'variants': rows,
              'claim_boundary': 'Bounded direct generation comparison, not live serving throughput or production quality.'}
    path = args.output_dir / 'real-model-profile.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
