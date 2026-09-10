#!/usr/bin/env python3
"""Real HTTP proof of graph slot reuse while an independent peer is active."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import shutil
import threading
import time
import urllib.request
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from continuous_service import ContinuousScheduler, SlotBackend
from real_model_service import make_server
from slot_decode import SlotDecode

MODEL = 'openai-community/gpt2'
REVISION = '607a30d783dfa663caf39e06633721c8d4cfcd7e'
PROMPTS = {'peer': 'The history of computer systems includes many advances because',
    'cancel': 'A short story about a small dog',
    'replacement': 'Paris is a city in France and its history'}


def post(url, payload):
    return urllib.request.urlopen(urllib.request.Request(url, json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}), timeout=120)


def client(url, name, cancellation=None):
    started = time.perf_counter()
    tokens, times, terminal, acknowledgement = [], [], None, None
    with post(url + '/stream', {'request_id': name, 'prompt': PROMPTS[name]}) as response:
        for line in response:
            event = json.loads(line)
            if event['type'] == 'token':
                tokens.append(event['token_id'])
                times.append((time.perf_counter() - started) * 1000)
                if cancellation is not None and len(tokens) == 2:
                    with post(url + '/cancel', {'request_id': name}) as reply:
                        acknowledgement = json.load(reply)['cancelled']
                    cancellation.set()
            else:
                terminal = event
    return {'token_ids': tokens, 'token_arrival_ms': times, 'terminal': terminal,
            'cancel_ack': acknowledgement, 'completion_ms': (time.perf_counter() - started) * 1000}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise SystemExit('CUDA required')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION,
        attn_implementation='eager', use_safetensors=True).cuda().eval()
    with torch.inference_mode():
        references = {name: model.generate(**tokenizer([prompt], return_tensors='pt').to('cuda'),
            do_sample=False, max_new_tokens=32, eos_token_id=None,
            pad_token_id=tokenizer.pad_token_id)[0, -32:].tolist() for name, prompt in PROMPTS.items()}
    engine = SlotDecode(model, 2, 256)
    engine.capture()
    scheduler = ContinuousScheduler(SlotBackend(engine, tokenizer), slots=2, max_tokens=32)
    server = make_server(scheduler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}'
    signal = threading.Event()
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            peer = pool.submit(client, url, 'peer')
            cancelled = pool.submit(client, url, 'cancel', signal)
            if not signal.wait(60):
                raise RuntimeError('cancellation acknowledgement timed out')
            replacement = pool.submit(client, url, 'replacement')
            clients = {'peer': peer.result(), 'cancel': cancelled.result(), 'replacement': replacement.result()}
        scheduler.close()
        state = scheduler.snapshot()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
        if not scheduler.closed:
            scheduler.close()
    admission = next(a for a in state['admissions'] if a['request_id'] == 'replacement')
    original = next(a for a in state['admissions'] if a['request_id'] == 'cancel')
    checks = {
        'peer_output_parity': clients['peer']['token_ids'] == references['peer'],
        'replacement_output_parity': clients['replacement']['token_ids'] == references['replacement'],
        'cancelled_prefix_parity': clients['cancel']['token_ids'] == references['cancel'][:len(clients['cancel']['token_ids'])],
        'cancelled_before_completion': clients['cancel']['cancel_ack'] is True and
            clients['cancel']['terminal']['status'] == 'cancelled_inflight' and len(clients['cancel']['token_ids']) < 32,
        'replacement_admitted_with_peer_active': 'peer' in admission['peers'],
        'cancelled_slot_reused': admission['slot'] == original['slot'] and admission['generation'] > original['generation'],
        'all_requests_accounted': state['active_or_queued'] == 0 and set(state['records']) == set(PROMPTS),
        'cache_empty_after_drain': all(bool(torch.count_nonzero(t) == 0) for t in engine.keys + engine.values),
    }
    sources = args.output_dir / 'sources'
    sources.mkdir(exist_ok=True)
    hashes = {}
    for name in ('graph_decode.py', 'slot_decode.py', 'continuous_service.py', 'real_model_service.py', 'run_continuous_http.py'):
        source = Path(__file__).with_name(name)
        shutil.copy2(source, sources / name)
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    report = {'schema_version': 'gpt2-continuous-http-v0.1', 'evidence_kind': 'measured_gpu',
        'status': 'passed' if all(checks.values()) else 'failed', 'checks': checks,
        'model_revision': REVISION, 'tokenizer_revision': REVISION, 'source_hashes': hashes,
        'device': torch.cuda.get_device_name(), 'torch': torch.__version__,
        'prompts': PROMPTS, 'references': references, 'clients': clients, 'scheduler': state,
        'limitations': ['Three-request loopback functional proof, not capacity/performance acceptance.',
            'Synchronous unchunked prefill; no independent replay or overload sweep.']}
    (args.output_dir / 'continuous-http.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': checks}), flush=True)
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
