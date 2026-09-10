"""Fixed-shape StaticCache CUDA-Graph bucket with recapture lifecycle."""
import time

import torch
from transformers import StaticCache


class StaticGraphBucket:
    def __init__(self, model, batch_size=2, max_cache_len=256):
        if batch_size < 1 or max_cache_len < 1:
            raise ValueError('invalid bucket bounds')
        self.model = model.eval()
        self.batch_size = batch_size
        self.max_cache_len = max_cache_len
        self.device = next(model.parameters()).device
        self.graph = None
        self.graph_output = None
        self.cache = None
        self.width = None
        self._ids = None
        self._positions = None
        self._cache_position = None
        self._mask = None

    @torch.inference_mode()
    def run(self, encoded, steps, *, recapture=True):
        ids, input_mask = encoded['input_ids'], encoded['attention_mask']
        if self.device.type != 'cuda':
            raise RuntimeError('CUDA required')
        if ids.shape[0] != self.batch_size or ids.shape[1] < 1 or steps < 1:
            raise ValueError('bucket shape or step bound invalid')
        width = ids.shape[1]
        if width + steps > self.max_cache_len:
            raise ValueError('bucket context exceeds max cache length')
        if not bool((input_mask[:, -1] == 1).all()):
            raise ValueError('each prompt must be nonempty')
        mask = torch.ones((self.batch_size, self.max_cache_len), dtype=input_mask.dtype, device=self.device)
        mask[:, :width] = input_mask
        positions = input_mask.long().cumsum(-1) - 1
        positions.masked_fill_(input_mask == 0, 1)
        cache = StaticCache(config=self.model.config, max_cache_len=self.max_cache_len)
        out = self.model(input_ids=ids, attention_mask=input_mask, position_ids=positions,
                         cache_position=torch.arange(width, device=self.device),
                         past_key_values=cache, use_cache=True)
        next_ids = out.logits[:, -1].argmax(-1, keepdim=True).contiguous()
        tokens = [next_ids[:, 0].clone()]
        if recapture or self.graph is None or self.width != width:
            # Warm up a separate cache; warm-up mutates cache state.
            warm_cache = StaticCache(config=self.model.config, max_cache_len=self.max_cache_len)
            warm_pos = torch.full((self.batch_size, 1), width, dtype=torch.long, device=self.device)
            warm_cp = torch.tensor([width], dtype=torch.long, device=self.device)
            for _ in range(3):
                self.model(input_ids=next_ids, attention_mask=mask, position_ids=warm_pos,
                           cache_position=warm_cp, past_key_values=warm_cache, use_cache=True)
            torch.cuda.synchronize(self.device)
            capture_start = time.perf_counter()
            self.graph = torch.cuda.CUDAGraph()
            self.cache = cache
            self._ids = next_ids
            self._positions = warm_pos.clone()
            self._cache_position = warm_cp.clone()
            self._mask = mask
            with torch.cuda.graph(self.graph):
                self.graph_output = self.model(input_ids=self._ids, attention_mask=self._mask,
                    position_ids=self._positions, cache_position=self._cache_position,
                    past_key_values=self.cache, use_cache=True)
            capture_ms = (time.perf_counter() - capture_start) * 1000
            self.width = width
        else:
            capture_ms = 0.0
        for step in range(steps - 1):
            self.graph.replay()
            token = self.graph_output.logits[:, -1].argmax(-1).clone()
            tokens.append(token)
            self._ids.copy_(token.unsqueeze(1))
            self._positions.fill_(width + step + 1)
            self._cache_position.fill_(width + step + 1)
        torch.cuda.synchronize(self.device)
        return torch.stack(tokens, dim=1), {'recapture_ms': capture_ms,
            'width': width, 'steps': steps, 'batch_size': self.batch_size,
            'max_cache_len': self.max_cache_len}
