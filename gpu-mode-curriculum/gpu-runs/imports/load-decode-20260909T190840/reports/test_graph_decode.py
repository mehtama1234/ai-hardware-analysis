import sys
from pathlib import Path

import pytest
import torch
from transformers import GPT2Config, GPT2LMHeadModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graph_decode import GraphDecode


@pytest.mark.parametrize('device', ['cpu', pytest.param('cuda', marks=pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA unavailable'))])
def test_static_decode_and_reused_graph_match_library(device):
    torch.manual_seed(19)
    model = GPT2LMHeadModel(GPT2Config(vocab_size=61, n_positions=32, n_embd=32,
        n_layer=2, n_head=4, attn_pdrop=0, resid_pdrop=0, embd_pdrop=0,
        bos_token_id=1, eos_token_id=None, pad_token_id=0)).eval().to(device)
    model.config._attn_implementation = 'eager'
    engine = GraphDecode(model, 2, 24)
    if device == 'cuda':
        engine.capture()
    pointers = [t.data_ptr() for t in engine.keys + engine.values]
    # Long -> short -> different long prompt tests stale cache and position reuse.
    for ids in ([[0, 0, 3, 4, 5], [7, 8, 9, 10, 11]], [[0, 3], [6, 7]],
                [[0, 8, 9, 10, 12], [3, 4, 5, 6, 7]]):
        ids = torch.tensor(ids, device=device)
        encoded = {'input_ids': ids, 'attention_mask': (ids != 0).long()}
        with torch.inference_mode():
            reference = model.generate(**encoded, max_new_tokens=5, do_sample=False)[:, -5:]
        # Switching modes must not leave logits pointing at eager allocations.
        if device == 'cuda':
            engine.generate(encoded, 5, use_graph=False)
        actual = engine.generate(encoded, 5, use_graph=device == 'cuda')
        assert torch.equal(actual, reference)
        assert pointers == [t.data_ptr() for t in engine.keys + engine.values]
        with pytest.raises(RuntimeError, match='exhausted'):
            engine.step()
        # Logits oracle catches errors hidden by argmax token parity.
        first = engine.prepare(encoded, 5)
        engine.step(device == 'cuda')
        full = torch.cat((ids, first[:, None]), 1)
        mask = torch.cat((encoded['attention_mask'], torch.ones_like(first[:, None])), 1)
        pos = mask.cumsum(-1) - 1
        pos.masked_fill_(mask == 0, 1)
        with torch.inference_mode():
            expected = model(input_ids=full, attention_mask=mask, position_ids=pos).logits[:, -1]
        torch.testing.assert_close(engine.logits, expected, atol=2e-5, rtol=2e-5)


def test_reject_capacity_and_invalid_padding():
    model = GPT2LMHeadModel(GPT2Config(vocab_size=20, n_positions=16, n_embd=8, n_layer=1, n_head=2)).eval()
    model.config._attn_implementation = 'eager'
    engine = GraphDecode(model, 1, 8)
    with pytest.raises(ValueError, match='capacity'):
        engine.prepare({'input_ids': torch.ones(1, 7, dtype=torch.long), 'attention_mask': torch.ones(1, 7)}, 2)
    with pytest.raises(ValueError, match='padding'):
        engine.prepare({'input_ids': torch.ones(1, 3, dtype=torch.long), 'attention_mask': torch.tensor([[1, 0, 1]])}, 2)
