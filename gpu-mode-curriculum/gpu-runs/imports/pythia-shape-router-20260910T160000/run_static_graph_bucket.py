"""Run two fixed-shape graph buckets and verify recapture-per-bucket lifecycle."""
import argparse
import json
import platform
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from static_graph_bucket import StaticGraphBucket


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--model-id', default='EleutherAI/pythia-70m')
    p.add_argument('--revision', required=True)
    p.add_argument('--steps', type=int, default=8)
    args = p.parse_args()
    if not torch.cuda.is_available():
        raise SystemExit('CUDA required')
    tok = AutoTokenizer.from_pretrained(args.model_id, revision=args.revision)
    tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model_id, revision=args.revision,
        attn_implementation='sdpa', use_safetensors=True).cuda().eval()
    prompts = ['GPU kernels expose memory hierarchy', 'A compiler lowers tensor programs']
    encoded = tok(prompts, return_tensors='pt', padding=True).to('cuda')
    bucket = StaticGraphBucket(model, batch_size=2, max_cache_len=256)
    first, first_meta = bucket.run(encoded, args.steps, recapture=True)
    second_encoded = {k: v.clone() for k, v in encoded.items()}
    second_encoded['input_ids'][:, -1] = (second_encoded['input_ids'][:, -1] + 1) % model.config.vocab_size
    second, second_meta = bucket.run(second_encoded, args.steps, recapture=True)
    with torch.inference_mode():
        refs = []
        for item in (encoded, second_encoded):
            refs.append(torch.stack([model.generate(input_ids=item['input_ids'][i:i+1],
                attention_mask=item['attention_mask'][i:i+1], max_new_tokens=args.steps,
                do_sample=False, eos_token_id=None, pad_token_id=tok.pad_token_id)[0, -args.steps:]
                for i in range(2)]))
    report = {'schema_version': 'static-graph-bucket-v0.1', 'evidence_kind': 'measured_gpu',
        'status': 'passed', 'model_id': args.model_id, 'model_revision': args.revision,
        'runtime': {'torch': torch.__version__, 'transformers': transformers.__version__,
                    'python': platform.python_version(), 'device': torch.cuda.get_device_name()},
        'protocol': {'batch_size': 2, 'steps': args.steps, 'attention': 'sdpa',
                     'cache': 'StaticCache', 'policy': 'recapture-per-bucket'},
        'checks': {'first_bucket_parity': bool(torch.equal(first, refs[0])),
                   'second_bucket_parity': bool(torch.equal(second, refs[1])),
                   'fixed_shape': first.shape == second.shape == (2, args.steps),
                   'recaptured': first_meta['recapture_ms'] > 0 and second_meta['recapture_ms'] > 0},
        'buckets': [first_meta, second_meta],
        'metrics': {'peak_allocated_bytes': torch.cuda.max_memory_allocated()},
        'limitations': ['Fixed batch and prompt width; no dynamic admission.',
                        'Recapture cost is measured per bucket; no amortized serving claim.']}
    report['status'] = 'passed' if all(report['checks'].values()) else 'failed'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': report['checks']}))
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
