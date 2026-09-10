import sys
from pathlib import Path

import pytest
import torch
from transformers import GPT2Config, GPT2LMHeadModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hf_slot_decode import HFSlotDecode


@pytest.mark.parametrize('device', ['cpu', pytest.param('cuda', marks=pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA unavailable'))])
def test_reusable_buffers_preserve_generation_and_reclamation(device):
    torch.manual_seed(73)
    model = GPT2LMHeadModel(GPT2Config(vocab_size=67, n_positions=48, n_embd=32,
        n_layer=2, n_head=4, pad_token_id=0, bos_token_id=1, eos_token_id=None)).eval().to(device)
    model.config._attn_implementation = 'eager'

    def encoded(values):
        ids = torch.tensor([values], dtype=torch.long, device=device)
        return {'input_ids': ids, 'attention_mask': torch.ones_like(ids)}

    inputs = {'a': encoded([3, 4, 5]), 'b': encoded([9, 8])}
    with torch.inference_mode():
        expected = {key: model.generate(**value, do_sample=False,
                    max_new_tokens=5)[0, -5:].tolist() for key, value in inputs.items()}

    engine = HFSlotDecode(model, slots=2, capacity=16)
    seen = {key: [] for key in inputs}
    first = engine.admit('a', inputs['a'], 5)
    second = engine.admit('b', inputs['b'], 5)
    seen['a'].append(first['token_id']); seen['b'].append(second['token_id'])
    assert engine.states[first['handle'].slot]['mask_buffer'].shape[-1] == 19
    while any(owner is not None for owner in engine.owners):
        for event in engine.tick():
            seen[event['handle'].request_id].append(event['token_id'])

    assert seen == expected
    assert all(owner is None for owner in engine.owners)
    assert engine.tick() == []
