#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from dataclasses import dataclass


Vector = list[float]
Matrix = list[list[float]]


@dataclass(frozen=True)
class ErrorCase:
    name: str
    dac_step: float
    conductance_noise: float
    adc_step: float
    stable_bias: float
    score_noise: float
    fallback_residual_budget: float


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [dot(row, vector) for row in matrix]


def add(a: Vector, b: Vector) -> Vector:
    return [x + y for x, y in zip(a, b)]


def rms(values: Vector) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: Vector, measured: Vector) -> float:
    return rms([a - b for a, b in zip(reference, measured)]) / max(1e-12, rms(reference))


def quantize(value: float, step: float) -> float:
    if step <= 0.0:
        return value
    return round(value / step) * step


def layer_norm(x: Vector) -> Vector:
    mean = sum(x) / len(x)
    centered = [value - mean for value in x]
    scale = math.sqrt(sum(value * value for value in centered) / len(centered) + 1e-6)
    return [value / scale for value in centered]


def softmax(scores: Vector) -> Vector:
    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def gelu_like(values: Vector) -> Vector:
    return [0.5 * x * (1.0 + math.tanh(0.79788456 * (x + 0.044715 * x * x * x))) for x in values]


def make_matrix(rng: random.Random, rows: int, cols: int, scale: float) -> Matrix:
    return [[rng.gauss(0.0, scale) for _ in range(cols)] for _ in range(rows)]


def analog_projection(matrix: Matrix, vector: Vector, rng: random.Random, case: ErrorCase) -> tuple[Vector, float, str]:
    q_vector = [quantize(value, case.dac_step) for value in vector]
    raw: Vector = []
    for row in matrix:
        total = 0.0
        for weight, value in zip(row, q_vector):
            damaged_weight = weight * (1.0 + rng.gauss(0.0, case.conductance_noise))
            total += damaged_weight * value
        raw.append(total)

    with_readout = [
        quantize(value, case.adc_step) + case.stable_bias + rng.gauss(0.0, case.adc_step * 0.15)
        for value in raw
    ]
    clean = matvec(matrix, vector)
    residual = rel_error(clean, with_readout)
    if residual > case.fallback_residual_budget:
        return clean, residual, "digital_fallback"
    return with_readout, residual, "analog_accepted"


def attention(query: Vector, keys: list[Vector], values: list[Vector], rng: random.Random, score_noise: float) -> tuple[Vector, int, Vector]:
    scores = [dot(query, key) / math.sqrt(len(query)) for key in keys]
    noisy_scores = [score + rng.gauss(0.0, score_noise) for score in scores]
    weights = softmax(noisy_scores)
    out = [0.0] * len(values[0])
    for weight, value in zip(weights, values):
        for i, element in enumerate(value):
            out[i] += weight * element
    return out, noisy_scores.index(max(noisy_scores)), weights


def run_case(case: ErrorCase, seed: int) -> dict[str, float | str]:
    rng = random.Random(seed)
    dim = 12
    context = 6
    x = [rng.gauss(0.0, 0.40) for _ in range(dim)]
    memory = [[rng.gauss(0.0, 0.50) for _ in range(dim)] for _ in range(context)]

    wq = make_matrix(rng, dim, dim, 0.18)
    wk = make_matrix(rng, dim, dim, 0.18)
    wv = make_matrix(rng, dim, dim, 0.18)
    wo = make_matrix(rng, dim, dim, 0.16)
    wup = make_matrix(rng, 2 * dim, dim, 0.13)
    wdown = make_matrix(rng, dim, 2 * dim, 0.12)

    nx = layer_norm(x)
    clean_q = matvec(wq, nx)
    clean_k = [matvec(wk, layer_norm(token)) for token in memory]
    clean_v = [matvec(wv, layer_norm(token)) for token in memory]
    clean_attn_raw, clean_top, clean_weights = attention(clean_q, clean_k, clean_v, rng, 0.0)
    clean_attn = matvec(wo, clean_attn_raw)
    clean_x1 = add(x, clean_attn)
    clean_mlp = matvec(wdown, gelu_like(matvec(wup, layer_norm(clean_x1))))
    clean_x2 = add(clean_x1, clean_mlp)

    q, q_residual, q_path = analog_projection(wq, nx, rng, case)
    keys: list[Vector] = []
    values: list[Vector] = []
    residuals = [q_residual]
    paths = [q_path]
    for token in memory:
        k, k_residual, k_path = analog_projection(wk, layer_norm(token), rng, case)
        v, v_residual, v_path = analog_projection(wv, layer_norm(token), rng, case)
        keys.append(k)
        values.append(v)
        residuals.extend([k_residual, v_residual])
        paths.extend([k_path, v_path])

    attn_raw, top, weights = attention(q, keys, values, rng, case.score_noise)
    attn, out_residual, out_path = analog_projection(wo, attn_raw, rng, case)
    x1 = add(x, attn)
    up, up_residual, up_path = analog_projection(wup, layer_norm(x1), rng, case)
    down, down_residual, down_path = analog_projection(wdown, gelu_like(up), rng, case)
    x2 = add(x1, down)
    residuals.extend([out_residual, up_residual, down_residual])
    paths.extend([out_path, up_path, down_path])

    return {
        "case": case.name,
        "mean_projection_residual": sum(residuals) / len(residuals),
        "max_projection_residual": max(residuals),
        "fallbacks": float(sum(1 for path in paths if path == "digital_fallback")),
        "attention_top_flip": 1.0 if clean_top != top else 0.0,
        "attention_probability_movement": sum(abs(a - b) for a, b in zip(clean_weights, weights)),
        "attention_output_error": rel_error(clean_attn, attn),
        "final_hidden_state_error": rel_error(clean_x2, x2),
    }


def summarize(case: ErrorCase, trials: int = 20) -> dict[str, float | str]:
    rows = [run_case(case, 12000 + i) for i in range(trials)]
    keys = [
        "mean_projection_residual",
        "max_projection_residual",
        "fallbacks",
        "attention_top_flip",
        "attention_probability_movement",
        "attention_output_error",
        "final_hidden_state_error",
    ]
    out: dict[str, float | str] = {"case": case.name}
    for key in keys:
        out[key] = sum(float(row[key]) for row in rows) / trials
    return out


def main() -> None:
    cases = [
        ErrorCase("clean_reference", 0.0, 0.0, 0.0, 0.0, 0.0, 10.0),
        ErrorCase("dac_quantization_only", 0.08, 0.0, 0.0, 0.0, 0.0, 10.0),
        ErrorCase("conductance_noise_only", 0.0, 0.030, 0.0, 0.0, 0.0, 10.0),
        ErrorCase("adc_readout_only", 0.0, 0.0, 0.050, 0.0, 0.0, 10.0),
        ErrorCase("stable_bias_only", 0.0, 0.0, 0.0, 0.025, 0.0, 10.0),
        ErrorCase("attention_score_noise_only", 0.0, 0.0, 0.0, 0.0, 0.08, 10.0),
        ErrorCase("combined_no_fallback", 0.08, 0.030, 0.050, 0.025, 0.08, 10.0),
        ErrorCase("combined_with_fallback", 0.08, 0.030, 0.050, 0.025, 0.08, 0.18),
    ]

    print("error_budget_ledger")
    print("hidden,12")
    print("context,6")
    print("trials,20")
    print()
    print("case,mean_projection_residual,max_projection_residual,mean_fallbacks_per_layer,attention_top_flip_rate,attention_probability_movement,attention_output_error,final_hidden_state_error")
    for case in cases:
        row = summarize(case)
        print(
            f"{row['case']},{float(row['mean_projection_residual']):.4f},"
            f"{float(row['max_projection_residual']):.4f},{float(row['fallbacks']):.2f},"
            f"{float(row['attention_top_flip']):.4f},{float(row['attention_probability_movement']):.4f},"
            f"{float(row['attention_output_error']):.4f},{float(row['final_hidden_state_error']):.4f}"
        )

    print()
    print("interpretation")
    print("Projection residual is a local boundary measurement.")
    print("Attention movement and hidden-state error are model-facing measurements.")
    print("Fallback can reduce hidden-state damage even when the analog attempt still happens.")


if __name__ == "__main__":
    main()
