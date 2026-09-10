#!/usr/bin/env python3
"""Run the bounded real-model streaming endpoint used by the GPU experiments."""
import argparse
import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import run_real_model_fused_paged_decode as decode
from run_real_model_http import GPT2Backend, MODEL_REVISION
from real_model_service import StreamingScheduler, make_server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8088)
    parser.add_argument('--backend', choices=['eager', 'sdpa', 'paged'], default='eager')
    parser.add_argument('--max-batch', type=int, default=4)
    parser.add_argument('--max-pending', type=int, default=32)
    parser.add_argument('--max-tokens', type=int, default=16)
    args = parser.parse_args()
    if not 1 <= args.max_tokens <= 64 or args.max_batch < 1 or args.max_pending < 1:
        parser.error('positive batch/queue bounds and 1–64 output tokens required')
    if not torch.cuda.is_available():
        parser.error('CUDA required for this measured serving path')
    tokenizer = AutoTokenizer.from_pretrained(decode.MODEL_ID, revision=MODEL_REVISION, padding_side='left')
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(decode.MODEL_ID, revision=MODEL_REVISION,
            use_safetensors=True, attn_implementation='sdpa' if args.backend == 'sdpa' else 'eager').to('cuda').eval()
    original = decode.gpt2_modeling.eager_attention_forward
    if args.backend == 'paged':
        decode.install_fused_attention(model, decode.build_extension())
    scheduler = StreamingScheduler(GPT2Backend(model, tokenizer), max_batch=args.max_batch,
            max_pending=args.max_pending, window_ms=5, max_tokens=args.max_tokens)
    server = make_server(scheduler, args.host, args.port)
    print(json.dumps({'url': f'http://{args.host}:{server.server_port}/stream', 'backend': args.backend,
                      'model_revision': MODEL_REVISION, 'max_tokens': args.max_tokens}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        scheduler.close()
        decode.gpt2_modeling.eager_attention_forward = original


if __name__ == '__main__':
    main()
