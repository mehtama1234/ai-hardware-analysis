#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from dataclasses import dataclass


Vector = list[float]
Matrix = list[list[float]]


@dataclass(frozen=True)
class HardwarePolicy:
    name: str
    qkv: str
    attention_scores: str
    value_mixing: str
    output_projection: str
    mlp: str
    logits: str
    state_error_budget: float
    score_flip_budget: float
    token_flip_budget: float
    analog_noise: float
    score_noise: float
    calibration_age: int
    tile_health: float


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def add(a: Vector, b: Vector) -> Vector:
    return [x + y for x, y in zip(a, b)]


def rms(values: Vector) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: Vector, measured: Vector) -> float:
    return rms([a - b for a, b in zip(reference, measured)]) / max(1e-12, rms(reference))


def softmax(scores: Vector) -> Vector:
    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def layer_norm(x: Vector) -> Vector:
    mean = sum(x) / len(x)
    centered = [value - mean for value in x]
    scale = math.sqrt(sum(value * value for value in centered) / len(centered) + 1e-6)
    return [value / scale for value in centered]


def gelu_like(values: Vector) -> Vector:
    return [0.5 * x * (1.0 + math.tanh(0.79788456 * (x + 0.044715 * x * x * x))) for x in values]


def make_matrix(rng: random.Random, rows: int, cols: int, scale: float) -> Matrix:
    return [[rng.gauss(0.0, scale) for _ in range(cols)] for _ in range(rows)]


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [dot(row, vector) for row in matrix]


def analog_matvec(matrix: Matrix, vector: Vector, rng: random.Random, policy: HardwarePolicy) -> Vector:
    drift = min(0.06, policy.calibration_age / 4096.0 * 0.03)
    health = policy.tile_health * 0.08
    sigma = policy.analog_noise + drift + health
    gain = 1.0 + rng.gauss(0.0, sigma * 0.35)
    bias = rng.gauss(0.0, sigma * 0.20)
    out: Vector = []
    for row in matrix:
        total = 0.0
        for weight, value in zip(row, vector):
            total += weight * (1.0 + rng.gauss(0.0, sigma)) * value
        out.append(gain * total + bias + rng.gauss(0.0, sigma))
    return out


def choose_matvec(kind: str, matrix: Matrix, vector: Vector, rng: random.Random, policy: HardwarePolicy) -> Vector:
    if kind == "analog":
        return analog_matvec(matrix, vector, rng, policy)
    if kind == "digital":
        return matvec(matrix, vector)
    raise ValueError(f"unknown placement {kind!r}")


def attention(query: Vector, keys: list[Vector], values: list[Vector], rng: random.Random, policy: HardwarePolicy) -> tuple[Vector, int, int, float]:
    clean_scores = [dot(query, key) / math.sqrt(len(query)) for key in keys]
    scores = list(clean_scores)
    if policy.attention_scores == "analog":
        scores = [score + rng.gauss(0.0, policy.score_noise + policy.tile_health * 0.08) for score in scores]
    elif policy.attention_scores != "digital":
        raise ValueError(f"unknown attention score placement {policy.attention_scores!r}")
    clean_weights = softmax(clean_scores)
    weights = softmax(scores)
    clean_top = clean_scores.index(max(clean_scores))
    chosen_top = scores.index(max(scores))
    prob_move = sum(abs(a - b) for a, b in zip(clean_weights, weights))
    out = [0.0] * len(values[0])
    for weight, value in zip(weights, values):
        for i, element in enumerate(value):
            out[i] += weight * element
    if policy.value_mixing == "analog":
        out = [value + rng.gauss(0.0, policy.analog_noise + policy.tile_health * 0.05) for value in out]
    elif policy.value_mixing != "digital":
        raise ValueError(f"unknown value mixing placement {policy.value_mixing!r}")
    return out, clean_top, chosen_top, prob_move


def block(seed: int, policy: HardwarePolicy) -> dict[str, float | str]:
    rng = random.Random(seed)
    dim = 24
    context = 12
    vocab = 48
    x = [rng.gauss(0.0, 0.35) for _ in range(dim)]
    memory = [[rng.gauss(0.0, 0.45) for _ in range(dim)] for _ in range(context)]

    wq = make_matrix(rng, dim, dim, 0.16)
    wk = make_matrix(rng, dim, dim, 0.16)
    wv = make_matrix(rng, dim, dim, 0.16)
    wo = make_matrix(rng, dim, dim, 0.15)
    wup = make_matrix(rng, 4 * dim, dim, 0.11)
    wdown = make_matrix(rng, dim, 4 * dim, 0.10)
    wvocab = make_matrix(rng, vocab, dim, 0.18)

    nx = layer_norm(x)
    clean_q = matvec(wq, nx)
    clean_k = [matvec(wk, layer_norm(token)) for token in memory]
    clean_v = [matvec(wv, layer_norm(token)) for token in memory]
    clean_attn_raw, clean_top, _, _ = attention(clean_q, clean_k, clean_v, rng, HardwarePolicy("clean", "digital", "digital", "digital", "digital", "digital", "digital", 1.0, 1.0, 1.0, 0.0, 0.0, 0, 0.0))
    clean_attn = matvec(wo, clean_attn_raw)
    clean_x1 = add(x, clean_attn)
    clean_mlp = matvec(wdown, gelu_like(matvec(wup, layer_norm(clean_x1))))
    clean_x2 = add(clean_x1, clean_mlp)
    clean_logits = matvec(wvocab, layer_norm(clean_x2))
    clean_token = clean_logits.index(max(clean_logits))
    clean_top3 = set(sorted(range(len(clean_logits)), key=lambda i: clean_logits[i], reverse=True)[:3])
    clean_probs = softmax(clean_logits)

    q = choose_matvec(policy.qkv, wq, nx, rng, policy)
    keys = [choose_matvec(policy.qkv, wk, layer_norm(token), rng, policy) for token in memory]
    values = [choose_matvec(policy.qkv, wv, layer_norm(token), rng, policy) for token in memory]
    attn_raw, _, noisy_top, prob_move = attention(q, keys, values, rng, policy)
    attn = choose_matvec(policy.output_projection, wo, attn_raw, rng, policy)
    x1 = add(x, attn)
    hidden = gelu_like(choose_matvec(policy.mlp, wup, layer_norm(x1), rng, policy))
    mlp = choose_matvec(policy.mlp, wdown, hidden, rng, policy)
    x2 = add(x1, mlp)
    logits = choose_matvec(policy.logits, wvocab, layer_norm(x2), rng, policy)
    token = logits.index(max(logits))
    top3 = set(sorted(range(len(logits)), key=lambda i: logits[i], reverse=True)[:3])
    probs = softmax(logits)

    state_error = rel_error(clean_x2, x2)
    attention_error = rel_error(clean_attn, attn)
    mlp_error = rel_error(clean_mlp, mlp)
    logit_error = rel_error(clean_logits, logits)
    top_flip = 1.0 if clean_top != noisy_top else 0.0
    token_flip = 1.0 if clean_token != token else 0.0
    top3_overlap = len(clean_top3 & top3) / 3.0
    logit_probability_movement = sum(abs(a - b) for a, b in zip(clean_probs, probs))
    allowed = state_error <= policy.state_error_budget and top_flip <= policy.score_flip_budget and token_flip <= policy.token_flip_budget
    reason = "allowed"
    if state_error > policy.state_error_budget:
        reason = "fallback_state_error"
    elif top_flip > policy.score_flip_budget:
        reason = "fallback_attention_selection"
    elif token_flip > policy.token_flip_budget:
        reason = "fallback_token_choice"
    return {
        "state_error": state_error,
        "attention_error": attention_error,
        "mlp_error": mlp_error,
        "logit_error": logit_error,
        "top_flip": top_flip,
        "token_flip": token_flip,
        "top3_overlap": top3_overlap,
        "probability_movement": prob_move,
        "logit_probability_movement": logit_probability_movement,
        "decision": "analog_path" if allowed else "digital_fallback",
        "reason": reason,
    }


def summarize(policy: HardwarePolicy, trials: int = 32) -> dict[str, float | str]:
    rows = [block(7000 + i, policy) for i in range(trials)]
    state_error = sum(float(row["state_error"]) for row in rows) / trials
    attention_error = sum(float(row["attention_error"]) for row in rows) / trials
    mlp_error = sum(float(row["mlp_error"]) for row in rows) / trials
    logit_error = sum(float(row["logit_error"]) for row in rows) / trials
    top_flip_rate = sum(float(row["top_flip"]) for row in rows) / trials
    token_flip_rate = sum(float(row["token_flip"]) for row in rows) / trials
    top3_overlap = sum(float(row["top3_overlap"]) for row in rows) / trials
    probability_movement = sum(float(row["probability_movement"]) for row in rows) / trials
    logit_probability_movement = sum(float(row["logit_probability_movement"]) for row in rows) / trials
    decision = "analog_path"
    reason = "allowed"
    if {policy.qkv, policy.attention_scores, policy.value_mixing, policy.output_projection, policy.mlp, policy.logits} == {"digital"}:
        decision = "digital_reference"
        reason = "reference_path"
    elif state_error > policy.state_error_budget:
        decision = "digital_fallback"
        reason = "fallback_state_error"
    elif top_flip_rate > policy.score_flip_budget:
        decision = "digital_fallback"
        reason = "fallback_attention_selection"
    elif token_flip_rate > policy.token_flip_budget:
        decision = "digital_fallback"
        reason = "fallback_token_choice"
    return {
        "policy": policy.name,
        "qkv": policy.qkv,
        "scores": policy.attention_scores,
        "value_mix": policy.value_mixing,
        "out_proj": policy.output_projection,
        "mlp": policy.mlp,
        "logits": policy.logits,
        "state_error": state_error,
        "attention_error": attention_error,
        "mlp_error": mlp_error,
        "logit_error": logit_error,
        "top_flip_rate": top_flip_rate,
        "token_flip_rate": token_flip_rate,
        "top3_overlap": top3_overlap,
        "probability_movement": probability_movement,
        "logit_probability_movement": logit_probability_movement,
        "decision": decision,
        "reason": reason,
    }


def main() -> None:
    policies = [
        HardwarePolicy("all_digital_reference", "digital", "digital", "digital", "digital", "digital", "digital", 0.10, 0.15, 0.15, 0.00, 0.00, 0, 0.00),
        HardwarePolicy("fixed_projection_analog", "analog", "digital", "digital", "analog", "analog", "digital", 0.10, 0.15, 0.15, 0.015, 0.00, 128, 0.02),
        HardwarePolicy("analog_logits_experiment", "analog", "digital", "digital", "analog", "analog", "analog", 0.10, 0.15, 0.15, 0.015, 0.00, 128, 0.02),
        HardwarePolicy("analog_attention_experiment", "analog", "analog", "analog", "analog", "analog", "digital", 0.10, 0.15, 0.15, 0.015, 0.08, 128, 0.02),
        HardwarePolicy("stale_unhealthy_tiles", "analog", "digital", "digital", "analog", "analog", "digital", 0.10, 0.15, 0.15, 0.020, 0.00, 2048, 0.25),
    ]
    print("transformer_partition_simulator")
    print("relative units,not model calibrated")
    print("hidden,24")
    print("context,12")
    print("trials,32")
    print()
    print("policy,qkv,scores,value_mix,out_proj,mlp,logits,state_error,attention_error,mlp_error,logit_error,top_flip_rate,token_flip_rate,top3_overlap,attention_probability_movement,logit_probability_movement,decision,reason")
    for policy in policies:
        row = summarize(policy)
        print(
            f"{row['policy']},{row['qkv']},{row['scores']},{row['value_mix']},{row['out_proj']},{row['mlp']},"
            f"{row['logits']},{row['state_error']:.4f},{row['attention_error']:.4f},{row['mlp_error']:.4f},"
            f"{row['logit_error']:.4f},{row['top_flip_rate']:.4f},{row['token_flip_rate']:.4f},"
            f"{row['top3_overlap']:.4f},{row['probability_movement']:.4f},{row['logit_probability_movement']:.4f},"
            f"{row['decision']},{row['reason']}"
        )


if __name__ == "__main__":
    main()
