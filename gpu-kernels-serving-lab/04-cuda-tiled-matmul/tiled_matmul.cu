#include <cuda_runtime.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

#define CHECK_CUDA(call)                                                       \
  do {                                                                         \
    cudaError_t err = call;                                                    \
    if (err != cudaSuccess) {                                                  \
      std::fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__,       \
                   cudaGetErrorString(err));                                   \
      std::exit(1);                                                            \
    }                                                                          \
  } while (0)

constexpr int TILE = 16;

__global__ void matmul_naive(const float* a, const float* b, float* c, int n) {
  int row = blockIdx.y * blockDim.y + threadIdx.y;
  int col = blockIdx.x * blockDim.x + threadIdx.x;
  if (row >= n || col >= n) {
    return;
  }
  float acc = 0.0f;
  for (int k = 0; k < n; ++k) {
    acc += a[row * n + k] * b[k * n + col];
  }
  c[row * n + col] = acc;
}

__global__ void matmul_tiled(const float* a, const float* b, float* c, int n) {
  __shared__ float as[TILE][TILE];
  __shared__ float bs[TILE][TILE];
  int row = blockIdx.y * TILE + threadIdx.y;
  int col = blockIdx.x * TILE + threadIdx.x;
  float acc = 0.0f;

  for (int t = 0; t < n; t += TILE) {
    int a_col = t + threadIdx.x;
    int b_row = t + threadIdx.y;
    as[threadIdx.y][threadIdx.x] = (row < n && a_col < n) ? a[row * n + a_col] : 0.0f;
    bs[threadIdx.y][threadIdx.x] = (b_row < n && col < n) ? b[b_row * n + col] : 0.0f;
    __syncthreads();
    for (int k = 0; k < TILE; ++k) {
      acc += as[threadIdx.y][k] * bs[k][threadIdx.x];
    }
    __syncthreads();
  }
  if (row < n && col < n) {
    c[row * n + col] = acc;
  }
}

float elapsed_ms(cudaEvent_t start, cudaEvent_t stop) {
  float ms = 0.0f;
  CHECK_CUDA(cudaEventElapsedTime(&ms, start, stop));
  return ms;
}

template <typename Kernel>
float time_kernel(Kernel kernel, const float* a, const float* b, float* c, int n, dim3 grid, dim3 block) {
  cudaEvent_t start, stop;
  CHECK_CUDA(cudaEventCreate(&start));
  CHECK_CUDA(cudaEventCreate(&stop));
  kernel<<<grid, block>>>(a, b, c, n);
  CHECK_CUDA(cudaGetLastError());
  CHECK_CUDA(cudaDeviceSynchronize());
  CHECK_CUDA(cudaEventRecord(start));
  for (int i = 0; i < 10; ++i) {
    kernel<<<grid, block>>>(a, b, c, n);
  }
  CHECK_CUDA(cudaEventRecord(stop));
  CHECK_CUDA(cudaEventSynchronize(stop));
  float ms = elapsed_ms(start, stop) / 10.0f;
  CHECK_CUDA(cudaEventDestroy(start));
  CHECK_CUDA(cudaEventDestroy(stop));
  return ms;
}

int main() {
  const int n = 512;
  const size_t bytes = static_cast<size_t>(n) * n * sizeof(float);
  std::vector<float> h_a(n * n), h_b(n * n), h_c(n * n), h_ref(n * n);
  for (int i = 0; i < n * n; ++i) {
    h_a[i] = std::sin(i * 0.001f);
    h_b[i] = std::cos(i * 0.001f);
  }

  float *d_a = nullptr, *d_b = nullptr, *d_c = nullptr, *d_t = nullptr;
  CHECK_CUDA(cudaMalloc(&d_a, bytes));
  CHECK_CUDA(cudaMalloc(&d_b, bytes));
  CHECK_CUDA(cudaMalloc(&d_c, bytes));
  CHECK_CUDA(cudaMalloc(&d_t, bytes));
  CHECK_CUDA(cudaMemcpy(d_a, h_a.data(), bytes, cudaMemcpyHostToDevice));
  CHECK_CUDA(cudaMemcpy(d_b, h_b.data(), bytes, cudaMemcpyHostToDevice));

  dim3 block(TILE, TILE);
  dim3 grid((n + TILE - 1) / TILE, (n + TILE - 1) / TILE);
  float naive_ms = time_kernel(matmul_naive, d_a, d_b, d_c, n, grid, block);
  float tiled_ms = time_kernel(matmul_tiled, d_a, d_b, d_t, n, grid, block);
  CHECK_CUDA(cudaMemcpy(h_c.data(), d_c, bytes, cudaMemcpyDeviceToHost));
  CHECK_CUDA(cudaMemcpy(h_ref.data(), d_t, bytes, cudaMemcpyDeviceToHost));

  float max_err = 0.0f;
  for (int i = 0; i < n * n; i += 97) {
    max_err = fmaxf(max_err, fabsf(h_c[i] - h_ref[i]));
  }

  cudaDeviceProp prop{};
  CHECK_CUDA(cudaGetDeviceProperties(&prop, 0));
  const double flops = 2.0 * n * n * n;
  std::printf("{\"device\":\"%s\",\"n\":%d,\"tile\":%d,"
              "\"naive_ms\":%.6f,\"tiled_ms\":%.6f,"
              "\"naive_tflops\":%.6f,\"tiled_tflops\":%.6f,"
              "\"speedup\":%.3f,\"sample_max_error\":%.8f}\n",
              prop.name, n, TILE, naive_ms, tiled_ms,
              flops / (naive_ms / 1000.0) / 1e12,
              flops / (tiled_ms / 1000.0) / 1e12,
              naive_ms / tiled_ms, max_err);

  CHECK_CUDA(cudaFree(d_a));
  CHECK_CUDA(cudaFree(d_b));
  CHECK_CUDA(cudaFree(d_c));
  CHECK_CUDA(cudaFree(d_t));
  return 0;
}

