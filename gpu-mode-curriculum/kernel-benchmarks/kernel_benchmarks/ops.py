from __future__ import annotations

import math
from typing import Any


try:
    import torch
except Exception:  # pragma: no cover - depends on local environment.
    torch = None


def has_torch() -> bool:
    return torch is not None


def device() -> str:
    if torch is not None and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def vector_copy(size: int, stride: int = 1) -> dict[str, Any]:
    if torch is not None:
        x = torch.arange(size * stride, dtype=torch.float32, device=device())
        y = x[::stride].contiguous()
        return {"sum": float(y.sum().item()), "shape": list(y.shape), "device": str(y.device)}
    y = list(range(0, size * stride, stride))
    return {"sum": float(sum(y)), "shape": [len(y)], "device": "python"}


def reduction(size: int) -> dict[str, Any]:
    if torch is not None:
        x = torch.linspace(-1.0, 1.0, size, dtype=torch.float32, device=device())
        return {"sum": float(x.sum().item()), "max": float(x.max().item()), "device": str(x.device)}
    xs = [-1.0 + 2.0 * i / max(1, size - 1) for i in range(size)]
    return {"sum": float(sum(xs)), "max": max(xs), "device": "python"}


def softmax(rows: int, cols: int) -> dict[str, Any]:
    if torch is not None:
        x = torch.arange(rows * cols, dtype=torch.float32, device=device()).reshape(rows, cols) / 100.0
        y = torch.softmax(x, dim=-1)
        return {"row_sums": [round(float(v), 6) for v in y.sum(dim=-1).detach().cpu().tolist()], "device": str(y.device)}
    out = []
    for row in range(rows):
        xs = [(row * cols + col) / 100.0 for col in range(cols)]
        m = max(xs)
        exps = [math.exp(x - m) for x in xs]
        s = sum(exps)
        out.append(round(sum(v / s for v in exps), 6))
    return {"row_sums": out, "device": "python"}


def layernorm(rows: int, cols: int, eps: float = 1e-5) -> dict[str, Any]:
    if torch is not None:
        x = torch.arange(rows * cols, dtype=torch.float32, device=device()).reshape(rows, cols) / 10.0
        mean = x.mean(dim=-1, keepdim=True)
        var = ((x - mean) ** 2).mean(dim=-1, keepdim=True)
        y = (x - mean) / torch.sqrt(var + eps)
        return {"means": [round(float(v), 5) for v in y.mean(dim=-1).detach().cpu().tolist()], "device": str(y.device)}
    means = []
    for row in range(rows):
        xs = [(row * cols + col) / 10.0 for col in range(cols)]
        mean = sum(xs) / len(xs)
        var = sum((x - mean) ** 2 for x in xs) / len(xs)
        ys = [(x - mean) / math.sqrt(var + eps) for x in xs]
        means.append(round(sum(ys) / len(ys), 5))
    return {"means": means, "device": "python"}


def matmul(m: int, n: int, k: int) -> dict[str, Any]:
    if torch is not None:
        a = torch.arange(m * k, dtype=torch.float32, device=device()).reshape(m, k) / 100.0
        b = torch.arange(k * n, dtype=torch.float32, device=device()).reshape(k, n) / 100.0
        c = a @ b
        return {"shape": list(c.shape), "checksum": round(float(c.sum().item()), 4), "device": str(c.device)}
    a = [[(i * k + j) / 100.0 for j in range(k)] for i in range(m)]
    b = [[(i * n + j) / 100.0 for j in range(n)] for i in range(k)]
    checksum = 0.0
    for i in range(m):
        for j in range(n):
            checksum += sum(a[i][x] * b[x][j] for x in range(k))
    return {"shape": [m, n], "checksum": round(checksum, 4), "device": "python"}


def fused_mlp(batch: int, hidden: int, intermediate: int) -> dict[str, Any]:
    if torch is not None:
        x = torch.arange(batch * hidden, dtype=torch.float32, device=device()).reshape(batch, hidden) / 100.0
        w1 = torch.ones((hidden, intermediate), dtype=torch.float32, device=device()) / hidden
        w2 = torch.ones((intermediate, hidden), dtype=torch.float32, device=device()) / intermediate
        y = torch.nn.functional.gelu(x @ w1) @ w2
        return {"shape": list(y.shape), "checksum": round(float(y.sum().item()), 4), "device": str(y.device)}
    return {"shape": [batch, hidden], "checksum": float(batch * hidden), "device": "python"}
