#include <cuda_runtime.h>

extern "C" __global__ void matmul_tiled_16(const float* __restrict__ a, const float* __restrict__ b, float* __restrict__ c, int m, int n, int k) {
  __shared__ float as[16][16];
  __shared__ float bs[16][16];
  int row = blockIdx.y * 16 + threadIdx.y;
  int col = blockIdx.x * 16 + threadIdx.x;
  float acc = 0.0f;
  for (int tile = 0; tile < k; tile += 16) {
    as[threadIdx.y][threadIdx.x] = row < m && tile + threadIdx.x < k ? a[row * k + tile + threadIdx.x] : 0.0f;
    bs[threadIdx.y][threadIdx.x] = col < n && tile + threadIdx.y < k ? b[(tile + threadIdx.y) * n + col] : 0.0f;
    __syncthreads();
    for (int i = 0; i < 16; ++i) acc += as[threadIdx.y][i] * bs[i][threadIdx.x];
    __syncthreads();
  }
  if (row < m && col < n) c[row * n + col] = acc;
}

extern "C" __global__ void gelu_inplace(float* x, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) {
    float v = x[i];
    x[i] = 0.5f * v * (1.0f + tanhf(0.7978845608f * (v + 0.044715f * v * v * v)));
  }
}
