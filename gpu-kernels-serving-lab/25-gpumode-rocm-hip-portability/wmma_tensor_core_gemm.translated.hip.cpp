#include <cuda_fp16.h>
#include <hip/hip_runtime.h>
#include <mma.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

using namespace nvcuda;

constexpr int M = 256;
constexpr int N = 256;
constexpr int K = 256;
constexpr int WMMA_M = 16;
constexpr int WMMA_N = 16;
constexpr int WMMA_K = 16;

#define CUDA_CHECK(expr)                                                        \
  do {                                                                          \
    hipError_t err = (expr);                                                   \
    if (err != hipSuccess) {                                                   \
      std::fprintf(stderr, "CUDA error %s at %s:%d\n",                         \
                   hipGetErrorString(err), __FILE__, __LINE__);                \
      std::exit(1);                                                             \
    }                                                                           \
  } while (0)

__global__ void wmma_gemm_kernel(const half* a, const half* b, float* c) {
  int warp_m = blockIdx.y;
  int warp_n = blockIdx.x;

  wmma::fragment<wmma::matrix_a, WMMA_M, WMMA_N, WMMA_K, half, wmma::row_major> a_frag;
  wmma::fragment<wmma::matrix_b, WMMA_M, WMMA_N, WMMA_K, half, wmma::row_major> b_frag;
  wmma::fragment<wmma::accumulator, WMMA_M, WMMA_N, WMMA_K, float> acc_frag;
  wmma::fill_fragment(acc_frag, 0.0f);

  for (int kk = 0; kk < K; kk += WMMA_K) {
    const half* a_tile = a + (warp_m * WMMA_M) * K + kk;
    const half* b_tile = b + kk * N + warp_n * WMMA_N;
    wmma::load_matrix_sync(a_frag, a_tile, K);
    wmma::load_matrix_sync(b_frag, b_tile, N);
    wmma::mma_sync(acc_frag, a_frag, b_frag, acc_frag);
  }

  float* c_tile = c + (warp_m * WMMA_M) * N + warp_n * WMMA_N;
  wmma::store_matrix_sync(c_tile, acc_frag, N, wmma::mem_row_major);
}

float max_abs_error(const std::vector<float>& got, const std::vector<float>& ref) {
  float err = 0.0f;
  for (size_t i = 0; i < got.size(); ++i) {
    err = std::max(err, std::abs(got[i] - ref[i]));
  }
  return err;
}

int main() {
  std::vector<half> h_a(M * K);
  std::vector<half> h_b(K * N);
  std::vector<float> h_c(M * N);
  std::vector<float> h_ref(M * N, 0.0f);

  for (int i = 0; i < M * K; ++i) {
    h_a[i] = __float2half(static_cast<float>((i % 17) - 8) / 17.0f);
  }
  for (int i = 0; i < K * N; ++i) {
    h_b[i] = __float2half(static_cast<float>((i % 13) - 6) / 13.0f);
  }
  for (int row = 0; row < M; ++row) {
    for (int col = 0; col < N; ++col) {
      float acc = 0.0f;
      for (int kk = 0; kk < K; ++kk) {
        acc += __half2float(h_a[row * K + kk]) * __half2float(h_b[kk * N + col]);
      }
      h_ref[row * N + col] = acc;
    }
  }

  half* d_a = nullptr;
  half* d_b = nullptr;
  float* d_c = nullptr;
  CUDA_CHECK(hipMalloc(&d_a, h_a.size() * sizeof(half)));
  CUDA_CHECK(hipMalloc(&d_b, h_b.size() * sizeof(half)));
  CUDA_CHECK(hipMalloc(&d_c, h_c.size() * sizeof(float)));
  CUDA_CHECK(hipMemcpy(d_a, h_a.data(), h_a.size() * sizeof(half), hipMemcpyHostToDevice));
  CUDA_CHECK(hipMemcpy(d_b, h_b.data(), h_b.size() * sizeof(half), hipMemcpyHostToDevice));

  dim3 grid(N / WMMA_N, M / WMMA_M);
  dim3 block(32);
  wmma_gemm_kernel<<<grid, block>>>(d_a, d_b, d_c);
  CUDA_CHECK(hipGetLastError());
  CUDA_CHECK(hipDeviceSynchronize());

  hipEvent_t start;
  hipEvent_t stop;
  CUDA_CHECK(hipEventCreate(&start));
  CUDA_CHECK(hipEventCreate(&stop));
  CUDA_CHECK(hipEventRecord(start));
  for (int i = 0; i < 100; ++i) {
    wmma_gemm_kernel<<<grid, block>>>(d_a, d_b, d_c);
  }
  CUDA_CHECK(hipEventRecord(stop));
  CUDA_CHECK(hipEventSynchronize(stop));
  float total_ms = 0.0f;
  CUDA_CHECK(hipEventElapsedTime(&total_ms, start, stop));
  float ms = total_ms / 100.0f;
  CUDA_CHECK(hipMemcpy(h_c.data(), d_c, h_c.size() * sizeof(float), hipMemcpyDeviceToHost));

  double flops = 2.0 * M * N * K;
  double gflops = flops / (ms / 1000.0) / 1.0e9;
  std::printf(
      "{\"shape\":[%d,%d,%d],\"wmma_tile\":[%d,%d,%d],"
      "\"milliseconds\":%.5f,\"gflops\":%.5f,\"max_abs_error\":%.8f}\n",
      M, N, K, WMMA_M, WMMA_N, WMMA_K, ms, gflops, max_abs_error(h_c, h_ref));

  CUDA_CHECK(hipEventDestroy(start));
  CUDA_CHECK(hipEventDestroy(stop));
  CUDA_CHECK(hipFree(d_a));
  CUDA_CHECK(hipFree(d_b));
  CUDA_CHECK(hipFree(d_c));
  return 0;
}
