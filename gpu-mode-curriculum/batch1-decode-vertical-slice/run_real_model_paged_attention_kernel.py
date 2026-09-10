#!/usr/bin/env python3
"""Run the paged-attention CUDA kernel against real GPT-2 KV tensors."""

from __future__ import annotations

import json
import math
import statistics
import time
from pathlib import Path

import torch
from torch.utils.cpp_extension import load_inline
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

from run_real_model_paged_cache_adapter import PAGE_SIZE
from paged_cache import PagedKVCache


REPORT = Path(__file__).resolve().parent / "reports" / "real-model-paged-attention-kernel.json"
MODEL_ID = "openai-community/gpt2"
CONTEXT_WORD_COUNTS = (2, 32, 128)


CUDA_SOURCE = r'''
#include <torch/extension.h>
#include <cuda.h>
#include <cuda_runtime.h>
#include <cmath>

__global__ void page_attention(const float* q, const float* keys, const float* values, const int* table, const int* length, float* out, int heads, int page_size, int dim) {
  int head = blockIdx.x;
  int tokens = length[0];
  extern __shared__ float scores[];
  if (threadIdx.x == 0) {
    float maximum = -1.0e30f;
    for (int t = 0; t < tokens; ++t) {
      int physical = table[t / page_size];
      int in_page = t % page_size;
      float dot = 0.0f;
      for (int d = 0; d < dim; ++d) {
        dot += q[head * dim + d] * keys[((physical * heads + head) * page_size + in_page) * dim + d];
      }
      scores[t] = dot / sqrtf((float)dim);
      maximum = fmaxf(maximum, scores[t]);
    }
    float normalizer = 0.0f;
    for (int t = 0; t < tokens; ++t) { scores[t] = expf(scores[t] - maximum); normalizer += scores[t]; }
    for (int t = 0; t < tokens; ++t) scores[t] /= normalizer;
  }
  __syncthreads();
  for (int d = threadIdx.x; d < dim; d += blockDim.x) {
    float value = 0.0f;
    for (int t = 0; t < tokens; ++t) {
      int physical = table[t / page_size];
      int in_page = t % page_size;
      value += scores[t] * values[((physical * heads + head) * page_size + in_page) * dim + d];
    }
    out[head * dim + d] = value;
  }
}

torch::Tensor run(torch::Tensor q, torch::Tensor keys, torch::Tensor values, torch::Tensor table, torch::Tensor length, int heads, int page_size, int dim) {
  auto out = torch::zeros({heads, dim}, q.options());
  page_attention<<<heads, 128, length.item<int>() * sizeof(float)>>>(q.data_ptr<float>(), keys.data_ptr<float>(), values.data_ptr<float>(), table.data_ptr<int>(), length.data_ptr<int>(), out.data_ptr<float>(), heads, page_size, dim);
  return out;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) { m.def("run", &run, "paged attention"); }
'''


def build_extension():
    return load_inline("real_gpt2_paged_attention", cpp_sources="", cuda_sources=CUDA_SOURCE, functions=None, extra_cuda_cflags=["-O3"], verbose=False)


def measure_kernel(module, model, tokenizer, words: int):
    prompt = ("context movement " * words).strip() + " because"
    encoded = tokenizer([prompt], return_tensors="pt").to("cuda")
    with torch.inference_mode():
        cache = DynamicCache(config=model.config)
        output = model(input_ids=encoded["input_ids"], attention_mask=encoded["attention_mask"], past_key_values=cache, use_cache=True)
    layer = output.past_key_values.layers[0]
    key, value = layer.keys[0].float().contiguous(), layer.values[0].float().contiguous()
    heads, tokens, dim = key.shape
    pages = PagedKVCache(capacity_pages=math.ceil(tokens / PAGE_SIZE), page_size=PAGE_SIZE, heads=heads, head_dim=dim, dtype=key.dtype, device=key.device)
    handle = pages.allocate()
    pages.append(handle, key, value)
    allocated_pages, logical_length = pages.sequences[handle.sequence_id]
    page_table = torch.tensor(allocated_pages, device="cuda", dtype=torch.int32)
    length = torch.tensor([tokens], device="cuda", dtype=torch.int32)
    query = key[:, -1, :].contiguous()
    oracle = torch.softmax(torch.einsum("hd,htd->ht", query, key) / math.sqrt(dim), dim=-1)
    oracle = torch.einsum("ht,htd->hd", oracle, value)
    module.run(query, pages.keys, pages.values, page_table, length, heads, PAGE_SIZE, dim)
    samples = []
    result = None
    for _ in range(10):
        torch.cuda.synchronize()
        start = time.perf_counter_ns()
        result = module.run(query, pages.keys, pages.values, page_table, length, heads, PAGE_SIZE, dim)
        torch.cuda.synchronize()
        samples.append((time.perf_counter_ns() - start) / 1e6)
    error = float((result - oracle).abs().max().item())
    return {"prompt_token_count": tokens, "heads": heads, "head_dim": dim, "dtype": str(key.dtype), "output_max_abs_error": error, "parity": error < 2e-5, "kernel_ms_median": statistics.median(samples), "page_count": len(allocated_pages)}


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; run this entrypoint in Google Colab")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_safetensors=True).to("cuda").eval()
    module = build_extension()
    rows = [measure_kernel(module, model, tokenizer, words) for words in CONTEXT_WORD_COUNTS]
    report = {"schema_version": "real-model-paged-attention-kernel-v0.1", "experiment": "real_gpt2_kv_to_cuda_paged_attention_oracle", "evidence_kind": "measured_gpu", "gpu_execution_accepted": True, "model_profile": {"model_id": MODEL_ID, "model_revision": getattr(model.config, "_commit_hash", None), "trained": True, "parameter_count": sum(parameter.numel() for parameter in model.parameters())}, "device": "cuda", "device_name": torch.cuda.get_device_name(0), "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__}, "protocol": {"page_size_tokens": PAGE_SIZE, "context_word_counts": list(CONTEXT_WORD_COUNTS), "layer": 0, "query": "last real GPT-2 layer-0 key used as a real-shaped query for attention-oracle comparison", "oracle": "PyTorch softmax(QK^T/sqrt(d))V", "timing": "CUDA synchronized around kernel call"}, "rows": rows, "decision": "real_model_paged_kernel_parity_passed" if all(row["parity"] for row in rows) else "real_model_paged_kernel_parity_failed", "claim_boundary": {"allowed": "CUDA paged-attention kernel parity and launch timing against real GPT-2 layer-0 K/V tensors.", "refused": "Full GPT-2 layer replacement, fused projection integration, production paged attention, energy savings, analog benefit, or silicon performance."}}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": report["device_name"], "parity": report["decision"] == "real_model_paged_kernel_parity_passed", "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
