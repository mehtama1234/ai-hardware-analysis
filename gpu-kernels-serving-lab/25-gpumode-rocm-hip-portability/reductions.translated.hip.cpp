#include <hip/hip_runtime.h>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <vector>

__global__ void shared_block_reduce(const float* x, float* partial, int n) {
  extern __shared__ float smem[];
  int tid = threadIdx.x;
  int i = blockIdx.x * blockDim.x * 2 + tid;
  float v = 0.0f;
  if (i < n) v += x[i];
  if (i + blockDim.x < n) v += x[i + blockDim.x];
  smem[tid] = v;
  __syncthreads();

  for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) smem[tid] += smem[tid + stride];
    __syncthreads();
  }
  if (tid == 0) partial[blockIdx.x] = smem[0];
}

__inline__ __device__ float warp_sum(float v) {
  for (int offset = 16; offset > 0; offset >>= 1) {
    v += __shfl_down_sync(0xffffffff, v, offset);
  }
  return v;
}

__global__ void warp_shuffle_reduce(const float* x, float* partial, int n) {
  extern __shared__ float warp_partials[];
  int tid = threadIdx.x;
  int lane = tid & 31;
  int warp = tid >> 5;
  int i = blockIdx.x * blockDim.x * 2 + tid;
  float v = 0.0f;
  if (i < n) v += x[i];
  if (i + blockDim.x < n) v += x[i + blockDim.x];

  v = warp_sum(v);
  if (lane == 0) warp_partials[warp] = v;
  __syncthreads();

  float block_sum = tid < blockDim.x / 32 ? warp_partials[lane] : 0.0f;
  if (warp == 0) block_sum = warp_sum(block_sum);
  if (tid == 0) partial[blockIdx.x] = block_sum;
}

template <typename Launch>
float time_kernel(hipEvent_t start, hipEvent_t stop, int repeat, Launch launch) {
  std::vector<float> samples;
  samples.reserve(repeat);
  for (int i = 0; i < repeat; ++i) {
    hipEventRecord(start);
    launch();
    hipGetLastError();
    hipEventRecord(stop);
    hipEventSynchronize(stop);
    float ms = 0.0f;
    hipEventElapsedTime(&ms, start, stop);
    samples.push_back(ms);
  }
  std::sort(samples.begin(), samples.end());
  return samples[samples.size() / 2];
}

double finalize_sum(float* partial, int blocks) {
  std::vector<float> h_partial(blocks);
  hipMemcpy(h_partial.data(), partial, blocks * sizeof(float), hipMemcpyDeviceToHost);
  return std::accumulate(h_partial.begin(), h_partial.end(), 0.0);
}

int main() {
  const int n = 1 << 24;
  const int repeat = 30;
  const int threads = 256;
  const int blocks = (n + threads * 2 - 1) / (threads * 2);

  std::vector<float> h_x(n);
  for (int i = 0; i < n; ++i) {
    h_x[i] = static_cast<float>((i % 97) - 48) * 0.001f;
  }
  double reference = std::accumulate(h_x.begin(), h_x.end(), 0.0);

  float *x = nullptr, *partial = nullptr;
  hipMalloc(&x, n * sizeof(float));
  hipMalloc(&partial, blocks * sizeof(float));
  hipMemcpy(x, h_x.data(), n * sizeof(float), hipMemcpyHostToDevice);

  hipEvent_t start, stop;
  hipEventCreate(&start);
  hipEventCreate(&stop);

  auto shared = [&]() {
    shared_block_reduce<<<blocks, threads, threads * sizeof(float)>>>(x, partial, n);
  };
  auto shuffle = [&]() {
    warp_shuffle_reduce<<<blocks, threads, (threads / 32) * sizeof(float)>>>(x, partial, n);
  };

  float shared_ms = time_kernel(start, stop, repeat, shared);
  shared();
  hipDeviceSynchronize();
  double shared_sum = finalize_sum(partial, blocks);

  float shuffle_ms = time_kernel(start, stop, repeat, shuffle);
  shuffle();
  hipDeviceSynchronize();
  double shuffle_sum = finalize_sum(partial, blocks);

  const double bytes = static_cast<double>(n) * sizeof(float) + static_cast<double>(blocks) * sizeof(float);
  std::cout << "{"
            << "\"n\":" << n << ","
            << "\"blocks\":" << blocks << ","
            << "\"reference_sum\":" << reference << ","
            << "\"rows\":["
            << "{\"pattern\":\"shared_memory_tree\",\"milliseconds\":" << shared_ms
            << ",\"effective_gbps\":" << bytes / (shared_ms / 1000.0) / 1e9
            << ",\"abs_error\":" << std::abs(shared_sum - reference) << "},"
            << "{\"pattern\":\"warp_shuffle_tree\",\"milliseconds\":" << shuffle_ms
            << ",\"effective_gbps\":" << bytes / (shuffle_ms / 1000.0) / 1e9
            << ",\"abs_error\":" << std::abs(shuffle_sum - reference) << "}"
            << "]}" << std::endl;

  hipEventDestroy(start);
  hipEventDestroy(stop);
  hipFree(x);
  hipFree(partial);
  return 0;
}
