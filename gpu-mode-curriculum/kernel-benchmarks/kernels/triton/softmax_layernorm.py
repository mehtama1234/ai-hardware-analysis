import triton
import triton.language as tl


@triton.jit
def row_softmax_kernel(x, y, cols: tl.constexpr, block: tl.constexpr):
    row = tl.program_id(0)
    offsets = tl.arange(0, block)
    mask = offsets < cols
    values = tl.load(x + row * cols + offsets, mask=mask, other=-float("inf"))
    values = values - tl.max(values, axis=0)
    numerator = tl.exp(values)
    denominator = tl.sum(numerator, axis=0)
    tl.store(y + row * cols + offsets, numerator / denominator, mask=mask)


@triton.jit
def row_layernorm_kernel(x, y, cols: tl.constexpr, eps: tl.constexpr, block: tl.constexpr):
    row = tl.program_id(0)
    offsets = tl.arange(0, block)
    mask = offsets < cols
    values = tl.load(x + row * cols + offsets, mask=mask, other=0.0)
    valid = mask.to(tl.float32)
    valid_count = tl.sum(valid, axis=0)
    mean = tl.sum(values, axis=0) / valid_count
    centered = values - mean
    centered = tl.where(mask, centered, 0.0)
    var = tl.sum(centered * centered, axis=0) / valid_count
    tl.store(y + row * cols + offsets, centered * tl.rsqrt(var + eps), mask=mask)
