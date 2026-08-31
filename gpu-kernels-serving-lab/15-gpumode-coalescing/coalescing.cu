#include <cuda_runtime.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <numeric>
#include <vector>

__global__ void contiguous_add(const float* a, const float* b, float* out, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) out[i] = a[i] + b[i];
}

__global__ void strided_add(const float* a, const float* b, float* out, int n, int stride) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) {
    int j = (i * stride) % n;
    out[i] = a[j] + b[j];
  }
}

__global__ void gathered_add(const float* a, const float* b, const int* index, float* out, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) {
    int j = index[i];
    out[i] = a[j] + b[j];
  }
}

template <typename Launch>
float time_kernel(cudaEvent_t start, cudaEvent_t stop, int repeat, Launch launch) {
  std::vector<float> samples;
  samples.reserve(repeat);
  for (int i = 0; i < repeat; ++i) {
    cudaEventRecord(start);
    launch();
    cudaGetLastError();
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float ms = 0.0f;
    cudaEventElapsedTime(&ms, start, stop);
    samples.push_back(ms);
  }
  std::sort(samples.begin(), samples.end());
  return samples[samples.size() / 2];
}

int main() {
  const int n = 1 << 24;
  const int stride = 17;
  const int repeat = 30;
  const int threads = 256;
  const int blocks = (n + threads - 1) / threads;

  std::vector<float> h_a(n), h_b(n), h_out(n);
  std::vector<int> h_index(n);
  for (int i = 0; i < n; ++i) {
    h_a[i] = static_cast<float>(i % 1024) * 0.25f;
    h_b[i] = static_cast<float>(i % 257) * 0.5f;
    h_index[i] = (i * 7919) % n;
  }

  float *a = nullptr, *b = nullptr, *out = nullptr;
  int* index = nullptr;
  cudaMalloc(&a, n * sizeof(float));
  cudaMalloc(&b, n * sizeof(float));
  cudaMalloc(&out, n * sizeof(float));
  cudaMalloc(&index, n * sizeof(int));
  cudaMemcpy(a, h_a.data(), n * sizeof(float), cudaMemcpyHostToDevice);
  cudaMemcpy(b, h_b.data(), n * sizeof(float), cudaMemcpyHostToDevice);
  cudaMemcpy(index, h_index.data(), n * sizeof(int), cudaMemcpyHostToDevice);

  cudaEvent_t start, stop;
  cudaEventCreate(&start);
  cudaEventCreate(&stop);

  auto contiguous = [&]() { contiguous_add<<<blocks, threads>>>(a, b, out, n); };
  auto strided = [&]() { strided_add<<<blocks, threads>>>(a, b, out, n, stride); };
  auto gathered = [&]() { gathered_add<<<blocks, threads>>>(a, b, index, out, n); };

  float contiguous_ms = time_kernel(start, stop, repeat, contiguous);
  float strided_ms = time_kernel(start, stop, repeat, strided);
  float gathered_ms = time_kernel(start, stop, repeat, gathered);

  const double contiguous_bytes = static_cast<double>(n) * sizeof(float) * 3.0;
  const double strided_bytes = contiguous_bytes;
  const double gathered_bytes = static_cast<double>(n) * (sizeof(float) * 3.0 + sizeof(int));
  std::cout << "{"
            << "\"n\":" << n << ","
            << "\"stride\":" << stride << ","
            << "\"rows\":["
            << "{\"pattern\":\"contiguous\",\"milliseconds\":" << contiguous_ms
            << ",\"effective_gbps\":" << contiguous_bytes / (contiguous_ms / 1000.0) / 1e9 << "},"
            << "{\"pattern\":\"strided\",\"milliseconds\":" << strided_ms
            << ",\"effective_gbps\":" << strided_bytes / (strided_ms / 1000.0) / 1e9 << "},"
            << "{\"pattern\":\"gathered\",\"milliseconds\":" << gathered_ms
            << ",\"effective_gbps\":" << gathered_bytes / (gathered_ms / 1000.0) / 1e9 << "}"
            << "]}" << std::endl;

  cudaFree(a);
  cudaFree(b);
  cudaFree(out);
  cudaFree(index);
  return 0;
}
