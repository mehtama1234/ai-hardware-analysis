#!/usr/bin/env python3
"""Pretrained GPT-2 slot admission/cancellation/reuse proof on a CUDA device."""
import argparse
from dataclasses import asdict
import hashlib
import json
import platform
import shutil
import sys
import time
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from slot_decode import SlotDecode

MODEL = 'openai-community/gpt2'
REVISION = '607a30d783dfa663caf39e06633721c8d4cfcd7e'
PROMPTS = {'peer': 'The history of computers includes many important developments because',
    'cancel': 'A short story about a small dog',
    'replacement': 'Paris is a city in France and its history',
    'single': 'The capital of France is', 'eos': 'The capital of France is'}


def exercise(model, encoded, references, use_graph):
    engine = SlotDecode(model, 2, 128)
    if use_graph:
        engine.capture()
    outputs, events, checks = {}, [], {}
    def record(event):
        request = event['handle'].request_id
        outputs.setdefault(request, []).append(event['token_id'])
        events.append({**event, 'handle': asdict(event['handle'])})
    def admit(name, count, eos=None):
        event = engine.admit(name, encoded[name], count, eos)
        record(event)
        return event['handle']
    peer = admit('peer', 12)
    cancelled = admit('cancel', 12)
    for event in engine.tick(use_graph):
        record(event)
    preserved = [tensor[peer.slot].clone() for tensor in engine.keys + engine.values]
    checks['cancellation_ack'] = engine.cancel(cancelled)
    checks['cancelled_cache_cleared'] = all(bool(torch.count_nonzero(t[cancelled.slot]) == 0) for t in engine.keys + engine.values)
    replacement = admit('replacement', 4)
    checks['slot_reused'] = replacement.slot == cancelled.slot and replacement.generation > cancelled.generation
    checks['stale_cancel_rejected'] = not engine.cancel(cancelled)
    checks['peer_cache_preserved'] = all(torch.equal(old, tensor[peer.slot]) for old, tensor in zip(preserved, engine.keys + engine.values))
    for _ in range(3):
        for event in engine.tick(use_graph):
            record(event)
    checks['completed_slot_reclaimed'] = engine.owners[replacement.slot] is None
    single = admit('single', 1)
    checks['one_token_reclaimed'] = engine.owners[single.slot] is None
    # Controlled EOS token: second library token, or first if both are identical.
    stop = references['eos'][1]
    eos_length = references['eos'].index(stop) + 1
    eos = admit('eos', 12, stop)
    while any(owner is not None for owner in engine.owners):
        for event in engine.tick(use_graph):
            record(event)
    expected_lengths = {'peer': 12, 'cancel': 2, 'replacement': 4, 'single': 1, 'eos': eos_length}
    checks['outputs_match_individual_library'] = all(outputs[name] == references[name][:length] for name, length in expected_lengths.items())
    checks['all_owners_released'] = all(owner is None for owner in engine.owners)
    checks['all_cache_cleared'] = all(bool(torch.count_nonzero(t) == 0) for t in engine.keys + engine.values)
    checks['idle_tick_empty'] = engine.tick(use_graph) == []
    checks['stale_eos_cancel_rejected'] = not engine.cancel(eos)
    return {'checks': checks, 'events': events, 'outputs': outputs,
            'expected_lengths': expected_lengths, 'controlled_eos_token_id': stop,
            'passed': all(checks.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).parent / 'reports/slot-decode')
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise SystemExit('CUDA required; no GPU evidence produced')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    torch.backends.cuda.matmul.allow_tf32 = False
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION,
        attn_implementation='eager', use_safetensors=True).cuda().eval()
    encoded = {name: tokenizer([prompt], return_tensors='pt').to('cuda') for name, prompt in PROMPTS.items()}
    with torch.inference_mode():
        references = {name: model.generate(**value, max_new_tokens=12, do_sample=False,
            eos_token_id=None, pad_token_id=tokenizer.pad_token_id)[0, -12:].tolist() for name, value in encoded.items()}
    rows = {}
    for graph in (False, True):
        mode = 'graph' if graph else 'eager'
        torch.cuda.synchronize()
        started = time.perf_counter()
        rows[mode] = exercise(model, encoded, references, graph)
        torch.cuda.synchronize()
        rows[mode]['proof_wall_seconds_including_checks_and_capture'] = time.perf_counter() - started
        print(json.dumps({'mode': mode, 'checks': rows[mode]['checks']}), flush=True)
    sources = args.output_dir / 'sources'
    sources.mkdir(exist_ok=True)
    hashes = {}
    for name in ('graph_decode.py', 'slot_decode.py', 'run_slot_decode.py'):
        source = Path(__file__).with_name(name)
        shutil.copy2(source, sources / name)
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    report = {'schema_version': 'gpt2-slot-lifecycle-v0.1', 'evidence_kind': 'measured_gpu',
        'status': 'passed' if all(row['passed'] for row in rows.values()) else 'failed',
        'model_id': MODEL, 'model_revision': REVISION, 'tokenizer_revision': REVISION,
        'runtime': {'torch': torch.__version__, 'transformers': transformers.__version__,
            'python': platform.python_version(), 'device': torch.cuda.get_device_name(), 'dtype': str(model.dtype)},
        'source_hashes': hashes, 'prompts': PROMPTS, 'reference_tokens': references, 'modes': rows,
        'limitations': ['Single-worker execution; synchronous admission prefill.',
            'Controlled EOS probe, not natural EOS frequency.',
            'No HTTP, sustained-load, performance-comparison, or independent replay claim.']}
    (args.output_dir / 'slot-lifecycle.json').write_text(json.dumps(report, indent=2) + '\n')
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
