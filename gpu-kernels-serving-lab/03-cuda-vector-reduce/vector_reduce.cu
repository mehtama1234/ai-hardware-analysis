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

__global__ void vector_add(const float* a, const float* b, float* c, int n) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx < n) {
    c[idx] = a[idx] + b[idx];
  }
}

__global__ void block_reduce_sum(const float* x, float* partial, int n) {
  extern __shared__ float smem[];
  int tid = threadIdx.x;
  int idx = blockIdx.x * blockDim.x * 2 + threadIdx.x;
  float sum = 0.0f;
  if (idx < n) {
    sum += x[idx];
  }
  if (idx + blockDim.x < n) {
    sum += x[idx + blockDim.x];
  }
  smem[tid] = sum;
  __syncthreads();

  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) {
      smem[tid] += smem[tid + stride];
    }
    __syncthreads();
  }
  if (tid == 0) {
    partial[blockIdx.x] = smem[0];
  }
}

float time_ms(cudaEvent_t start, cudaEvent_t stop) {
  float ms = 0.0f;
  CHECK_CUDA(cudaEventElapsedTime(&ms, start, stop));
  return ms;
}

int main() {
  const int n = 1 << 24;
  const int block = 256;
  const int grid = (n + block - 1) / block;
  const int red_grid = (n + block * 2 - 1) / (block * 2);

  std::vector<float> h_a(n), h_b(n), h_c(n);
  for (int i = 0; i < n; ++i) {
    h_a[i] = std::sin(i * 0.001f);
    h_b[i] = std::cos(i * 0.001f);
  }

  float *d_a = nullptr, *d_b = nullptr, *d_c = nullptr, *d_partial = nullptr;
  CHECK_CUDA(cudaMalloc(&d_a, n * sizeof(float)));
  CHECK_CUDA(cudaMalloc(&d_b, n * sizeof(float)));
  CHECK_CUDA(cudaMalloc(&d_c, n * sizeof(float)));
  CHECK_CUDA(cudaMalloc(&d_partial, red_grid * sizeof(float)));
  CHECK_CUDA(cudaMemcpy(d_a, h_a.data(), n * sizeof(float), cudaMemcpyHostToDevice));
  CHECK_CUDA(cudaMemcpy(d_b, h_b.data(), n * sizeof(float), cudaMemcpyHostToDevice));

  cudaEvent_t start, stop;
  CHECK_CUDA(cudaEventCreate(&start));
  CHECK_CUDA(cudaEventCreate(&stop));

  vector_add<<<grid, block>>>(d_a, d_b, d_c, n);
  CHECK_CUDA(cudaGetLastError());
  CHECK_CUDA(cudaDeviceSynchronize());

  CHECK_CUDA(cudaEventRecord(start));
  for (int i = 0; i < 50; ++i) {
    vector_add<<<grid, block>>>(d_a, d_b, d_c, n);
  }
  CHECK_CUDA(cudaEventRecord(stop));
  CHECK_CUDA(cudaEventSynchronize(stop));
  float add_ms = time_ms(start, stop) / 50.0f;

  block_reduce_sum<<<red_grid, block, block * sizeof(float)>>>(d_c, d_partial, n);
  CHECK_CUDA(cudaGetLastError());
  CHECK_CUDA(cudaDeviceSynchronize());

  CHECK_CUDA(cudaEventRecord(start));
  for (int i = 0; i < 50; ++i) {
    block_reduce_sum<<<red_grid, block, block * sizeof(float)>>>(d_c, d_partial, n);
  }
  CHECK_CUDA(cudaEventRecord(stop));
  CHECK_CUDA(cudaEventSynchronize(stop));
  float reduce_ms = time_ms(start, stop) / 50.0f;

  CHECK_CUDA(cudaMemcpy(h_c.data(), d_c, n * sizeof(float), cudaMemcpyDeviceToHost));
  float max_err = 0.0f;
  for (int i = 0; i < n; i += 4096) {
    max_err = std::max(max_err, std::abs(h_c[i] - (h_a[i] + h_b[i])));
  }

  int device = 0;
  cudaDeviceProp prop{};
  CHECK_CUDA(cudaGetDeviceProperties(&prop, device));
  double add_bytes = 3.0 * n * sizeof(float);
  double reduce_bytes = 1.0 * n * sizeof(float);
  std::printf("{\"device\":\"%s\",\"n\":%d,\"block\":%d,"
              "\"vector_add_ms\":%.6f,\"vector_add_gbps\":%.3f,"
              "\"reduce_ms\":%.6f,\"reduce_gbps\":%.3f,"
              "\"sample_max_error\":%.8f}\n",
              prop.name, n, block, add_ms, add_bytes / (add_ms / 1000.0) / 1e9,
              reduce_ms, reduce_bytes / (reduce_ms / 1000.0) / 1e9, max_err);

  CHECK_CUDA(cudaFree(d_a));
  CHECK_CUDA(cudaFree(d_b));
  CHECK_CUDA(cudaFree(d_c));
  CHECK_CUDA(cudaFree(d_partial));
  CHECK_CUDA(cudaEventDestroy(start));
  CHECK_CUDA(cudaEventDestroy(stop));
  return 0;
}

