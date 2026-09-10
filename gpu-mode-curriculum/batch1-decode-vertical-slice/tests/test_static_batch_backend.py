import sys
from pathlib import Path
from types import SimpleNamespace

import torch
from transformers import GPT2Config, GPT2LMHeadModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from microbatch_control import NativeBatchBackend


class Tokenizer:
    def __call__(self, prompts, **kwargs):
        rows = [[int(x) for x in p.split()] for p in prompts]
        width = max(map(len, rows))
        ids = torch.tensor([[0] * (width - len(r)) + r for r in rows])
        return Encoded(input_ids=ids, attention_mask=(ids != 0).long())


class Encoded(dict):
    def to(self, device):
        return Encoded({key: value.to(device) for key, value in self.items()})


def test_static_cache_batch_backend_matches_generation_and_compaction():
    torch.manual_seed(101)
    model = GPT2LMHeadModel(GPT2Config(vocab_size=71, n_positions=48, n_embd=32,
        n_layer=2, n_head=4, pad_token_id=0, bos_token_id=1, eos_token_id=None)).eval()
    model.config._attn_implementation = 'eager'
    tokenizer = Tokenizer()
    requests = [SimpleNamespace(request_id=str(i), prompt=p, max_new_tokens=n,
        cancelled=__import__('threading').Event()) for i, (p, n) in enumerate((('3 4', 1), ('5 6 7 8', 5), ('9', 3)))]
    expected = {}
    with torch.inference_mode():
        for r in requests:
            encoded = tokenizer([r.prompt])
            expected[r.request_id] = model.generate(**encoded, do_sample=False,
                max_new_tokens=r.max_new_tokens)[0, -r.max_new_tokens:].tolist()

    backend = NativeBatchBackend(model, tokenizer, cache_kind='static')
    outputs = {r.request_id: [] for r in requests}
    for events in backend.batch_events(requests):
        for event in events:
            outputs[event['request_id']].append(event['token_id'])
    assert outputs == expected
