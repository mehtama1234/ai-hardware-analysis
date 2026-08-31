#include <hip/hip_runtime.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

constexpr int N = 8192;
constexpr int M = 64;
constexpr int K = 64;
constexpr int TILE = 16;
constexpr int BLOCK = 256;

#define HIP_CHECK(expr)                                                         \
  do {                                                                          \
    hipError_t err = (expr);                                                    \
    if (err != hipSuccess) {                                                    \
      std::fprintf(stderr, "HIP error %s at %s:%d\n",                          \
                   hipGetErrorString(err), __FILE__, __LINE__);                 \
      std::exit(1);                                                             \
    }                                                                           \
  } while (0)

__global__ void vector_add_kernel(const float* x, const float* y, float* out, int n) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx < n) {
    out[idx] = x[idx] + y[idx];
  }
}

__global__ void block_reduce_kernel(const float* x, float* partial, int n) {
  __shared__ float scratch[BLOCK];
  int tid = threadIdx.x;
  int idx = blockIdx.x * blockDim.x + tid;
  scratch[tid] = idx < n ? x[idx] : 0.0f;
  __syncthreads();
  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) {
      scratch[tid] += scratch[tid + stride];
    }
    __syncthreads();
  }
  if (tid == 0) {
    partial[blockIdx.x] = scratch[0];
  }
}

__global__ void tiled_gemm_kernel(const float* a, const float* b, float* c) {
  __shared__ float tile_a[TILE][TILE];
  __shared__ float tile_b[TILE][TILE];
  int row = blockIdx.y * TILE + threadIdx.y;
  int col = blockIdx.x * TILE + threadIdx.x;
  float acc = 0.0f;
  for (int base = 0; base < K; base += TILE) {
    int a_col = base + threadIdx.x;
    int b_row = base + threadIdx.y;
    tile_a[threadIdx.y][threadIdx.x] = (row < M && a_col < K) ? a[row * K + a_col] : 0.0f;
    tile_b[threadIdx.y][threadIdx.x] = (b_row < K && col < M) ? b[b_row * M + col] : 0.0f;
    __syncthreads();
    for (int kk = 0; kk < TILE; ++kk) {
      acc += tile_a[threadIdx.y][kk] * tile_b[kk][threadIdx.x];
    }
    __syncthreads();
  }
  if (row < M && col < M) {
    c[row * M + col] = acc;
  }
}

float max_abs_error(const std::vector<float>& got, const std::vector<float>& ref) {
  float err = 0.0f;
  for (size_t i = 0; i < got.size(); ++i) {
    err = std::max(err, std::abs(got[i] - ref[i]));
  }
  return err;
}

int main() {
  std::vector<float> h_x(N);
  std::vector<float> h_y(N);
  std::vector<float> h_vec(N);
  std::vector<float> h_vec_ref(N);
  for (int i = 0; i < N; ++i) {
    h_x[i] = static_cast<float>((i % 31) - 15) / 31.0f;
    h_y[i] = static_cast<float>((i % 19) - 9) / 19.0f;
    h_vec_ref[i] = h_x[i] + h_y[i];
  }

  float* d_x = nullptr;
  float* d_y = nullptr;
  float* d_vec = nullptr;
  HIP_CHECK(hipMalloc(&d_x, N * sizeof(float)));
  HIP_CHECK(hipMalloc(&d_y, N * sizeof(float)));
  HIP_CHECK(hipMalloc(&d_vec, N * sizeof(float)));
  HIP_CHECK(hipMemcpy(d_x, h_x.data(), N * sizeof(float), hipMemcpyHostToDevice));
  HIP_CHECK(hipMemcpy(d_y, h_y.data(), N * sizeof(float), hipMemcpyHostToDevice));
  hipLaunchKernelGGL(vector_add_kernel, dim3((N + BLOCK - 1) / BLOCK), dim3(BLOCK), 0, 0, d_x, d_y, d_vec, N);
  HIP_CHECK(hipGetLastError());
  HIP_CHECK(hipDeviceSynchronize());
  HIP_CHECK(hipMemcpy(h_vec.data(), d_vec, N * sizeof(float), hipMemcpyDeviceToHost));

  int blocks = (N + BLOCK - 1) / BLOCK;
  float* d_partial = nullptr;
  std::vector<float> h_partial(blocks);
  HIP_CHECK(hipMalloc(&d_partial, blocks * sizeof(float)));
  hipLaunchKernelGGL(block_reduce_kernel, dim3(blocks), dim3(BLOCK), 0, 0, d_x, d_partial, N);
  HIP_CHECK(hipGetLastError());
  HIP_CHECK(hipDeviceSynchronize());
  HIP_CHECK(hipMemcpy(h_partial.data(), d_partial, blocks * sizeof(float), hipMemcpyDeviceToHost));
  float reduce_got = 0.0f;
  for (float value : h_partial) {
    reduce_got += value;
  }
  float reduce_ref = 0.0f;
  for (float value : h_x) {
    reduce_ref += value;
  }

  std::vector<float> h_a(M * K);
  std::vector<float> h_b(K * M);
  std::vector<float> h_c(M * M);
  std::vector<float> h_c_ref(M * M, 0.0f);
  for (int i = 0; i < M * K; ++i) {
    h_a[i] = static_cast<float>((i % 17) - 8) / 17.0f;
  }
  for (int i = 0; i < K * M; ++i) {
    h_b[i] = static_cast<float>((i % 13) - 6) / 13.0f;
  }
  for (int row = 0; row < M; ++row) {
    for (int col = 0; col < M; ++col) {
      float acc = 0.0f;
      for (int kk = 0; kk < K; ++kk) {
        acc += h_a[row * K + kk] * h_b[kk * M + col];
      }
      h_c_ref[row * M + col] = acc;
    }
  }

  float* d_a = nullptr;
  float* d_b = nullptr;
  float* d_c = nullptr;
  HIP_CHECK(hipMalloc(&d_a, h_a.size() * sizeof(float)));
  HIP_CHECK(hipMalloc(&d_b, h_b.size() * sizeof(float)));
  HIP_CHECK(hipMalloc(&d_c, h_c.size() * sizeof(float)));
  HIP_CHECK(hipMemcpy(d_a, h_a.data(), h_a.size() * sizeof(float), hipMemcpyHostToDevice));
  HIP_CHECK(hipMemcpy(d_b, h_b.data(), h_b.size() * sizeof(float), hipMemcpyHostToDevice));
  hipLaunchKernelGGL(tiled_gemm_kernel, dim3(M / TILE, M / TILE), dim3(TILE, TILE), 0, 0, d_a, d_b, d_c);
  HIP_CHECK(hipGetLastError());
  HIP_CHECK(hipDeviceSynchronize());
  HIP_CHECK(hipMemcpy(h_c.data(), d_c, h_c.size() * sizeof(float), hipMemcpyDeviceToHost));

  std::printf(
      "{\"vector_max_abs_error\":%.8f,\"reduction_abs_error\":%.8f,"
      "\"gemm_max_abs_error\":%.8f,\"operations\":[\"vector_add\",\"block_reduce\",\"tiled_gemm\"]}\n",
      max_abs_error(h_vec, h_vec_ref), std::abs(reduce_got - reduce_ref), max_abs_error(h_c, h_c_ref));

  HIP_CHECK(hipFree(d_x));
  HIP_CHECK(hipFree(d_y));
  HIP_CHECK(hipFree(d_vec));
  HIP_CHECK(hipFree(d_partial));
  HIP_CHECK(hipFree(d_a));
  HIP_CHECK(hipFree(d_b));
  HIP_CHECK(hipFree(d_c));
  return 0;
}
