#include <cuda_runtime.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <vector>

extern "C" __global__ void coalesced_copy(const float* __restrict__ x, float* __restrict__ y, int n);
extern "C" __global__ void strided_copy(const float* __restrict__ x, float* __restrict__ y, int n, int stride);

#define CUDA_CHECK(expr) do { \
  cudaError_t error = (expr); \
  if (error != cudaSuccess) { \
    std::fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(error)); \
    return 2; \
  } \
} while (0)

int main() {
  constexpr int n = 1 << 20;
  constexpr int block = 256;
  std::vector<float> host_x(n), host_y(n), expected(n);
  std::iota(host_x.begin(), host_x.end(), -static_cast<float>(n) / 2.0f);
  float* device_x = nullptr;
  float* device_y = nullptr;
  CUDA_CHECK(cudaMalloc(&device_x, n * sizeof(float)));
  CUDA_CHECK(cudaMalloc(&device_y, n * sizeof(float)));
  CUDA_CHECK(cudaMemcpy(device_x, host_x.data(), n * sizeof(float), cudaMemcpyHostToDevice));

  std::cout << "{\"status\":\"passed\",\"n\":" << n << ",\"cases\":[";
  bool all_passed = true;
  bool first_case = true;
  for (int stride : {1, 4, 16}) {
    CUDA_CHECK(cudaMemset(device_y, 0, n * sizeof(float)));
    int work = (n + stride - 1) / stride;
    cudaEvent_t start, stop;
    CUDA_CHECK(cudaEventCreate(&start));
    CUDA_CHECK(cudaEventCreate(&stop));
    std::vector<float> samples;
    for (int sample = 0; sample < 7; ++sample) {
      if (stride == 1) {
        coalesced_copy<<<(work + block - 1) / block, block>>>(device_x, device_y, n);
      } else {
        strided_copy<<<(work + block - 1) / block, block>>>(device_x, device_y, n, stride);
      }
      CUDA_CHECK(cudaGetLastError());
      CUDA_CHECK(cudaEventRecord(start));
      if (stride == 1) {
        coalesced_copy<<<(work + block - 1) / block, block>>>(device_x, device_y, n);
      } else {
        strided_copy<<<(work + block - 1) / block, block>>>(device_x, device_y, n, stride);
      }
      CUDA_CHECK(cudaGetLastError());
      CUDA_CHECK(cudaEventRecord(stop));
      CUDA_CHECK(cudaEventSynchronize(stop));
      float milliseconds = 0.0f;
      CUDA_CHECK(cudaEventElapsedTime(&milliseconds, start, stop));
      if (!std::isfinite(milliseconds) || milliseconds <= 0.0f) return 3;
      samples.push_back(milliseconds);
    }
    CUDA_CHECK(cudaMemcpy(host_y.data(), device_y, n * sizeof(float), cudaMemcpyDeviceToHost));
    std::fill(expected.begin(), expected.end(), 0.0f);
    for (int i = 0; i < work; ++i) expected[i * stride] = host_x[i * stride];
    float max_error = 0.0f;
    for (int i = 0; i < n; ++i) max_error = std::max(max_error, std::abs(host_y[i] - expected[i]));
    std::sort(samples.begin(), samples.end());
    bool passed = max_error <= 0.0f;
    all_passed = all_passed && passed;
    if (!first_case) std::cout << ",";
    first_case = false;
    std::cout << "{\"stride\":" << stride << ",\"work_items\":" << work
              << ",\"passed\":" << (passed ? "true" : "false")
              << ",\"max_abs_error\":" << std::setprecision(9) << max_error
              << ",\"median_ms\":" << samples[3] << ",\"samples_ms\":[";
    for (size_t i = 0; i < samples.size(); ++i) std::cout << (i ? "," : "") << samples[i];
    std::cout << "]}";
    CUDA_CHECK(cudaEventDestroy(start));
    CUDA_CHECK(cudaEventDestroy(stop));
  }
  CUDA_CHECK(cudaFree(device_x));
  CUDA_CHECK(cudaFree(device_y));
  std::cout << "],\"gpu_execution_accepted\":" << (all_passed ? "true" : "false") << "}\n";
  return all_passed ? 0 : 1;
}
