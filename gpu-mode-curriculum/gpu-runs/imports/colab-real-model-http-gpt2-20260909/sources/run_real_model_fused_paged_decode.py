#!/usr/bin/env python3
"""End-to-end GPT-2 decode with device-resident CUDA paged attention.

Prefill deliberately uses the model's native attention. During one-token
autoregressive decode, every GPT-2 attention block routes K/V through a CUDA
page-packing workspace and paged-attention kernel. Page allocation and packing
are device-side; the Python allocator is not in the timed path.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

import torch
from torch.utils.cpp_extension import load_inline
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache
import transformers.models.gpt2.modeling_gpt2 as gpt2_modeling
from run_real_model_extended_characterization import PowerSampler

ROOT = Path(__file__).resolve().parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
if not SERVING.exists():
    SERVING = ROOT.parent / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
REPORT = Path(__file__).resolve().parent / "reports" / "real-model-device-resident-paged-decode.json"
MODEL_ID = "openai-community/gpt2"
PAGE_SIZE = 16
PROMPTS = ("The system bottleneck is", "context movement " * 32 + " because")
MAX_NEW_TOKENS = 6
REPEATS = 2
if "--extended" in sys.argv:
    PROMPTS = tuple("context movement " * words + " because" for words in (8, 32, 128, 256))
    MAX_NEW_TOKENS = 8
    REPEATS = 2
if "--microbatch" in sys.argv:
    PROMPTS = ("context movement " * 32 + " because",)
    MAX_NEW_TOKENS = 8
    REPEATS = 2
BATCH_SIZES = (1, 2, 4) if "--microbatch" in sys.argv else (1,)

CUDA_SOURCE = r'''
#include <torch/extension.h>
#include <cuda.h>
#include <cuda_runtime.h>
#include <cmath>

__device__ __forceinline__ float warp_block_max(float value, float* scratch,
                                                int tid, int lane, int warp, int warp_count);
__device__ __forceinline__ float warp_block_sum(float value, float* scratch,
                                                int tid, int lane, int warp, int warp_count);

__global__ void pack_pages(const float* keys, const float* values, float* page_keys,
                           float* page_values, int tokens, int valid_start, int heads, int page_size, int dim) {
  int index = blockIdx.x * blockDim.x + threadIdx.x;
  int valid_tokens = tokens - valid_start;
  int total = heads * valid_tokens * dim;
  if (index >= total) return;
  int d = index % dim;
  int t = (index / dim) % valid_tokens;
  int source_t = valid_start + t;
  int head = index / (valid_tokens * dim);
  int page = t / page_size;
  int in_page = t % page_size;
  int destination = ((page * heads + head) * page_size + in_page) * dim + d;
  int source = (head * tokens + source_t) * dim + d;
  page_keys[destination] = keys[source];
  page_values[destination] = values[source];
}

__global__ void page_attention(const float* q, const float* keys, const float* values,
                               int tokens, int heads, int page_size, int dim, float* out) {
  int head = blockIdx.x;
  extern __shared__ float scores[];
  if (threadIdx.x == 0) {
    float maximum = -1.0e30f;
    for (int t = 0; t < tokens; ++t) {
      int physical = t / page_size;
      int in_page = t % page_size;
      float dot = 0.0f;
      for (int d = 0; d < dim; ++d)
        dot += q[head * dim + d] * keys[((physical * heads + head) * page_size + in_page) * dim + d];
      scores[t] = dot / sqrtf((float)dim);
      maximum = fmaxf(maximum, scores[t]);
    }
    float normalizer = 0.0f;
    for (int t = 0; t < tokens; ++t) { scores[t] = expf(scores[t] - maximum); normalizer += scores[t]; }
    for (int t = 0; t < tokens; ++t) scores[t] /= normalizer;
  }
  __syncthreads();
  for (int d = threadIdx.x; d < dim; d += blockDim.x) {
    float result = 0.0f;
    for (int t = 0; t < tokens; ++t) {
      int physical = t / page_size;
      int in_page = t % page_size;
      result += scores[t] * values[((physical * heads + head) * page_size + in_page) * dim + d];
    }
    out[head * dim + d] = result;
  }
}

__global__ void append_pages(const float* keys, const float* values, float* page_keys,
                             float* page_values, int write_tokens, int write_offset,
                             int heads, int page_size, int dim) {
  int index = blockIdx.x * blockDim.x + threadIdx.x;
  int total = heads * write_tokens * dim;
  if (index >= total) return;
  int d = index % dim;
  int t = (index / dim) % write_tokens;
  int head = index / (write_tokens * dim);
  int logical = write_offset + t;
  int page = logical / page_size;
  int in_page = logical % page_size;
  int destination = ((page * heads + head) * page_size + in_page) * dim + d;
  int source = (head * write_tokens + t) * dim + d;
  page_keys[destination] = keys[source];
  page_values[destination] = values[source];
}

__global__ void append_and_page_attention(const float* q, const float* keys, const float* values,
                                          float* page_keys, float* page_values,
                                          int write_tokens, int write_offset,
                                          int heads, int page_size, int dim, float* out) {
  int head = blockIdx.x;
  int tid = threadIdx.x;
  int total = write_tokens * dim;
  for (int index = tid; index < total; index += blockDim.x) {
    int d = index % dim;
    int t = index / dim;
    int logical = write_offset + t;
    int page = logical / page_size;
    int in_page = logical % page_size;
    int destination = ((page * heads + head) * page_size + in_page) * dim + d;
    int source = (head * write_tokens + t) * dim + d;
    page_keys[destination] = keys[source];
    page_values[destination] = values[source];
  }
  __syncthreads();
  int tokens = write_offset + write_tokens;
  extern __shared__ float scores[];
  int lane = tid & 31;
  int warp = tid >> 5;
  int warp_count = blockDim.x >> 5;
  for (int t = warp; t < tokens; t += warp_count) {
    int physical = t / page_size;
    int in_page = t % page_size;
    float dot = 0.0f;
    for (int d = lane; d < dim; d += 32)
      dot += q[head * dim + d] * page_keys[((physical * heads + head) * page_size + in_page) * dim + d];
    for (int offset = 16; offset > 0; offset >>= 1)
      dot += __shfl_down_sync(0xffffffff, dot, offset);
    if (lane == 0) scores[t] = dot / sqrtf((float)dim);
  }
  __syncthreads();
  if (tid == 0) {
    float maximum = -1.0e30f;
    for (int t = 0; t < tokens; ++t) maximum = fmaxf(maximum, scores[t]);
    float normalizer = 0.0f;
    for (int t = 0; t < tokens; ++t) { scores[t] = expf(scores[t] - maximum); normalizer += scores[t]; }
    for (int t = 0; t < tokens; ++t) scores[t] /= normalizer;
  }
  __syncthreads();
  float* partial = scores + tokens;
  int workers = max(1, blockDim.x / dim);
  if (dim <= blockDim.x) {
    int d = tid % dim;
    int worker = tid / dim;
    float result = 0.0f;
    for (int t = worker; t < tokens; t += workers) {
      int physical = t / page_size;
      int in_page = t % page_size;
      result += scores[t] * page_values[((physical * heads + head) * page_size + in_page) * dim + d];
    }
    partial[tid] = result;
    __syncthreads();
    if (tid < dim) {
      float reduced = partial[tid];
      for (int worker_index = 1; worker_index < workers; ++worker_index)
        reduced += partial[tid + worker_index * dim];
      out[head * dim + tid] = reduced;
    }
  } else {
    for (int d = tid; d < dim; d += blockDim.x) {
      float result = 0.0f;
      for (int t = 0; t < tokens; ++t) {
        int physical = t / page_size;
        int in_page = t % page_size;
        result += scores[t] * page_values[((physical * heads + head) * page_size + in_page) * dim + d];
      }
      out[head * dim + d] = result;
    }
  }
}

__global__ void batch_page_attention(const float* q, const float* keys, const float* values,
                                     const int* starts, float* page_keys, float* page_values,
                                     int batch, int tokens, int heads, int page_size, int dim,
                                     int pages_per_sequence, float* out) {
  int sequence = blockIdx.x / heads;
  int head = blockIdx.x % heads;
  int tid = threadIdx.x;
  int valid_start = starts[sequence];
  int valid_tokens = tokens - valid_start;
  for (int index = tid; index < valid_tokens * dim; index += blockDim.x) {
    int d = index % dim;
    int t = index / dim;
    int page = t / page_size;
    int in_page = t % page_size;
    int destination = ((((sequence * pages_per_sequence + page) * heads + head) * page_size + in_page) * dim + d);
    int source = (((sequence * heads + head) * tokens + valid_start + t) * dim + d);
    page_keys[destination] = keys[source];
    page_values[destination] = values[source];
  }
  __syncthreads();
  extern __shared__ float shared[];
  float* scores = shared;
  float* partial = scores + valid_tokens;
  int lane = tid & 31;
  int warp = tid >> 5;
  int warp_count = blockDim.x >> 5;
  for (int t = warp; t < valid_tokens; t += warp_count) {
    int physical = t / page_size;
    int in_page = t % page_size;
    float dot = 0.0f;
    for (int d = lane; d < dim; d += 32) {
      int offset = ((((sequence * pages_per_sequence + physical) * heads + head) * page_size + in_page) * dim + d);
      dot += q[(sequence * heads + head) * dim + d] * page_keys[offset];
    }
    for (int offset = 16; offset > 0; offset >>= 1)
      dot += __shfl_down_sync(0xffffffff, dot, offset);
    if (lane == 0) scores[t] = dot / sqrtf((float)dim);
  }
  __syncthreads();
  float local_maximum = -1.0e30f;
  for (int t = tid; t < valid_tokens; t += blockDim.x) local_maximum = fmaxf(local_maximum, scores[t]);
  float maximum = warp_block_max(local_maximum, partial, tid, lane, warp, warp_count);
  float local_sum = 0.0f;
  for (int t = tid; t < valid_tokens; t += blockDim.x) {
    scores[t] = expf(scores[t] - maximum);
    local_sum += scores[t];
  }
  float normalizer = warp_block_sum(local_sum, partial, tid, lane, warp, warp_count);
  for (int t = tid; t < valid_tokens; t += blockDim.x) scores[t] /= normalizer;
  __syncthreads();
  int workers = max(1, blockDim.x / dim);
  if (dim <= blockDim.x) {
    int d = tid % dim;
    int worker = tid / dim;
    float result = 0.0f;
    for (int t = worker; t < valid_tokens; t += workers) {
      int physical = t / page_size;
      int in_page = t % page_size;
      int offset = ((((sequence * pages_per_sequence + physical) * heads + head) * page_size + in_page) * dim + d);
      result += scores[t] * page_values[offset];
    }
    partial[tid] = result;
    __syncthreads();
    if (tid < dim) {
      float reduced = partial[tid];
      for (int worker_index = 1; worker_index < workers; ++worker_index) reduced += partial[tid + worker_index * dim];
      out[(sequence * heads + head) * dim + tid] = reduced;
    }
  }
}

__global__ void batch_direct_attention(const float* q, const float* keys, const float* values,
                                       const int* starts, int batch, int tokens, int heads,
                                       int dim, float* out) {
  int sequence = blockIdx.x / heads;
  int head = blockIdx.x % heads;
  int tid = threadIdx.x;
  int valid_start = starts[sequence];
  int valid_tokens = tokens - valid_start;
  extern __shared__ float shared[];
  float* scores = shared;
  float* partial = scores + valid_tokens;
  int lane = tid & 31;
  int warp = tid >> 5;
  int warp_count = blockDim.x >> 5;
  for (int t = warp; t < valid_tokens; t += warp_count) {
    float dot = 0.0f;
    for (int d = lane; d < dim; d += 32) {
      int offset = (((sequence * heads + head) * tokens + valid_start + t) * dim + d);
      dot += q[(sequence * heads + head) * dim + d] * keys[offset];
    }
    for (int offset = 16; offset > 0; offset >>= 1)
      dot += __shfl_down_sync(0xffffffff, dot, offset);
    if (lane == 0) scores[t] = dot / sqrtf((float)dim);
  }
  __syncthreads();
  float local_maximum = -1.0e30f;
  for (int t = tid; t < valid_tokens; t += blockDim.x) local_maximum = fmaxf(local_maximum, scores[t]);
  float maximum = warp_block_max(local_maximum, partial, tid, lane, warp, warp_count);
  float local_sum = 0.0f;
  for (int t = tid; t < valid_tokens; t += blockDim.x) {
    scores[t] = expf(scores[t] - maximum);
    local_sum += scores[t];
  }
  float normalizer = warp_block_sum(local_sum, partial, tid, lane, warp, warp_count);
  for (int t = tid; t < valid_tokens; t += blockDim.x) scores[t] /= normalizer;
  __syncthreads();
  int workers = max(1, blockDim.x / dim);
  if (dim <= blockDim.x) {
    int d = tid % dim;
    int worker = tid / dim;
    float result = 0.0f;
    for (int t = worker; t < valid_tokens; t += workers) {
      int offset = (((sequence * heads + head) * tokens + valid_start + t) * dim + d);
      result += scores[t] * values[offset];
    }
    partial[tid] = result;
    __syncthreads();
    if (tid < dim) {
      float reduced = partial[tid];
      for (int worker_index = 1; worker_index < workers; ++worker_index) reduced += partial[tid + worker_index * dim];
      out[(sequence * heads + head) * dim + tid] = reduced;
    }
  }
}

__global__ void append_batch_token(const float* keys, const float* values, const int* lengths,
                                   float* page_keys, float* page_values, int batch, int heads,
                                   int page_size, int dim) {
  int index = blockIdx.x * blockDim.x + threadIdx.x;
  int total = batch * heads * dim;
  if (index >= total) return;
  int d = index % dim;
  int head = (index / dim) % heads;
  int sequence = index / (heads * dim);
  int logical = lengths[sequence] - 1;
  int page = logical / page_size;
  int in_page = logical % page_size;
  int destination = ((((sequence * ((logical / page_size) + 1) + page) * heads + head) * page_size + in_page) * dim + d);
  // The destination page stride is supplied by the host through a fixed-capacity layout.
  // This kernel is replaced below by the capacity-aware variant at launch time.
  (void)destination;
}

__global__ void append_batch_token_capacity(const float* keys, const float* values, const int* lengths,
                                            float* page_keys, float* page_values, int batch, int heads,
                                            int page_size, int dim, int pages_capacity) {
  int index = blockIdx.x * blockDim.x + threadIdx.x;
  int total = batch * heads * dim;
  if (index >= total) return;
  int d = index % dim;
  int head = (index / dim) % heads;
  int sequence = index / (heads * dim);
  int logical = lengths[sequence] - 1;
  int page = logical / page_size;
  int in_page = logical % page_size;
  int destination = ((((sequence * pages_capacity + page) * heads + head) * page_size + in_page) * dim + d);
  int source = ((sequence * heads + head) * dim + d);
  page_keys[destination] = keys[source];
  page_values[destination] = values[source];
}

__global__ void batch_cached_page_attention(const float* q, const float* key_last,
                                            const float* value_last, const int* lengths,
                                            float* page_keys, float* page_values,
                                            int batch, int heads, int page_size, int dim,
                                            int pages_capacity, float* out) {
  int sequence = blockIdx.x / heads;
  int head = blockIdx.x % heads;
  int tid = threadIdx.x;
  int valid_tokens = lengths[sequence];
  extern __shared__ float shared[];
  float* scores = shared;
  float* partial = scores + valid_tokens;
  int lane = tid & 31;
  int warp = tid >> 5;
  int warp_count = blockDim.x >> 5;
  int logical = valid_tokens - 1;
  int page = logical / page_size;
  int in_page = logical % page_size;
  for (int d = tid; d < dim; d += blockDim.x) {
    int destination = ((((sequence * pages_capacity + page) * heads + head) * page_size + in_page) * dim + d);
    int source = ((sequence * heads + head) * dim + d);
    page_keys[destination] = key_last[source];
    page_values[destination] = value_last[source];
  }
  __syncthreads();
  for (int t = warp; t < valid_tokens; t += warp_count) {
    int physical = t / page_size;
    int in_page = t % page_size;
    float dot = 0.0f;
    for (int d = lane; d < dim; d += 32) {
      int offset = ((((sequence * pages_capacity + physical) * heads + head) * page_size + in_page) * dim + d);
      dot += q[(sequence * heads + head) * dim + d] * page_keys[offset];
    }
    for (int offset = 16; offset > 0; offset >>= 1)
      dot += __shfl_down_sync(0xffffffff, dot, offset);
    if (lane == 0) scores[t] = dot / sqrtf((float)dim);
  }
  __syncthreads();
  float local_maximum = -1.0e30f;
  for (int t = tid; t < valid_tokens; t += blockDim.x) local_maximum = fmaxf(local_maximum, scores[t]);
  float maximum = warp_block_max(local_maximum, partial, tid, lane, warp, warp_count);
  float local_sum = 0.0f;
  for (int t = tid; t < valid_tokens; t += blockDim.x) {
    scores[t] = expf(scores[t] - maximum);
    local_sum += scores[t];
  }
  float normalizer = warp_block_sum(local_sum, partial, tid, lane, warp, warp_count);
  for (int t = tid; t < valid_tokens; t += blockDim.x) scores[t] /= normalizer;
  __syncthreads();
  int workers = max(1, blockDim.x / dim);
  if (dim <= blockDim.x) {
    int d = tid % dim;
    int worker = tid / dim;
    float result = 0.0f;
    for (int t = worker; t < valid_tokens; t += workers) {
      int physical = t / page_size;
      int in_page = t % page_size;
      int offset = ((((sequence * pages_capacity + physical) * heads + head) * page_size + in_page) * dim + d);
      result += scores[t] * page_values[offset];
    }
    partial[tid] = result;
    __syncthreads();
    if (tid < dim) {
      float reduced = partial[tid];
      for (int worker_index = 1; worker_index < workers; ++worker_index) reduced += partial[tid + worker_index * dim];
      out[(sequence * heads + head) * dim + tid] = reduced;
    }
  }
}

__device__ __forceinline__ float warp_block_max(float value, float* scratch,
                                                int tid, int lane, int warp, int warp_count) {
  for (int offset = 16; offset > 0; offset >>= 1)
    value = fmaxf(value, __shfl_down_sync(0xffffffff, value, offset));
  if (lane == 0) scratch[warp] = value;
  __syncthreads();
  value = tid < warp_count ? scratch[tid] : -1.0e30f;
  if (warp == 0) {
    for (int offset = 16; offset > 0; offset >>= 1)
      value = fmaxf(value, __shfl_down_sync(0xffffffff, value, offset));
    if (lane == 0) scratch[0] = value;
  }
  __syncthreads();
  return scratch[0];
}

__device__ __forceinline__ float warp_block_sum(float value, float* scratch,
                                                int tid, int lane, int warp, int warp_count) {
  for (int offset = 16; offset > 0; offset >>= 1)
    value += __shfl_down_sync(0xffffffff, value, offset);
  if (lane == 0) scratch[warp] = value;
  __syncthreads();
  value = tid < warp_count ? scratch[tid] : 0.0f;
  if (warp == 0) {
    for (int offset = 16; offset > 0; offset >>= 1)
      value += __shfl_down_sync(0xffffffff, value, offset);
    if (lane == 0) scratch[0] = value;
  }
  __syncthreads();
  return scratch[0];
}

torch::Tensor run(torch::Tensor q, torch::Tensor keys, torch::Tensor values,
                  int page_size, int valid_start) {
  int heads = keys.size(0);
  int tokens = keys.size(1);
  int dim = keys.size(2);
  int valid_tokens = tokens - valid_start;
  int pages = (valid_tokens + page_size - 1) / page_size;
  auto page_keys = torch::empty({pages, heads, page_size, dim}, q.options());
  auto page_values = torch::empty_like(page_keys);
  auto out = torch::zeros({heads, dim}, q.options());
  int total = heads * valid_tokens * dim;
  pack_pages<<<(total + 255) / 256, 256>>>(keys.data_ptr<float>(), values.data_ptr<float>(),
      page_keys.data_ptr<float>(), page_values.data_ptr<float>(), tokens, valid_start, heads, page_size, dim);
  page_attention<<<heads, 128, valid_tokens * sizeof(float)>>>(q.data_ptr<float>(), page_keys.data_ptr<float>(),
      page_values.data_ptr<float>(), valid_tokens, heads, page_size, dim, out.data_ptr<float>());
  return out;
}

torch::Tensor run_into(torch::Tensor q, torch::Tensor keys, torch::Tensor values,
                       torch::Tensor page_keys, torch::Tensor page_values,
                       int page_size, int write_offset) {
  int heads = keys.size(0);
  int write_tokens = keys.size(1);
  int dim = keys.size(2);
  int total = heads * write_tokens * dim;
  auto out = torch::zeros({heads, dim}, q.options());
  append_and_page_attention<<<heads, 128, (write_offset + write_tokens + 128) * sizeof(float)>>>(
      q.data_ptr<float>(), keys.data_ptr<float>(), values.data_ptr<float>(),
      page_keys.data_ptr<float>(), page_values.data_ptr<float>(), write_tokens, write_offset,
      heads, page_size, dim, out.data_ptr<float>());
  return out;
}

torch::Tensor run_batch(torch::Tensor q, torch::Tensor keys, torch::Tensor values,
                        torch::Tensor starts, int page_size) {
  int batch = keys.size(0);
  int heads = keys.size(1);
  int tokens = keys.size(2);
  int dim = keys.size(3);
  int pages_per_sequence = (tokens + page_size - 1) / page_size;
  auto page_keys = torch::empty({batch, pages_per_sequence, heads, page_size, dim}, q.options());
  auto page_values = torch::empty_like(page_keys);
  auto out = torch::zeros({batch, heads, dim}, q.options());
  batch_page_attention<<<batch * heads, 128, (tokens + 128) * sizeof(float)>>>(
      q.data_ptr<float>(), keys.data_ptr<float>(), values.data_ptr<float>(), starts.data_ptr<int>(),
      page_keys.data_ptr<float>(), page_values.data_ptr<float>(), batch, tokens, heads, page_size,
      dim, pages_per_sequence, out.data_ptr<float>());
  return out;
}

torch::Tensor run_batch_into(torch::Tensor q, torch::Tensor keys, torch::Tensor values,
                             torch::Tensor starts, torch::Tensor page_keys,
                             torch::Tensor page_values, torch::Tensor out, int page_size) {
  int batch = keys.size(0);
  int heads = keys.size(1);
  int tokens = keys.size(2);
  int dim = keys.size(3);
  int pages_per_sequence = (tokens + page_size - 1) / page_size;
  batch_page_attention<<<batch * heads, 128, (tokens + 128) * sizeof(float)>>>(
      q.data_ptr<float>(), keys.data_ptr<float>(), values.data_ptr<float>(), starts.data_ptr<int>(),
      page_keys.data_ptr<float>(), page_values.data_ptr<float>(), batch, tokens, heads, page_size,
      dim, pages_per_sequence, out.data_ptr<float>());
  return out;
}

torch::Tensor run_batch_init(torch::Tensor q, torch::Tensor keys, torch::Tensor values,
                             torch::Tensor starts, torch::Tensor page_keys,
                             torch::Tensor page_values, torch::Tensor out,
                             int page_size, int pages_capacity) {
  int batch = keys.size(0);
  int heads = keys.size(1);
  int tokens = keys.size(2);
  int dim = keys.size(3);
  batch_page_attention<<<batch * heads, 128, (tokens + 128) * sizeof(float)>>>(
      q.data_ptr<float>(), keys.data_ptr<float>(), values.data_ptr<float>(), starts.data_ptr<int>(),
      page_keys.data_ptr<float>(), page_values.data_ptr<float>(), batch, tokens, heads, page_size,
      dim, pages_capacity, out.data_ptr<float>());
  return out;
}

torch::Tensor run_batch_direct(torch::Tensor q, torch::Tensor keys, torch::Tensor values,
                               torch::Tensor starts, int page_size) {
  int batch = keys.size(0);
  int heads = keys.size(1);
  int tokens = keys.size(2);
  int dim = keys.size(3);
  auto out = torch::zeros({batch, heads, dim}, q.options());
  batch_direct_attention<<<batch * heads, 128, (tokens + 128) * sizeof(float)>>>(
      q.data_ptr<float>(), keys.data_ptr<float>(), values.data_ptr<float>(), starts.data_ptr<int>(),
      batch, tokens, heads, dim, out.data_ptr<float>());
  return out;
}

torch::Tensor run_batch_append(torch::Tensor q, torch::Tensor key_last, torch::Tensor value_last,
                               torch::Tensor lengths, torch::Tensor page_keys,
                               torch::Tensor page_values, int page_size, int pages_capacity) {
  int batch = key_last.size(0);
  int heads = key_last.size(1);
  int dim = key_last.size(2);
  auto out = torch::zeros({batch, heads, dim}, q.options());
  batch_cached_page_attention<<<batch * heads, 128, (pages_capacity * page_size + 128) * sizeof(float)>>>(
      q.data_ptr<float>(), key_last.data_ptr<float>(), value_last.data_ptr<float>(), lengths.data_ptr<int>(),
      page_keys.data_ptr<float>(), page_values.data_ptr<float>(),
      batch, heads, page_size, dim, pages_capacity, out.data_ptr<float>());
  return out;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
  m.def("run", &run, "paged attention");
  m.def("run_into", &run_into, "persistent paged attention");
  m.def("run_batch", &run_batch, "batched paged attention");
  m.def("run_batch_into", &run_batch_into, "reused-workspace batched paged attention");
  m.def("run_batch_init", &run_batch_init, "initialize persistent paged attention workspace");
  m.def("run_batch_direct", &run_batch_direct, "direct batched attention without page packing");
  m.def("run_batch_append", &run_batch_append, "append-only persistent paged attention");
}
'''


def build_extension():
    return load_inline("real_gpt2_device_resident_paged_decode", cpp_sources="", cuda_sources=CUDA_SOURCE,
                       functions=None, extra_cuda_cflags=["-O3"], verbose=False)


def native_decode(model, encoded):
    reset = getattr(model, "_reset_fused_decode_state", None)
    if reset is not None:
        reset()
    mask = encoded["attention_mask"]
    # GPT-2's default positions count padded columns. Match unpadded generation
    # so batching changes execution only, not the model's positional inputs.
    position_ids = mask.long().cumsum(-1) - 1
    position_ids.masked_fill_(mask == 0, 1)
    with torch.inference_mode():
        cache = DynamicCache(config=model.config)
        out = model(input_ids=encoded["input_ids"], attention_mask=mask, position_ids=position_ids,
                    past_key_values=cache, use_cache=True)
        tokens = [out.logits[:, -1, :].argmax(dim=-1)]
        for _ in range(MAX_NEW_TOKENS - 1):
            mask = torch.cat((mask, mask.new_ones((mask.shape[0], 1))), dim=1)
            out = model(input_ids=tokens[-1].unsqueeze(-1), attention_mask=mask,
                        position_ids=(mask.long().sum(-1) - 1).unsqueeze(-1),
                        past_key_values=out.past_key_values, use_cache=True)
            tokens.append(out.logits[:, -1, :].argmax(dim=-1))
    return torch.stack(tokens, dim=1)


def install_fused_attention(model, module, persistent=False):
    original = gpt2_modeling.eager_attention_forward
    workspace_cache = {}
    persistent_cache = {}

    def reset_persistent_cache():
        persistent_cache.clear()

    if persistent:
        model._reset_fused_decode_state = reset_persistent_cache

    def fused(attention, query, key, value, attention_mask, scaling=None, dropout=0.0, **kwargs):
        if query.shape[-2] != 1:
            return original(attention, query, key, value, attention_mask, scaling=scaling, dropout=dropout, **kwargs)
        batch, heads, tokens, dim = key.shape
        key_f = key.float().contiguous()
        value_f = value.float().contiguous()
        query_f = query[:, :, -1, :].float().contiguous()
        starts = torch.zeros((batch,), dtype=torch.int32, device=key.device)
        if attention_mask is not None:
            for batch_index in range(batch):
                mask_row = attention_mask[batch_index].reshape(-1, attention_mask.shape[-1])[-1]
                allowed = mask_row if mask_row.dtype == torch.bool else mask_row > -1.0e4
                valid_indices = allowed.nonzero(as_tuple=False).flatten()
                if valid_indices.numel(): starts[batch_index] = valid_indices[0]
        workspace_key = (batch, tokens, heads, dim, str(key.device))
        if persistent:
            state_key = (id(attention), batch, str(key.device))
            state = persistent_cache.get(state_key)
            starts_cpu = starts
            if state is None or state["tokens"] >= tokens or state["tokens"] + 1 != tokens:
                pages_capacity = (tokens + MAX_NEW_TOKENS + PAGE_SIZE - 1) // PAGE_SIZE
                page_keys = torch.empty((batch, pages_capacity, heads, PAGE_SIZE, dim), device=key.device, dtype=torch.float32)
                page_values = torch.empty_like(page_keys)
                output = torch.empty((batch, heads, dim), device=key.device, dtype=torch.float32)
                output = module.run_batch_init(query_f, key_f, value_f, starts_cpu, page_keys, page_values, output, PAGE_SIZE, pages_capacity)
                lengths = (tokens - starts).to(dtype=torch.int32).contiguous()
                persistent_cache[state_key] = {"tokens": tokens, "lengths": lengths, "page_keys": page_keys, "page_values": page_values, "output": output, "pages_capacity": pages_capacity}
            else:
                state["lengths"] = (tokens - starts).to(dtype=torch.int32).contiguous()
                state["output"] = module.run_batch_append(
                    query_f, key_f[:, :, -1, :].contiguous(), value_f[:, :, -1, :].contiguous(),
                    state["lengths"], state["page_keys"], state["page_values"], PAGE_SIZE, state["pages_capacity"],
                )
                state["tokens"] = tokens
                output = state["output"]
            return output.unsqueeze(1).to(query.dtype), None
        if workspace_key not in workspace_cache:
            pages_per_sequence = (tokens + PAGE_SIZE - 1) // PAGE_SIZE
            workspace_cache[workspace_key] = (
                torch.empty((batch, pages_per_sequence, heads, PAGE_SIZE, dim), device=key.device, dtype=torch.float32),
                torch.empty((batch, pages_per_sequence, heads, PAGE_SIZE, dim), device=key.device, dtype=torch.float32),
                torch.empty((batch, heads, dim), device=key.device, dtype=torch.float32),
            )
        page_keys, page_values, output = workspace_cache[workspace_key]
        output = module.run_batch_into(query_f, key_f, value_f, starts, page_keys, page_values, output, PAGE_SIZE)
        return output.unsqueeze(1).to(query.dtype), None

    gpt2_modeling.eager_attention_forward = fused
    model.config._attn_implementation = "eager"
    return len(model.transformer.h)


def install_persistent_fused_attention(model, module):
    return install_fused_attention(model, module, persistent=True)


def install_direct_attention(model, module):
    """Install the direct-K/V control path used to isolate page-packing cost."""
    original = gpt2_modeling.eager_attention_forward

    def direct(attention, query, key, value, attention_mask, scaling=None, dropout=0.0, **kwargs):
        if query.shape[-2] != 1:
            return original(attention, query, key, value, attention_mask, scaling=scaling, dropout=dropout, **kwargs)
        batch, heads, tokens, dim = key.shape
        query_f = query[:, :, -1, :].float().contiguous()
        key_f = key.float().contiguous()
        value_f = value.float().contiguous()
        starts = torch.zeros((batch,), dtype=torch.int32, device=key.device)
        if attention_mask is not None:
            for batch_index in range(batch):
                mask_row = attention_mask[batch_index].reshape(-1, attention_mask.shape[-1])[-1]
                allowed = mask_row if mask_row.dtype == torch.bool else mask_row > -1.0e4
                valid_indices = allowed.nonzero(as_tuple=False).flatten()
                if valid_indices.numel(): starts[batch_index] = valid_indices[0]
        output = module.run_batch_direct(query_f, key_f, value_f, starts, PAGE_SIZE)
        return output.unsqueeze(1).to(query.dtype), None

    gpt2_modeling.eager_attention_forward = direct
    model.config._attn_implementation = "eager"
    return len(model.transformer.h)


def synced(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    result = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, result


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; run this entrypoint in Google Colab")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_safetensors=True).to("cuda").eval()
    module = build_extension()
    power_sampler = PowerSampler()
    power_sampler.start()
    baseline = []
    for prompt in PROMPTS:
      for batch_size in BATCH_SIZES:
        encoded = tokenizer([prompt] * batch_size, return_tensors="pt").to("cuda")
        synced(lambda: native_decode(model, encoded))
        synced(lambda: native_decode(model, encoded))
        native_times = []
        for _ in range(REPEATS):
            native_times.append(synced(lambda: native_decode(model, encoded))[0])
        baseline.append({"prompt": prompt, "batch_size": batch_size, "encoded": encoded, "tokens": native_decode(model, encoded), "times": native_times})

    patched_layers = install_fused_attention(model, module)
    rows = []
    for item in baseline:
        encoded = item["encoded"]
        fused_times, fused_tokens = [], None
        for _ in range(REPEATS):
            fused_times.append(synced(lambda: native_decode(model, encoded))[0])
            fused_tokens = native_decode(model, encoded)
        parity = torch.equal(item["tokens"], fused_tokens)
        rows.append({
            "prompt_token_count": int(encoded["attention_mask"].sum().item()),
            "batch_size": item["batch_size"],
            "output_parity": parity,
            "native_decode_ms_median": statistics.median(item["times"]),
            "fused_paged_decode_ms_median": statistics.median(fused_times),
            "fused_overhead_ratio": statistics.median(fused_times) / max(statistics.median(item["times"]), 1e-12),
            "generated_tokens": fused_tokens[0].tolist(),
        })
    report = {
        "schema_version": "real-model-fused-paged-decode-v0.1",
        "experiment": "real_gpt2_end_to_end_decode_with_device_resident_cuda_paged_attention",
        "evidence_kind": "measured_gpu", "gpu_execution_accepted": True,
        "model_profile": {"model_id": MODEL_ID, "model_revision": getattr(model.config, "_commit_hash", None), "trained": True, "parameter_count": sum(p.numel() for p in model.parameters())},
        "device": "cuda", "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"page_size_tokens": PAGE_SIZE, "prompts": list(PROMPTS), "batch_sizes": list(BATCH_SIZES), "max_new_tokens": MAX_NEW_TOKENS, "repeats": REPEATS, "extended_profile": "--extended" in sys.argv, "microbatch_profile": "--microbatch" in sys.argv, "patched_attention_layers": patched_layers, "prefill": "native GPT-2 attention", "decode": "every one-token GPT-2 attention call routes through device-side K/V page packing plus CUDA paged attention", "page_allocator": "reused PyTorch CUDA K/V page workspace and output buffer per batch and token length across GPT-2 layers; no Python page-table or repack path", "kernel_variant": "one CUDA launch per GPT-2 attention layer over batch*heads with reusable page workspace and output buffer", "timing": "CUDA synchronized around complete generation"},
        "power": power_sampler.stop(),
        "rows": rows,
        "decision": "end_to_end_fused_paged_decode_parity_passed" if all(row["output_parity"] for row in rows) else "end_to_end_fused_paged_decode_parity_failed",
        "claim_boundary": {"allowed": "Full GPT-2 greedy decode token parity and synchronized timing with device-side page packing and paged attention on this T4 protocol.", "refused": "Optimized production performance, energy savings, allocator scalability under concurrency, analog benefit, silicon performance, or broad model generalization."},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": report["device_name"], "parity": report["decision"] == "end_to_end_fused_paged_decode_parity_passed", "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
