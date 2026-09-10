#!/usr/bin/env python3
"""Compare every real-data GPT-2 gradient, parameter update and AdamW moment.

Reference tensors spill to a temporary directory so only one model and optimizer
are resident at a time. This correctness experiment does not benchmark speed.
"""
import argparse
import gc
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM

from prepare_training_data import REVISION, sha
from fused_training_kernels.linear_cross_entropy import linear_cross_entropy


def compare(actual, expected, *, atol, rtol):
    actual, expected = actual.detach().cpu(), expected.detach().cpu()
    if actual.shape != expected.shape or actual.numel() == 0:
        raise ValueError('matching nonempty tensor shapes required')
    actual, expected = actual.reshape(-1), expected.reshape(-1)
    finite, outside, maximum = True, 0, 0.0
    # GPT-2's tied embedding alone has over 38 million elements. Bound checker
    # temporaries instead of allocating several additional full-sized tensors.
    for start in range(0, actual.numel(), 262144):
        a, e = actual[start:start + 262144], expected[start:start + 262144]
        error = (a - e).abs()
        bound = atol + rtol * e.abs()
        finite = finite and bool(torch.isfinite(a).all() and torch.isfinite(e).all())
        outside += int((error > bound).sum())
        maximum = max(maximum, float(torch.nan_to_num(error, nan=float('inf')).max()))
    return {'passed': finite and outside == 0, 'finite': finite,
        'elements': actual.numel(), 'max_abs_error': maximum,
        'outside_tolerance': outside, 'atol': atol, 'rtol': rtol}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'data')
    p.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    p.add_argument('--sequence', type=int, default=8)
    p.add_argument('--seed', type=int, default=7)
    p.add_argument('--chunk-size', type=int, default=3)
    args = p.parse_args()
    if not 1 <= args.sequence <= 1024 or args.chunk_size < 1:
        p.error('sequence 1..1024 and positive chunk size required')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / 'real-training-parity.json'
    if output.exists():
        raise ValueError('use a fresh output directory')
    manifest = json.loads((args.data_dir / 'manifest.json').read_text())
    row = manifest['splits']['train']
    path = args.data_dir / row['file']
    if sha(path) != row['sha256'] or manifest['tokenizer_revision'] != REVISION:
        raise ValueError('training data/tokenizer identity mismatch')
    tokens = np.load(path, allow_pickle=False)
    start = int(np.random.default_rng(args.seed).integers(0, len(tokens) - args.sequence))
    device = torch.device(args.device)
    ids = torch.tensor(tokens[start:start + args.sequence + 1].copy(), device=device).unsqueeze(0)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    report = {'schema_version': 'real-training-parity-v0.1', 'status': 'running',
        'evidence_kind': f'measured_{device.type}', 'model_revision': REVISION,
        'torch': torch.__version__, 'data_manifest_sha256': sha(args.data_dir / 'manifest.json'),
        'training_start': start, 'input_and_target_ids': ids.tolist(), 'seed': args.seed,
        'sequence': args.sequence, 'chunk_size': args.chunk_size,
        'protocol': 'one full-parameter AdamW update per arm; lr=1e-5, dropout disabled, float32, TF32 disabled; same pinned initialization',
        'tolerances': {'gradient_and_moments': {'atol': 2e-5, 'rtol': 5e-4},
            'parameters': {'atol': 2e-6, 'rtol': 2e-5}, 'loss': {'atol': 5e-5, 'rtol': 2e-5}},
        'checks': {}, 'losses': {}, 'source_hashes': {}}
    for name in ('check_real_training_parity.py', 'prepare_training_data.py', 'fused_training_kernels/linear_cross_entropy.py'):
        source = Path(__file__).parent / name
        target = args.output_dir / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        report['source_hashes'][name] = sha(source)
    def persist():
        output.write_text(json.dumps(report, indent=2) + '\n')
    persist()
    try:
        with tempfile.TemporaryDirectory(prefix='gpt2-training-parity-') as tmp:
            tmp = Path(tmp)
            for mode in ('standard', 'recomputed'):
                torch.manual_seed(args.seed)
                model = AutoModelForCausalLM.from_pretrained('openai-community/gpt2', revision=REVISION,
                    attn_implementation='eager').to(device).eval()
                optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
                hidden = model.transformer(input_ids=ids[:, :-1], use_cache=False).last_hidden_state.reshape(-1, model.config.n_embd)
                labels = ids[:, 1:].reshape(-1)
                loss = (F.cross_entropy(model.lm_head(hidden), labels) if mode == 'standard' else
                    linear_cross_entropy(hidden, model.lm_head.weight, labels, chunk_size=args.chunk_size))
                loss.backward()
                report['losses'][mode] = float(loss.detach())
                for i, (name, parameter) in enumerate(model.named_parameters()):
                    if parameter.grad is None:
                        raise AssertionError(f'missing gradient: {name}')
                    if mode == 'standard':
                        torch.save(parameter.grad.detach().cpu(), tmp / f'gradient-{i}.pt')
                    else:
                        reference = torch.load(tmp / f'gradient-{i}.pt', weights_only=True)
                        report['checks'][name] = {'gradient': compare(parameter.grad, reference,
                            **report['tolerances']['gradient_and_moments'])}
                optimizer.step()
                for i, (name, parameter) in enumerate(model.named_parameters()):
                    state = optimizer.state[parameter]
                    values = {'parameter': parameter.detach().cpu(),
                        'exp_avg': state['exp_avg'].detach().cpu(),
                        'exp_avg_sq': state['exp_avg_sq'].detach().cpu()}
                    if mode == 'standard':
                        torch.save(values, tmp / f'updated-{i}.pt')
                    else:
                        reference = torch.load(tmp / f'updated-{i}.pt', weights_only=True)
                        for key, value in values.items():
                            tolerance = report['tolerances']['parameters' if key == 'parameter' else 'gradient_and_moments']
                            report['checks'][name][key] = compare(value, reference[key], **tolerance)
                persist()
                del model, optimizer, hidden, loss, parameter, state, values
                gc.collect()
                if device.type == 'cuda':
                    torch.cuda.empty_cache()
            report['loss_check'] = compare(torch.tensor(report['losses']['recomputed']),
                torch.tensor(report['losses']['standard']), **report['tolerances']['loss'])
            report['status'] = 'passed' if report['loss_check']['passed'] and all(
                check['passed'] for checks in report['checks'].values() for check in checks.values()) else 'failed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        persist()
    print(json.dumps({'status': report['status'], 'parameter_tensors': len(report['checks'])}), flush=True)
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
