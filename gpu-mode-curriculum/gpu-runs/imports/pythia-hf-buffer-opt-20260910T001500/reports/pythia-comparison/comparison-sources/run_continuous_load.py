#!/usr/bin/env python3
"""Repeated mixed-length HTTP arrival load on the graph admission scheduler."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import platform
import shutil
import statistics
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from continuous_http import make_server
from continuous_service import ContinuousScheduler, SlotBackend
from slot_decode import SlotDecode
from hf_slot_decode import HFSlotDecode

MODEL = 'openai-community/gpt2'
REVISION = '607a30d783dfa663caf39e06633721c8d4cfcd7e'
PROMPTS = ['The history of computer systems includes many advances because',
    'A short story about a small dog', 'Paris is a city in France and its history',
    'memory bandwidth and computation ' * 12 + ' therefore']
BUDGETS = [1, 8, 16, 32]


def request(url, request_id, prompt, budget, planned):
    started = time.perf_counter()
    tokens, arrivals, terminal = [], [], None
    status = None
    error = None
    try:
        data = json.dumps({'request_id': request_id, 'prompt': prompt, 'max_new_tokens': budget}).encode()
        with urllib.request.urlopen(urllib.request.Request(url + '/stream', data,
                headers={'Content-Type': 'application/json'}), timeout=60) as response:
            status = response.status
            for line in response:
                event = json.loads(line)
                if event['type'] == 'token':
                    tokens.append(event['token_id'])
                    arrivals.append((time.perf_counter() - started) * 1000)
                else:
                    terminal = event
    except urllib.error.HTTPError as exc:
        status = exc.code
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'
    ended = time.perf_counter()
    return {'request_id': request_id, 'max_new_tokens': budget, 'http_status': status,
        'token_ids': tokens, 'token_arrival_ms': arrivals, 'terminal': terminal,
        'planned_start_s': planned, 'actual_start_s': started, 'actual_end_s': ended,
        'arrival_lateness_ms': (started - planned) * 1000,
        'completion_ms': (ended - started) * 1000, 'error': error}


def percentile(values, q):
    values = sorted(values)
    return values[max(0, math.ceil(q * len(values)) - 1)] if values else None


def eos_probe(engine, tokenizer, references):
    stop = references[0][1]
    length = references[0].index(stop) + 1
    scheduler = ContinuousScheduler(SlotBackend(engine, tokenizer, eos_token_id=stop), slots=2, max_tokens=32)
    server = make_server(scheduler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        row = request(f'http://127.0.0.1:{server.server_port}', 'controlled-eos', PROMPTS[0], 32, time.perf_counter())
        scheduler.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(10)
        if not scheduler.closed:
            scheduler.close()
    passed = (row['http_status'] == 200 and row['terminal']['finish_reason'] == 'eos'
              and row['token_ids'] == references[0][:length] and length < 32)
    return {'passed': passed, 'eos_token_id': stop, 'expected_length': length, 'request': row,
            'scope': 'EOS configured to a known reference token to exercise early termination'}


def load(engine, tokenizer, references, rate, seconds, run, scheduler_factory=None):
    scheduler = (scheduler_factory() if scheduler_factory else
                 ContinuousScheduler(SlotBackend(engine, tokenizer), slots=2, max_pending=8, max_tokens=32))
    server = make_server(scheduler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}'
    torch.cuda.reset_peak_memory_stats()
    try:
        start = time.perf_counter() + .1
        futures = []
        with ThreadPoolExecutor(max_workers=128) as pool:
            for i in range(int(rate * seconds)):
                planned = start + i / rate
                delay = planned - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                futures.append(pool.submit(request, url, f'{run}-{i}', PROMPTS[i % 4], BUDGETS[(i // 4 + i) % 4], planned))
            rows = [future.result() for future in futures]
        scheduler.close()
        state = scheduler.snapshot()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(10)
        if not scheduler.closed:
            scheduler.close()
    completed, rejected, failures = [], [], []
    for i, row in enumerate(rows):
        row['prompt_index'] = i % 4
        row['output_parity'] = row['token_ids'] == references[i % 4][:row['max_new_tokens']]
        if row['http_status'] == 429:
            rejected.append(row)
        elif row['http_status'] == 200 and row['terminal'] and row['terminal']['status'] == 'completed' and row['output_parity']:
            completed.append(row)
        else:
            failures.append(row)
        arrivals = row['token_arrival_ms']
        row['meets_latency_targets'] = (row in completed and arrivals[0] <= 1000
            and row['completion_ms'] <= 3000 and all(b - a <= 500 for a, b in zip(arrivals, arrivals[1:])))
    duration = max(r['actual_end_s'] for r in rows) - min(r['actual_start_s'] for r in rows)
    checks = {'no_failed_requests': not failures, 'all_accounted': len(completed) + len(rejected) == len(rows),
        'queue_rejections_match': len(rejected) == state['rejected'],
        'accepted_records_match': {r['request_id'] for r in completed} == set(state['records']),
        'drained': state['active_or_queued'] == 0 and all(owner is None for owner in engine.owners),
        'cache_cleared': all(bool(torch.count_nonzero(t) == 0) for t in engine.keys + engine.values)}
    return {'offered_rate': rate, 'duration_requested_s': seconds, 'round': run,
        'requests': rows, 'scheduler': state, 'checks': checks,
        'summary': {'completed': len(completed), 'rejected': len(rejected), 'failed': len(failures),
            'measured_window_s': duration, 'completion_p95_ms': percentile([r['completion_ms'] for r in completed], .95),
            'ttft_p95_ms': percentile([r['token_arrival_ms'][0] for r in completed], .95),
            'arrival_lateness_p95_ms': percentile([r['arrival_lateness_ms'] for r in rows], .95),
            'goodput_requests_per_s': sum(r['meets_latency_targets'] for r in rows) / duration,
            'output_tokens_per_s': sum(len(r['token_ids']) for r in completed) / duration,
            'peak_allocated_bytes': torch.cuda.max_memory_allocated()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=8)
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--model-id', default=MODEL)
    parser.add_argument('--revision', default=REVISION)
    parser.add_argument('--engine', choices=('gpt2', 'hf'), default='gpt2')
    args = parser.parse_args()
    if args.seconds < 4 or not torch.cuda.is_available():
        raise SystemExit('CUDA and >=4 seconds per load window required')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    torch.backends.cuda.matmul.allow_tf32 = False
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, revision=args.revision)
    tokenizer.pad_token = tokenizer.eos_token
    if args.checkpoint:
        model = AutoModelForCausalLM.from_pretrained(
            args.checkpoint, local_files_only=True, attn_implementation='eager').cuda().eval()
    else:
        model = AutoModelForCausalLM.from_pretrained(args.model_id, revision=args.revision,
            attn_implementation='eager', use_safetensors=True).cuda().eval()
    with torch.inference_mode():
        references = [model.generate(**tokenizer([prompt], return_tensors='pt').to('cuda'),
            max_new_tokens=32, do_sample=False, eos_token_id=None,
            pad_token_id=tokenizer.pad_token_id)[0, -32:].tolist() for prompt in PROMPTS]
    engine = (HFSlotDecode(model, 2, 256) if args.engine == 'hf' else SlotDecode(model, 2, 256))
    engine.capture()
    rows = []
    for round_index, rates in enumerate(((4, 16, 48), (48, 16, 4))):
        for rate in rates:
            row = load(engine, tokenizer, references, rate, args.seconds, f'r{round_index}-rate{rate}')
            rows.append(row)
            print(json.dumps({'run': row['round'], 'checks': row['checks'], 'summary': row['summary']}), flush=True)
    sources = args.output_dir / 'load-sources'
    sources.mkdir(exist_ok=True)
    hashes = {}
    source_names = ('graph_decode.py','slot_decode.py','continuous_service.py','continuous_http.py','real_model_service.py','run_continuous_load.py')
    if args.engine == 'hf':
        source_names += ('hf_slot_decode.py',)
    for name in source_names:
        path = Path(__file__).with_name(name)
        shutil.copy2(path, sources / name)
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    eos = eos_probe(engine, tokenizer, references)
    checks = {'all_load_checks_passed': all(all(r['checks'].values()) for r in rows),
              'controlled_http_eos_passed': eos['passed'],
              'gpu_overload_rejection_observed': any(r['summary']['rejected'] > 0 for r in rows)}
    report = {'schema_version': 'continuous-arrival-load-v0.1', 'evidence_kind': 'measured_gpu',
        'status': 'passed' if all(checks.values()) else 'failed', 'checks': checks,
        'model_id': args.model_id, 'model_revision': args.revision, 'tokenizer_revision': args.revision,
        'checkpoint': str(args.checkpoint) if args.checkpoint else None,
        'source_hashes': hashes, 'engine': args.engine, 'prompts': PROMPTS, 'references': references,
        'runtime': {'torch': torch.__version__, 'transformers': transformers.__version__,
            'python': platform.python_version(), 'device': torch.cuda.get_device_name(), 'dtype': str(model.dtype), 'tf32': False},
        'protocol': {'rates': [4,16,48], 'rounds': 2, 'seconds_per_window': args.seconds, 'budgets': BUDGETS,
            'slots': 2, 'queue_limit': 8, 'ttft_target_ms': 1000, 'completion_target_ms': 3000,
            'max_intertoken_gap_ms': 500, 'timing': 'actual client wall clock including queue and HTTP; goodput denominator includes drain'},
        'runs': rows, 'eos_probe': eos, 'limitations': ['Bounded loopback arrival windows, not production capacity.',
            'No matched native microbatch comparison or independent replay yet.',
            'Prefill synchronous and unchunked; main-load EOS disabled for fixed-length reference checks.']}
    (args.output_dir / 'continuous-load.json').write_text(json.dumps(report, indent=2) + '\n')
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
