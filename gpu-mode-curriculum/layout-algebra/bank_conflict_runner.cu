#include <cuda_runtime.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <vector>

extern "C" void launch_probe(int mode, float* output, int blocks, int rounds);

#define CUDA_CHECK(expr) do { cudaError_t error = (expr); if (error != cudaSuccess) { std::fprintf(stderr, "%s\n", cudaGetErrorString(error)); return 2; } } while (0)

int main() {
  constexpr int blocks = 128;
  constexpr int threads = 32;
  constexpr int rounds = 100000;
  constexpr int samples_count = 7;
  float* device_output = nullptr;
  std::vector<float> host_output(blocks * threads);
  CUDA_CHECK(cudaMalloc(&device_output, host_output.size() * sizeof(float)));
  std::cout << "{\"status\":\"passed\",\"blocks\":" << blocks << ",\"rounds\":" << rounds << ",\"cases\":[";
  bool all_passed = true;
  for (int mode = 0; mode < 3; ++mode) {
    launch_probe(mode, device_output, blocks, rounds);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    cudaEvent_t start, stop;
    CUDA_CHECK(cudaEventCreate(&start));
    CUDA_CHECK(cudaEventCreate(&stop));
    std::vector<float> samples;
    for (int sample = 0; sample < samples_count; ++sample) {
      CUDA_CHECK(cudaEventRecord(start));
      launch_probe(mode, device_output, blocks, rounds);
      CUDA_CHECK(cudaEventRecord(stop));
      CUDA_CHECK(cudaEventSynchronize(stop));
      float milliseconds = 0.0f;
      CUDA_CHECK(cudaEventElapsedTime(&milliseconds, start, stop));
      if (!std::isfinite(milliseconds) || milliseconds <= 0.0f) return 3;
      samples.push_back(milliseconds);
    }
    CUDA_CHECK(cudaMemcpy(host_output.data(), device_output, host_output.size() * sizeof(float), cudaMemcpyDeviceToHost));
    float max_error = 0.0f;
    float max_relative_error = 0.0f;
    for (int block = 0; block < blocks; ++block) {
      for (int lane = 0; lane < threads; ++lane) {
        int shared_index = mode == 0 ? lane : mode == 1 ? lane * 32 : lane * 33;
        float expected = static_cast<float>(rounds * (shared_index + 1));
        float error = std::abs(host_output[block * threads + lane] - expected);
        max_error = std::max(max_error, error);
        max_relative_error = std::max(max_relative_error, error / std::abs(expected));
      }
    }
    std::sort(samples.begin(), samples.end());
    bool passed = max_relative_error <= 0.002f;
    all_passed = all_passed && passed;
    if (mode) std::cout << ",";
    const char* name = mode == 0 ? "distinct-bank" : mode == 1 ? "32-way-conflict" : "xor-bank-spread";
    std::cout << "{\"name\":\"" << name << "\",\"passed\":" << (passed ? "true" : "false")
              << ",\"max_abs_error\":" << max_error << ",\"max_relative_error\":" << max_relative_error
              << ",\"median_ms\":" << samples[3] << ",\"samples_ms\":[";
    for (size_t index = 0; index < samples.size(); ++index) std::cout << (index ? "," : "") << samples[index];
    std::cout << "]}";
    CUDA_CHECK(cudaEventDestroy(start));
    CUDA_CHECK(cudaEventDestroy(stop));
  }
  CUDA_CHECK(cudaFree(device_output));
  std::cout << "],\"gpu_execution_accepted\":" << (all_passed ? "true" : "false") << "}\n";
  return all_passed ? 0 : 1;
}
