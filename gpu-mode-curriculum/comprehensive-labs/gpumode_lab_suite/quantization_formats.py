from __future__ import annotations

import math

from .common import Check, emit


LAB_ID = "comp-lab-04-quantization-formats"


def quantize_symmetric(values: list[float], bits: int) -> tuple[list[int], float]:
    qmax = 2 ** (bits - 1) - 1
    scale = max(abs(x) for x in values) / qmax
    quantized = [max(-qmax - 1, min(qmax, round(x / scale))) for x in values]
    return quantized, scale


def dequantize_symmetric(values: list[int], scale: float) -> list[float]:
    return [x * scale for x in values]


def mse(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)


def block_quantize(values: list[float], block: int, bits: int) -> list[dict[str, object]]:
    out = []
    for offset in range(0, len(values), block):
        chunk = values[offset : offset + block]
        q, scale = quantize_symmetric(chunk, bits)
        out.append({"offset": offset, "scale": scale, "q": q, "dequant": dequantize_symmetric(q, scale)})
    return out


def fp8_like(value: float) -> float:
    if value == 0:
        return 0.0
    sign = -1 if value < 0 else 1
    value = abs(value)
    exponent = max(-8, min(7, math.floor(math.log2(value))))
    mantissa = round((value / (2**exponent) - 1) * 8) / 8
    return sign * (2**exponent) * (1 + mantissa)


def nvfp4_like(value: float) -> float:
    levels = [-6.0, -4.0, -3.0, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
    return min(levels, key=lambda x: abs(x - value))


def run() -> dict[str, object]:
    values = [math.sin(i / 3) * (1 + i % 5) for i in range(32)]
    q8, s8 = quantize_symmetric(values, 8)
    q4, s4 = quantize_symmetric(values, 4)
    dq8 = dequantize_symmetric(q8, s8)
    dq4 = dequantize_symmetric(q4, s4)
    blocks = block_quantize(values, block=8, bits=4)
    fp8 = [fp8_like(x) for x in values]
    nvfp4 = [nvfp4_like(x) for x in values]
    checks = [
        Check("int8_lower_error_than_int4", mse(values, dq8) < mse(values, dq4), f"{mse(values, dq8):.6f} < {mse(values, dq4):.6f}").__dict__,
        Check("block_quantization_has_four_blocks", len(blocks) == 4, str(len(blocks))).__dict__,
        Check("fp8_like_is_finite", all(math.isfinite(x) for x in fp8), str(fp8[:4])).__dict__,
        Check("nvfp4_like_uses_limited_levels", len(set(nvfp4)) <= 15, str(sorted(set(nvfp4)))).__dict__,
    ]
    return {
        "summary": "Implements int8/int4 block quantization plus fp8/nvfp4-style format modeling.",
        "results": {"mse_int8": mse(values, dq8), "mse_int4": mse(values, dq4), "block_scales": [round(row["scale"], 6) for row in blocks]},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
