"""Token-boundary admission scheduler; compatible with the existing HTTP server.

The worker alone owns the backend. Admission prefill is synchronous; this is
continuous admission, not chunked prefill or prefill/decode overlap.
"""
import queue
import time
from dataclasses import dataclass

from real_model_service import Request, StreamingScheduler


@dataclass
class ContinuousRequest(Request):
    max_new_tokens: int = 16


class ContinuousScheduler(StreamingScheduler):
    def __init__(self, backend, *, slots=4, max_pending=32, max_tokens=16):
        self.live = {}
        self.admissions = []
        super().__init__(backend, max_batch=slots, max_pending=max_pending,
                         window_ms=0, max_tokens=max_tokens)

    def submit(self, request_id, prompt, max_new_tokens=None):
        limit = self.max_tokens if max_new_tokens is None else max_new_tokens
        if type(limit) is not int or not 1 <= limit <= self.max_tokens:
            raise ValueError(f'max_new_tokens must be an integer in 1..{self.max_tokens}')
        with self.lock:
            if self.closed:
                raise RuntimeError('scheduler closed')
            if request_id in self.records or request_id in self.requests:
                raise ValueError('duplicate request id')
            request = ContinuousRequest(request_id, prompt, max_new_tokens=limit)
            try:
                self.pending.put_nowait(request)
            except queue.Full:
                self.rejected += 1
                raise
            self.requests[request_id] = request
            return request

    def _complete(self, request, state, status, error=None):
        self.live.pop(request.request_id, None)
        self.finish(request, {'status': status, 'error': error, 'token_ids': state['tokens'],
            'max_new_tokens': request.max_new_tokens, 'finish_reason': state.get('finish_reason', status),
            'ttft_ms': state['ttft_ms'], 'queue_wait_ms': state['queue_ms'],
            'completion_ms': (time.perf_counter() - request.submitted) * 1000,
            'prefill_batch_ms': state['prefill_ms'], 'decode_batch_ms': state['decode_ms']})

    def _event(self, request, state, event):
        if request.cancelled.is_set():
            self.backend.cancel(state['handle'])
            self._complete(request, state, 'cancelled_inflight')
            return
        index = len(state['tokens'])
        if event['index'] != index:
            raise RuntimeError('out-of-order backend token')
        if index >= request.max_new_tokens:
            raise RuntimeError('backend exceeded output budget')
        state['tokens'].append(event['token_id'])
        if state['ttft_ms'] is None:
            state['ttft_ms'] = (time.perf_counter() - request.submitted) * 1000
        request.events.put({'type': 'token', 'token_id': event['token_id'], 'index': index})
        if event['status'] in ('completed', 'eos'):
            if event['status'] == 'completed' and len(state['tokens']) != request.max_new_tokens:
                raise RuntimeError('backend completed before output budget without EOS')
            state['finish_reason'] = 'eos' if event['status'] == 'eos' else 'length'
            self._complete(request, state, 'completed')

    def _admit(self, request):
        start = time.perf_counter()
        state = {'tokens': [], 'ttft_ms': None, 'queue_ms': (start - request.submitted) * 1000,
                 'prefill_ms': 0.0, 'decode_ms': 0.0, 'handle': None}
        if request.cancelled.is_set():
            self._complete(request, state, 'cancelled_queued')
            return
        try:
            peers = list(self.live)
            event = self.backend.admit(request.request_id, request.prompt, request.max_new_tokens)
            state['prefill_ms'] = (time.perf_counter() - start) * 1000
            state['handle'] = event['handle']
            self.live[request.request_id] = (request, state)
            with self.lock:
                self.admissions.append({'request_id': request.request_id, 'peers': peers,
                    'slot': event['handle'].slot, 'generation': event['handle'].generation})
            self._event(request, state, event)
        except Exception as exc:
            if state['handle'] is not None:
                self.backend.cancel(state['handle'])
            self._complete(request, state, 'failed', f'{type(exc).__name__}: {exc}')

    def _work(self):
        while True:
            for request, state in list(self.live.values()):
                if request.cancelled.is_set():
                    self.backend.cancel(state['handle'])
                    self._complete(request, state, 'cancelled_inflight')
            if not self.live:
                request = self.pending.get()
                if request is None:
                    return
                self._admit(request)
            # Bound admission work even when immediate-EOS requests keep arriving.
            for _ in range(self.max_batch - len(self.live)):
                try:
                    request = self.pending.get_nowait()
                except queue.Empty:
                    break
                if request is None:
                    return
                self._admit(request)
            if not self.live:
                continue
            try:
                start = time.perf_counter()
                events = self.backend.tick()
                elapsed = (time.perf_counter() - start) * 1000
                expected = {state['handle'] for _, state in self.live.values()}
                if len(events) != len(expected) or {e['handle'] for e in events} != expected:
                    raise RuntimeError('backend tick lost or duplicated a request')
                for event in events:
                    request, state = self.live[event['handle'].request_id]
                    state['decode_ms'] += elapsed
                    self._event(request, state, event)
            except Exception as exc:
                for request, state in list(self.live.values()):
                    self.backend.cancel(state['handle'])
                    self._complete(request, state, 'failed', f'{type(exc).__name__}: {exc}')

    def snapshot(self):
        state = super().snapshot()
        with self.lock:
            state['admissions'] = list(self.admissions)
        return state


class SlotBackend:
    def __init__(self, engine, tokenizer, *, use_graph=True, eos_token_id=None):
        self.engine, self.tokenizer = engine, tokenizer
        self.use_graph, self.eos_token_id = use_graph, eos_token_id

    def admit(self, request_id, prompt, max_tokens):
        encoded = self.tokenizer([prompt], return_tensors='pt').to(self.engine.ids.device)
        return self.engine.admit(request_id, encoded, max_tokens, self.eos_token_id)

    def cancel(self, handle):
        return self.engine.cancel(handle)

    def tick(self):
        return self.engine.tick(self.use_graph)
