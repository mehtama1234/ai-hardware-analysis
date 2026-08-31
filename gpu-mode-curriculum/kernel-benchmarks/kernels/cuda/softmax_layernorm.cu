#include <cuda_runtime.h>
#include <math.h>

extern "C" __global__ void row_softmax_small(const float* __restrict__ x, float* __restrict__ y, int cols) {
  int row = blockIdx.x;
  int tid = threadIdx.x;
  extern __shared__ float smem[];
  float value = tid < cols ? x[row * cols + tid] : -INFINITY;
  smem[tid] = value;
  __syncthreads();
  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) smem[tid] = fmaxf(smem[tid], smem[tid + stride]);
    __syncthreads();
  }
  float max_value = smem[0];
  float exp_value = tid < cols ? expf(value - max_value) : 0.0f;
  smem[tid] = exp_value;
  __syncthreads();
  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) smem[tid] += smem[tid + stride];
    __syncthreads();
  }
  if (tid < cols) y[row * cols + tid] = exp_value / smem[0];
}

extern "C" __global__ void row_layernorm_small(const float* __restrict__ x, float* __restrict__ y, int cols, float eps) {
  int row = blockIdx.x;
  int tid = threadIdx.x;
  extern __shared__ float smem[];
  float value = tid < cols ? x[row * cols + tid] : 0.0f;
  smem[tid] = value;
  __syncthreads();
  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) smem[tid] += smem[tid + stride];
    __syncthreads();
  }
  float mean = smem[0] / cols;
  float centered = tid < cols ? value - mean : 0.0f;
  smem[tid] = centered * centered;
  __syncthreads();
  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) smem[tid] += smem[tid + stride];
    __syncthreads();
  }
  float inv_std = rsqrtf(smem[0] / cols + eps);
  if (tid < cols) y[row * cols + tid] = centered * inv_std;
}
