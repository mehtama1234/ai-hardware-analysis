#!/usr/bin/env python3
"""Counterbalanced pretrained GPT-2 dynamic/static/graph decode experiment."""
import argparse
import hashlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache
from graph_decode import GraphDecode

MODEL = 'openai-community/gpt2'
REVISION = '607a30d783dfa663caf39e06633721c8d4cfcd7e'


@torch.inference_mode()
def dynamic(model, encoded, count):
    mask = encoded['attention_mask']
    positions = mask.long().cumsum(-1) - 1
    positions.masked_fill_(mask == 0, 1)
    cache = DynamicCache(config=model.config)
    ids = encoded['input_ids']
    tokens = []
    for _ in range(count):
        out = model(input_ids=ids, attention_mask=mask, position_ids=positions,
                    past_key_values=cache, use_cache=True)
        ids = out.logits[:, -1].argmax(-1, keepdim=True)
        tokens.append(ids[:, 0])
        mask = torch.cat((mask, mask.new_ones((len(ids), 1))), -1)
        positions = mask.long().sum(-1, keepdim=True) - 1
    return torch.stack(tokens, 1)


def timed(fn):
    torch.cuda.synchronize()
    before = time.perf_counter_ns()
    result = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - before) / 1e6, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).parent / 'reports/graph-decode')
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--max-new-tokens', type=int, default=16)
    args = parser.parse_args()
    if args.repeats < 3 or not 2 <= args.max_new_tokens <= 32:
        parser.error('requires >=3 repeats and 2..32 generated tokens')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / 'real-model-graph-decode.json'
    if not torch.cuda.is_available():
        destination.write_text(json.dumps({'status': 'unavailable', 'evidence_kind': 'unavailable',
            'reason': 'CUDA unavailable; no graph execution measured'}, indent=2) + '\n')
        return 2
    torch.backends.cuda.matmul.allow_tf32 = False
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, padding_side='left')
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION,
        attn_implementation='eager', use_safetensors=True).cuda().eval()
    rows = []
    modes = ['dynamic_eager', 'static_eager', 'static_graph']
    for batch, capacity in ((1, 128), (4, 256)):
        allocation_before = torch.cuda.memory_allocated()
        engine = GraphDecode(model, batch, capacity)
        cache_bytes = sum(t.numel() * t.element_size() for t in engine.keys + engine.values)
        capture_ms, _ = timed(engine.capture)
        resident_bytes = torch.cuda.memory_allocated() - allocation_before
        # Long -> short -> different long fixtures reuse the same captured graph.
        for fixture, words in enumerate((24, 5, 31)):
            prompts = [('context movement ' * (words + i * 3)) + (' because' if fixture != 2 else ' therefore') for i in range(batch)]
            encoded = tokenizer(prompts, return_tensors='pt', padding=True).to('cuda')
            with torch.inference_mode():
                reference = model.generate(**encoded, max_new_tokens=args.max_new_tokens,
                    do_sample=False, eos_token_id=None, pad_token_id=tokenizer.pad_token_id)[:, -args.max_new_tokens:]
                singles = [model.generate(**tokenizer([p], return_tensors='pt').to('cuda'),
                    max_new_tokens=args.max_new_tokens, do_sample=False, eos_token_id=None,
                    pad_token_id=tokenizer.pad_token_id)[0, -args.max_new_tokens:] for p in prompts]
            functions = {'dynamic_eager': lambda: dynamic(model, encoded, args.max_new_tokens),
                'static_eager': lambda: engine.generate(encoded, args.max_new_tokens),
                'static_graph': lambda: engine.generate(encoded, args.max_new_tokens, True)}
            samples = {mode: [] for mode in modes}
            parity = all(torch.equal(reference[i], token) for i, token in enumerate(singles))
            for fn in functions.values():
                _, tokens = timed(fn)
                parity = parity and torch.equal(tokens, reference)
            for repeat in range(args.repeats):
                order = modes[repeat % 3:] + modes[:repeat % 3]
                for mode in order:
                    torch.cuda.reset_peak_memory_stats()
                    elapsed, tokens = timed(functions[mode])
                    matches = torch.equal(tokens, reference)
                    parity = parity and matches
                    samples[mode].append({'round': repeat, 'order': order.index(mode),
                        'wall_ms': elapsed, 'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
                        'output_parity': matches, 'token_ids': tokens.tolist()})
            trace = args.output_dir / f'graph-b{batch}-fixture{fixture}.json'
            with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
                    torch.profiler.ProfilerActivity.CUDA]) as profiler:
                profiled = functions['static_graph']()
                torch.cuda.synchronize()
            profiler.export_chrome_trace(str(trace))
            parity = parity and torch.equal(profiled, reference)
            operations = [{'name': event.key, 'count': event.count} for event in profiler.key_averages()]
            row = {'batch': batch, 'capacity': capacity, 'fixture': fixture, 'prompts': prompts,
                'input_token_ids': encoded['input_ids'].tolist(), 'attention_mask': encoded['attention_mask'].tolist(),
                'reference_token_ids': reference.tolist(), 'output_parity': parity,
                'capture_and_warmup_ms': capture_ms, 'cache_bytes': cache_bytes,
                'resident_allocation_including_graph_bytes': resident_bytes, 'samples': samples,
                'median_ms': {mode: statistics.median(s['wall_ms'] for s in samples[mode]) for mode in modes},
                'profile': {'file': trace.name, 'sha256': hashlib.sha256(trace.read_bytes()).hexdigest(), 'operations': operations}}
            rows.append(row)
            print(json.dumps({k: row[k] for k in ('batch', 'fixture', 'output_parity', 'median_ms')}), flush=True)
        del functions, engine
        torch.cuda.empty_cache()
    sources = args.output_dir / 'sources'
    sources.mkdir(exist_ok=True)
    hashes = {}
    for path in (Path(__file__), Path(__file__).with_name('graph_decode.py')):
        shutil.copy2(path, sources / path.name)
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (args.output_dir / 'requirements.recorded.txt').write_text(subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True))
    accepted = all(row['output_parity'] for row in rows)
    report = {'schema_version': 'real-model-graph-decode-v0.1', 'status': 'passed' if accepted else 'failed',
        'evidence_kind': 'measured_gpu', 'model_id': MODEL, 'model_revision': REVISION,
        'tokenizer_revision': REVISION, 'source_hashes': hashes, 'command': sys.argv,
        'runtime': {'python': platform.python_version(), 'torch': torch.__version__,
            'transformers': transformers.__version__, 'cuda': torch.version.cuda,
            'device': torch.cuda.get_device_name(), 'dtype': str(model.dtype), 'tf32': False},
        'protocol': {'repeats': args.repeats, 'max_new_tokens': args.max_new_tokens,
            'warmups_per_mode': 1, 'order': 'rotating three-way',
            'timing': 'synchronized host wall time including prefill/cache reset and all decode steps; capture excluded',
            'memory': 'all modes measured with the static cache and graph resident',
            'graph_reuse': 'one capture per batch/capacity across three distinct prompt fixtures'},
        'rows': rows, 'limitations': ['Fixed batch to completion; no admission or EOS stopping.',
            'No HTTP or continuous batching claim.', 'Static cache attends to masked full capacity.',
            'Profiler capture separate from timing; native/static eager trace comparison remains follow-up.',
            'Independent replay and trained-logit error sweep remain open.']}
    destination.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
