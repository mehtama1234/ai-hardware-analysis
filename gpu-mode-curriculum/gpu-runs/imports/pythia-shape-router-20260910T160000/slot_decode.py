"""Single-worker GPT-2 slot ownership and graph replay with per-request cursors.

Admission prefill is synchronous. Slots advance together at decode boundaries,
but have independent positions, lengths, output budgets, and reclamation.
"""
from dataclasses import dataclass
import math

import torch
from graph_decode import GraphDecode


@dataclass(frozen=True)
class SlotHandle:
    slot: int
    generation: int
    request_id: str


class SlotDecode(GraphDecode):
    def __init__(self, model, slots, capacity):
        super().__init__(model, slots, capacity)
        self.cursor = torch.zeros(slots, dtype=torch.long, device=self.ids.device)
        self.active = torch.zeros(slots, dtype=torch.bool, device=self.ids.device)
        self.owners = [None] * slots
        self.generations = [0] * slots
        self.budgets = [0] * slots
        self.emitted = [0] * slots
        self.eos = [None] * slots

    def _step(self):
        core = self.model.transformer
        hidden = core.wte(self.ids) + core.wpe(self.positions)
        self.mask.scatter_(1, self.cursor[:, None], self.active[:, None])
        for i, block in enumerate(core.h):
            residual = hidden
            q, k, v = block.attn.c_attn(block.ln_1(hidden)).split(self.model.config.n_embd, dim=2)
            def heads(x):
                return x.view(self.batch_size, 1, block.attn.num_heads, block.attn.head_dim).transpose(1, 2)
            q, k, v = heads(q), heads(k), heads(v)
            indices = self.cursor[:, None, None, None].expand_as(k)
            live = self.active[:, None, None, None]
            self.keys[i].scatter_(2, indices, k * live)
            self.values[i].scatter_(2, indices, v * live)
            scaling = 1 / math.sqrt(block.attn.head_dim) if self.model.config.scale_attn_weights else 1.0
            if self.model.config.scale_attn_by_inverse_layer_idx:
                scaling /= float(i + 1)
            scores = (q @ self.keys[i].transpose(-1, -2)) * scaling
            scores = scores.masked_fill(~self.mask[:, None, None, :], torch.finfo(scores.dtype).min)
            attention = (scores.softmax(-1).to(v.dtype) @ self.values[i]).transpose(1, 2).reshape(self.batch_size, 1, -1)
            hidden = residual + block.attn.c_proj(attention)
            hidden = hidden + block.mlp(block.ln_2(hidden))
        self.logits = self.model.lm_head(core.ln_f(hidden))[:, -1]
        self.ids.copy_(torch.where(self.active[:, None], self.logits.argmax(-1, keepdim=True), 0))
        self.positions.add_(self.active[:, None])
        self.cursor.add_(self.active)

    @torch.inference_mode()
    def capture(self):
        if any(owner is not None for owner in self.owners):
            raise RuntimeError('capture must precede admission')
        super().capture()
        for slot in range(self.batch_size):
            self._clear(slot)

    @torch.inference_mode()
    def _clear(self, slot):
        self.active[slot] = False
        self.cursor[slot] = 0
        self.positions[slot].zero_()
        self.ids[slot].zero_()
        self.mask[slot].zero_()
        for tensor in self.keys + self.values:
            tensor[slot].zero_()
        if self.logits is not None:
            self.logits[slot].zero_()
        if self.graph_logits is not None:
            self.graph_logits[slot].zero_()
        self.owners[slot] = None
        self.budgets[slot] = self.emitted[slot] = 0
        self.eos[slot] = None

    def _owned(self, handle):
        return (isinstance(handle, SlotHandle) and 0 <= handle.slot < self.batch_size
                and self.owners[handle.slot] == handle)

    @torch.inference_mode()
    def cancel(self, handle):
        if not self._owned(handle):
            return False
        self._clear(handle.slot)
        return True

    @torch.inference_mode()
    def admit(self, request_id, encoded, max_new_tokens, eos_token_id=None):
        if not isinstance(request_id, str) or not request_id:
            raise ValueError('nonempty request identity required')
        if any(owner is not None and owner.request_id == request_id for owner in self.owners):
            raise ValueError('duplicate active request')
        ids, mask = encoded['input_ids'], encoded['attention_mask']
        if ids.ndim != 2 or ids.shape[0] != 1 or ids.shape[1] == 0 or mask.shape != ids.shape or not bool((mask == 1).all()):
            raise ValueError('admission requires one nonempty unpadded prompt')
        width = ids.shape[1]
        if max_new_tokens < 1 or width + max_new_tokens > self.capacity:
            raise ValueError('request exceeds slot capacity')
        try:
            slot = self.owners.index(None)
        except ValueError:
            raise RuntimeError('no free slot') from None
        # No ownership/cache mutation until prefill succeeds.
        out = self.model(**encoded, use_cache=True)
        first = int(out.logits[0, -1].argmax().item())
        self._clear(slot)
        for i, layer in enumerate(out.past_key_values.layers):
            self.keys[i][slot, :, :width].copy_(layer.keys[0])
            self.values[i][slot, :, :width].copy_(layer.values[0])
        self.mask[slot, :width] = True
        self.cursor[slot] = width
        self.positions[slot] = width
        self.ids[slot] = first
        self.active[slot] = True
        self.generations[slot] += 1
        handle = SlotHandle(slot, self.generations[slot], request_id)
        self.owners[slot] = handle
        self.budgets[slot], self.emitted[slot], self.eos[slot] = max_new_tokens, 1, eos_token_id
        status = 'eos' if first == eos_token_id else 'completed' if max_new_tokens == 1 else 'active'
        if status != 'active':
            self._clear(slot)
        return {'handle': handle, 'token_id': first, 'index': 0, 'status': status}

    @torch.inference_mode()
    def tick(self, use_graph=False):
        if not any(owner is not None for owner in self.owners):
            return []
        if use_graph:
            if self.graph is None:
                raise RuntimeError('capture required')
            self.graph.replay()
            self.logits = self.graph_logits
        else:
            self._step()
        tokens = self.ids[:, 0].tolist()
        events = []
        for slot, handle in enumerate(self.owners):
            if handle is None:
                continue
            index = self.emitted[slot]
            self.emitted[slot] += 1
            status = ('eos' if tokens[slot] == self.eos[slot] else
                      'completed' if self.emitted[slot] >= self.budgets[slot] else 'active')
            events.append({'handle': handle, 'token_id': tokens[slot], 'index': index, 'status': status})
            if status != 'active':
                self._clear(slot)
        return events

    def prepare(self, *args, **kwargs):
        raise RuntimeError('use admit() for slot ownership')

    def step(self, *args, **kwargs):
        raise RuntimeError('use tick() for slot ownership')
