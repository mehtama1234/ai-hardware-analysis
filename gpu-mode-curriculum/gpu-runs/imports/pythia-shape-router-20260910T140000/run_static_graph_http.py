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


class BucketBackend:
    def __init__(self, model, tokenizer, bucket):
        self.model, self.tokenizer, self.bucket = model, tokenizer, bucket
        self.bucket_meta = []

    def cancel(self, _handle):
        return False

    def batch_events(self, requests):
        if len(requests) != 2 or len({r.max_new_tokens for r in requests}) != 1:
            raise ValueError('fixed bucket requires exactly two requests with one budget')
        encoded = self.tokenizer([r.prompt for r in requests], padding=True, return_tensors='pt').to('cuda')
        tokens, meta = self.bucket.run(encoded, requests[0].max_new_tokens, recapture=True)
        self.bucket_meta.append(meta)
        for index in range(tokens.shape[1]):
            status = 'completed' if index + 1 == tokens.shape[1] else 'active'
            yield [{'request_id': r.request_id, 'token_id': int(tokens[i, index]),
                    'index': index, 'status': status} for i, r in enumerate(requests)]


class ShapeBucketRouter:
    """Route requests into independent fixed-shape schedulers."""
    def __init__(self, model, tokenizer):
        self.model, self.tokenizer = model, tokenizer
        self.schedulers, self.routes, self.bucket_meta = {}, {}, []

    def submit(self, request_id, prompt, max_new_tokens=None):
        encoded = self.tokenizer([prompt], return_tensors='pt')
        key = (int(encoded['input_ids'].shape[1]), int(max_new_tokens or 8))
        scheduler = self.schedulers.get(key)
        if scheduler is None:
            bucket = StaticGraphBucket(self.model, batch_size=2, max_cache_len=256)
            backend = BucketBackend(self.model, self.tokenizer, bucket)
            scheduler = MicrobatchScheduler(backend, slots=2, max_pending=8,
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


def post(url, request_id, prompt):
    body = json.dumps({'request_id': request_id, 'prompt': prompt, 'max_new_tokens': 8}).encode()
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
    p.add_argument('--model-id', default='EleutherAI/pythia-70m'); p.add_argument('--revision', required=True)
    a = p.parse_args()
    if not torch.cuda.is_available(): raise SystemExit('CUDA required')
    tok = AutoTokenizer.from_pretrained(a.model_id, revision=a.revision); tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model_id, revision=a.revision,
        attn_implementation='sdpa', use_safetensors=True).cuda().eval()
    prompts = ['GPU kernels expose memory hierarchy', 'A compiler lowers tensor programs']
    prompt_batches = [prompts, [p + ' again' for p in prompts]]
    with torch.inference_mode():
        refs = [[model.generate(**tok([x], return_tensors='pt').to('cuda'), max_new_tokens=8,
            do_sample=False, eos_token_id=None, pad_token_id=tok.pad_token_id)[0, -8:].tolist() for x in batch]
            for batch in prompt_batches]
    scheduler = ShapeBucketRouter(model, tok)
    server = make_server(scheduler); thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    rounds = []
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(post, f'http://127.0.0.1:{server.server_port}',
                f'bucket-{round_index}-{i}', prompt)
                for round_index, batch in enumerate(prompt_batches) for i, prompt in enumerate(batch)]
            rows = [f.result() for f in futures]
        rounds.append(rows)
    finally:
        scheduler.close(); server.shutdown(); server.server_close(); thread.join(10)
    outputs = []
    for round_index, rows in enumerate(rounds):
        for i, row in enumerate(rows):
            source_round, source_i = divmod(i, 2)
            tokens = [e['token_id'] for e in row.get('events', []) if e.get('type') == 'token']
            outputs.append({'round': source_round, 'request': source_i, 'status': row.get('status'),
                            'tokens': tokens, 'terminal': next((e for e in row.get('events', []) if e.get('type') == 'done'), None)})
    checks = {'two_shape_classes': len(scheduler.schedulers) == 2, 'four_requests': len(outputs) == 4,
              'all_http_ok': all(x['status'] == 200 for x in outputs),
              'all_eight_tokens': all(len(x['tokens']) == 8 for x in outputs),
              'token_parity': all(x['tokens'] == refs[x['round']][x['request']] for x in outputs),
              'drained': scheduler.snapshot()['active_or_queued'] == 0,
              'two_recaptures': sum(len(s.backend.bucket_meta) for s in scheduler.schedulers.values()) == 2}
    bucket_meta = [m for s in scheduler.schedulers.values() for m in s.backend.bucket_meta]
    report = {'schema_version': 'static-graph-http-v0.1', 'evidence_kind': 'measured_gpu',
        'status': 'passed', 'model_id': a.model_id, 'model_revision': a.revision,
        'runtime': {'torch': torch.__version__, 'transformers': transformers.__version__,
                    'python': platform.python_version(), 'device': torch.cuda.get_device_name()},
        'protocol': {'buckets': 2, 'batch_size': 2, 'steps': 8, 'policy': 'recapture-per-bucket', 'transport': 'HTTP loopback'},
        'checks': checks, 'bucket_meta': bucket_meta, 'outputs': outputs,
        'router': scheduler.snapshot(),
        'references': refs, 'metrics': {'peak_allocated_bytes': torch.cuda.max_memory_allocated()},
        'limitations': ['Fixed batch, prompt width, and output budget; no dynamic admission.',
                        'Loopback HTTP bucket proof, not production capacity.']}
    report['status'] = 'passed' if all(checks.values()) else 'failed'
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': checks})); return int(report['status'] != 'passed')


if __name__ == '__main__': raise SystemExit(main())
