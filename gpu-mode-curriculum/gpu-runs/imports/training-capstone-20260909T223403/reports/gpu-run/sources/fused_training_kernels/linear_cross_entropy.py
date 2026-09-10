"""First-order linear cross-entropy with token-chunked logit recomputation.

This is an executable PyTorch algorithm, not a fused CUDA/Triton kernel.
Only float32/float64 without autocast are currently supported.
"""
import torch
from torch.autograd.function import once_differentiable


class _LinearCrossEntropy(torch.autograd.Function):
    @staticmethod
    def forward(ctx, hidden, weight, targets, bias, chunk_size, ignore_index, reduction):
        valid = targets != ignore_index
        count = valid.sum()
        total = hidden.new_zeros(())
        for start in range(0, hidden.shape[0], chunk_size):
            end = start + chunk_size
            logits = hidden[start:end] @ weight.t()
            if bias is not None:
                logits = logits + bias
            labels = targets[start:end].masked_fill(~valid[start:end], 0)
            # Normalize before selecting the target to avoid subtracting two
            # large, nearly equal float32 values in logsumexp(Z) - Z[target].
            losses = -logits.log_softmax(-1).gather(1, labels[:, None]).squeeze(1)
            total = total + losses.masked_fill(~valid[start:end], 0).sum()
        ctx.save_for_backward(hidden, weight, targets, bias, count)
        ctx.chunk_size, ctx.ignore_index, ctx.reduction = chunk_size, ignore_index, reduction
        return total / count if reduction == 'mean' else total

    @staticmethod
    @once_differentiable
    def backward(ctx, grad_output):
        hidden, weight, targets, bias, count = ctx.saved_tensors
        dh = torch.zeros_like(hidden) if ctx.needs_input_grad[0] else None
        dw = torch.zeros_like(weight) if ctx.needs_input_grad[1] else None
        db = torch.zeros_like(bias) if bias is not None and ctx.needs_input_grad[3] else None
        scale = grad_output / count.clamp_min(1) if ctx.reduction == 'mean' else grad_output
        for start in range(0, hidden.shape[0], ctx.chunk_size):
            end = start + ctx.chunk_size
            x, labels = hidden[start:end], targets[start:end]
            logits = x @ weight.t()
            if bias is not None:
                logits = logits + bias
            # Use the same stabilized normalization family as forward. This
            # avoids a separate softmax implementation producing a different
            # rounding path on large vocabularies.
            dz = logits.log_softmax(-1).exp()
            valid = labels != ctx.ignore_index
            safe_labels = labels.masked_fill(~valid, 0)
            dz.scatter_add_(1, safe_labels[:, None], -torch.ones_like(dz[:, :1]))
            dz.masked_fill_(~valid[:, None], 0)
            dz.mul_(scale)
            if dh is not None:
                dh[start:end] = dz @ weight
            if dw is not None:
                dw.add_(dz.t() @ x)
            if db is not None:
                db.add_(dz.sum(0))
        return dh, dw, None, db, None, None, None


def linear_cross_entropy(hidden, weight, targets, bias=None, *, chunk_size=128,
                         ignore_index=-100, reduction='mean'):
    """Loss for hidden[N,H], weight[V,H], targets[N], optional bias[V].

    Mean excludes ignored targets; an all-ignored mean is NaN with zero
    gradients, matching torch cross_entropy. Second derivatives are unsupported.
    """
    if hidden.ndim != 2 or weight.ndim != 2 or targets.shape != hidden.shape[:1]:
        raise ValueError('expected hidden[N,H], weight[V,H], targets[N]')
    if hidden.shape[1] != weight.shape[1] or min(*hidden.shape, weight.shape[0]) < 1:
        raise ValueError('positive, compatible dimensions required')
    if bias is not None and bias.shape != weight.shape[:1]:
        raise ValueError('expected bias[V]')
    if type(chunk_size) is not int or chunk_size < 1 or reduction not in ('mean', 'sum'):
        raise ValueError('positive integer chunk_size and mean/sum reduction required')
    floats = [hidden, weight] + ([] if bias is None else [bias])
    if hidden.dtype not in (torch.float32, torch.float64) or any(t.dtype != hidden.dtype for t in floats):
        raise ValueError('matching float32 or float64 tensors required')
    if targets.dtype != torch.long or any(t.device != hidden.device for t in floats + [targets]):
        raise ValueError('int64 targets and a common device required')
    if torch.is_autocast_enabled() or torch.is_autocast_enabled('cpu'):
        raise ValueError('autocast is not supported')
    invalid = (targets != ignore_index) & ((targets < 0) | (targets >= weight.shape[0]))
    if bool(invalid.any()):
        raise ValueError('target outside vocabulary')
    return _LinearCrossEntropy.apply(hidden, weight, targets, bias, chunk_size, ignore_index, reduction)
