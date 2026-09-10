#!/usr/bin/env python3
"""Matched full-parameter GPT-2 fine-tuning with standard/recomputed output loss."""
import argparse
import gc
import json
import platform
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM

from prepare_training_data import REVISION, sha
from fused_training_kernels.linear_cross_entropy import linear_cross_entropy
from fused_training_kernels.evaluation import evaluate_tokens


def synchronize(device):
    if device.type == 'cuda':
        torch.cuda.synchronize(device)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'data')
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    p.add_argument('--steps', type=int, default=20)
    p.add_argument('--sequence', type=int, default=64)
    p.add_argument('--seeds', type=int, nargs='+', default=[7, 19, 41])
    p.add_argument('--chunk-size', type=int, default=16)
    p.add_argument('--validation-tokens', type=int, default=0,
        help='number of scored validation targets; zero evaluates the full split')
    p.add_argument('--save-checkpoints', action='store_true')
    args = p.parse_args()
    if min(args.steps, args.sequence, args.chunk_size) < 1 or args.sequence > 1024 or args.validation_tokens < 0:
        p.error('positive sizes required; sequence <= 1024')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / 'real-training.json'
    if report_path.exists():
        raise ValueError('use a fresh output directory')
    device = torch.device(args.device)
    if device.type == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable')
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    manifest = json.loads((args.data_dir / 'manifest.json').read_text())
    if manifest['tokenizer_revision'] != REVISION:
        raise ValueError('tokenizer revision mismatch')
    data = {}
    for split in ('train', 'validation'):
        row = manifest['splits'][split]
        path = args.data_dir / row['file']
        if sha(path) != row['sha256']:
            raise ValueError(f'{split} checksum mismatch')
        data[split] = np.load(path, allow_pickle=False)
    source_files = [Path(__file__), Path(__file__).with_name('prepare_training_data.py'),
        Path(__file__).parent / 'fused_training_kernels/linear_cross_entropy.py',
        Path(__file__).parent / 'fused_training_kernels/evaluation.py']
    validation_count = args.validation_tokens or len(data['validation']) - 1
    if validation_count > len(data['validation']) - 1:
        raise ValueError('requested validation targets exceed split')
    validation_tokens = data['validation'][:validation_count + 1]
    for source in source_files:
        target = args.output_dir / 'sources' / source.relative_to(Path(__file__).parent)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    report = {'schema_version': 'real-training-v0.2', 'status': 'running',
        'evidence_kind': f'measured_{device.type}', 'model_revision': REVISION,
        'data_manifest': manifest, 'data_manifest_sha256': sha(args.data_dir / 'manifest.json'),
        'source_hashes': {str(f.relative_to(Path(__file__).parent)): sha(f) for f in source_files},
        'runtime': {'python': platform.python_version(), 'torch': torch.__version__, 'device': str(device)},
        'protocol': {'steps': args.steps, 'sequence': args.sequence, 'batch': 1, 'seeds': args.seeds,
            'chunk_size': args.chunk_size, 'optimizer': 'AdamW lr=0.00001 default betas/eps/weight_decay',
            'parameters': 'all parameters including tied input/output embedding', 'dtype': 'float32',
            'dropout': 'disabled in both arms to isolate loss intervention',
            'evaluation': 'token-weighted validation; context resets per sequence block; each target scored once; test unused',
            'validation_targets': validation_count,
            'validation_scope': 'full_split' if validation_count == len(data['validation']) - 1 else 'prefix_probe',
            'timing': 'synchronized wall forward/backward/optimizer; includes first-step state initialization; evaluation and loading excluded',
            'selection': 'no cross-run selection; checkpoints optional; larger validation evaluation still required'},
        'runs': [], 'limitations': ['bounded integration experiment; not full quality acceptance',
            'no GPU claims from CPU execution', 'CPU peak memory not measured',
            'step samples are not independent performance trials']}
    def persist():
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    persist()
    try:
        for index, seed in enumerate(args.seeds):
            rng = np.random.default_rng(seed)
            starts = rng.integers(0, len(data['train']) - args.sequence, size=args.steps).tolist()
            modes = ('standard', 'recomputed') if index % 2 == 0 else ('recomputed', 'standard')
            for mode in modes:
                torch.manual_seed(seed)
                model = AutoModelForCausalLM.from_pretrained('openai-community/gpt2', revision=REVISION,
                    attn_implementation='eager').to(device)
                model.eval()  # Disable dropout, while leaving autograd and parameters enabled.
                optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
                def batch(split, start):
                    return torch.tensor(data[split][start:start + args.sequence + 1].copy(), device=device).unsqueeze(0)
                def evaluate():
                    return evaluate_tokens(model, validation_tokens, sequence=args.sequence, device=device)
                run = {'seed': seed, 'mode': mode, 'training_starts': starts,
                    'validation_before': evaluate(), 'steps': []}
                report['runs'].append(run)
                for step, start in enumerate(starts):
                    ids = batch('train', start)
                    optimizer.zero_grad(set_to_none=True)
                    if device.type == 'cuda':
                        torch.cuda.reset_peak_memory_stats(device)
                    synchronize(device)
                    begin = time.perf_counter()
                    hidden = model.transformer(input_ids=ids[:, :-1], use_cache=False).last_hidden_state.reshape(-1, model.config.n_embd)
                    labels = ids[:, 1:].reshape(-1)
                    loss = (linear_cross_entropy(hidden, model.lm_head.weight, labels, chunk_size=args.chunk_size)
                        if mode == 'recomputed' else F.cross_entropy(model.lm_head(hidden), labels))
                    loss.backward()
                    optimizer.step()
                    synchronize(device)
                    elapsed = time.perf_counter() - begin
                    value = float(loss.detach())
                    if not np.isfinite(value):
                        raise RuntimeError('nonfinite training loss')
                    run['steps'].append({'step': step, 'loss': value, 'seconds': elapsed,
                        'tokens_processed': (step + 1) * args.sequence,
                        'cuda_peak_allocated_bytes': torch.cuda.max_memory_allocated(device) if device.type == 'cuda' else None})
                    persist()
                run['validation_after'] = evaluate()
                if args.save_checkpoints:
                    checkpoint = args.output_dir / f'{seed}-{mode}'
                    model.save_pretrained(checkpoint)
                    torch.save({'optimizer': optimizer.state_dict(), 'torch_rng': torch.get_rng_state(),
                        'training_starts': starts, 'steps': args.steps}, checkpoint / 'training-state.pt')
                    run['checkpoint_hashes'] = {f.name: sha(f) for f in checkpoint.iterdir() if f.is_file()}
                run['status'] = 'completed'
                persist()
                del model, optimizer, hidden, loss
                gc.collect()
                if device.type == 'cuda':
                    torch.cuda.empty_cache()
        report['status'] = 'completed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        persist()
    print(json.dumps({'status': report['status'], 'runs': len(report['runs']), 'report': str(report_path)}))


if __name__ == '__main__':
    main()
