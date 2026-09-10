#!/usr/bin/env python3
"""Serve one selected training checkpoint through the continuous HTTP stack on CUDA."""
import argparse
import json
import threading
import time
import urllib.request
from pathlib import Path
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from prepare_training_data import REVISION, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--serving-dir', type=Path, required=True)
    parser.add_argument('--max-new-tokens', type=int, default=4)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required for this smoke')
    if not 1 <= args.max_new_tokens <= 32:
        parser.error('max-new-tokens must be 1..32')
    sys.path.insert(0, str(args.serving_dir.resolve()))
    from continuous_http import make_server
    from continuous_service import ContinuousScheduler, SlotBackend
    from slot_decode import SlotDecode

    device = torch.device('cuda')
    tokenizer = AutoTokenizer.from_pretrained('openai-community/gpt2', revision=REVISION)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.checkpoint, local_files_only=True, attn_implementation='eager').to(device).eval()
    prompt = 'To be, or not to be'
    encoded = tokenizer(prompt, return_tensors='pt').to(device)
    with torch.inference_mode():
        reference = model.generate(
            **encoded, do_sample=False, max_new_tokens=args.max_new_tokens,
            eos_token_id=None, pad_token_id=tokenizer.pad_token_id,
        )[0, -args.max_new_tokens:].tolist()
    engine = SlotDecode(model, 1, 64)
    scheduler = ContinuousScheduler(
        SlotBackend(engine, tokenizer, use_graph=False), slots=1, max_pending=2, max_tokens=32)
    server = make_server(scheduler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}'
    tokens, terminal = [], None
    started = time.perf_counter()
    try:
        request = urllib.request.Request(
            url + '/stream',
            json.dumps({'request_id': 'gpu-checkpoint', 'prompt': prompt,
                        'max_new_tokens': args.max_new_tokens}).encode(),
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=180) as response:
            for line in response:
                event = json.loads(line)
                if event['type'] == 'token':
                    tokens.append(event['token_id'])
                elif event['type'] == 'done':
                    terminal = event
        scheduler.close()
        state = scheduler.snapshot()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
        if not scheduler.closed:
            scheduler.close()
    checks = {
        'token_parity': tokens == reference,
        'terminal_completed': terminal is not None and terminal['status'] == 'completed'
            and terminal['finish_reason'] == 'length'
            and terminal['max_new_tokens'] == args.max_new_tokens,
        'accounted': state['active_or_queued'] == 0,
        'cache_empty': all(bool(torch.count_nonzero(t) == 0)
                           for t in engine.keys + engine.values),
    }
    report = {
        'schema_version': 'gpu-checkpoint-serving-v0.1',
        'status': 'passed' if all(checks.values()) else 'failed',
        'evidence_kind': 'measured_cuda',
        'device': str(device),
        'checkpoint': str(args.checkpoint),
        'checkpoint_hashes': {f.name: sha(f) for f in sorted(args.checkpoint.iterdir()) if f.is_file()},
        'model_revision': REVISION,
        'tokenizer_revision': REVISION,
        'prompt': prompt,
        'reference_tokens': reference,
        'served_tokens': tokens,
        'terminal': terminal,
        'checks': checks,
        'scheduler': state,
        'elapsed_seconds': time.perf_counter() - started,
        'limitations': ['one request loopback smoke', 'no multi-request GPU capacity claim'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': checks,
                      'decoded': tokenizer.decode(tokens)}))
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
