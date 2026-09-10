"""Bounded streaming microbatches for the real-model inference experiment.

One GPU worker owns all model state. Cancellation suppresses delivery at token
boundaries; mixed-batch slots remain allocated until their batch ends.
"""
from __future__ import annotations

import json
import queue
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


@dataclass
class Request:
    request_id: str
    prompt: str
    submitted: float = field(default_factory=time.perf_counter)
    cancelled: threading.Event = field(default_factory=threading.Event)
    events: queue.Queue = field(default_factory=queue.Queue)


class StreamingScheduler:
    def __init__(self, backend, *, max_batch=4, max_pending=8, window_ms=5, max_tokens=16):
        if max_batch < 1 or max_pending < 1 or max_tokens < 1 or window_ms < 0:
            raise ValueError('invalid scheduler bounds')
        self.backend = backend
        self.max_batch, self.max_tokens = max_batch, max_tokens
        self.window = window_ms / 1000
        self.pending = queue.Queue(maxsize=max_pending)
        self.lock = threading.Lock()
        self.requests, self.records, self.batches = {}, {}, []
        self.rejected = 0
        self.closed = False
        self.thread = threading.Thread(target=self._work, daemon=True)
        self.thread.start()

    def submit(self, request_id, prompt):
        with self.lock:
            if self.closed:
                raise RuntimeError('scheduler closed')
            if request_id in self.records or request_id in self.requests:
                raise ValueError('duplicate request id')
            request = Request(request_id, prompt)
            try:
                self.pending.put_nowait(request)
            except queue.Full:
                self.rejected += 1
                raise
            self.requests[request_id] = request
            return request

    def cancel(self, request_id):
        with self.lock:
            request = self.requests.get(request_id)
            if request is None:
                return False
            request.cancelled.set()
            return True

    def snapshot(self):
        with self.lock:
            return {'active_or_queued': len(self.requests), 'rejected': self.rejected,
                    'records': dict(self.records), 'batches': list(self.batches)}

    def finish(self, request, record):
        with self.lock:
            self.records[request.request_id] = record
            self.requests.pop(request.request_id, None)
        request.events.put({'type': 'done', **record})

    def _work(self):
        while True:
            first = self.pending.get()
            if first is None:
                return
            group = [first]
            deadline = time.perf_counter() + self.window
            while len(group) < self.max_batch:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    break
                try:
                    group.append(self.pending.get(timeout=remaining))
                except queue.Empty:
                    break
            active = []
            for request in group:
                if request.cancelled.is_set():
                    self.finish(request, {'status': 'cancelled_queued', 'token_ids': []})
                else:
                    active.append(request)
            if not active:
                continue
            started = time.perf_counter()
            tokens = [[] for _ in active]
            first_token = [None for _ in active]
            prefill_ms, decode_ms = 0.0, 0.0
            peak_kv_bytes = 0
            error = None
            try:
                for step, event in enumerate(self.backend.batch_events([r.prompt for r in active], self.max_tokens, [r.cancelled for r in active])):
                    now = time.perf_counter()
                    peak_kv_bytes = max(peak_kv_bytes, event.get("kv_cache_bytes", 0))
                    if step == 0:
                        prefill_ms += event['step_ms']
                    else:
                        decode_ms += event['step_ms']
                    if len(event['token_ids']) != len(active):
                        raise RuntimeError('backend returned wrong batch size')
                    for i, request in enumerate(active):
                        if request.cancelled.is_set():
                            continue
                        token = event['token_ids'][i]
                        tokens[i].append(token)
                        if first_token[i] is None:
                            first_token[i] = (now - request.submitted) * 1000
                        request.events.put({'type': 'token', 'token_id': token, 'index': step})
            except Exception as exc:
                error = f'{type(exc).__name__}: {exc}'
            ended = time.perf_counter()
            with self.lock:
                self.batches.append({'request_ids': [r.request_id for r in active], 'size': len(active),
                                     'prefill_ms': prefill_ms, 'decode_ms': decode_ms,
                                     'service_wall_ms': (ended - started) * 1000, 'peak_kv_cache_bytes': peak_kv_bytes})
            for i, request in enumerate(active):
                status = 'failed' if error else ('cancelled_inflight' if request.cancelled.is_set() else 'completed')
                if status == 'completed' and len(tokens[i]) != self.max_tokens:
                    status, error = 'failed', 'backend returned incomplete output'
                self.finish(request, {'status': status, 'error': error, 'token_ids': tokens[i],
                        'ttft_ms': first_token[i], 'queue_wait_ms': (started - request.submitted) * 1000,
                        'completion_ms': (ended - request.submitted) * 1000,
                        'batch_size': len(active), 'prefill_batch_ms': prefill_ms, 'decode_batch_ms': decode_ms})

    def close(self):
        with self.lock:
            self.closed = True
        # Drain accepted work before the sentinel; send it only after the queue
        # is empty so a grouping window cannot accidentally consume it.
        deadline = time.monotonic() + 60
        while True:
            if time.monotonic() > deadline:
                raise RuntimeError("accepted requests did not drain")
            with self.lock:
                if not self.requests:
                    break
            time.sleep(0.01)
        self.pending.put(None)
        self.thread.join(timeout=30)
        if self.thread.is_alive():
            raise RuntimeError('GPU worker did not stop')


def make_server(scheduler, host='127.0.0.1', port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def reply(self, code, payload):
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.reply(200 if self.path == '/health' else 404, {'status': 'ok'} if self.path == '/health' else {'error': 'not found'})

        def do_POST(self):
            request = None
            try:
                self.connection.settimeout(30)
                size = int(self.headers.get('Content-Length', '0'))
                if not 1 <= size <= 65536 or self.headers.get('Transfer-Encoding'):
                    raise ValueError('bounded Content-Length required')
                body = json.loads(self.rfile.read(size))
                request_id = body.get('request_id')
                if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
                    raise ValueError('request_id required')
                if self.path == '/cancel':
                    self.reply(200, {'cancelled': scheduler.cancel(request_id)})
                    return
                if self.path != '/stream':
                    self.reply(404, {'error': 'not found'})
                    return
                prompt = body.get('prompt')
                if not isinstance(prompt, str) or not prompt or len(prompt) > 4096:
                    raise ValueError('bounded nonempty prompt required')
                request = scheduler.submit(request_id, prompt)
            except queue.Full:
                self.reply(429, {'error': 'queue full'})
                return
            except (ValueError, TypeError, AttributeError) as exc:
                self.reply(400, {'error': str(exc)})
                return
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-ndjson')
                self.end_headers()
                while True:
                    event = request.events.get(timeout=60)
                    self.wfile.write((json.dumps(event) + '\n').encode())
                    self.wfile.flush()
                    if event['type'] == 'done':
                        break
            except (OSError, queue.Empty):
                scheduler.cancel(request_id)
            finally:
                scheduler.cancel(request.request_id)
    class Server(ThreadingHTTPServer):
        request_queue_size = 128

    return Server((host, port), Handler)
