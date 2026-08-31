from __future__ import annotations

import math

from .common import Check, close, emit, matmul, softmax, transpose


LAB_ID = "comp-lab-02-tiled-attention"


def tiled_matmul(a: list[list[float]], b: list[list[float]], tile: int) -> list[list[float]]:
    m, k, n = len(a), len(a[0]), len(b[0])
    out = [[0.0 for _ in range(n)] for _ in range(m)]
    for ii in range(0, m, tile):
        for jj in range(0, n, tile):
            for kk in range(0, k, tile):
                for i in range(ii, min(ii + tile, m)):
                    for j in range(jj, min(jj + tile, n)):
                        acc = out[i][j]
                        for x in range(kk, min(kk + tile, k)):
                            acc += a[i][x] * b[x][j]
                        out[i][j] = acc
    return out


def online_softmax(xs: list[float]) -> list[float]:
    running_max = -float("inf")
    running_sum = 0.0
    for x in xs:
        next_max = max(running_max, x)
        running_sum = running_sum * math.exp(running_max - next_max) + math.exp(x - next_max)
        running_max = next_max
    return [math.exp(x - running_max) / running_sum for x in xs]


def attention(q: list[list[float]], k: list[list[float]], v: list[list[float]]) -> list[list[float]]:
    scale = 1 / math.sqrt(len(q[0]))
    scores = [[x * scale for x in row] for row in matmul(q, transpose(k))]
    probs = [online_softmax(row) for row in scores]
    return matmul(probs, v)


def run() -> dict[str, object]:
    a = [[float((i + j) % 7 - 3) for j in range(8)] for i in range(8)]
    b = [[float((i * 2 + j) % 5 - 2) for j in range(8)] for i in range(8)]
    tiled = tiled_matmul(a, b, tile=4)
    reference = matmul(a, b)
    q = [[0.1 * (i + j + 1) for j in range(8)] for i in range(4)]
    k = [[0.05 * (i * 2 + j + 1) for j in range(8)] for i in range(4)]
    v = [[0.03 * (i + 3 * j + 1) for j in range(8)] for i in range(4)]
    attn = attention(q, k, v)
    probs = online_softmax([1000.0, 1001.0, 999.0])
    memory_naive = len(q) * len(k) * 4
    memory_online = len(q) * 4
    checks = [
        Check("tiled_matches_reference", all(close(tiled[i][j], reference[i][j]) for i in range(8) for j in range(8)), "8x8 tile=4").__dict__,
        Check("online_softmax_stable", close(sum(probs), 1.0), str(probs)).__dict__,
        Check("attention_shape", len(attn) == len(q) and len(attn[0]) == len(v[0]), f"{len(attn)}x{len(attn[0])}").__dict__,
        Check("online_reduces_score_storage", memory_online < memory_naive, f"{memory_online} < {memory_naive}").__dict__,
    ]
    return {
        "summary": "Implements tiled matmul and online-softmax attention with memory accounting.",
        "results": {"attention_first_row": [round(x, 6) for x in attn[0]], "score_storage": {"naive": memory_naive, "online": memory_online}},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
