import triton
import triton.language as tl


@triton.jit
def matmul_kernel(a, b, c, m: tl.constexpr, n: tl.constexpr, k: tl.constexpr, bm: tl.constexpr, bn: tl.constexpr, bk: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    offs_m = pid_m * bm + tl.arange(0, bm)
    offs_n = pid_n * bn + tl.arange(0, bn)
    offs_k = tl.arange(0, bk)
    acc = tl.zeros((bm, bn), tl.float32)
    for kk in range(0, k, bk):
        av = tl.load(a + offs_m[:, None] * k + (kk + offs_k[None, :]), mask=(offs_m[:, None] < m) & (kk + offs_k[None, :] < k), other=0.0)
        bv = tl.load(b + (kk + offs_k[:, None]) * n + offs_n[None, :], mask=(kk + offs_k[:, None] < k) & (offs_n[None, :] < n), other=0.0)
        acc += tl.dot(av, bv)
    tl.store(c + offs_m[:, None] * n + offs_n[None, :], acc, mask=(offs_m[:, None] < m) & (offs_n[None, :] < n))
