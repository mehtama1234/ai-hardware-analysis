#!/usr/bin/env python3
"""Reload a saved training checkpoint and run a deterministic generation smoke."""
import argparse
import hashlib
import json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from prepare_training_data import REVISION, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-new-tokens', type=int, default=4)
    args = p.parse_args()
    if not 1 <= args.max_new_tokens <= 32:
        p.error('max-new-tokens must be 1..32')
    if not args.checkpoint.is_dir() or not (args.checkpoint / 'config.json').is_file():
        raise ValueError('checkpoint directory/config missing')
    hashes = {path.name: sha(path) for path in sorted(args.checkpoint.iterdir()) if path.is_file()}
    state = args.checkpoint / 'training-state.pt'
    if not state.is_file():
        raise ValueError('training state missing')
    training_state = torch.load(state, map_location='cpu', weights_only=False)
    if not isinstance(training_state, dict) or not isinstance(training_state.get('optimizer'), dict):
        raise ValueError('invalid optimizer state')
    tokenizer = AutoTokenizer.from_pretrained('openai-community/gpt2', revision=REVISION)
    model = AutoModelForCausalLM.from_pretrained(args.checkpoint, local_files_only=True,
        attn_implementation='eager').eval()
    prompt = 'To be, or not to be'
    encoded = tokenizer(prompt, return_tensors='pt')
    ids = encoded['input_ids']
    with torch.no_grad():
        output = model.generate(input_ids=ids, attention_mask=encoded['attention_mask'], do_sample=False, max_new_tokens=args.max_new_tokens,
            pad_token_id=tokenizer.eos_token_id, use_cache=True)
    if output.shape[1] != ids.shape[1] + args.max_new_tokens:
        raise AssertionError('unexpected generation length')
    report = {'schema_version':'checkpoint-reload-v0.1','status':'passed','evidence_kind':'measured_cpu',
        'checkpoint':str(args.checkpoint),'checkpoint_hashes':hashes,'checkpoint_sha256':hashlib.sha256(
            ''.join(f'{k}:{v}' for k,v in sorted(hashes.items())).encode()).hexdigest(),
        'training_state_steps':training_state.get('steps'),'model_revision':REVISION,
        'tokenizer_revision':REVISION,'prompt':prompt,'input_ids':ids.tolist(),
        'output_ids':output.tolist(),'decoded':tokenizer.decode(output[0]),
        'protocol':{'sampling':'greedy','max_new_tokens':args.max_new_tokens,'device':'cpu','cache':True},
        'limitations':['reload/generation smoke only','no serving transport or GPU latency claim']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'decoded':report['decoded'],'steps':report['training_state_steps']}))


if __name__ == '__main__':
    main()
