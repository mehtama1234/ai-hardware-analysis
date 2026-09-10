"""Bounded HTTP service using fixed-shape StaticCache graph buckets."""
import argparse
import json
import platform
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from continuous_http import make_server
from microbatch_control import MicrobatchScheduler
from static_graph_bucket import StaticGraphBucket

GPU_BUCKET_LOCK = threading.Lock()
TOKENIZER_LOCK = threading.Lock()


class BucketBackend:
    def __init__(self, model, tokenizer, bucket):
        self.model, self.tokenizer, self.bucket = model, tokenizer, bucket
        self.bucket_meta = []

    def cancel(self, _handle):
        return False

    def batch_events(self, requests):
        if not 1 <= len(requests) <= 2 or len({r.max_new_tokens for r in requests}) != 1:
            raise ValueError('fixed bucket requires at most two requests with one budget')
        # A queue can drain to one request after the grouping window. Keep the
        # captured batch shape fixed by duplicating that request in the graph
        # input, while exposing events only for the real request.
        graph_requests = list(requests)
        if len(graph_requests) == 1:
            graph_requests.append(graph_requests[0])
        with TOKENIZER_LOCK:
            encoded = self.tokenizer([r.prompt for r in graph_requests], padding=True, return_tensors='pt').to('cuda')
        # CUDA Graph capture and replay use the process CUDA stream/context;
        # concurrent shape buckets must serialize GPU ownership.
        with GPU_BUCKET_LOCK:
            tokens, meta = self.bucket.run(encoded, graph_requests[0].max_new_tokens, recapture=True)
        self.bucket_meta.append(meta)
        for index in range(tokens.shape[1]):
            status = 'completed' if index + 1 == tokens.shape[1] else 'active'
            yield [{'request_id': r.request_id, 'token_id': int(tokens[i, index]),
                    'index': index, 'status': status} for i, r in enumerate(requests)]


class ShapeBucketRouter:
    """Route requests into independent fixed-shape schedulers."""
    def __init__(self, model, tokenizer):
        self.model, self.tokenizer = model, tokenizer
        self.max_tokens = 8
        self.schedulers, self.routes, self.bucket_meta = {}, {}, []

    def submit(self, request_id, prompt, max_new_tokens=None):
        with TOKENIZER_LOCK:
            encoded = self.tokenizer([prompt], return_tensors='pt')
        key = (int(encoded['input_ids'].shape[1]), int(max_new_tokens or 8))
        scheduler = self.schedulers.get(key)
        if scheduler is None:
            bucket = StaticGraphBucket(self.model, batch_size=2, max_cache_len=256)
            backend = BucketBackend(self.model, self.tokenizer, bucket)
            scheduler = MicrobatchScheduler(backend, slots=2, max_pending=2,
                                            max_tokens=8, window_ms=500)
            self.schedulers[key] = scheduler
        request = scheduler.submit(request_id, prompt, max_new_tokens)
        self.routes[request_id] = (scheduler, key)
        return request

    def cancel(self, request_id):
        route = self.routes.get(request_id)
        return route[0].cancel(request_id) if route else False

    def snapshot(self):
        rows = [scheduler.snapshot() for scheduler in self.schedulers.values()]
        return {'active_or_queued': sum(r['active_or_queued'] for r in rows),
                'rejected': sum(r['rejected'] for r in rows),
                'buckets': {str(key): r for key, r in zip(self.schedulers, rows)}}

    def close(self):
        for scheduler in self.schedulers.values():
            scheduler.close()


def post(url, request_id, prompt, max_new_tokens):
    body = json.dumps({'request_id': request_id, 'prompt': prompt,
                       'max_new_tokens': max_new_tokens}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url + '/stream', body,
                headers={'Content-Type': 'application/json'}), timeout=60) as response:
            events = [json.loads(line) for line in response]
        return {'status': response.status, 'events': events}
    except urllib.error.HTTPError as exc:
        try: body = exc.read().decode()
        except Exception: body = ''
        return {'status': exc.code, 'error': body}
    except Exception as exc:
        return {'status': None, 'error': f'{type(exc).__name__}: {exc}'}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--rounds', type=int, default=1)
    p.add_argument('--model-id', default='EleutherAI/pythia-70m'); p.add_argument('--revision', required=True)
    a = p.parse_args()
    if a.rounds < 1 or a.rounds > 16: raise SystemExit('--rounds must be in 1..16')
    if not torch.cuda.is_available(): raise SystemExit('CUDA required')
    tok = AutoTokenizer.from_pretrained(a.model_id, revision=a.revision); tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model_id, revision=a.revision,
        attn_implementation='sdpa', use_safetensors=True).cuda().eval()
    prompts = ['GPU kernels expose memory hierarchy', 'A compiler lowers tensor programs']
    prompt_batches = [prompts, [p + ' again' for p in prompts]]
    with torch.inference_mode():
        refs = {json.dumps([x, budget]): model.generate(**tok([x], return_tensors='pt').to('cuda'),
            max_new_tokens=budget, do_sample=False, eos_token_id=None,
            pad_token_id=tok.pad_token_id)[0, -budget:].tolist()
            for batch in prompt_batches for x in batch for budget in (4, 8)}
    scheduler = ShapeBucketRouter(model, tok)
    server = make_server(scheduler); thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    rounds = []
    primary_plan = [(round_index, i, prompt, budget)
                    for round_index, batch in enumerate(prompt_batches)
                    for budget in (4, 8) for i, prompt in enumerate(batch)]
    try:
        for repeat in range(a.rounds):
            with ThreadPoolExecutor(max_workers=8) as pool:
                futures = [pool.submit(post, f'http://127.0.0.1:{server.server_port}',
                    f'bucket-{repeat}-{round_index}-{budget}-{i}', prompt, budget)
                    for round_index, i, prompt, budget in primary_plan]
                rows = [f.result() for f in futures]
            rounds.append(rows)
        # Deliberately exceed one bucket's pending bound. The request bodies
        # are identical in shape, so any 429s are queue backpressure rather
        # than shape incompatibility.
        with ThreadPoolExecutor(max_workers=12) as pool:
            overload_futures = [pool.submit(post, f'http://127.0.0.1:{server.server_port}',
                f'overload-{i}', prompts[0], 4) for i in range(12)]
            overload = [f.result() for f in overload_futures]
    finally:
        scheduler.close(); server.shutdown(); server.server_close(); thread.join(10)
    outputs = []
    for repeat, rows in enumerate(rounds):
        for (source_round, source_i, prompt, budget), row in zip(primary_plan, rows):
            tokens = [e['token_id'] for e in row.get('events', []) if e.get('type') == 'token']
            outputs.append({'repeat': repeat, 'round': source_round, 'request': source_i, 'budget': budget,
                            'prompt': prompt, 'status': row.get('status'),
                            'error': row.get('error'), 'tokens': tokens,
                            'terminal': next((e for e in row.get('events', []) if e.get('type') == 'done'), None)})
    overload_statuses = [row.get('status') for row in overload]
    expected_primary = 8 * a.rounds
    checks = {'four_shape_budget_classes': len(scheduler.schedulers) == 4,
              'eight_requests_per_round': len(outputs) == expected_primary,
              'all_http_ok': all(x['status'] == 200 for x in outputs),
              'mixed_output_budgets': {x['budget'] for x in outputs} == {4, 8} and
                                      all(len(x['tokens']) == x['budget'] for x in outputs),
              'token_parity': all(x['tokens'] == refs[json.dumps([x['prompt'], x['budget']])] for x in outputs),
              'bounded_backpressure': 429 in overload_statuses,
              'overload_accounted': all(s in (200, 429) for s in overload_statuses),
              'drained': scheduler.snapshot()['active_or_queued'] == 0,
              'four_recaptures_per_round': sum(len(s.backend.bucket_meta) for s in scheduler.schedulers.values()) >= 4 * a.rounds}
    bucket_meta = [m for s in scheduler.schedulers.values() for m in s.backend.bucket_meta]
    served_tokens = sum(len(x['tokens']) for x in outputs)
    recapture_total_ms = sum(float(m.get('recapture_ms', 0.0)) for m in bucket_meta)
    report = {'schema_version': 'static-graph-http-v0.1', 'evidence_kind': 'measured_gpu',
        'status': 'passed', 'model_id': a.model_id, 'model_revision': a.revision,
        'runtime': {'torch': torch.__version__, 'transformers': transformers.__version__,
                    'python': platform.python_version(), 'device': torch.cuda.get_device_name()},
        'protocol': {'shape_classes': 2, 'output_budgets': [4, 8], 'primary_requests_per_round': 8,
                     'rounds': a.rounds,
                     'batch_size': 2, 'max_pending_per_bucket': 2, 'steps': '4 or 8',
                     'policy': 'recapture-per-bucket', 'transport': 'HTTP loopback'},
        'checks': checks, 'bucket_meta': bucket_meta, 'outputs': outputs,
        'overload': {'requests': len(overload), 'statuses': overload_statuses,
                     'accepted': sum(s == 200 for s in overload_statuses),
                     'rejected_429': sum(s == 429 for s in overload_statuses)},
        'router': scheduler.snapshot(),
        'references': refs, 'metrics': {'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
            'primary_served_tokens': served_tokens,
            'recapture_total_ms': recapture_total_ms,
            'recapture_ms_per_primary_token': (recapture_total_ms / served_tokens
                                               if served_tokens else None),
            'recapture_ms_per_primary_request': (recapture_total_ms / len(outputs)
                                                 if outputs else None)},
        'limitations': ['Each graph bucket remains fixed-shape and recaptures for a new cache lifetime.',
                        'Backpressure is a bounded loopback queue experiment, not production capacity.',
                        'Singleton groups are padded with a duplicate input to preserve graph batch shape.']}
    report['status'] = 'passed' if all(checks.values()) else 'failed'
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': checks})); return int(report['status'] != 'passed')


if __name__ == '__main__': raise SystemExit(main())
