#!/usr/bin/env python3
"""Memory-bounded real GPT-2 output-head parity check."""
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
    p.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'data')
    p.add_argument('--chunk-size', type=int, default=3)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / 'output-head-parity.json'
    if output.exists():
        raise ValueError('fresh output directory required')
    root = Path(__file__).parent
    manifest = json.loads((args.data_dir / 'manifest.json').read_text())
    data_path = args.data_dir / manifest['splits']['train']['file']
    if sha(data_path) != manifest['splits']['train']['sha256']:
        raise ValueError('training data checksum')
    tokens = np.load(data_path, allow_pickle=False)
    start = int(np.random.default_rng(7).integers(0, len(tokens) - 8))
    ids = torch.tensor(tokens[start:start + 9].copy()).unsqueeze(0)
    torch.manual_seed(7)
    model = AutoModelForCausalLM.from_pretrained('openai-community/gpt2', revision=REVISION,
        attn_implementation='eager').eval()
    with torch.no_grad():
        hidden = model.transformer(input_ids=ids[:, :-1], use_cache=False).last_hidden_state.reshape(-1, model.config.n_embd).detach()
    weight = model.lm_head.weight.detach().clone()
    labels = ids[:, 1:].reshape(-1)
    del model
    gc.collect()
    report = {'schema_version':'output-head-parity-v0.1','status':'running','evidence_kind':'measured_cpu',
        'model_revision':REVISION,'training_start':start,'ids':ids.tolist(),'chunk_size':args.chunk_size,
        'protocol':'same detached pretrained GPT-2 hidden states and output-head initialization; one SGD update lr=1e-5; compare loss, hidden gradient, head gradient and updated head',
        'checks':{},'losses':{},'source_hashes':{}}
    for name in ('check_output_head_parity.py','check_real_training_parity.py','prepare_training_data.py','fused_training_kernels/linear_cross_entropy.py'):
        src=root/name; dst=args.output_dir/'sources'/name; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst); report['source_hashes'][name]=sha(src)
    for mode in ('standard','recomputed'):
        x=hidden.clone().requires_grad_(); w=weight.clone().requires_grad_()
        logits=x@w.t()
        loss=F.cross_entropy(logits,labels) if mode=='standard' else linear_cross_entropy(x,w,labels,chunk_size=args.chunk_size)
        gx,gw=torch.autograd.grad(loss,(x,w)); updated=w.detach()-1e-5*gw.detach()
        report['losses'][mode]=float(loss.detach())
        if mode=='standard':
            ref=(loss.detach(),gx.detach(),gw.detach(),updated); continue
        report['checks']={'loss':compare(loss,ref[0],atol=5e-5,rtol=2e-5),
            'hidden_gradient':compare(gx,ref[1],atol=2e-5,rtol=5e-4),
            'head_gradient':compare(gw,ref[2],atol=2e-5,rtol=5e-4),
            'updated_head':compare(updated,ref[3],atol=2e-6,rtol=2e-5)}
        report['status']='passed' if all(row['passed'] for row in report['checks'].values()) else 'failed'
        output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':report['checks']}),flush=True)
    return int(report['status']!='passed')


if __name__=='__main__': raise SystemExit(main())
