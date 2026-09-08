#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <mma.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <vector>

using namespace nvcuda;
constexpr int M = 128;
constexpr int N = 128;
constexpr int K = 128;
constexpr int TILE = 16;

#define CUDA_CHECK(expr) do { cudaError_t e = (expr); if (e != cudaSuccess) { \
  std::fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(e)); return 2; } } while (0)
#define CUBLAS_CHECK(expr) do { cublasStatus_t e = (expr); if (e != CUBLAS_STATUS_SUCCESS) { \
  std::fprintf(stderr, "cuBLAS error %d at %s:%d\n", static_cast<int>(e), __FILE__, __LINE__); return 2; } } while (0)

__global__ void wmma_gemm(const half* a, const half* b, float* c) {
  int tile_row = blockIdx.y;
  int tile_col = blockIdx.x;
  wmma::fragment<wmma::accumulator, TILE, TILE, TILE, float> acc;
  wmma::fill_fragment(acc, 0.0f);
  for (int tile_k = 0; tile_k < K / TILE; ++tile_k) {
    wmma::fragment<wmma::matrix_a, TILE, TILE, TILE, half, wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, TILE, TILE, TILE, half, wmma::row_major> b_frag;
    wmma::load_matrix_sync(a_frag, a + tile_row * TILE * K + tile_k * TILE, K);
    wmma::load_matrix_sync(b_frag, b + tile_k * TILE * N + tile_col * TILE, N);
    wmma::mma_sync(acc, a_frag, b_frag, acc);
  }
  wmma::store_matrix_sync(c + tile_row * TILE * N + tile_col * TILE, acc, N, wmma::mem_row_major);
}

template <typename Launch>
float timed(Launch launch, std::vector<float>& samples) {
  cudaEvent_t start, stop;
  CUDA_CHECK(cudaEventCreate(&start));
  CUDA_CHECK(cudaEventCreate(&stop));
  // Keep enough independent launches for the profiler contract to expose a
  // meaningful normalized capture, while still reporting the median rather
  // than a single noisy event on a small GEMM.
  for (int i = 0; i < 9; ++i) {
    CUDA_CHECK(cudaEventRecord(start));
    launch();
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaEventRecord(stop));
    CUDA_CHECK(cudaEventSynchronize(stop));
    float ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop));
    if (!std::isfinite(ms) || ms <= 0.0f) return -1.0f;
    samples.push_back(ms);
  }
  CUDA_CHECK(cudaEventDestroy(start));
  CUDA_CHECK(cudaEventDestroy(stop));
  auto sorted = samples;
  std::sort(sorted.begin(), sorted.end());
  return sorted[4];
}

double max_error(const std::vector<float>& got, const std::vector<double>& expected) {
  double value = 0.0;
  for (size_t i = 0; i < got.size(); ++i) value = std::max(value, std::abs(static_cast<double>(got[i]) - expected[i]));
  return value;
}

int main() {
  std::vector<half> host_a(M * K), host_b(K * N);
  std::vector<float> host_af(M * K), host_bf(K * N), host_wmma(M * N), host_blas(M * N);
  std::vector<double> reference(M * N, 0.0);
  for (int i = 0; i < M * K; ++i) { host_af[i] = static_cast<float>((i % 19) - 9) / 19.0f; host_a[i] = __float2half(host_af[i]); }
  for (int i = 0; i < K * N; ++i) { host_bf[i] = static_cast<float>((i % 23) - 11) / 23.0f; host_b[i] = __float2half(host_bf[i]); }
  for (int row = 0; row < M; ++row) for (int col = 0; col < N; ++col)
    for (int kk = 0; kk < K; ++kk) reference[row * N + col] += __half2float(host_a[row * K + kk]) * __half2float(host_b[kk * N + col]);
  half* device_a = nullptr; half* device_b = nullptr; float* device_wmma = nullptr; float* device_af = nullptr; float* device_bf = nullptr; float* device_blas = nullptr;
  CUDA_CHECK(cudaMalloc(&device_a, host_a.size() * sizeof(half))); CUDA_CHECK(cudaMalloc(&device_b, host_b.size() * sizeof(half)));
  CUDA_CHECK(cudaMalloc(&device_wmma, host_wmma.size() * sizeof(float))); CUDA_CHECK(cudaMalloc(&device_af, host_af.size() * sizeof(float)));
  CUDA_CHECK(cudaMalloc(&device_bf, host_bf.size() * sizeof(float))); CUDA_CHECK(cudaMalloc(&device_blas, host_blas.size() * sizeof(float)));
  CUDA_CHECK(cudaMemcpy(device_a, host_a.data(), host_a.size() * sizeof(half), cudaMemcpyHostToDevice)); CUDA_CHECK(cudaMemcpy(device_b, host_b.data(), host_b.size() * sizeof(half), cudaMemcpyHostToDevice));
  CUDA_CHECK(cudaMemcpy(device_af, host_af.data(), host_af.size() * sizeof(float), cudaMemcpyHostToDevice)); CUDA_CHECK(cudaMemcpy(device_bf, host_bf.data(), host_bf.size() * sizeof(float), cudaMemcpyHostToDevice));
  std::vector<float> wmma_samples, blas_samples;
  float wmma_ms = timed([&] { wmma_gemm<<<dim3(N / TILE, M / TILE), 32>>>(device_a, device_b, device_wmma); }, wmma_samples);
  CUDA_CHECK(cudaMemcpy(host_wmma.data(), device_wmma, host_wmma.size() * sizeof(float), cudaMemcpyDeviceToHost));
  cublasHandle_t handle; CUBLAS_CHECK(cublasCreate(&handle));
  const float alpha = 1.0f, beta = 0.0f;
  float blas_ms = timed([&] { cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K, &alpha, device_bf, N, device_af, K, &beta, device_blas, N); }, blas_samples);
  CUDA_CHECK(cudaMemcpy(host_blas.data(), device_blas, host_blas.size() * sizeof(float), cudaMemcpyDeviceToHost));
  CUBLAS_CHECK(cublasDestroy(handle));
  CUDA_CHECK(cudaFree(device_a)); CUDA_CHECK(cudaFree(device_b)); CUDA_CHECK(cudaFree(device_wmma)); CUDA_CHECK(cudaFree(device_af)); CUDA_CHECK(cudaFree(device_bf)); CUDA_CHECK(cudaFree(device_blas));
  double wmma_error = max_error(host_wmma, reference), blas_error = max_error(host_blas, reference);
  // FP16-input WMMA is compared against an FP64 reference with a 0.02 bound;
  // the FP32 cuBLAS baseline uses a tighter but nonzero rounding bound.
  bool passed = wmma_ms > 0 && blas_ms > 0 && wmma_error <= 0.02 && blas_error <= 5e-4;
  std::cout << "{\"status\":\"" << (passed ? "passed" : "failed") << "\",\"shape\":[" << M << "," << N << "," << K
            << "],\"wmma_max_abs_error\":" << std::setprecision(12) << wmma_error << ",\"cublas_max_abs_error\":" << blas_error
            << ",\"wmma_median_ms\":" << wmma_ms << ",\"cublas_median_ms\":" << blas_ms << ",\"wmma_samples_ms\":[";
  for (size_t i = 0; i < wmma_samples.size(); ++i) std::cout << (i ? "," : "") << wmma_samples[i];
  std::cout << "],\"cublas_samples_ms\":[";
  for (size_t i = 0; i < blas_samples.size(); ++i) std::cout << (i ? "," : "") << blas_samples[i];
  std::cout << "],\"gpu_execution_accepted\":" << (passed ? "true" : "false") << "}\n";
  return passed ? 0 : 1;
}
