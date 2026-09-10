#!/usr/bin/env python3
"""Isolate chunked projection versus custom backward on real pretrained states."""
import argparse
import gc
import json
import shutil
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM
from prepare_training_data import REVISION, sha
from check_real_training_parity import compare
from fused_training_kernels.linear_cross_entropy import linear_cross_entropy


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / 'loss-numerics.json'
    if output.exists():
        raise ValueError('fresh output required')
    root = Path(__file__).parent
    manifest = json.loads((root / 'data/manifest.json').read_text())
    data_path = root / 'data' / manifest['splits']['train']['file']
    if sha(data_path) != manifest['splits']['train']['sha256']:
        raise ValueError('data checksum')
    tokens = np.load(data_path, allow_pickle=False)
    start = int(np.random.default_rng(7).integers(0, len(tokens) - 8))
    ids = torch.tensor(tokens[start:start + 9].copy()).unsqueeze(0)
    model = AutoModelForCausalLM.from_pretrained('openai-community/gpt2', revision=REVISION,
        attn_implementation='eager').eval()
    with torch.no_grad():
        hidden = model.transformer(input_ids=ids[:, :-1], use_cache=False).last_hidden_state.reshape(-1, 768).detach()
    weight = model.lm_head.weight.detach()
    labels = ids[:, 1:].reshape(-1)
    del model
    gc.collect()
    report = {'evidence_kind': 'measured_cpu', 'model_revision': REVISION,
        'training_start': start, 'ids': ids.tolist(), 'rows': [], 'source_hashes': {}}
    for name in ('diagnose_loss_numerics.py', 'check_real_training_parity.py', 'prepare_training_data.py',
                 'fused_training_kernels/linear_cross_entropy.py'):
        target = args.output_dir / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
        report['source_hashes'][name] = sha(target)
    for chunk, mode in ((8, 'native'), (3, 'native_chunked'), (8, 'custom'), (3, 'custom'), (3, 'logsoftmax_chunked')):
        x = hidden.clone().requires_grad_()
        if mode == 'custom':
            loss = linear_cross_entropy(x, weight, labels, chunk_size=chunk)
        elif mode == 'logsoftmax_chunked':
            loss = sum(-(x[i:i+chunk] @ weight.t()).log_softmax(-1)
                .gather(1, labels[i:i+chunk, None]).sum() for i in range(0, 8, chunk)) / 8
        else:
            loss = sum(F.cross_entropy(x[i:i+chunk] @ weight.t(), labels[i:i+chunk], reduction='sum')
                for i in range(0, 8, chunk)) / 8
        gradient, = torch.autograd.grad(loss, x)
        if mode == 'native':
            reference = gradient.detach().clone()
            reference_loss = loss.detach().clone()
        report['rows'].append({'mode': mode, 'chunk': chunk, 'loss': float(loss.detach()),
            'loss_error': float((loss.detach() - reference_loss).abs()),
            'hidden_gradient': compare(gradient, reference, atol=2e-5, rtol=5e-4)})
        output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['rows'], indent=2))


if __name__ == '__main__':
    main()
