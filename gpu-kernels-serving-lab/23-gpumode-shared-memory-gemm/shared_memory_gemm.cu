#include <cuda_runtime.h>
#include <cublas_v2.h>

#include <cmath>
#include <algorithm>
#include <limits>
#include <cstdio>
#include <cstdlib>
#include <vector>

#ifndef GEMM_M
#define GEMM_M 256
#endif
#ifndef GEMM_N
#define GEMM_N 256
#endif
#ifndef GEMM_K
#define GEMM_K 256
#endif
constexpr int M = GEMM_M;
constexpr int N = GEMM_N;
constexpr int K = GEMM_K;
constexpr int TILE = 16;
static_assert(M > 0 && N > 0 && K > 0, "positive GEMM dimensions required");

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

double max_abs_error(const std::vector<float>& got, const std::vector<double>& ref) {
  double err = 0.0;
  for (size_t i = 0; i < got.size(); ++i) {
    if (!std::isfinite(got[i]) || !std::isfinite(ref[i])) {
      return std::numeric_limits<double>::infinity();
    }
    err = std::max(err, std::abs(static_cast<double>(got[i]) - ref[i]));
  }
  return err;
}

void check_blas(cublasStatus_t status) {
  if (status != CUBLAS_STATUS_SUCCESS) {
    std::fprintf(stderr, "cuBLAS error %d\n", static_cast<int>(status));
    std::exit(1);
  }
}

template <typename Launch>
float run_operation(Launch launch, int repeat, std::vector<float>& samples) {
  cudaEvent_t start;
  cudaEvent_t stop;
  CUDA_CHECK(cudaEventCreate(&start));
  CUDA_CHECK(cudaEventCreate(&stop));
  launch();
  CUDA_CHECK(cudaGetLastError());
  CUDA_CHECK(cudaDeviceSynchronize());
  for (int sample = 0; sample < 7; ++sample) {
    CUDA_CHECK(cudaEventRecord(start));
    for (int i = 0; i < repeat; ++i) {
      launch();
      CUDA_CHECK(cudaGetLastError());
    }
    CUDA_CHECK(cudaEventRecord(stop));
    CUDA_CHECK(cudaEventSynchronize(stop));
    float ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop));
    if (!std::isfinite(ms) || ms <= 0) {
      std::fprintf(stderr, "Invalid event duration\n");
      std::exit(2);
    }
    samples.push_back(ms / repeat);
  }
  CUDA_CHECK(cudaEventDestroy(start));
  CUDA_CHECK(cudaEventDestroy(stop));
  auto sorted = samples;
  std::sort(sorted.begin(), sorted.end());
  return sorted[sorted.size() / 2];
}

void print_samples(const char* name, const std::vector<float>& samples) {
  std::printf(",\"%s\":[", name);
  for (size_t i = 0; i < samples.size(); ++i) {
    std::printf("%s%.9g", i ? "," : "", samples[i]);
  }
  std::printf("]");
}

int main() {
  std::vector<float> h_a(M * K);
  std::vector<float> h_b(K * N);
  std::vector<float> h_c(M * N);
  std::vector<float> h_tiled(M * N);
  std::vector<float> h_blas(M * N);
  std::vector<double> h_ref(M * N, 0.0);
  for (int i = 0; i < M * K; ++i) {
    h_a[i] = static_cast<float>((i % 17) - 8) / 17.0f;
  }
  for (int i = 0; i < K * N; ++i) {
    h_b[i] = static_cast<float>((i % 13) - 6) / 13.0f;
  }
  for (int row = 0; row < M; ++row) {
    for (int col = 0; col < N; ++col) {
      double acc = 0.0;
      for (int kk = 0; kk < K; ++kk) {
        acc += static_cast<double>(h_a[row * K + kk]) * h_b[kk * N + col];
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
  std::vector<float> naive_samples, tiled_samples, blas_samples;
  CUDA_CHECK(cudaMemset(d_c, 0xff, h_c.size() * sizeof(float)));
  float naive_ms = run_operation([&]() { naive_gemm<<<grid, block>>>(d_a, d_b, d_c); }, 30, naive_samples);
  CUDA_CHECK(cudaMemcpy(h_c.data(), d_c, h_c.size() * sizeof(float), cudaMemcpyDeviceToHost));
  CUDA_CHECK(cudaMemset(d_c, 0xff, h_c.size() * sizeof(float)));
  float tiled_ms = run_operation([&]() { tiled_gemm<<<grid, block>>>(d_a, d_b, d_c); }, 30, tiled_samples);
  CUDA_CHECK(cudaMemcpy(h_tiled.data(), d_c, h_tiled.size() * sizeof(float), cudaMemcpyDeviceToHost));

  cublasHandle_t handle;
  check_blas(cublasCreate(&handle));
  check_blas(cublasSetMathMode(handle, CUBLAS_PEDANTIC_MATH));
  const float alpha = 1.0f, beta = 0.0f;
  CUDA_CHECK(cudaMemset(d_c, 0xff, h_c.size() * sizeof(float)));
  // Row-major C=A*B is column-major C^T=B^T*A^T: swap operands and M/N.
  float blas_ms = run_operation([&]() {
    check_blas(cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K,
                          &alpha, d_b, N, d_a, K, &beta, d_c, N));
  }, 30, blas_samples);
  CUDA_CHECK(cudaMemcpy(h_blas.data(), d_c, h_blas.size() * sizeof(float), cudaMemcpyDeviceToHost));
  int blas_version = 0, runtime_version = 0, driver_version = 0, device = 0;
  check_blas(cublasGetVersion(handle, &blas_version));
  CUDA_CHECK(cudaRuntimeGetVersion(&runtime_version));
  CUDA_CHECK(cudaDriverGetVersion(&driver_version));
  CUDA_CHECK(cudaGetDevice(&device));
  cudaDeviceProp properties;
  CUDA_CHECK(cudaGetDeviceProperties(&properties, device));
  check_blas(cublasDestroy(handle));

  double flops = 2.0 * M * N * K;
  double naive_gflops = flops / (naive_ms / 1000.0) / 1.0e9;
  double tiled_gflops = flops / (tiled_ms / 1000.0) / 1.0e9;
  double naive_error = max_abs_error(h_c, h_ref);
  double tiled_error = max_abs_error(h_tiled, h_ref);
  double blas_error = max_abs_error(h_blas, h_ref);
  if (!std::isfinite(naive_error) || !std::isfinite(tiled_error) ||
      !std::isfinite(blas_error) || naive_error > 1e-4 || tiled_error > 1e-4 || blas_error > 1e-4) {
    std::fprintf(stderr, "GEMM numerical validation failed: naive=%g tiled=%g cublas=%g\n",
                 naive_error, tiled_error, blas_error);
    CUDA_CHECK(cudaFree(d_a));
    CUDA_CHECK(cudaFree(d_b));
    CUDA_CHECK(cudaFree(d_c));
    return 2;
  }
  std::printf(
      "{\"shape\":[%d,%d,%d],\"tile\":%d,"
      "\"naive_ms\":%.5f,\"tiled_ms\":%.5f,"
      "\"naive_gflops\":%.5f,\"tiled_gflops\":%.5f,"
      "\"speedup\":%.5f,\"naive_max_abs_error\":%.8f,\"tiled_max_abs_error\":%.8f",
      M, N, K, TILE, naive_ms, tiled_ms, naive_gflops, tiled_gflops,
      naive_ms / tiled_ms, naive_error, tiled_error);
  print_samples("naive_samples_ms", naive_samples);
  print_samples("tiled_samples_ms", tiled_samples);
  print_samples("cublas_samples_ms", blas_samples);
  std::printf(",\"cublas_ms\":%.9g,\"cublas_max_abs_error\":%.9g,"
              "\"cublas_gflops\":%.9g,\"tiled_vs_cublas_speedup\":%.9g,"
              "\"cublas_math_mode\":\"CUBLAS_PEDANTIC_MATH\","
              "\"cublas_version\":%d,\"cuda_runtime_version\":%d,\"cuda_driver_version\":%d,"
              "\"compute_capability\":[%d,%d],\"device_ordinal\":%d,\"device_memory_bytes\":%llu",
              blas_ms, blas_error, flops / (blas_ms / 1000.0) / 1e9, blas_ms / tiled_ms,
              blas_version, runtime_version, driver_version, properties.major, properties.minor,
              device, static_cast<unsigned long long>(properties.totalGlobalMem));
  std::printf(",\"evidence_kind\":\"measured_gpu\",\"warmup_launches\":1,"
              "\"launches_per_sample\":30,\"sample_count\":7,"
              "\"reference\":\"CPU FP64 accumulation\","
              "\"timing_scope\":\"median of seven CUDA-event batch means; 30 launches per batch; excludes allocation and transfers\"}\n");

  CUDA_CHECK(cudaFree(d_a));
  CUDA_CHECK(cudaFree(d_b));
  CUDA_CHECK(cudaFree(d_c));
  return 0;
}
