import triton
import triton.language as tl


@triton.jit
def block_sum_kernel(x, partial, n: tl.constexpr, block: tl.constexpr):
    offsets = tl.program_id(0) * block + tl.arange(0, block)
    mask = offsets < n
    values = tl.load(x + offsets, mask=mask, other=0.0)
    total = tl.sum(values, axis=0)
    tl.store(partial + tl.program_id(0), total)
