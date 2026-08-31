import triton
import triton.language as tl


@triton.jit
def vector_copy_kernel(x, y, n: tl.constexpr, stride: tl.constexpr, block: tl.constexpr):
    offsets = tl.program_id(0) * block + tl.arange(0, block)
    src = offsets * stride
    mask = src < n
    values = tl.load(x + src, mask=mask, other=0.0)
    tl.store(y + src, values, mask=mask)
