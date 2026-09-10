"""Offline tests of the real-model generation contract; no weights downloaded."""
import sys
from pathlib import Path

import pytest
import torch
from transformers import GPT2Config, GPT2LMHeadModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_real_model_fused_paged_decode as decode


@pytest.mark.parametrize("backend", ["eager", "sdpa"])
def test_left_padded_batch_matches_individual_and_library_generation(backend, monkeypatch):
    torch.manual_seed(7)
    config = GPT2Config(vocab_size=41, n_positions=32, n_embd=24,
                        n_layer=2, n_head=2, bos_token_id=1,
                        eos_token_id=None, pad_token_id=0)
    config._attn_implementation = backend
    model = GPT2LMHeadModel(config).eval()
    monkeypatch.setattr(decode, "MAX_NEW_TOKENS", 4)
    encoded = {"input_ids": torch.tensor([[0, 0, 5, 8], [3, 9, 7, 4]]),
               "attention_mask": torch.tensor([[0, 0, 1, 1], [1, 1, 1, 1]])}
    actual = decode.native_decode(model, encoded)
    with torch.inference_mode():
        expected = model.generate(**encoded, max_new_tokens=4, do_sample=False)[:, -4:]
    assert torch.equal(actual, expected)
    for index in range(2):
        ids = encoded["input_ids"][index][encoded["attention_mask"][index].bool()].unsqueeze(0)
        single = decode.native_decode(model, {"input_ids": ids, "attention_mask": torch.ones_like(ids)})
        assert torch.equal(actual[index], single[0])


@pytest.mark.parametrize('boolean', [True, False])
def test_vectorized_cache_offsets_match_first_allowed_mask_entry(boolean):
    mask = torch.tensor([[[[False, False, True, True]]], [[[True, True, True, True]]],
                         [[[False, False, False, False]]]])
    if not boolean:
        mask = torch.where(mask, 0.0, torch.finfo(torch.float32).min)
    offsets = decode.decode_start_offsets(mask, 3, 'cpu')
    assert offsets.dtype == torch.int32
    assert offsets.tolist() == [2, 0, 0]
    assert decode.decode_start_offsets(None, 3, 'cpu').tolist() == [0, 0, 0]
