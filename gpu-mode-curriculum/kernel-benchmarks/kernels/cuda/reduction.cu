#include <cuda_runtime.h>

extern "C" __global__ void block_reduce_sum(const float* __restrict__ x, float* __restrict__ partial, int n) {
  extern __shared__ float smem[];
  int tid = threadIdx.x;
  int i = blockIdx.x * blockDim.x * 2 + tid;
  float value = 0.0f;
  if (i < n) value += x[i];
  if (i + blockDim.x < n) value += x[i + blockDim.x];
  smem[tid] = value;
  __syncthreads();

  for (int stride = blockDim.x / 2; stride > 32; stride >>= 1) {
    if (tid < stride) smem[tid] += smem[tid + stride];
    __syncthreads();
  }
  if (tid < 32) {
    volatile float* vmem = smem;
    vmem[tid] += vmem[tid + 32];
    vmem[tid] += vmem[tid + 16];
    vmem[tid] += vmem[tid + 8];
    vmem[tid] += vmem[tid + 4];
    vmem[tid] += vmem[tid + 2];
    vmem[tid] += vmem[tid + 1];
  }
  if (tid == 0) partial[blockIdx.x] = smem[0];
}
