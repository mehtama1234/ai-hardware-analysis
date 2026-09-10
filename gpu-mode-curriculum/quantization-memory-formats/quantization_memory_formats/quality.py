"""Application-level metrics for a packed-weight linear layer."""
import math
import torch
from .packed_int4 import pack_int4, linear


@torch.no_grad()
def measure_linear_quality(inputs, weight, bias=None):
    """Compare packed/dequantized linear output against the float reference."""
    if inputs.ndim != 2 or weight.ndim != 2 or inputs.shape[1] != weight.shape[1]:
        raise ValueError('expected inputs[N,H] and weight[M,H]')
    packed = pack_int4(weight)
    reference = inputs @ weight.t() + (bias if bias is not None else 0)
    candidate = linear(inputs, packed, bias)
    difference = candidate - reference
    ref_norm = reference.norm()
    cosine = F_cosine(candidate, reference)
    return {'rows': inputs.shape[0], 'input_features': weight.shape[1], 'output_features': weight.shape[0],
        'packed_bytes': packed.storage_bytes, 'float32_bytes': weight.numel() * 4 + (bias.numel() * 4 if bias is not None else 0),
        'storage_ratio': packed.storage_bytes / (weight.numel() * 4 + (bias.numel() * 4 if bias is not None else 0)),
        'max_abs_error': float(difference.abs().max()), 'rmse': float(difference.square().mean().sqrt()),
        'relative_l2_error': float(difference.norm() / ref_norm.clamp_min(torch.finfo(reference.dtype).tiny)),
        'cosine_similarity': cosine}


def F_cosine(a, b):
    denominator = a.norm() * b.norm()
    value = (a.flatten() @ b.flatten()) / denominator.clamp_min(torch.finfo(a.dtype).tiny)
    return float(value) if math.isfinite(float(value)) else None
