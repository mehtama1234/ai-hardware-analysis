#!/usr/bin/env python3
from __future__ import annotations

import math
import random


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: list[float], measured: list[float]) -> float:
    return rms([a - b for a, b in zip(reference, measured)]) / max(1e-12, rms(reference))


def add(a: list[float], b: list[float]) -> list[float]:
    return [x + y for x, y in zip(a, b)]


def tanh_vec(values: list[float]) -> list[float]:
    return [math.tanh(x) for x in values]


def softmax(scores: list[float]) -> list[float]:
    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def layer_norm(x: list[float]) -> list[float]:
    mean = sum(x) / len(x)
    centered = [value - mean for value in x]
    scale = math.sqrt(sum(value * value for value in centered) / len(centered) + 1e-6)
    return [value / scale for value in centered]


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [dot(row, vector) for row in matrix]


def noisy_matvec(matrix: list[list[float]], vector: list[float], rng: random.Random, weight_noise: float, output_noise: float) -> list[float]:
    out: list[float] = []
    for row in matrix:
        total = 0.0
        for weight, value in zip(row, vector):
            total += weight * (1.0 + rng.gauss(0.0, weight_noise)) * value
        out.append(total + rng.gauss(0.0, output_noise))
    return out


def make_matrix(rng: random.Random, rows: int, cols: int, scale: float) -> list[list[float]]:
    return [[rng.gauss(0.0, scale) for _ in range(cols)] for _ in range(rows)]


def attention(query: list[float], keys: list[list[float]], values: list[list[float]], score_noise: float, rng: random.Random) -> tuple[list[float], int, int, float]:
    clean_scores = [dot(query, key) / math.sqrt(len(query)) for key in keys]
    noisy_scores = [score + rng.gauss(0.0, score_noise) for score in clean_scores]
    clean_weights = softmax(clean_scores)
    noisy_weights = softmax(noisy_scores)
    clean_out = [0.0] * len(values[0])
    noisy_out = [0.0] * len(values[0])
    for clean_weight, noisy_weight, value in zip(clean_weights, noisy_weights, values):
        for i, element in enumerate(value):
            clean_out[i] += clean_weight * element
            noisy_out[i] += noisy_weight * element
    clean_top = clean_scores.index(max(clean_scores))
    noisy_top = noisy_scores.index(max(noisy_scores))
    prob_move = sum(abs(a - b) for a, b in zip(clean_weights, noisy_weights))
    return noisy_out, clean_top, noisy_top, prob_move


def clean_attention(query: list[float], keys: list[list[float]], values: list[list[float]]) -> list[float]:
    scores = [dot(query, key) / math.sqrt(len(query)) for key in keys]
    weights = softmax(scores)
    out = [0.0] * len(values[0])
    for weight, value in zip(weights, values):
        for i, element in enumerate(value):
            out[i] += weight * element
    return out


def block_once(weight_noise: float, score_noise: float, seed: int) -> tuple[float, float, float, bool, float]:
    rng = random.Random(seed)
    dim = 16
    context = 8
    x = [rng.gauss(0.0, 0.4) for _ in range(dim)]
    memory = [[rng.gauss(0.0, 0.5) for _ in range(dim)] for _ in range(context)]

    wq = make_matrix(rng, dim, dim, 0.18)
    wk = make_matrix(rng, dim, dim, 0.18)
    wv = make_matrix(rng, dim, dim, 0.18)
    wo = make_matrix(rng, dim, dim, 0.16)
    wup = make_matrix(rng, 2 * dim, dim, 0.14)
    wdown = make_matrix(rng, dim, 2 * dim, 0.12)

    nx = layer_norm(x)
    clean_q = matvec(wq, nx)
    clean_k = [matvec(wk, layer_norm(token)) for token in memory]
    clean_v = [matvec(wv, layer_norm(token)) for token in memory]
    clean_attn = matvec(wo, clean_attention(clean_q, clean_k, clean_v))
    clean_x1 = add(x, clean_attn)
    clean_mlp = matvec(wdown, tanh_vec(matvec(wup, layer_norm(clean_x1))))
    clean_x2 = add(clean_x1, clean_mlp)

    noisy_q = noisy_matvec(wq, nx, rng, weight_noise, weight_noise)
    noisy_k = [noisy_matvec(wk, layer_norm(token), rng, weight_noise, weight_noise) for token in memory]
    noisy_v = [noisy_matvec(wv, layer_norm(token), rng, weight_noise, weight_noise) for token in memory]
    noisy_attn_raw, clean_top, noisy_top, prob_move = attention(noisy_q, noisy_k, noisy_v, score_noise, rng)
    noisy_attn = noisy_matvec(wo, noisy_attn_raw, rng, weight_noise, weight_noise)
    noisy_x1 = add(x, noisy_attn)
    noisy_hidden = tanh_vec(noisy_matvec(wup, layer_norm(noisy_x1), rng, weight_noise, weight_noise))
    noisy_mlp = noisy_matvec(wdown, noisy_hidden, rng, weight_noise, weight_noise)
    noisy_x2 = add(noisy_x1, noisy_mlp)

    return (
        rel_error(clean_attn, noisy_attn),
        rel_error(clean_mlp, noisy_mlp),
        rel_error(clean_x2, noisy_x2),
        clean_top != noisy_top,
        prob_move,
    )


def summarize(weight_noise: float, score_noise: float) -> tuple[float, float, float, float, float]:
    trials = [block_once(weight_noise, score_noise, 1000 + i) for i in range(24)]
    n = len(trials)
    return (
        sum(row[0] for row in trials) / n,
        sum(row[1] for row in trials) / n,
        sum(row[2] for row in trials) / n,
        sum(1 for row in trials if row[3]) / n,
        sum(row[4] for row in trials) / n,
    )


def main() -> None:
    print("tiny_transformer_block_noise")
    print("hidden,16")
    print("context,8")
    print("trials,24")
    print()
    print("weight_noise,score_noise,attention_error,mlp_error,block_state_error,top_flip_rate,probability_movement")
    for weight_noise in [0.00, 0.02, 0.05]:
        for score_noise in [0.00, 0.05, 0.10]:
            attn_error, mlp_error, state_error, flip_rate, prob_move = summarize(weight_noise, score_noise)
            print(f"{weight_noise:.2f},{score_noise:.2f},{attn_error:.4f},{mlp_error:.4f},{state_error:.4f},{flip_rate:.4f},{prob_move:.4f}")


if __name__ == "__main__":
    main()
