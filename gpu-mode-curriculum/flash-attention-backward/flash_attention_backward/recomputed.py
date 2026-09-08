"""Blockwise PyTorch teaching implementation; not a fused GPU kernel."""
import torch
from torch.autograd.function import once_differentiable

from .reference import _validate


def _scores(q, k, scale, allowed, causal, i, j):
    scores = (q @ k.transpose(-2, -1)) * scale
    if allowed is not None:
        scores = scores.masked_fill(~allowed[..., i:i + q.shape[-2], j:j + k.shape[-2]], -torch.inf)
    if causal:
        keep = torch.arange(j, j + k.shape[-2], device=q.device)[None, :] <= \
               torch.arange(i, i + q.shape[-2], device=q.device)[:, None]
        scores = scores.masked_fill(~keep, -torch.inf)
    return scores


class _Recomputed(torch.autograd.Function):
    @staticmethod
    def forward(ctx, q, k, v, allowed, causal, block):
        scale = q.shape[-1] ** -0.5
        out = q.new_zeros((*q.shape[:-1], v.shape[-1]))
        lse = q.new_empty(q.shape[:-1])
        for i in range(0, q.shape[-2], block):
            qi = q[..., i:i + block, :]
            maximum = q.new_full(qi.shape[:-1], -torch.inf)
            denominator = torch.zeros_like(maximum)
            numerator = q.new_zeros((*qi.shape[:-1], v.shape[-1]))
            for j in range(0, k.shape[-2], block):
                scores = _scores(qi, k[..., j:j + block, :], scale, allowed, causal, i, j)
                updated = torch.maximum(maximum, scores.amax(dim=-1))
                # An entirely masked tile has no contribution, including before
                # this row has seen its first allowed key.
                safe = torch.where(torch.isfinite(updated), updated, 0)
                correction = torch.exp(maximum - safe)
                weights = torch.exp(scores - safe.unsqueeze(-1))
                numerator = numerator * correction.unsqueeze(-1) + weights @ v[..., j:j + block, :]
                denominator = denominator * correction + weights.sum(dim=-1)
                maximum = updated
            out[..., i:i + block, :] = numerator / denominator.unsqueeze(-1)
            lse[..., i:i + block] = maximum + denominator.log()
        # Save an optional caller-supplied mask through autograd hooks too.
        mask = allowed if allowed is not None else torch.empty(0, dtype=torch.bool, device=q.device)
        ctx.save_for_backward(q, k, v, out, lse, mask)
        ctx.has_mask, ctx.causal, ctx.block, ctx.scale = allowed is not None, causal, block, scale
        return out

    @staticmethod
    @once_differentiable
    def backward(ctx, grad_output):
        q, k, v, out, lse, mask = ctx.saved_tensors
        allowed = mask if ctx.has_mask else None
        dq, dk, dv = torch.zeros_like(q), torch.zeros_like(k), torch.zeros_like(v)
        delta = (out * grad_output).sum(dim=-1)
        block = ctx.block
        for i in range(0, q.shape[-2], block):
            qi, gi = q[..., i:i + block, :], grad_output[..., i:i + block, :]
            for j in range(0, k.shape[-2], block):
                kj, vj = k[..., j:j + block, :], v[..., j:j + block, :]
                scores = _scores(qi, kj, ctx.scale, allowed, ctx.causal, i, j)
                p = torch.exp(scores - lse[..., i:i + block].unsqueeze(-1))
                ds = p * (gi @ vj.transpose(-2, -1) - delta[..., i:i + block].unsqueeze(-1))
                dq[..., i:i + block, :] += (ds @ kj) * ctx.scale
                dk[..., j:j + block, :] += (ds.transpose(-2, -1) @ qi) * ctx.scale
                dv[..., j:j + block, :] += p.transpose(-2, -1) @ gi
        return dq, dk, dv, None, None, None


def recomputed_attention(q, k, v, *, allowed=None, causal=False, block=32):
    if not isinstance(block, int) or isinstance(block, bool) or block <= 0:
        raise ValueError("block must be a positive integer")
    if causal and allowed is not None:
        raise ValueError("supply causal or allowed, not both")
    # Do not materialize a quadratic causal mask. Construct each tile on demand.
    allowed = _validate(q, k, v, allowed=allowed)
    return _Recomputed.apply(q, k, v, allowed, causal, block)
