from __future__ import annotations

import math

import torch


def reference_bias_gelu_residual(x: torch.Tensor, bias: torch.Tensor, residual: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.gelu(x + bias, approximate="tanh") + residual


class _FusedBiasGeluResidual(torch.autograd.Function):
    @staticmethod
    def forward(ctx: torch.autograd.function.FunctionCtx, x: torch.Tensor, bias: torch.Tensor, residual: torch.Tensor) -> torch.Tensor:
        z = x + bias
        tanh_arg = math.sqrt(2.0 / math.pi) * (z + 0.044715 * z * z * z)
        tanh_out = torch.tanh(tanh_arg)
        out = 0.5 * z * (1.0 + tanh_out) + residual
        ctx.save_for_backward(z, tanh_out)
        return out

    @staticmethod
    def backward(ctx: torch.autograd.function.FunctionCtx, grad_out: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        z, tanh_out = ctx.saved_tensors
        sech2 = 1.0 - tanh_out * tanh_out
        coeff = math.sqrt(2.0 / math.pi)
        inner_grad = coeff * (1.0 + 3.0 * 0.044715 * z * z)
        gelu_grad = 0.5 * (1.0 + tanh_out) + 0.5 * z * sech2 * inner_grad
        grad_z = grad_out * gelu_grad
        grad_bias = grad_z
        while grad_bias.ndim > 1:
            grad_bias = grad_bias.sum(dim=0)
        return grad_z, grad_bias, grad_out


def fused_bias_gelu_residual(x: torch.Tensor, bias: torch.Tensor, residual: torch.Tensor) -> torch.Tensor:
    if bias.ndim != 1:
        raise ValueError("bias must be a rank-1 hidden-dimension tensor")
    if x.shape != residual.shape:
        raise ValueError("x and residual must have the same shape")
    if x.shape[-1] != bias.shape[0]:
        raise ValueError("bias length must match the final input dimension")
    return _FusedBiasGeluResidual.apply(x, bias, residual)
