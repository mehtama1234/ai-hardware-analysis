#include <cuda_runtime.h>

template <int MODE>
__global__ void shared_bank_probe(float* output, int rounds) {
  __shared__ volatile float tile[32 * 32];
  int lane = threadIdx.x & 31;
  for (int index = threadIdx.x; index < 32 * 32; index += blockDim.x) {
    tile[index] = static_cast<float>(index + 1);
  }
  __syncthreads();
  int shared_index;
  if constexpr (MODE == 0) {
    shared_index = lane;
  } else if constexpr (MODE == 1) {
    shared_index = lane * 32;
  } else {
    shared_index = lane * 32 + lane;
  }
  float accumulator = 0.0f;
  for (int iteration = 0; iteration < rounds; ++iteration) {
    accumulator += tile[shared_index];
  }
  output[blockIdx.x * blockDim.x + threadIdx.x] = accumulator;
}

extern "C" void launch_probe(int mode, float* output, int blocks, int rounds) {
  if (mode == 0) {
    shared_bank_probe<0><<<blocks, 32>>>(output, rounds);
  } else if (mode == 1) {
    shared_bank_probe<1><<<blocks, 32>>>(output, rounds);
  } else {
    shared_bank_probe<2><<<blocks, 32>>>(output, rounds);
  }
}
