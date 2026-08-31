#include <stdio.h>

extern "C" __global__ void coalesced_copy(const float* __restrict__ x, float* __restrict__ y, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) y[i] = x[i];
}

extern "C" __global__ void strided_copy(const float* __restrict__ x, float* __restrict__ y, int n, int stride) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  int j = i * stride;
  if (j < n) y[j] = x[j];
}

int main() {
  printf("{\"status\":\"source-only\",\"next\":\"compile with nvcc on a CUDA machine\"}\n");
  return 0;
}
