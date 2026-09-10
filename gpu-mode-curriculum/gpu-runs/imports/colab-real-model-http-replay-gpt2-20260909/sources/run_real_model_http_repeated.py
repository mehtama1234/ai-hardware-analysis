#!/usr/bin/env python3
"""Counterbalanced native/custom HTTP comparisons with a captured source bundle."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import statistics
import subprocess
import sys
import tarfile
import threading
from pathlib import Path
from types import SimpleNamespace

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import run_real_model_http as http
import run_real_model_fused_paged_decode as decode
from verify_real_model_system import validate

ROOT = Path(__file__).resolve().parent
MODES = ('eager_serial', 'eager_microbatch', 'sdpa_microbatch', 'paged_microbatch')


def source_closure(entrypoints):
    pending = list(entrypoints)
    sources = {}
    while pending:
        path = pending.pop().resolve()
        if path.name in sources:
            continue
        sources[path.name] = path
        for node in ast.walk(ast.parse(path.read_text())):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for name in names:
                candidate = path.parent / (name.split('.')[0] + '.py')
                if candidate.is_file():
                    pending.append(candidate)
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'reports')
    parser.add_argument('--rounds', type=int, default=4)
    args = parser.parse_args()
    if args.rounds < 4 or args.rounds % 4:
        parser.error('round count must be a positive multiple of four')
    if not torch.cuda.is_available():
        raise SystemExit('CUDA required')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(decode.MODEL_ID, revision=http.MODEL_REVISION, padding_side='left')
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(decode.MODEL_ID, revision=http.MODEL_REVISION,
            use_safetensors=True, attn_implementation='eager').to('cuda').eval()
    backend = http.GPT2Backend(model, tokenizer)
    references = []
    with torch.inference_mode():
        for prompt in http.PROMPTS:
            encoded = tokenizer([prompt], return_tensors='pt').to('cuda')
            references.append(model.generate(**encoded, max_new_tokens=http.MAX_TOKENS, do_sample=False,
                              eos_token_id=None, pad_token_id=tokenizer.pad_token_id)[0, -http.MAX_TOKENS:].tolist())
    extension = decode.build_extension()
    original = decode.gpt2_modeling.eager_attention_forward
    calls = [0]
    def counted(*params):
        result = extension.run_batch_into(*params)
        calls[0] += 1
        return result
    counted_module = SimpleNamespace(run_batch_into=counted)
    rounds = []
    try:
        for index in range(args.rounds):
            order = list(MODES[index % 4:] + MODES[:index % 4])
            modes = {}
            for name in order:
                decode.gpt2_modeling.eager_attention_forward = original
                model.config._attn_implementation = 'sdpa' if name == 'sdpa_microbatch' else 'eager'
                if name == 'paged_microbatch':
                    decode.install_fused_attention(model, counted_module)
                batch = 1 if name == 'eager_serial' else 4
                list(backend.batch_events(list(http.PROMPTS[:batch]), http.MAX_TOKENS, [threading.Event() for _ in range(batch)]))
                calls[0] = 0
                row = http.run_load(backend, f'{name}-r{index}', batch, references)
                row['custom_attention_calls'] = calls[0]
                row['attention_backend'] = model.config._attn_implementation
                modes[name] = row
                print(json.dumps({'round': index, 'mode': name, 'parity': row['output_parity'],
                                  'p95_ms': row['completion_ms_p95'], 'custom_calls': calls[0]}), flush=True)
            rounds.append({'index': index, 'order': order, 'modes': modes})
    finally:
        decode.gpt2_modeling.eager_attention_forward = original
        model.config._attn_implementation = 'eager'
    controls = http.run_load(backend, 'controls', 1, references, control=True)
    sources = source_closure([Path(__file__), ROOT / 'verify_real_model_system.py'])
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(sources.items())}
    freeze = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze', '--all'], text=True)
    requirements = args.output_dir / 'requirements.recorded.txt'
    requirements.write_text(freeze)
    manifest = args.output_dir / 'source-manifest.json'
    manifest.write_text(json.dumps({'source_hashes': hashes, 'model_revision': http.MODEL_REVISION,
                                    'requirements_sha256': hashlib.sha256(requirements.read_bytes()).hexdigest(),
                                    'command': 'python run_real_model_http_repeated.py --output-dir reports'}, indent=2) + '\n')
    bundle = args.output_dir / 'real-model-http-reproduction.tar.gz'
    with tarfile.open(bundle, 'w:gz') as archive:
        for name, path in sorted(sources.items()):
            archive.add(path, arcname=name)
        archive.add(requirements, arcname=requirements.name)
        archive.add(manifest, arcname=manifest.name)
    summaries = {}
    for name in MODES:
        summaries[name] = {key: [r['modes'][name][key] for r in rounds]
                           for key in ('completion_ms_p95', 'ttft_ms_median', 'output_tokens_per_second')}
    report = {'schema_version': 'real-model-http-repeated-v0.1', 'evidence_kind': 'measured_gpu',
              'gpu_execution_accepted': True, 'model_id': decode.MODEL_ID,
              'model_revision': http.MODEL_REVISION, 'tokenizer_revision': http.MODEL_REVISION,
              'device_name': torch.cuda.get_device_name(), 'dtype': str(model.dtype),
              'runtime': {'torch': torch.__version__, 'transformers': __import__('transformers').__version__, 'cuda': torch.version.cuda, 'python': sys.version},
              'command': [sys.executable, *sys.argv], 'source_hashes': hashes,
              'reference_token_ids': references,
              'protocol': {'prompts': list(http.PROMPTS), 'max_new_tokens': http.MAX_TOKENS,
                           'requests_per_mode': 16, 'round_count': args.rounds,
                           'mode_order': 'cyclic rotation; each mode occupies each position equally',
                           'arrival_ms': [(i // 4) * 20 + (i % 4) * .5 for i in range(16)],
                           'warmups_per_mode_per_round': 1, 'batch_window_ms': 5},
              'rounds': rounds, 'controls': controls, 'summary_samples': summaries,
              'reproduction_bundle': {'path': bundle.name, 'sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
                                      'source_manifest': manifest.name, 'requirements': requirements.name},
              'claim_boundary': 'Bounded loopback HTTP comparisons with counterbalanced order; not production capacity or model-quality evaluation.'}
    errors = validate(report)
    report['gpu_execution_accepted'] = not errors
    report['validation_errors'] = errors
    (args.output_dir / 'real-model-http-repeated.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': 'failed' if errors else 'passed', 'errors': errors}), flush=True)
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
