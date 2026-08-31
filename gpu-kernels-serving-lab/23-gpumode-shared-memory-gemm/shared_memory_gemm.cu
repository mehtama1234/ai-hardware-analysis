#include <cuda_runtime.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

constexpr int M = 256;
constexpr int N = 256;
constexpr int K = 256;
constexpr int TILE = 16;

#define CUDA_CHECK(expr)                                                        \
  do {                                                                          \
    cudaError_t err = (expr);                                                   \
    if (err != cudaSuccess) {                                                   \
      std::fprintf(stderr, "CUDA error %s at %s:%d\n",                         \
                   cudaGetErrorString(err), __FILE__, __LINE__);                \
      std::exit(1);                                                             \
    }                                                                           \
  } while (0)

__global__ void naive_gemm(const float* a, const float* b, float* c) {
  int row = blockIdx.y * blockDim.y + threadIdx.y;
  int col = blockIdx.x * blockDim.x + threadIdx.x;
  if (row >= M || col >= N) {
    return;
  }
  float acc = 0.0f;
  for (int kk = 0; kk < K; ++kk) {
    acc += a[row * K + kk] * b[kk * N + col];
  }
  c[row * N + col] = acc;
}

__global__ void tiled_gemm(const float* a, const float* b, float* c) {
  __shared__ float tile_a[TILE][TILE];
  __shared__ float tile_b[TILE][TILE];

  int row = blockIdx.y * TILE + threadIdx.y;
  int col = blockIdx.x * TILE + threadIdx.x;
  float acc = 0.0f;

  for (int base = 0; base < K; base += TILE) {
    int a_col = base + threadIdx.x;
    int b_row = base + threadIdx.y;
    tile_a[threadIdx.y][threadIdx.x] = (row < M && a_col < K) ? a[row * K + a_col] : 0.0f;
    tile_b[threadIdx.y][threadIdx.x] = (b_row < K && col < N) ? b[b_row * N + col] : 0.0f;
    __syncthreads();

    for (int kk = 0; kk < TILE; ++kk) {
      acc += tile_a[threadIdx.y][kk] * tile_b[kk][threadIdx.x];
    }
    __syncthreads();
  }

  if (row < M && col < N) {
    c[row * N + col] = acc;
  }
}

float max_abs_error(const std::vector<float>& got, const std::vector<float>& ref) {
  float err = 0.0f;
  for (size_t i = 0; i < got.size(); ++i) {
    err = std::max(err, std::abs(got[i] - ref[i]));
  }
  return err;
}

float run_kernel(void (*kernel)(const float*, const float*, float*), const float* a,
                 const float* b, float* c, dim3 grid, dim3 block, int repeat) {
  cudaEvent_t start;
  cudaEvent_t stop;
  CUDA_CHECK(cudaEventCreate(&start));
  CUDA_CHECK(cudaEventCreate(&stop));
  kernel<<<grid, block>>>(a, b, c);
  CUDA_CHECK(cudaGetLastError());
  CUDA_CHECK(cudaDeviceSynchronize());
  CUDA_CHECK(cudaEventRecord(start));
  for (int i = 0; i < repeat; ++i) {
    kernel<<<grid, block>>>(a, b, c);
  }
  CUDA_CHECK(cudaEventRecord(stop));
  CUDA_CHECK(cudaEventSynchronize(stop));
  float ms = 0.0f;
  CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop));
  CUDA_CHECK(cudaEventDestroy(start));
  CUDA_CHECK(cudaEventDestroy(stop));
  return ms / repeat;
}

int main() {
  std::vector<float> h_a(M * K);
  std::vector<float> h_b(K * N);
  std::vector<float> h_c(M * N);
  std::vector<float> h_tiled(M * N);
  std::vector<float> h_ref(M * N, 0.0f);
  for (int i = 0; i < M * K; ++i) {
    h_a[i] = static_cast<float>((i % 17) - 8) / 17.0f;
  }
  for (int i = 0; i < K * N; ++i) {
    h_b[i] = static_cast<float>((i % 13) - 6) / 13.0f;
  }
  for (int row = 0; row < M; ++row) {
    for (int col = 0; col < N; ++col) {
      float acc = 0.0f;
      for (int kk = 0; kk < K; ++kk) {
        acc += h_a[row * K + kk] * h_b[kk * N + col];
      }
      h_ref[row * N + col] = acc;
    }
  }

  float* d_a = nullptr;
  float* d_b = nullptr;
  float* d_c = nullptr;
  CUDA_CHECK(cudaMalloc(&d_a, h_a.size() * sizeof(float)));
  CUDA_CHECK(cudaMalloc(&d_b, h_b.size() * sizeof(float)));
  CUDA_CHECK(cudaMalloc(&d_c, h_c.size() * sizeof(float)));
  CUDA_CHECK(cudaMemcpy(d_a, h_a.data(), h_a.size() * sizeof(float), cudaMemcpyHostToDevice));
  CUDA_CHECK(cudaMemcpy(d_b, h_b.data(), h_b.size() * sizeof(float), cudaMemcpyHostToDevice));

  dim3 block(TILE, TILE);
  dim3 grid((N + TILE - 1) / TILE, (M + TILE - 1) / TILE);
  float naive_ms = run_kernel(naive_gemm, d_a, d_b, d_c, grid, block, 30);
  CUDA_CHECK(cudaMemcpy(h_c.data(), d_c, h_c.size() * sizeof(float), cudaMemcpyDeviceToHost));
  float tiled_ms = run_kernel(tiled_gemm, d_a, d_b, d_c, grid, block, 30);
  CUDA_CHECK(cudaMemcpy(h_tiled.data(), d_c, h_tiled.size() * sizeof(float), cudaMemcpyDeviceToHost));

  double flops = 2.0 * M * N * K;
  double naive_gflops = flops / (naive_ms / 1000.0) / 1.0e9;
  double tiled_gflops = flops / (tiled_ms / 1000.0) / 1.0e9;
  std::printf(
      "{\"shape\":[%d,%d,%d],\"tile\":%d,"
      "\"naive_ms\":%.5f,\"tiled_ms\":%.5f,"
      "\"naive_gflops\":%.5f,\"tiled_gflops\":%.5f,"
      "\"speedup\":%.5f,\"naive_max_abs_error\":%.8f,\"tiled_max_abs_error\":%.8f}\n",
      M, N, K, TILE, naive_ms, tiled_ms, naive_gflops, tiled_gflops,
      naive_ms / tiled_ms, max_abs_error(h_c, h_ref), max_abs_error(h_tiled, h_ref));

  CUDA_CHECK(cudaFree(d_a));
  CUDA_CHECK(cudaFree(d_b));
  CUDA_CHECK(cudaFree(d_c));
  return 0;
}
