#!/usr/bin/env python3
"""Measure real HTTP streaming, microbatching and cancellation on pretrained GPT-2."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

import run_real_model_fused_paged_decode as decode
from run_real_model_sdpa_backend import MODEL_REVISION
from run_real_model_continuous_microbatch import PROMPTS
from real_model_service import StreamingScheduler, make_server

ROOT = Path(__file__).resolve().parent
MAX_TOKENS = 16


class GPT2Backend:
    def __init__(self, model, tokenizer):
        self.model, self.tokenizer = model, tokenizer

    def batch_events(self, prompts, max_tokens, cancellations):
        encoded = self.tokenizer(prompts, padding=True, return_tensors='pt').to('cuda')
        mask = encoded['attention_mask']
        ids = encoded['input_ids']
        if ids.shape[1] + max_tokens > self.model.config.n_positions:
            raise ValueError('request exceeds model context limit')
        positions = mask.long().cumsum(-1) - 1
        positions.masked_fill_(mask == 0, 1)
        cache = DynamicCache(config=self.model.config)
        reset = getattr(self.model, '_reset_fused_decode_state', None)
        if reset:
            reset()
        with torch.inference_mode():
            for _ in range(max_tokens):
                if all(event.is_set() for event in cancellations):
                    break
                torch.cuda.synchronize()
                start = time.perf_counter_ns()
                out = self.model(input_ids=ids, attention_mask=mask, position_ids=positions,
                                 past_key_values=cache, use_cache=True)
                token = out.logits[:, -1].argmax(-1)
                torch.cuda.synchronize()
                elapsed = (time.perf_counter_ns() - start) / 1e6
                kv_bytes = sum(tensor.numel() * tensor.element_size()
                               for layer in out.past_key_values.layers
                               for tensor in (layer.keys, layer.values) if tensor is not None)
                yield {'token_ids': token.tolist(), 'step_ms': elapsed, 'kv_cache_bytes': kv_bytes}
                cache = out.past_key_values
                ids = token.unsqueeze(-1)
                mask = torch.cat((mask, mask.new_ones((len(prompts), 1))), -1)
                positions = (mask.long().sum(-1) - 1).unsqueeze(-1)


def post(url, payload):
    return urllib.request.urlopen(urllib.request.Request(url, json.dumps(payload).encode(),
                                  headers={'Content-Type': 'application/json'}), timeout=120)


def client(url, request_id, prompt, *, start_at=None, offset_ms=0, cancel=False):
    if start_at is not None:
        delay = start_at + offset_ms / 1000 - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
    started = time.perf_counter()
    tokens, ttft, done = [], None, None
    cancelled = None
    try:
        with post(url + '/stream', {'request_id': request_id, 'prompt': prompt}) as response:
            for line in response:
                event = json.loads(line)
                if event['type'] == 'token':
                    if ttft is None:
                        ttft = (time.perf_counter() - started) * 1000
                    tokens.append(event['token_id'])
                    if cancel and cancelled is None:
                        with post(url + '/cancel', {'request_id': request_id}) as reply:
                            cancelled = json.load(reply)['cancelled']
                else:
                    done = event
        status = 200
    except urllib.error.HTTPError as exc:
        status = exc.code
    ended = time.perf_counter()
    return {'request_id': request_id, 'http_status': status, 'token_ids': tokens,
            'ttft_ms': ttft, 'completion_ms': (ended - started) * 1000,
            'actual_start_s': started, 'actual_end_s': ended,
            'planned_offset_ms': offset_ms, 'cancel_ack': cancelled, 'terminal': done}


def run_load(backend, name, max_batch, references, *, control=False):
    scheduler = StreamingScheduler(backend, max_batch=max_batch, max_pending=1 if control else 32,
                                   window_ms=0 if max_batch == 1 else 5, max_tokens=MAX_TOKENS)
    server = make_server(scheduler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}'
    try:
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        start_at = time.perf_counter() + 0.2
        count = 16
        with ThreadPoolExecutor(max_workers=count) as pool:
            futures = [pool.submit(client, url, f'{name}-{i}', PROMPTS[i % len(PROMPTS)],
                                   start_at=start_at, offset_ms=0 if control else (i // 4) * 20 + (i % 4) * 0.5)
                       for i in range(count)]
            rows = [f.result() for f in futures]
        cancellation = client(url, f'{name}-cancel', PROMPTS[0], cancel=True) if control else None
        scheduler.close()
        state = scheduler.snapshot()
        completed = [row for row in rows if row['http_status'] == 200 and row['terminal'] and row['terminal']['status'] == 'completed']
        parity = all(row['token_ids'] == references[int(row['request_id'].rsplit('-', 1)[1]) % len(PROMPTS)] for row in completed)
        duration = max(row['actual_end_s'] for row in rows) - min(row['actual_start_s'] for row in rows)
        latencies = sorted(row['completion_ms'] for row in completed)
        first = sorted(row['ttft_ms'] for row in completed)
        return {'requests': rows, 'scheduler': state, 'output_parity': parity,
                'accepted_count': sum(row['http_status'] == 200 for row in rows),
                'completed_count': len(completed), 'rejected_count': sum(row['http_status'] == 429 for row in rows),
                'completion_ms_median': statistics.median(latencies) if latencies else None,
                'completion_ms_p95': latencies[math.ceil(.95 * len(latencies)) - 1] if latencies else None,
                'ttft_ms_median': statistics.median(first) if first else None,
                'ttft_ms_p95': first[math.ceil(.95 * len(first)) - 1] if first else None,
                'output_tokens_per_second': sum(len(row['token_ids']) for row in completed) / duration,
                'window_wall_seconds': duration,
                'peak_memory_allocated_bytes': torch.cuda.max_memory_allocated(),
                'cancellation_probe': cancellation}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
        if not scheduler.closed:
            scheduler.close()


def main():
    if not torch.cuda.is_available():
        raise SystemExit('CUDA required')
    tokenizer = AutoTokenizer.from_pretrained(decode.MODEL_ID, revision=MODEL_REVISION, padding_side='left')
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(decode.MODEL_ID, revision=MODEL_REVISION,
            use_safetensors=True, attn_implementation='eager').to('cuda').eval()
    backend = GPT2Backend(model, tokenizer)
    references = []
    with torch.inference_mode():
        for prompt in PROMPTS:
            encoded = tokenizer([prompt], return_tensors='pt').to('cuda')
            references.append(model.generate(**encoded, max_new_tokens=MAX_TOKENS, do_sample=False,
                              eos_token_id=None, pad_token_id=tokenizer.pad_token_id)[0, -MAX_TOKENS:].tolist())
    rows = {}
    for name, attention, batch in [('eager_serial', 'eager', 1), ('eager_microbatch', 'eager', 4), ('sdpa_microbatch', 'sdpa', 4)]:
        model.config._attn_implementation = attention
        list(backend.batch_events(list(PROMPTS[:4]), MAX_TOKENS, [threading.Event() for _ in range(4)]))
        rows[name] = run_load(backend, name, batch, references)
        print(json.dumps({'mode': name, 'parity': rows[name]['output_parity'], 'completed': rows[name]['completed_count'],
                          'p95_ms': rows[name]['completion_ms_p95']}), flush=True)
    controls = run_load(backend, 'controls', 1, references, control=True)
    cancel = controls['cancellation_probe']
    accepted = all(row['output_parity'] and row['completed_count'] == 16 and row['scheduler']['active_or_queued'] == 0 for row in rows.values())
    accepted = accepted and controls['rejected_count'] > 0 and controls['output_parity'] and cancel['cancel_ack'] is True and cancel['terminal']['status'] == 'cancelled_inflight' and len(cancel['token_ids']) < MAX_TOKENS
    report = {'schema_version': 'real-model-http-v0.1', 'evidence_kind': 'measured_gpu', 'gpu_execution_accepted': accepted,
              'model_id': decode.MODEL_ID, 'model_revision': MODEL_REVISION, 'tokenizer_revision': MODEL_REVISION,
              'device_name': torch.cuda.get_device_name(), 'dtype': str(model.dtype),
              'runtime': {'torch': torch.__version__, 'transformers': __import__('transformers').__version__, 'cuda': torch.version.cuda},
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), ROOT / 'real_model_service.py', ROOT / 'run_real_model_continuous_microbatch.py', ROOT / 'run_real_model_sdpa_backend.py', Path(decode.__file__))},
              'command': [sys.executable, *sys.argv], 'reference_token_ids': references,
              'protocol': {'prompts': list(PROMPTS), 'max_new_tokens': MAX_TOKENS, 'requests_per_mode': 16,
                           'arrival_ms': [(i // 4) * 20 + (i % 4) * .5 for i in range(16)], 'batch_window_ms': 5,
                           'timing': 'Actual client first-token and terminal HTTP latency; synchronized per-step batch compute',
                           'cancellation': 'Explicit HTTP cancellation at token boundaries; mixed-batch slots retained until batch completion'},
              'modes': rows, 'controls': controls,
              'claim_boundary': 'Bounded single-host loopback load on pretrained GPT-2; 16 requests per mode do not establish production tail capacity.'}
    path = ROOT / 'reports' / 'real-model-http.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
