#include <hip/hip_runtime.h>
#include <stdio.h>

__global__ void hip_vector_add(const float* a, const float* b, float* c, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) c[i] = a[i] + b[i];
}

int main() {
  printf("{\"status\":\"source-only\",\"next\":\"compile with hipcc on a ROCm machine\"}\n");
  return 0;
}
