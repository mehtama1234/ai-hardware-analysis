#include <torch/extension.h>

torch::Tensor fused_bias_gelu_residual_cuda(torch::Tensor x, torch::Tensor bias, torch::Tensor residual);

torch::Tensor fused_bias_gelu_residual(torch::Tensor x, torch::Tensor bias, torch::Tensor residual) {
  TORCH_CHECK(x.dim() == 2, "x must be rank-2 [batch, hidden]");
  TORCH_CHECK(residual.sizes() == x.sizes(), "residual must match x");
  TORCH_CHECK(bias.dim() == 1 && bias.size(0) == x.size(1), "bias must match hidden dimension");
  TORCH_CHECK(x.is_cuda(), "compiled extension path expects CUDA tensors");
  return fused_bias_gelu_residual_cuda(x, bias, residual);
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
  m.def("fused_bias_gelu_residual", &fused_bias_gelu_residual, "Fused bias + GELU + residual forward");
}
