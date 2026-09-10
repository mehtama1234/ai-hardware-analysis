"""Fixed-group controls with per-request output limits and early completion."""
import queue
import time

from continuous_service import ContinuousScheduler


class MicrobatchScheduler(ContinuousScheduler):
    def __init__(self, backend, *, slots=2, max_pending=8, max_tokens=32, window_ms=5):
        self.group_window = window_ms / 1000
        super().__init__(backend, slots=slots, max_pending=max_pending, max_tokens=max_tokens)

    def _work(self):
        while True:
            first = self.pending.get()
            if first is None:
                return
            group = [first]
            deadline = time.perf_counter() + self.group_window
            while len(group) < self.max_batch:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    break
                try:
                    request = self.pending.get(timeout=remaining)
                except queue.Empty:
                    break
                if request is None:
                    return
                group.append(request)
            active = []
            for request in group:
                state = {'tokens': [], 'ttft_ms': None, 'queue_ms': (time.perf_counter() - request.submitted) * 1000,
                         'prefill_ms': 0., 'decode_ms': 0., 'handle': None}
                if request.cancelled.is_set():
                    self._complete(request, state, 'cancelled_queued')
                else:
                    self.live[request.request_id] = (request, state)
                    active.append(request)
            if not active:
                continue
            try:
                for events in self.backend.batch_events(active):
                    for event in events:
                        # A request may be canceled after an earlier token in
                        # this fixed-group stream. Its backend can still emit
                        # already-in-flight rows; discard those rows after
                        # the scheduler has completed the request rather than
                        # raising a spurious KeyError for the peer request.
                        entry = self.live.get(event['request_id'])
                        if entry is None:
                            continue
                        request, state = entry
                        state['handle'] = event.get('handle')
                        self._event(request, state, event)
                for request, state in list(self.live.values()):
                    if request.cancelled.is_set():
                        self.backend.cancel(state['handle'])
                        self._complete(request, state, 'cancelled_inflight')
                if self.live:
                    raise RuntimeError('backend omitted terminal events')
            except Exception as exc:
                for request, state in list(self.live.values()):
                    self.backend.cancel(state['handle'])
                    self._complete(request, state, 'failed', f'{type(exc).__name__}: {exc}')


class NativeBatchBackend:
    def __init__(self, model, tokenizer, profile=False, cache_kind='dynamic'):
        self.model, self.tokenizer = model, tokenizer
        if cache_kind not in ('dynamic', 'static'):
            raise ValueError('cache_kind must be dynamic or static')
        self.cache_kind = cache_kind
        self.profile = bool(profile)
        self.profile_stats = {'model_calls': 0, 'total_batch_items': 0,
                              'prep_ms': 0.0, 'model_wall_ms': 0.0,
                              'model_cuda_ms': 0.0, 'batch_sizes': []}

    def reset_profile(self):
        self.profile_stats = {'model_calls': 0, 'total_batch_items': 0,
                              'prep_ms': 0.0, 'model_wall_ms': 0.0,
                              'model_cuda_ms': 0.0, 'batch_sizes': []}

    def profile_snapshot(self):
        return dict(self.profile_stats)

    def cancel(self, handle):
        # Request cancellation flags are consulted at each generator boundary.
        return False

    def batch_events(self, requests):
        import torch
        from transformers import DynamicCache, StaticCache
        with torch.inference_mode():
            encoded = self.tokenizer([r.prompt for r in requests], padding=True, return_tensors='pt').to(self.model.device)
            mask, ids = encoded['attention_mask'], encoded['input_ids']
            context_limit = getattr(self.model.config, 'n_positions', getattr(self.model.config, 'max_position_embeddings', 0))
            if ids.shape[1] + max(r.max_new_tokens for r in requests) > context_limit:
                raise ValueError('context limit exceeded')
            positions = mask.long().cumsum(-1) - 1
            positions.masked_fill_(mask == 0, 1)
            if self.cache_kind == 'static':
                cache = StaticCache(config=self.model.config, max_cache_len=context_limit)
            else:
                cache = DynamicCache(config=self.model.config)
            live = list(requests)
            index = 0
            while live:
                prep_start = time.perf_counter() if self.profile else None
                cache_position = torch.arange(ids.shape[1], device=ids.device) if index == 0 else torch.tensor([cache.get_seq_length()], device=ids.device)
                event_start = None
                if self.profile:
                    if prep_start is not None:
                        self.profile_stats['prep_ms'] += (time.perf_counter() - prep_start) * 1000
                    if ids.device.type == 'cuda':
                        torch.cuda.synchronize(ids.device)
                        event_start = torch.cuda.Event(enable_timing=True)
                        event_end = torch.cuda.Event(enable_timing=True)
                        event_start.record()
                    model_start = time.perf_counter()
                out = self.model(input_ids=ids, attention_mask=mask, position_ids=positions,
                                 past_key_values=cache, cache_position=cache_position, use_cache=True)
                if self.profile:
                    if event_start is not None:
                        event_end.record(); event_end.synchronize()
                        self.profile_stats['model_cuda_ms'] += event_start.elapsed_time(event_end)
                    self.profile_stats['model_wall_ms'] += (time.perf_counter() - model_start) * 1000
                    self.profile_stats['model_calls'] += 1
                    self.profile_stats['total_batch_items'] += len(live)
                    self.profile_stats['batch_sizes'].append(len(live))
                ids = out.logits[:, -1].argmax(-1, keepdim=True)
                tokens = ids[:, 0].tolist()
                yield [{'request_id': r.request_id, 'token_id': tokens[i], 'index': index,
                        'status': 'completed' if index + 1 == r.max_new_tokens else 'active'} for i,r in enumerate(live)]
                keep = [i for i,r in enumerate(live) if index + 1 < r.max_new_tokens and not r.cancelled.is_set()]
                if not keep:
                    break
                if len(keep) != len(live):
                    selected = torch.tensor(keep, device=ids.device)
                    if self.cache_kind == 'static':
                        # StaticLayer in Transformers 5.12 has no row-select
                        # helper; compact its fixed storage explicitly so the
                        # next call keeps the same batch semantics.
                        for layer in cache.layers:
                            layer.keys = layer.keys.index_select(0, selected)
                            layer.values = layer.values.index_select(0, selected)
                            layer.max_batch_size = len(keep)
                    else:
                        cache.batch_select_indices(selected)
                    ids = ids.index_select(0, selected)
                    mask = mask.index_select(0, selected)
                    live = [live[i] for i in keep]
                mask = torch.cat((mask, mask.new_ones((len(live), 1))), -1)
                positions = mask.long().sum(-1, keepdim=True) - 1
                index += 1


class GraphGroupBackend:
    def __init__(self, slot_backend):
        self.backend = slot_backend

    def cancel(self, handle):
        return self.backend.cancel(handle) if handle is not None else False

    def reset_profile(self):
        if hasattr(self.backend, 'reset_profile'):
            self.backend.reset_profile()

    def profile_snapshot(self):
        if hasattr(self.backend, 'profile_snapshot'):
            return self.backend.profile_snapshot()
        return None

    def batch_events(self, requests):
        live = {}
        try:
            for request in requests:
                event = self.backend.admit(request.request_id, request.prompt, request.max_new_tokens)
                if event['status'] == 'active':
                    live[request.request_id] = event['handle']
                yield [{**event, 'request_id': request.request_id}]
            while live:
                for request in requests:
                    if request.cancelled.is_set() and request.request_id in live:
                        # Scheduler has already completed canceled requests when
                        # processing their previous event; engine.cancel is idempotent.
                        self.cancel(live.pop(request.request_id))
                if not live:
                    break
                events = self.backend.tick()
                for event in events:
                    if event['status'] != 'active':
                        live.pop(event['handle'].request_id, None)
                yield [{**event, 'request_id': event['handle'].request_id} for event in events]
        finally:
            for handle in live.values():
                self.cancel(handle)
