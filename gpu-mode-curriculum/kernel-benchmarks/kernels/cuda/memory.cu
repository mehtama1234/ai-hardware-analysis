#include <cuda_runtime.h>

extern "C" __global__ void vector_copy_contiguous(const float* __restrict__ x, float* __restrict__ y, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) {
    y[i] = x[i];
  }
}

extern "C" __global__ void vector_copy_strided(const float* __restrict__ x, float* __restrict__ y, int n, int stride) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  int j = i * stride;
  if (j < n) {
    y[j] = x[j];
  }
}

extern "C" __global__ void shared_bank_probe(const float* __restrict__ x, float* __restrict__ y, int stride) {
  __shared__ float tile[1024];
  int lane = threadIdx.x;
  int offset = lane * stride;
  tile[offset & 1023] = x[lane];
  __syncthreads();
  y[lane] = tile[offset & 1023];
}
