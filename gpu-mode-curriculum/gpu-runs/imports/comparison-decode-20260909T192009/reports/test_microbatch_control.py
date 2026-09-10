import sys
from pathlib import Path
from types import SimpleNamespace
import threading

import pytest
import torch
from transformers import GPT2Config, GPT2LMHeadModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from microbatch_control import NativeBatchBackend, MicrobatchScheduler


class Encoded(dict):
    def to(self, device):
        return Encoded({key: value.to(device) for key,value in self.items()})


class Tokenizer:
    def __call__(self, prompts, **kwargs):
        rows = [[int(x) for x in prompt.split()] for prompt in prompts]
        width = max(map(len, rows))
        ids = torch.tensor([[0] * (width - len(row)) + row for row in rows])
        return Encoded(input_ids=ids, attention_mask=(ids != 0).long())


@pytest.mark.parametrize('device', ['cpu', pytest.param('cuda', marks=pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA unavailable'))])
def test_native_compaction_matches_individual_generation(device):
    torch.manual_seed(41)
    model = GPT2LMHeadModel(GPT2Config(vocab_size=61, n_positions=32, n_embd=32,
        n_layer=2, n_head=4, pad_token_id=0, bos_token_id=1, eos_token_id=None)).eval().to(device)
    model.config._attn_implementation = 'eager'
    tokenizer = Tokenizer()
    requests = [SimpleNamespace(request_id=str(i), prompt=prompt, max_new_tokens=count,
        cancelled=threading.Event()) for i,(prompt,count) in enumerate([('3 4',1),('5 6 7 8',5),('9',3)])]
    outputs = {r.request_id: [] for r in requests}
    for events in NativeBatchBackend(model, tokenizer).batch_events(requests):
        for event in events:
            outputs[event['request_id']].append(event['token_id'])
    with torch.inference_mode():
        for request in requests:
            expected = model.generate(**tokenizer([request.prompt]).to(device),
                do_sample=False, max_new_tokens=request.max_new_tokens)[0,-request.max_new_tokens:].tolist()
            assert outputs[request.request_id] == expected


def test_microbatch_terminal_budgets():
    class Backend:
        def cancel(self, handle):
            return False
        def batch_events(self, requests):
            for step in range(max(r.max_new_tokens for r in requests)):
                yield [{'request_id': r.request_id, 'token_id': step, 'index': step,
                        'status': 'completed' if step + 1 == r.max_new_tokens else 'active'}
                       for r in requests if step < r.max_new_tokens]
    scheduler = MicrobatchScheduler(Backend(), slots=2, max_tokens=5, window_ms=20)
    try:
        a,b = scheduler.submit('a','x',1), scheduler.submit('b','y',5)
        for request,count in ((a,1),(b,5)):
            while True:
                event = request.events.get(timeout=5)
                if event['type'] == 'done':
                    assert event['token_ids'] == list(range(count))
                    assert event['finish_reason'] == 'length'
                    break
    finally:
        scheduler.close()
