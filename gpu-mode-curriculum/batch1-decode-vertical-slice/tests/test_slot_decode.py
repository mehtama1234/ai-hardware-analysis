import sys
from pathlib import Path

import pytest
import torch
from transformers import GPT2Config, GPT2LMHeadModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slot_decode import SlotDecode


@pytest.mark.parametrize('device', ['cpu', pytest.param('cuda', marks=pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA unavailable'))])
def test_admission_reclamation_and_peer_isolation(device):
    torch.manual_seed(29)
    model = GPT2LMHeadModel(GPT2Config(vocab_size=61, n_positions=32, n_embd=32,
        n_head=4, n_layer=2, eos_token_id=None, pad_token_id=0, bos_token_id=1)).eval().to(device)
    model.config._attn_implementation = 'eager'
    engine = SlotDecode(model, 2, 24)
    if device == 'cuda':
        engine.capture()
    def encoded(ids):
        ids = torch.tensor([ids], device=device)
        return {'input_ids': ids, 'attention_mask': torch.ones_like(ids)}
    inputs = {'long': encoded([3, 4, 5, 6, 7]), 'cancel': encoded([9, 10]),
              'replacement': encoded([11, 12, 13]), 'last': encoded([8])}
    with torch.inference_mode():
        references = {name: model.generate(**value, max_new_tokens=7, do_sample=False)[0, -7:].tolist() for name, value in inputs.items()}
    outputs = {}
    def record(event):
        outputs.setdefault(event['handle'].request_id, []).append(event['token_id'])
    a = engine.admit('long', inputs['long'], 7)
    b = engine.admit('cancel', inputs['cancel'], 7)
    record(a); record(b)
    with pytest.raises(RuntimeError, match='no free'):
        engine.admit('full', inputs['last'], 1)
    for event in engine.tick(device == 'cuda'):
        record(event)
    peer = [tensor[a['handle'].slot].clone() for tensor in engine.keys + engine.values]
    assert engine.cancel(b['handle'])
    assert all(torch.count_nonzero(t[b['handle'].slot]) == 0 for t in engine.keys + engine.values)
    c = engine.admit('replacement', inputs['replacement'], 3)
    record(c)
    assert c['handle'].slot == b['handle'].slot
    assert not engine.cancel(b['handle'])  # stale handle cannot cancel new owner
    for before, tensor in zip(peer, engine.keys + engine.values):
        torch.testing.assert_close(before, tensor[a['handle'].slot], atol=0, rtol=0)
    for _ in range(2):
        for event in engine.tick(device == 'cuda'):
            record(event)
    assert engine.owners[c['handle'].slot] is None
    d = engine.admit('last', inputs['last'], 1)
    record(d)
    assert d['status'] == 'completed'
    while any(owner is not None for owner in engine.owners):
        for event in engine.tick(device == 'cuda'):
            record(event)
    assert outputs['long'] == references['long']
    assert outputs['cancel'] == references['cancel'][:2]
    assert outputs['replacement'] == references['replacement'][:3]
    assert outputs['last'] == references['last'][:1]
    assert engine.tick(device == 'cuda') == []
    eos = engine.admit('eos', inputs['last'], 7, eos_token_id=references['last'][0])
    assert eos['status'] == 'eos'
    assert all(owner is None for owner in engine.owners)
    assert all(torch.count_nonzero(t) == 0 for t in engine.keys + engine.values)
