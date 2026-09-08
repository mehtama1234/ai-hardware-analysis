#include <cuda_runtime.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cfloat>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <vector>

constexpr int BLOCK = 256;
constexpr int ROWS = 128;
constexpr int COLS = 1024;

#define CUDA_CHECK(expr) do { cudaError_t e = (expr); if (e != cudaSuccess) { \
  std::fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(e)); return 2; } } while (0)

__global__ void reduce_sum_max(const float* x, int n, float* sum_out, float* max_out) {
  __shared__ float sums[BLOCK]; __shared__ float maxima[BLOCK];
  float sum = 0.0f; float maximum = -FLT_MAX;
  for (int i = threadIdx.x; i < n; i += BLOCK) { sum += x[i]; maximum = fmaxf(maximum, x[i]); }
  sums[threadIdx.x] = sum; maxima[threadIdx.x] = maximum; __syncthreads();
  for (int stride = BLOCK / 2; stride; stride >>= 1) { if (threadIdx.x < stride) { sums[threadIdx.x] += sums[threadIdx.x + stride]; maxima[threadIdx.x] = fmaxf(maxima[threadIdx.x], maxima[threadIdx.x + stride]); } __syncthreads(); }
  if (threadIdx.x == 0) { *sum_out = sums[0]; *max_out = maxima[0]; }
}

__global__ void row_softmax(const float* x, float* y, int rows, int cols) {
  int row = blockIdx.x; if (row >= rows) return;
  __shared__ float maxima[BLOCK]; __shared__ float sums[BLOCK];
  float maximum = -FLT_MAX;
  for (int col = threadIdx.x; col < cols; col += BLOCK) maximum = fmaxf(maximum, x[row * cols + col]);
  maxima[threadIdx.x] = maximum; __syncthreads();
  for (int stride = BLOCK / 2; stride; stride >>= 1) { if (threadIdx.x < stride) maxima[threadIdx.x] = fmaxf(maxima[threadIdx.x], maxima[threadIdx.x + stride]); __syncthreads(); }
  maximum = maxima[0]; float total = 0.0f;
  for (int col = threadIdx.x; col < cols; col += BLOCK) total += expf(x[row * cols + col] - maximum);
  sums[threadIdx.x] = total; __syncthreads();
  for (int stride = BLOCK / 2; stride; stride >>= 1) { if (threadIdx.x < stride) sums[threadIdx.x] += sums[threadIdx.x + stride]; __syncthreads(); }
  total = sums[0];
  for (int col = threadIdx.x; col < cols; col += BLOCK) y[row * cols + col] = expf(x[row * cols + col] - maximum) / total;
}

__global__ void row_layernorm(const float* x, float* y, int rows, int cols, float eps) {
  int row = blockIdx.x; if (row >= rows) return;
  __shared__ float sums[BLOCK]; __shared__ float squares[BLOCK];
  float sum = 0.0f;
  for (int col = threadIdx.x; col < cols; col += BLOCK) sum += x[row * cols + col];
  sums[threadIdx.x] = sum; __syncthreads();
  for (int stride = BLOCK / 2; stride; stride >>= 1) { if (threadIdx.x < stride) sums[threadIdx.x] += sums[threadIdx.x + stride]; __syncthreads(); }
  float mean = sums[0] / cols; float square = 0.0f;
  for (int col = threadIdx.x; col < cols; col += BLOCK) { float d = x[row * cols + col] - mean; square += d * d; }
  squares[threadIdx.x] = square; __syncthreads();
  for (int stride = BLOCK / 2; stride; stride >>= 1) { if (threadIdx.x < stride) squares[threadIdx.x] += squares[threadIdx.x + stride]; __syncthreads(); }
  float inverse = rsqrtf(squares[0] / cols + eps);
  for (int col = threadIdx.x; col < cols; col += BLOCK) y[row * cols + col] = (x[row * cols + col] - mean) * inverse;
}

template <typename Launch>
float timed(Launch launch, std::vector<float>& samples) {
  cudaEvent_t start, stop; CUDA_CHECK(cudaEventCreate(&start)); CUDA_CHECK(cudaEventCreate(&stop));
  for (int i = 0; i < 7; ++i) { CUDA_CHECK(cudaEventRecord(start)); launch(); CUDA_CHECK(cudaGetLastError()); CUDA_CHECK(cudaEventRecord(stop)); CUDA_CHECK(cudaEventSynchronize(stop)); float ms = 0.0f; CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop)); if (!std::isfinite(ms) || ms <= 0) return -1.0f; samples.push_back(ms); }
  CUDA_CHECK(cudaEventDestroy(start)); CUDA_CHECK(cudaEventDestroy(stop)); std::sort(samples.begin(), samples.end()); return samples[3];
}

int main() {
  constexpr int n = 1 << 20;
  std::vector<float> host_reduce(n), host_rows(ROWS * COLS), host_out(ROWS * COLS), host_reduce_out(2);
  for (int i = 0; i < n; ++i) host_reduce[i] = static_cast<float>((i % 101) - 50) / 17.0f;
  for (int i = 0; i < ROWS * COLS; ++i) host_rows[i] = static_cast<float>((i % 67) - 33) / 19.0f;
  double ref_sum = std::accumulate(host_reduce.begin(), host_reduce.end(), 0.0); float ref_max = *std::max_element(host_reduce.begin(), host_reduce.end());
  std::vector<double> softmax_ref(ROWS * COLS), layer_ref(ROWS * COLS);
  for (int row = 0; row < ROWS; ++row) {
    double maximum = -std::numeric_limits<double>::infinity(); for (int col = 0; col < COLS; ++col) maximum = std::max(maximum, static_cast<double>(host_rows[row * COLS + col]));
    double total = 0.0; for (int col = 0; col < COLS; ++col) total += std::exp(static_cast<double>(host_rows[row * COLS + col]) - maximum);
    for (int col = 0; col < COLS; ++col) softmax_ref[row * COLS + col] = std::exp(static_cast<double>(host_rows[row * COLS + col]) - maximum) / total;
    double mean = 0.0; for (int col = 0; col < COLS; ++col) mean += host_rows[row * COLS + col]; mean /= COLS;
    double variance = 0.0; for (int col = 0; col < COLS; ++col) { double d = host_rows[row * COLS + col] - mean; variance += d * d; } variance /= COLS;
    for (int col = 0; col < COLS; ++col) layer_ref[row * COLS + col] = (host_rows[row * COLS + col] - mean) / std::sqrt(variance + 1e-5);
  }
  float *d_reduce = nullptr, *d_sum = nullptr, *d_max = nullptr, *d_rows = nullptr, *d_softmax = nullptr, *d_layer = nullptr;
  CUDA_CHECK(cudaMalloc(&d_reduce, n * sizeof(float))); CUDA_CHECK(cudaMalloc(&d_sum, sizeof(float))); CUDA_CHECK(cudaMalloc(&d_max, sizeof(float)));
  CUDA_CHECK(cudaMalloc(&d_rows, host_rows.size() * sizeof(float))); CUDA_CHECK(cudaMalloc(&d_softmax, host_rows.size() * sizeof(float))); CUDA_CHECK(cudaMalloc(&d_layer, host_rows.size() * sizeof(float)));
  CUDA_CHECK(cudaMemcpy(d_reduce, host_reduce.data(), n * sizeof(float), cudaMemcpyHostToDevice)); CUDA_CHECK(cudaMemcpy(d_rows, host_rows.data(), host_rows.size() * sizeof(float), cudaMemcpyHostToDevice));
  std::vector<float> reduction_samples, softmax_samples, layer_samples;
  float reduction_ms = timed([&] { reduce_sum_max<<<1, BLOCK>>>(d_reduce, n, d_sum, d_max); }, reduction_samples);
  float softmax_ms = timed([&] { row_softmax<<<ROWS, BLOCK>>>(d_rows, d_softmax, ROWS, COLS); }, softmax_samples);
  float layer_ms = timed([&] { row_layernorm<<<ROWS, BLOCK>>>(d_rows, d_layer, ROWS, COLS, 1e-5f); }, layer_samples);
  CUDA_CHECK(cudaMemcpy(host_reduce_out.data(), d_sum, sizeof(float), cudaMemcpyDeviceToHost)); float gpu_max = 0.0f; CUDA_CHECK(cudaMemcpy(&gpu_max, d_max, sizeof(float), cudaMemcpyDeviceToHost)); CUDA_CHECK(cudaMemcpy(host_out.data(), d_softmax, host_out.size() * sizeof(float), cudaMemcpyDeviceToHost));
  std::vector<float> host_layer(host_out.size()); CUDA_CHECK(cudaMemcpy(host_layer.data(), d_layer, host_layer.size() * sizeof(float), cudaMemcpyDeviceToHost));
  double softmax_error = 0.0, layer_error = 0.0; for (size_t i = 0; i < host_out.size(); ++i) { softmax_error = std::max(softmax_error, std::abs(static_cast<double>(host_out[i]) - softmax_ref[i])); layer_error = std::max(layer_error, std::abs(static_cast<double>(host_layer[i]) - layer_ref[i])); }
  double sum_error = std::abs(static_cast<double>(host_reduce_out[0]) - ref_sum); double max_error = std::abs(static_cast<double>(gpu_max) - ref_max);
  bool passed = reduction_ms > 0 && softmax_ms > 0 && layer_ms > 0 && sum_error <= 0.02 && max_error == 0.0 && softmax_error <= 3e-6 && layer_error <= 3e-5;
  std::cout << "{\"status\":\"" << (passed ? "passed" : "failed") << "\",\"reduction_sum_error\":" << sum_error << ",\"reduction_max_error\":" << max_error << ",\"softmax_max_abs_error\":" << softmax_error << ",\"layernorm_max_abs_error\":" << layer_error << ",\"reduction_median_ms\":" << reduction_ms << ",\"softmax_median_ms\":" << softmax_ms << ",\"layernorm_median_ms\":" << layer_ms << ",\"reduction_samples_ms\":[";
  for (size_t i = 0; i < reduction_samples.size(); ++i) std::cout << (i ? "," : "") << reduction_samples[i]; std::cout << "],\"softmax_samples_ms\":["; for (size_t i = 0; i < softmax_samples.size(); ++i) std::cout << (i ? "," : "") << softmax_samples[i]; std::cout << "],\"layernorm_samples_ms\":["; for (size_t i = 0; i < layer_samples.size(); ++i) std::cout << (i ? "," : "") << layer_samples[i]; std::cout << "],\"gpu_execution_accepted\":" << (passed ? "true" : "false") << "}\n";
  CUDA_CHECK(cudaFree(d_reduce)); CUDA_CHECK(cudaFree(d_sum)); CUDA_CHECK(cudaFree(d_max)); CUDA_CHECK(cudaFree(d_rows)); CUDA_CHECK(cudaFree(d_softmax)); CUDA_CHECK(cudaFree(d_layer)); return passed ? 0 : 1;
}
