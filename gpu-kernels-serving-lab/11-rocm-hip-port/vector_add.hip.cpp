#include <hip/hip_runtime.h>

#include <cstdio>
#include <cstdlib>

#define CHECK_HIP(call)                                                         \
  do {                                                                          \
    hipError_t err = call;                                                       \
    if (err != hipSuccess) {                                                     \
      std::fprintf(stderr, "HIP error %s:%d: %s\n", __FILE__, __LINE__,         \
                   hipGetErrorString(err));                                      \
      std::exit(1);                                                             \
    }                                                                           \
  } while (0)

__global__ void vector_add(const float* a, const float* b, float* c, int n) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx < n) {
    c[idx] = a[idx] + b[idx];
  }
}

int main() {
  const int n = 1 << 20;
  const int block = 256;
  const int grid = (n + block - 1) / block;
  float *a = nullptr, *b = nullptr, *c = nullptr;
  CHECK_HIP(hipMalloc(&a, n * sizeof(float)));
  CHECK_HIP(hipMalloc(&b, n * sizeof(float)));
  CHECK_HIP(hipMalloc(&c, n * sizeof(float)));
  hipLaunchKernelGGL(vector_add, dim3(grid), dim3(block), 0, 0, a, b, c, n);
  CHECK_HIP(hipGetLastError());
  CHECK_HIP(hipDeviceSynchronize());
  hipDeviceProp_t prop{};
  CHECK_HIP(hipGetDeviceProperties(&prop, 0));
  std::printf("{\"device\":\"%s\",\"n\":%d,\"block\":%d,\"status\":\"ran\"}\n",
              prop.name, n, block);
  CHECK_HIP(hipFree(a));
  CHECK_HIP(hipFree(b));
  CHECK_HIP(hipFree(c));
  return 0;
}

