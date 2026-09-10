"""Architecture-generic CUDA slot engine backed by Hugging Face KV caches."""
from dataclasses import dataclass
import torch


@dataclass(frozen=True)
class SlotHandle:
    slot: int
    generation: int
    request_id: str


class HFSlotDecode:
    def __init__(self, model, slots, capacity):
        if slots < 1 or capacity < 1:
            raise ValueError('invalid slot bounds')
        self.model, self.batch_size, self.capacity = model, slots, capacity
        self.device = next(model.parameters()).device
        self.ids = torch.zeros((slots, 1), dtype=torch.long, device=self.device)
        self.owners = [None] * slots
        self.generations = [0] * slots
        self.states = [None] * slots
        self.keys = [torch.zeros(1, device=self.device)]
        self.values = [torch.zeros(1, device=self.device)]

    def capture(self):
        return None

    @staticmethod
    def _positions(mask):
        positions = mask.long().cumsum(-1) - 1
        return positions.masked_fill(mask == 0, 0)

    @staticmethod
    def _cache_length(past):
        return past.get_seq_length() if hasattr(past, 'get_seq_length') else past[0][0].shape[-2]

    @torch.inference_mode()
    def admit(self, request_id, encoded, max_new_tokens, eos_token_id=None):
        if not isinstance(request_id, str) or not request_id:
            raise ValueError('nonempty request identity required')
        if not 1 <= max_new_tokens <= self.capacity:
            raise ValueError('request exceeds slot capacity')
        try:
            slot = self.owners.index(None)
        except ValueError:
            raise RuntimeError('no free slot') from None
        input_ids, mask = encoded['input_ids'], encoded['attention_mask']
        if input_ids.shape[0] != 1 or input_ids.shape[1] < 1:
            raise ValueError('one nonempty prompt required')
        positions = self._positions(mask)
        cache_position = torch.arange(input_ids.shape[1], device=self.device)
        out = self.model(input_ids=input_ids, attention_mask=mask, position_ids=positions,
                         cache_position=cache_position, use_cache=True)
        first = int(out.logits[0, -1].argmax().item())
        self.generations[slot] += 1
        handle = SlotHandle(slot, self.generations[slot], request_id)
        self.owners[slot] = handle
        self.states[slot] = {'past': out.past_key_values, 'mask': mask,
                             'next': first, 'emitted': 1, 'budget': max_new_tokens,
                             'eos': eos_token_id}
        self.ids[slot, 0] = first
        status = 'eos' if first == eos_token_id else 'completed' if max_new_tokens == 1 else 'active'
        event = {'handle': handle, 'token_id': first, 'index': 0, 'status': status}
        if status != 'active':
            self._clear(slot)
        return event

    @torch.inference_mode()
    def tick(self, _use_graph=False):
        events = []
        for slot, handle in enumerate(self.owners):
            if handle is None:
                continue
            state = self.states[slot]
            token = state['next']
            old_index = state['emitted']
            mask = torch.cat((state['mask'], state['mask'].new_ones((1, 1))), dim=1)
            input_ids = torch.tensor([[token]], dtype=torch.long, device=self.device)
            position_ids = mask.long().sum(-1, keepdim=True) - 1
            cache_position = torch.tensor([self._cache_length(state['past'])], device=self.device)
            out = self.model(input_ids=input_ids, attention_mask=mask,
                             position_ids=position_ids, cache_position=cache_position,
                             past_key_values=state['past'], use_cache=True)
            next_token = int(out.logits[0, -1].argmax().item())
            state.update({'past': out.past_key_values, 'mask': mask, 'next': next_token,
                          'emitted': old_index + 1})
            self.ids[slot, 0] = next_token
            status = 'eos' if next_token == state['eos'] else 'completed' if state['emitted'] >= state['budget'] else 'active'
            events.append({'handle': handle, 'token_id': next_token, 'index': old_index, 'status': status})
            if status != 'active':
                self._clear(slot)
        return events

    @torch.inference_mode()
    def cancel(self, handle):
        if not isinstance(handle, SlotHandle):
            return False
        slot = handle.slot
        if not (0 <= slot < self.batch_size) or self.owners[slot] != handle:
            return False
        self._clear(slot)
        return True

    def _clear(self, slot):
        self.owners[slot] = None
        self.states[slot] = None
        self.ids[slot].zero_()
