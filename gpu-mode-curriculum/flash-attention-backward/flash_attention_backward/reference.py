"""Executable attention derivative reference, NOT a FlashAttention kernel.

Materializes the score/probability matrix. No dropout, GQA, broadcasting of
batch/head dimensions, additive masks, or higher-order gradients are supported.
"""
from __future__ import annotations

import torch
from torch.autograd.function import once_differentiable


class _Attention(torch.autograd.Function):
    @staticmethod
    def forward(ctx, q, k, v, allowed):
        scale = q.shape[-1] ** -0.5
        scores = (q @ k.transpose(-2, -1)) * scale
        if allowed is not None:
            scores = scores.masked_fill(~allowed, -torch.inf)
        probabilities = scores.softmax(dim=-1)
        ctx.save_for_backward(q, k, v, probabilities)
        ctx.scale = scale
        return probabilities @ v

    @staticmethod
    @once_differentiable
    def backward(ctx, grad_output):
        q, k, v, p = ctx.saved_tensors
        dv = p.transpose(-2, -1) @ grad_output
        dp = grad_output @ v.transpose(-2, -1)
        ds = p * (dp - (dp * p).sum(dim=-1, keepdim=True))
        dq = (ds @ k) * ctx.scale
        dk = (ds.transpose(-2, -1) @ q) * ctx.scale
        return dq, dk, dv, None


def _validate(q, k, v, *, allowed=None, causal=False):
    """FP32/FP64 first-order reference with True=allowed boolean masking.

    Causal alignment is upper-left for rectangular inputs. Fully masked rows
    are rejected explicitly rather than assigning an implicit output convention.
    """
    if q.ndim < 2 or k.ndim != q.ndim or v.ndim != q.ndim:
        raise ValueError("q/k/v must have equal rank >= 2")
    if q.shape[:-2] != k.shape[:-2] or k.shape[:-2] != v.shape[:-2]:
        raise ValueError("batch/head dimensions must match exactly")
    if q.shape[-1] != k.shape[-1] or k.shape[-2] != v.shape[-2]:
        raise ValueError("incompatible attention dimensions")
    if any(size == 0 for tensor in (q, k, v) for size in tensor.shape):
        raise ValueError("empty dimensions are unsupported")
    if q.dtype not in (torch.float32, torch.float64) or k.dtype != q.dtype or v.dtype != q.dtype:
        raise ValueError("matching FP32 or FP64 dtypes required")
    if q.device != k.device or q.device != v.device:
        raise ValueError("matching devices required")
    if causal and allowed is not None:
        raise ValueError("supply causal or allowed, not both")
    if causal:
        allowed = torch.ones((q.shape[-2], k.shape[-2]), dtype=torch.bool, device=q.device).tril()
    if allowed is not None:
        if allowed.dtype != torch.bool or allowed.device != q.device:
            raise ValueError("mask must be boolean and on the input device")
        try:
            allowed = torch.broadcast_to(allowed, (*q.shape[:-1], k.shape[-2]))
        except RuntimeError as exc:
            raise ValueError("mask is not broadcastable to attention scores") from exc
        if not bool(allowed.any(dim=-1).all()):
            raise ValueError("fully masked rows are unsupported")
    return allowed


def attention(q, k, v, *, allowed=None, causal=False):
    """Materialized first-order attention; see _validate for the input contract."""
    return _Attention.apply(q, k, v, _validate(q, k, v, allowed=allowed, causal=causal))
