#include <ATen/cuda/CUDAContext.h>
#include <torch/extension.h>

namespace {

template <typename scalar_t>
__device__ scalar_t gelu_tanh(scalar_t value) {
  const scalar_t kBeta = static_cast<scalar_t>(0.7978845608028654);
  const scalar_t kKappa = static_cast<scalar_t>(0.044715);
  return static_cast<scalar_t>(0.5) * value *
         (static_cast<scalar_t>(1.0) + tanh(kBeta * (value + kKappa * value * value * value)));
}

template <typename scalar_t>
__global__ void fused_bias_gelu_residual_kernel(
    const scalar_t* __restrict__ x,
    const scalar_t* __restrict__ bias,
    const scalar_t* __restrict__ residual,
    scalar_t* __restrict__ out,
    int64_t total,
    int64_t hidden) {
  int64_t idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx >= total) {
    return;
  }
  int64_t col = idx % hidden;
  scalar_t value = x[idx] + bias[col];
  out[idx] = gelu_tanh(value) + residual[idx];
}

}  // namespace

torch::Tensor fused_bias_gelu_residual_cuda(torch::Tensor x, torch::Tensor bias, torch::Tensor residual) {
  auto out = torch::empty_like(x);
  const int64_t total = x.numel();
  const int threads = 256;
  const int blocks = static_cast<int>((total + threads - 1) / threads);
  AT_DISPATCH_FLOATING_TYPES_AND_HALF(x.scalar_type(), "fused_bias_gelu_residual_cuda", [&] {
    fused_bias_gelu_residual_kernel<scalar_t><<<blocks, threads, 0, at::cuda::getCurrentCUDAStream()>>>(
        x.data_ptr<scalar_t>(),
        bias.data_ptr<scalar_t>(),
        residual.data_ptr<scalar_t>(),
        out.data_ptr<scalar_t>(),
        total,
        x.size(1));
  });
  return out;
}
