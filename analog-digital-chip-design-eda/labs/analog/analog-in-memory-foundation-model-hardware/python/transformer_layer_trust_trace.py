#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from tile_readout_boundary import ReadoutCase, readout


Vector = list[float]
Matrix = list[list[float]]


@dataclass(frozen=True)
class ProjectionTrustCase:
    name: str
    matrix: Matrix
    vector: Vector
    readout_case: ReadoutCase
    analog_noise: float


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


def noisy_projection(matrix: Matrix, vector: Vector, rng: random.Random, sigma: float) -> Vector:
    out: Vector = []
    gain = 1.0 + rng.gauss(0.0, sigma * 0.4)
    bias = rng.gauss(0.0, sigma * 0.1)
    for row in matrix:
        value = 0.0
        for weight, activation in zip(row, vector):
            value += weight * (1.0 + rng.gauss(0.0, sigma)) * activation
        out.append(gain * value + bias + rng.gauss(0.0, sigma * 0.25))
    return out


def trusted_projection(case: ProjectionTrustCase, rng: random.Random) -> tuple[Vector, dict[str, str | float | int]]:
    digital = matvec(case.matrix, case.vector)
    analog = noisy_projection(case.matrix, case.vector, rng, case.analog_noise)
    measured = readout(case.readout_case)

    if measured["valid"] == 1:
        return analog, {
            "op": case.name,
            "placement": "analog",
            "readout": measured["reason"],
            "final_path": "analog_accepted",
            "relative_error": rel_error(digital, analog),
        }

    return digital, {
        "op": case.name,
        "placement": "analog",
        "readout": measured["reason"],
        "final_path": "digital_fallback",
        "relative_error": 0.0,
    }


def attention(query: Vector, keys: list[Vector], values: list[Vector]) -> tuple[Vector, int, Vector]:
    scores = [dot(query, key) / math.sqrt(len(query)) for key in keys]
    weights = softmax(scores)
    out = [0.0] * len(values[0])
    for weight, value in zip(weights, values):
        for i, element in enumerate(value):
            out[i] += weight * element
    return out, scores.index(max(scores)), weights


def main() -> None:
    rng = random.Random(9041)
    dim = 8
    context = 5
    x = [rng.gauss(0.0, 0.4) for _ in range(dim)]
    memory = [[rng.gauss(0.0, 0.5) for _ in range(dim)] for _ in range(context)]

    wq = make_matrix(rng, dim, dim, 0.20)
    wk = make_matrix(rng, dim, dim, 0.20)
    wv = make_matrix(rng, dim, dim, 0.20)
    wo = make_matrix(rng, dim, dim, 0.18)
    wup = make_matrix(rng, 2 * dim, dim, 0.14)
    wdown = make_matrix(rng, dim, 2 * dim, 0.14)

    clean_q = matvec(wq, layer_norm(x))
    clean_k = [matvec(wk, layer_norm(token)) for token in memory]
    clean_v = [matvec(wv, layer_norm(token)) for token in memory]
    clean_attn_raw, clean_top, clean_weights = attention(clean_q, clean_k, clean_v)
    clean_attn = matvec(wo, clean_attn_raw)
    clean_x1 = add(x, clean_attn)
    clean_mlp = matvec(wdown, gelu_like(matvec(wup, layer_norm(clean_x1))))
    clean_x2 = add(clean_x1, clean_mlp)

    ok = ReadoutCase("ok", True, 160, 128, 64, 0, 4, 20, 64)
    bad_residual = ReadoutCase("bad_residual", True, 160, 128, 64, 0, 44, 20, 64)
    stale = ReadoutCase("stale", True, 160, 128, 64, 0, 4, 20, 2048)

    q, q_trace = trusted_projection(ProjectionTrustCase("q_projection", wq, layer_norm(x), ok, 0.015), rng)
    keys: list[Vector] = []
    values: list[Vector] = []
    traces = [q_trace]
    for i, token in enumerate(memory):
        k, k_trace = trusted_projection(ProjectionTrustCase(f"k_projection_{i}", wk, layer_norm(token), ok, 0.015), rng)
        v_readout = bad_residual if i == 2 else ok
        v, v_trace = trusted_projection(ProjectionTrustCase(f"v_projection_{i}", wv, layer_norm(token), v_readout, 0.015), rng)
        keys.append(k)
        values.append(v)
        traces.extend([k_trace, v_trace])

    attn_raw, top, weights = attention(q, keys, values)
    out_proj, out_trace = trusted_projection(ProjectionTrustCase("output_projection", wo, attn_raw, ok, 0.015), rng)
    x1 = add(x, out_proj)
    up, up_trace = trusted_projection(ProjectionTrustCase("mlp_up", wup, layer_norm(x1), ok, 0.018), rng)
    down, down_trace = trusted_projection(ProjectionTrustCase("mlp_down", wdown, gelu_like(up), stale, 0.018), rng)
    traces.extend([out_trace, up_trace, down_trace])
    x2 = add(x1, down)

    print("transformer_layer_trust_trace")
    print("dim,8")
    print("context,5")
    print()
    print("op,placement,readout,final_path,relative_error")
    for trace in traces:
        print(
            f"{trace['op']},{trace['placement']},{trace['readout']},"
            f"{trace['final_path']},{float(trace['relative_error']):.4f}"
        )

    print()
    print("layer_summary")
    print(f"attention_top_clean,{clean_top}")
    print(f"attention_top_traced,{top}")
    print(f"attention_probability_movement,{sum(abs(a - b) for a, b in zip(clean_weights, weights)):.4f}")
    print(f"final_hidden_state_relative_error,{rel_error(clean_x2, x2):.4f}")
    print()
    print("interpretation")
    print("Q, K, V, output, and MLP projections may be analog candidates.")
    print("Each candidate still crosses a readout trust boundary before the layer uses it.")
    print("Failed readout returns the digital projection, so fallback protects the hidden state.")


if __name__ == "__main__":
    main()
