#include <cuda_runtime.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iomanip>
#include <iostream>
#include <vector>

constexpr int BATCH = 16;
constexpr int HIDDEN = 128;
constexpr int INTERMEDIATE = 256;

#define CUDA_CHECK(expr) do { cudaError_t e = (expr); if (e != cudaSuccess) { \
  std::fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(e)); return 2; } } while (0)

__device__ float gelu_tanh(float x) {
  constexpr float coeff = 0.7978845608028654f;
  return 0.5f * x * (1.0f + tanhf(coeff * (x + 0.044715f * x * x * x)));
}

__global__ void fused_mlp(const float* x, const float* w1, const float* w2, float* y) {
  int index = blockIdx.x * blockDim.x + threadIdx.x;
  if (index >= BATCH * HIDDEN) return;
  int batch = index / HIDDEN;
  int hidden = index % HIDDEN;
  float output = 0.0f;
  for (int intermediate = 0; intermediate < INTERMEDIATE; ++intermediate) {
    float inner = 0.0f;
    for (int input = 0; input < HIDDEN; ++input) inner += x[batch * HIDDEN + input] * w1[input * INTERMEDIATE + intermediate];
    output += gelu_tanh(inner) * w2[intermediate * HIDDEN + hidden];
  }
  y[index] = output;
}

template <typename Launch>
float timed(Launch launch, std::vector<float>& samples) {
  cudaEvent_t start, stop; CUDA_CHECK(cudaEventCreate(&start)); CUDA_CHECK(cudaEventCreate(&stop));
  for (int i = 0; i < 7; ++i) { CUDA_CHECK(cudaEventRecord(start)); launch(); CUDA_CHECK(cudaGetLastError()); CUDA_CHECK(cudaEventRecord(stop)); CUDA_CHECK(cudaEventSynchronize(stop)); float ms = 0.0f; CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop)); if (!std::isfinite(ms) || ms <= 0) return -1.0f; samples.push_back(ms); }
  CUDA_CHECK(cudaEventDestroy(start)); CUDA_CHECK(cudaEventDestroy(stop)); std::sort(samples.begin(), samples.end()); return samples[3];
}

int main() {
  std::vector<float> x(BATCH * HIDDEN), w1(HIDDEN * INTERMEDIATE), w2(INTERMEDIATE * HIDDEN), output(BATCH * HIDDEN);
  std::vector<double> reference(BATCH * HIDDEN, 0.0);
  for (size_t i = 0; i < x.size(); ++i) x[i] = static_cast<float>((static_cast<int>(i) % 17) - 8) / 31.0f;
  for (size_t i = 0; i < w1.size(); ++i) w1[i] = static_cast<float>((static_cast<int>(i) % 13) - 6) / 47.0f;
  for (size_t i = 0; i < w2.size(); ++i) w2[i] = static_cast<float>((static_cast<int>(i) % 11) - 5) / 43.0f;
  for (int batch = 0; batch < BATCH; ++batch) for (int hidden = 0; hidden < HIDDEN; ++hidden) for (int intermediate = 0; intermediate < INTERMEDIATE; ++intermediate) {
    double inner = 0.0; for (int input = 0; input < HIDDEN; ++input) inner += x[batch * HIDDEN + input] * w1[input * INTERMEDIATE + intermediate];
    double activated = 0.5 * inner * (1.0 + std::tanh(std::sqrt(2.0 / M_PI) * (inner + 0.044715 * inner * inner * inner)));
    reference[batch * HIDDEN + hidden] += activated * w2[intermediate * HIDDEN + hidden];
  }
  float *dx = nullptr, *dw1 = nullptr, *dw2 = nullptr, *dy = nullptr;
  CUDA_CHECK(cudaMalloc(&dx, x.size() * sizeof(float))); CUDA_CHECK(cudaMalloc(&dw1, w1.size() * sizeof(float))); CUDA_CHECK(cudaMalloc(&dw2, w2.size() * sizeof(float))); CUDA_CHECK(cudaMalloc(&dy, output.size() * sizeof(float)));
  CUDA_CHECK(cudaMemcpy(dx, x.data(), x.size() * sizeof(float), cudaMemcpyHostToDevice)); CUDA_CHECK(cudaMemcpy(dw1, w1.data(), w1.size() * sizeof(float), cudaMemcpyHostToDevice)); CUDA_CHECK(cudaMemcpy(dw2, w2.data(), w2.size() * sizeof(float), cudaMemcpyHostToDevice));
  std::vector<float> samples; float median_ms = timed([&] { fused_mlp<<<(BATCH * HIDDEN + 255) / 256, 256>>>(dx, dw1, dw2, dy); }, samples);
  CUDA_CHECK(cudaMemcpy(output.data(), dy, output.size() * sizeof(float), cudaMemcpyDeviceToHost));
  double max_error = 0.0; for (size_t i = 0; i < output.size(); ++i) max_error = std::max(max_error, std::abs(static_cast<double>(output[i]) - reference[i]));
  bool passed = median_ms > 0 && max_error <= 2e-5;
  std::cout << "{\"status\":\"" << (passed ? "passed" : "failed") << "\",\"shape\":[" << BATCH << "," << HIDDEN << "," << INTERMEDIATE << "],\"max_abs_error\":" << std::setprecision(12) << max_error << ",\"median_ms\":" << median_ms << ",\"samples_ms\":[";
  for (size_t i = 0; i < samples.size(); ++i) std::cout << (i ? "," : "") << samples[i];
  std::cout << "],\"gpu_execution_accepted\":" << (passed ? "true" : "false") << "}\n";
  CUDA_CHECK(cudaFree(dx)); CUDA_CHECK(cudaFree(dw1)); CUDA_CHECK(cudaFree(dw2)); CUDA_CHECK(cudaFree(dy)); return passed ? 0 : 1;
}
