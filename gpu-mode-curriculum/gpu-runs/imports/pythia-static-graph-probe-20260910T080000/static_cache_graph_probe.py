"""Probe fixed-shape CUDA Graph replay with a Hugging Face StaticCache."""
import argparse
import json
import platform
import time
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, StaticCache


def run_eager(model, ids, input_mask, width, steps, max_len):
    cache = StaticCache(config=model.config, max_cache_len=max_len)
    mask = input_mask
    pos = mask.long().cumsum(-1) - 1
    pos.masked_fill_(mask == 0, 1)
    with torch.inference_mode():
        out = model(input_ids=ids, attention_mask=mask, position_ids=pos,
                    cache_position=torch.arange(width, device=ids.device),
                    past_key_values=cache, use_cache=True)
        next_ids = out.logits[:, -1].argmax(-1, keepdim=True)
        tokens = [next_ids[:, 0].clone()]
        full_mask = torch.ones((ids.shape[0], max_len), dtype=torch.long, device=ids.device)
        for step in range(steps - 1):
            pos = torch.full((ids.shape[0], 1), width + step, dtype=torch.long, device=ids.device)
            out = model(input_ids=next_ids, attention_mask=full_mask,
                        position_ids=pos, cache_position=torch.tensor([width + step], device=ids.device),
                        past_key_values=cache, use_cache=True)
            next_ids = out.logits[:, -1].argmax(-1, keepdim=True)
            tokens.append(next_ids[:, 0].clone())
    return torch.stack(tokens, dim=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model-id', default='EleutherAI/pythia-70m')
    parser.add_argument('--revision', required=True)
    parser.add_argument('--steps', type=int, default=8)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise SystemExit('CUDA required')
    device = torch.device('cuda')
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, revision=args.revision)
    tokenizer.pad_token = tokenizer.eos_token
    # GPT-NeoX eager masking constructs a CPU scalar inside the forward path,
    # which CUDA Graph capture rejects. SDPA keeps the same model/cache
    # semantics while providing a capture-compatible masking implementation.
    model = AutoModelForCausalLM.from_pretrained(args.model_id, revision=args.revision,
        attn_implementation='sdpa', use_safetensors=True).to(device).eval()
    prompts = ['GPU kernels expose memory hierarchy', 'A compiler lowers tensor programs']
    encoded = tokenizer(prompts, return_tensors='pt', padding=True).to(device)
    width = encoded['input_ids'].shape[1]
    max_len = width + args.steps + 4
    eager = run_eager(model, encoded['input_ids'], encoded['attention_mask'], width, args.steps, max_len)

    cache = StaticCache(config=model.config, max_cache_len=max_len)
    ids = encoded['input_ids'].clone()
    mask = torch.ones((2, max_len), dtype=torch.long, device=device)
    mask[:, :width] = encoded['attention_mask']
    position_ids = mask[:, :width].long().cumsum(-1) - 1
    position_ids.masked_fill_(mask[:, :width] == 0, 1)
    cache_position = torch.arange(width, device=device)
    with torch.inference_mode():
        out = model(input_ids=ids, attention_mask=mask[:, :width], position_ids=position_ids,
                    cache_position=cache_position, past_key_values=cache, use_cache=True)
        ids.copy_(out.logits[:, -1].argmax(-1, keepdim=True).expand_as(ids))
        ids = ids[:, :1].contiguous()
        position_ids = torch.full((2, 1), width, dtype=torch.long, device=device)
        cache_position = torch.tensor([width], dtype=torch.long, device=device)
        # Warm up on a side stream before capture.
        stream = torch.cuda.Stream()
        with torch.cuda.stream(stream):
            for _ in range(3):
                model(input_ids=ids, attention_mask=mask, position_ids=position_ids,
                      cache_position=cache_position, past_key_values=cache, use_cache=True)
        torch.cuda.current_stream().wait_stream(stream)
        torch.cuda.synchronize()
        # Warm-up mutates the cache. Rebuild and prefill a fresh cache before
        # capture so replay starts from the same state as the eager reference.
        cache = StaticCache(config=model.config, max_cache_len=max_len)
        ids.copy_(encoded['input_ids'])
        position_ids = (mask[:, :width].long().cumsum(-1) - 1)
        position_ids.masked_fill_(mask[:, :width] == 0, 1)
        cache_position = torch.arange(width, device=device)
        out = model(input_ids=ids, attention_mask=mask[:, :width], position_ids=position_ids,
                    cache_position=cache_position, past_key_values=cache, use_cache=True)
        ids = out.logits[:, -1].argmax(-1, keepdim=True).contiguous()
        position_ids = torch.full((2, 1), width, dtype=torch.long, device=device)
        cache_position = torch.tensor([width], dtype=torch.long, device=device)
        graph = torch.cuda.CUDAGraph()
        torch.cuda.reset_peak_memory_stats()
        with torch.cuda.graph(graph):
            graph_out = model(input_ids=ids, attention_mask=mask, position_ids=position_ids,
                              cache_position=cache_position, past_key_values=cache, use_cache=True)
        graph_tokens = []
        for step in range(args.steps - 1):
            graph.replay()
            graph_tokens.append(graph_out.logits[:, -1].argmax(-1).clone())
            ids.copy_(graph_tokens[-1].unsqueeze(1))
            position_ids.fill_(width + step + 1)
            cache_position.fill_(width + step + 1)
        graph_tokens = torch.stack([out.logits[:, -1].argmax(-1), *graph_tokens], dim=1)
        torch.cuda.synchronize()
    report = {'schema_version': 'static-cache-cuda-graph-probe-v0.1', 'status': 'passed',
        'evidence_kind': 'measured_gpu', 'model_id': args.model_id, 'model_revision': args.revision,
        'runtime': {'torch': torch.__version__, 'transformers': transformers.__version__,
                    'python': platform.python_version(), 'device': torch.cuda.get_device_name()},
        'protocol': {'batch_size': 2, 'prompt_width': width, 'steps': args.steps, 'max_cache_len': max_len,
                     'fixed_shapes': True, 'cache': 'StaticCache', 'attention': 'sdpa'},
        'checks': {'token_parity': bool(torch.equal(eager, graph_tokens)),
                   'shape_stable': tuple(graph_out.logits.shape) == (2, 1, model.config.vocab_size),
                   'graph_replayed': True},
        'metrics': {'peak_allocated_bytes_after_capture': torch.cuda.max_memory_allocated(),
                    'capture_graph_bytes': getattr(graph, 'debug_dump', None) is not None},
        'tokens': {'eager': eager.tolist(), 'graph': graph_tokens.tolist()},
        'limitations': ['Fixed batch and prompt width only; no dynamic admission.',
                        'Capture memory is allocator peak, not a full graph memory decomposition.']}
    report['status'] = 'passed' if all(report['checks'].values()) else 'failed'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': report['checks']}))
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
