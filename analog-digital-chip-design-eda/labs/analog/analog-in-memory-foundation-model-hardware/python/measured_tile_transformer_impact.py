#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
NONIDEALITY_CSV = MEASUREMENTS_DIR / "analog-nonideality-stack.csv"
CSV_OUT = MEASUREMENTS_DIR / "measured-tile-transformer-impact.csv"
MD_OUT = MEASUREMENTS_DIR / "measured-tile-transformer-impact.md"

Vector = list[float]
Matrix = list[list[float]]


@dataclass(frozen=True)
class Policy:
    name: str
    qkv: str
    output_projection: str
    mlp: str
    attention_scores: str
    logits: str
    tile_residual_scale: float
    state_budget: float
    attention_flip_budget: float
    token_flip_budget: float


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def rms(values: Vector) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: Vector, measured: Vector) -> float:
    return rms([a - b for a, b in zip(reference, measured)]) / max(1e-12, rms(reference))


def add(a: Vector, b: Vector) -> Vector:
    return [x + y for x, y in zip(a, b)]


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


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [dot(row, vector) for row in matrix]


def load_measured_tile_residual() -> tuple[float, int]:
    with NONIDEALITY_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    final = next((row for row in rows if row["stage"] == "adc_quantized_column_readout"), None)
    if final is None:
        raise ValueError("missing adc_quantized_column_readout stage in analog nonideality stack")
    return float(final["residual_relative"]), int(final["residual_q8"])


def measured_analog_matvec(matrix: Matrix, vector: Vector, rng: random.Random, measured_residual: float, scale: float) -> Vector:
    clean = matvec(matrix, vector)
    clean_norm = max(1e-12, rms(clean))
    sigma = measured_residual * scale
    gain = 1.0 + rng.gauss(0.0, sigma * 0.30)
    bias = rng.gauss(0.0, sigma * clean_norm * 0.08)
    return [gain * value + bias + rng.gauss(0.0, sigma * clean_norm) for value in clean]


def choose_matvec(kind: str, matrix: Matrix, vector: Vector, rng: random.Random, measured_residual: float, policy: Policy) -> Vector:
    if kind == "digital":
        return matvec(matrix, vector)
    if kind == "analog":
        return measured_analog_matvec(matrix, vector, rng, measured_residual, policy.tile_residual_scale)
    raise ValueError(f"unknown placement {kind!r}")


def attention(query: Vector, keys: list[Vector], values: list[Vector], score_noise: float, rng: random.Random) -> tuple[Vector, int, Vector]:
    scores = [dot(query, key) / math.sqrt(len(query)) for key in keys]
    noisy_scores = [score + rng.gauss(0.0, score_noise) for score in scores]
    weights = softmax(noisy_scores)
    out = [0.0] * len(values[0])
    for weight, value in zip(weights, values):
        for idx, element in enumerate(value):
            out[idx] += weight * element
    return out, noisy_scores.index(max(noisy_scores)), weights


def block(seed: int, policy: Policy, measured_residual: float) -> dict[str, float]:
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
    clean_attn_raw, clean_top, clean_weights = attention(clean_q, clean_k, clean_v, 0.0, rng)
    clean_attn = matvec(wo, clean_attn_raw)
    clean_x1 = add(x, clean_attn)
    clean_mlp = matvec(wdown, gelu_like(matvec(wup, layer_norm(clean_x1))))
    clean_x2 = add(clean_x1, clean_mlp)
    clean_logits = matvec(wvocab, layer_norm(clean_x2))
    clean_token = clean_logits.index(max(clean_logits))
    clean_probs = softmax(clean_logits)

    q = choose_matvec(policy.qkv, wq, nx, rng, measured_residual, policy)
    keys = [choose_matvec(policy.qkv, wk, layer_norm(token), rng, measured_residual, policy) for token in memory]
    values = [choose_matvec(policy.qkv, wv, layer_norm(token), rng, measured_residual, policy) for token in memory]
    score_noise = measured_residual * policy.tile_residual_scale if policy.attention_scores == "analog" else 0.0
    attn_raw, chosen_top, weights = attention(q, keys, values, score_noise, rng)
    if policy.attention_scores == "digital":
        attn_raw, chosen_top, weights = attention(q, keys, values, 0.0, rng)
    attn = choose_matvec(policy.output_projection, wo, attn_raw, rng, measured_residual, policy)
    x1 = add(x, attn)
    up = choose_matvec(policy.mlp, wup, layer_norm(x1), rng, measured_residual, policy)
    mlp = choose_matvec(policy.mlp, wdown, gelu_like(up), rng, measured_residual, policy)
    x2 = add(x1, mlp)
    logits = choose_matvec(policy.logits, wvocab, layer_norm(x2), rng, measured_residual, policy)
    token = logits.index(max(logits))
    probs = softmax(logits)

    return {
        "state_error": rel_error(clean_x2, x2),
        "attention_error": rel_error(clean_attn, attn),
        "mlp_error": rel_error(clean_mlp, mlp),
        "logit_error": rel_error(clean_logits, logits),
        "attention_top_flip": 1.0 if clean_top != chosen_top else 0.0,
        "token_flip": 1.0 if clean_token != token else 0.0,
        "attention_probability_movement": sum(abs(a - b) for a, b in zip(clean_weights, weights)),
        "logit_probability_movement": sum(abs(a - b) for a, b in zip(clean_probs, probs)),
    }


def summarize(policy: Policy, measured_residual: float, measured_q8: int, trials: int = 40) -> dict[str, str | float]:
    rows = [block(19000 + idx, policy, measured_residual) for idx in range(trials)]
    averaged = {key: sum(row[key] for row in rows) / trials for key in rows[0]}
    decision = "analog_path"
    reason = "measured_tile_within_budget"
    if {policy.qkv, policy.output_projection, policy.mlp, policy.attention_scores, policy.logits} == {"digital"}:
        decision = "digital_reference"
        reason = "reference_path"
    elif averaged["state_error"] > policy.state_budget:
        decision = "digital_fallback"
        reason = "state_error_from_measured_tile_residual"
    elif averaged["attention_top_flip"] > policy.attention_flip_budget:
        decision = "digital_fallback"
        reason = "attention_selection_too_sensitive"
    elif averaged["token_flip"] > policy.token_flip_budget:
        decision = "digital_fallback"
        reason = "token_choice_too_sensitive"
    return {
        "policy": policy.name,
        "qkv": policy.qkv,
        "attention_scores": policy.attention_scores,
        "output_projection": policy.output_projection,
        "mlp": policy.mlp,
        "logits": policy.logits,
        "measured_tile_residual": measured_residual,
        "measured_tile_residual_q8": measured_q8,
        "tile_residual_scale": policy.tile_residual_scale,
        "state_error": averaged["state_error"],
        "attention_error": averaged["attention_error"],
        "mlp_error": averaged["mlp_error"],
        "logit_error": averaged["logit_error"],
        "attention_top_flip_rate": averaged["attention_top_flip"],
        "token_flip_rate": averaged["token_flip"],
        "attention_probability_movement": averaged["attention_probability_movement"],
        "logit_probability_movement": averaged["logit_probability_movement"],
        "decision": decision,
        "reason": reason,
    }


def run() -> list[dict[str, str | float]]:
    measured_residual, measured_q8 = load_measured_tile_residual()
    policies = [
        Policy("all_digital_reference", "digital", "digital", "digital", "digital", "digital", 0.0, 0.12, 0.15, 0.15),
        Policy("measured_fixed_projection_tile", "analog", "analog", "analog", "digital", "digital", 0.40, 0.12, 0.15, 0.20),
        Policy("measured_projection_stressed_tile", "analog", "analog", "analog", "digital", "digital", 1.00, 0.12, 0.15, 0.20),
        Policy("measured_attention_scores_analog", "analog", "analog", "analog", "analog", "digital", 0.65, 0.12, 0.15, 0.20),
        Policy("measured_logits_analog", "analog", "analog", "analog", "digital", "analog", 0.65, 0.12, 0.15, 0.15),
    ]
    return [summarize(policy, measured_residual, measured_q8) for policy in policies]


def write_csv(rows: list[dict[str, str | float]]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str | float]]) -> None:
    measured = float(rows[0]["measured_tile_residual"])
    measured_q8 = int(rows[0]["measured_tile_residual_q8"])
    lines = [
        "# Measured Tile Transformer Impact",
        "",
        "This experiment takes the residual from `analog-nonideality-stack.csv` and uses it as the analog tile error source inside a small transformer block. The question is no longer whether one tile output is close to one dot product. The question is whether that measured tile error can enter attention, MLP, logits, and the residual stream without changing the model decision too much.",
        "",
        "```text",
        f"measured_tile_residual: {measured:.5f}",
        f"measured_tile_residual_q8: {measured_q8}",
        "hidden: 24",
        "context: 12",
        "trials: 40",
        "```",
        "",
        "## Results",
        "",
        "| policy | qkv | scores | out proj | mlp | logits | scale | state error | attention error | mlp error | logit error | attention flip | token flip | decision | reason |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['policy']} | {row['qkv']} | {row['attention_scores']} | {row['output_projection']} | "
            f"{row['mlp']} | {row['logits']} | {float(row['tile_residual_scale']):.2f} | "
            f"{float(row['state_error']):.4f} | {float(row['attention_error']):.4f} | "
            f"{float(row['mlp_error']):.4f} | {float(row['logit_error']):.4f} | "
            f"{float(row['attention_top_flip_rate']):.4f} | {float(row['token_flip_rate']):.4f} | "
            f"{row['decision']} | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A tile residual is not automatically a model residual. The tile error first changes Q, K, V, output projection, or MLP vectors. Those changed vectors then pass through attention selection, value mixing, residual addition, nonlinear activation, and logits. Some errors shrink. Some errors line up with sensitive decisions and grow.",
            "",
            "The fixed-projection case is the useful analog target. It sends Q/K/V, output projection, and MLP matvecs through the measured tile model while keeping attention scores and logits digital. That is the cleanest claim because trained weights are resident and the digital side still owns selection and token choice.",
            "",
            "The stressed-tile case uses the same placement but spends the full measured residual. If state error crosses the budget, the right conclusion is not that analog compute failed everywhere. The right conclusion is narrower: this tile state should not serve this model path without calibration, correction, or digital fallback.",
            "",
            "The analog-attention case changes the object. Attention scores choose changing memory. A small score movement can change which token is selected. That is why attention top-flip rate is a first-class metric, not an afterthought.",
            "",
            "The analog-logits case changes the final ranking. Logit RMS error is incomplete because generation depends on rank and probability movement. A logits accelerator must prove that it preserves the choices the sampler will see.",
            "",
            "The control-plane rule is simple: the scheduler may choose analog for a class of operations, but the governor must judge the measured state error, attention selection movement, and token-choice movement before the result is trusted.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = run()
    write_csv(rows)
    write_markdown(rows)
    print("measured_tile_transformer_impact")
    print(f"policies,{len(rows)}")
    print(f"measured_tile_residual,{float(rows[0]['measured_tile_residual']):.5f}")
    print(f"measured_tile_residual_q8,{int(rows[0]['measured_tile_residual_q8'])}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
