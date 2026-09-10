#!/usr/bin/env python3
"""Counterbalanced pretrained GPT-2 dynamic/static/graph decode experiment."""
import argparse
import gzip
import hashlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache
from graph_decode import GraphDecode

MODEL = 'openai-community/gpt2'
REVISION = '607a30d783dfa663caf39e06633721c8d4cfcd7e'


@torch.inference_mode()
def dynamic(model, encoded, count, stages=None):
    mask = encoded['attention_mask']
    positions = mask.long().cumsum(-1) - 1
    positions.masked_fill_(mask == 0, 1)
    cache = DynamicCache(config=model.config)
    ids = encoded['input_ids']
    tokens = []
    if stages is not None:
        torch.cuda.synchronize()
        started = time.perf_counter_ns()
    for step in range(count):
        out = model(input_ids=ids, attention_mask=mask, position_ids=positions,
                    past_key_values=cache, use_cache=True)
        ids = out.logits[:, -1].argmax(-1, keepdim=True)
        tokens.append(ids[:, 0])
        mask = torch.cat((mask, mask.new_ones((len(ids), 1))), -1)
        positions = mask.long().sum(-1, keepdim=True) - 1
        if stages is not None and step == 0:
            torch.cuda.synchronize()
            split = time.perf_counter_ns()
    if stages is not None:
        torch.cuda.synchronize()
        stages.update(prefill_ms=(split - started) / 1e6,
                      decode_ms=(time.perf_counter_ns() - split) / 1e6)
    return torch.stack(tokens, 1)


def timed(fn):
    torch.cuda.synchronize()
    before = time.perf_counter_ns()
    result = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - before) / 1e6, result


def staged(engine, encoded, count, graph):
    prefill, first = timed(lambda: engine.prepare(encoded, count))
    decode, rest = timed(lambda: [engine.step(graph) for _ in range(count - 1)])
    return {'prefill_ms': prefill, 'decode_ms': decode}, torch.stack([first, *rest], 1)


@torch.inference_mode()
def logit_check(model, engine, encoded, count, graph):
    mask = encoded['attention_mask']
    positions = mask.long().cumsum(-1) - 1
    positions.masked_fill_(mask == 0, 1)
    cache = DynamicCache(config=model.config)
    out = model(**encoded, position_ids=positions, past_key_values=cache, use_cache=True)
    first = engine.prepare(encoded, count)
    rows = []
    for step in range(count - 1):
        ids = out.logits[:, -1].argmax(-1, keepdim=True)
        mask = torch.cat((mask, mask.new_ones((len(ids), 1))), -1)
        out = model(input_ids=ids, attention_mask=mask,
                    position_ids=mask.long().sum(-1, keepdim=True) - 1,
                    past_key_values=cache, use_cache=True)
        engine.step(graph)
        expected = out.logits[:, -1]
        error = (engine.logits - expected).abs()
        rows.append({'step': step, 'max_abs_error': error.max().item(),
            'finite': bool(torch.isfinite(engine.logits).all()),
            'allclose': torch.allclose(engine.logits, expected, atol=2e-4, rtol=2e-4)})
    return {'atol': 2e-4, 'rtol': 2e-4, 'steps': rows,
            'passed': all(row['finite'] and row['allclose'] for row in rows)}


def capture_profile(fn, path):
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
            torch.profiler.ProfilerActivity.CUDA]) as profiler:
        result = fn()
        torch.cuda.synchronize()
    with tempfile.TemporaryDirectory() as temp:
        raw = Path(temp) / 'trace.json'
        profiler.export_chrome_trace(str(raw))
        with raw.open('rb') as source, gzip.open(path, 'wb') as target:
            shutil.copyfileobj(source, target)
    operations = [{'name': event.key, 'count': event.count,
        'self_cpu_us': event.self_cpu_time_total,
        'self_device_us': getattr(event, 'self_device_time_total', 0.0)} for event in profiler.key_averages()]
    return {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'operations': operations}, result


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
            stages, profiles, logits = {mode: [] for mode in modes}, {}, {}
            for repeat in range(args.repeats):
                for mode in modes[repeat % 3:] + modes[:repeat % 3]:
                    if mode == 'dynamic_eager':
                        measured = {}
                        output = dynamic(model, encoded, args.max_new_tokens, measured)
                    else:
                        measured, output = staged(engine, encoded, args.max_new_tokens, mode == 'static_graph')
                    measured['output_parity'] = torch.equal(output, reference)
                    parity = parity and measured['output_parity']
                    stages[mode].append(measured)
            for mode in modes:
                profiles[mode], profiled = capture_profile(functions[mode],
                    args.output_dir / f'{mode}-b{batch}-fixture{fixture}.json.gz')
                parity = parity and torch.equal(profiled, reference)
                if mode != 'dynamic_eager':
                    logits[mode] = logit_check(model, engine, encoded, args.max_new_tokens, mode == 'static_graph')
                    parity = parity and logits[mode]['passed']
            row = {'batch': batch, 'capacity': capacity, 'fixture': fixture, 'prompts': prompts,
                'input_token_ids': encoded['input_ids'].tolist(), 'attention_mask': encoded['attention_mask'].tolist(),
                'reference_token_ids': reference.tolist(), 'output_parity': parity,
                'capture_and_warmup_ms': capture_ms, 'cache_bytes': cache_bytes,
                'resident_allocation_including_graph_bytes': resident_bytes, 'samples': samples,
                'median_ms': {mode: statistics.median(s['wall_ms'] for s in samples[mode]) for mode in modes},
                'profile': profiles['static_graph'], 'profiles': profiles,
                'stage_samples': stages, 'logit_checks': logits}
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
    requirements = args.output_dir / 'requirements.recorded.txt'
    requirements.write_text(subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True))
    manifest = args.output_dir / 'source-manifest.json'
    manifest.write_text(json.dumps({'source_hashes': hashes,
        'requirements_sha256': hashlib.sha256(requirements.read_bytes()).hexdigest()}, indent=2) + '\n')
    bundle = args.output_dir / 'graph-decode-source.tar.gz'
    with tarfile.open(bundle, 'w:gz') as archive:
        for path in [*(sources / name for name in hashes), requirements, manifest]:
            archive.add(path, arcname=path.name)
    accepted = all(row['output_parity'] for row in rows)
    report = {'schema_version': 'real-model-graph-decode-v0.2', 'status': 'passed' if accepted else 'failed',
        'evidence_kind': 'measured_gpu', 'model_id': MODEL, 'model_revision': REVISION,
        'tokenizer_revision': REVISION, 'source_hashes': hashes, 'command': sys.argv,
        'reproduction_bundle': {'path': bundle.name, 'sha256': hashlib.sha256(bundle.read_bytes()).hexdigest()},
        'runtime': {'python': platform.python_version(), 'torch': torch.__version__,
            'transformers': transformers.__version__, 'cuda': torch.version.cuda,
            'device': torch.cuda.get_device_name(), 'dtype': str(model.dtype), 'tf32': False},
        'protocol': {'repeats': args.repeats, 'max_new_tokens': args.max_new_tokens,
            'warmups_per_mode': 1, 'order': 'rotating three-way',
            'timing': 'synchronized host wall time including prefill/cache reset and all decode steps; capture excluded',
            'memory': 'all modes measured with the static cache and graph resident',
            'stages': 'Separate synchronized prefill/decode measurements; split synchronization perturbs timing, so do not add to uninstrumented wall time.',
            'profiles': 'All three modes profiled separately on identical inputs; ATen and runtime/kernel attribution overlap.',
            'graph_reuse': 'one capture per batch/capacity across three distinct prompt fixtures'},
        'rows': rows, 'limitations': ['Fixed batch to completion; no admission or EOS stopping.',
            'No HTTP or continuous batching claim.', 'Static cache attends to masked full capacity.',
            'Independent replay remains open until verified separately.',
            'Logit checks cover this bounded pretrained fixture set, not all shapes or precisions.']}
    destination.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
