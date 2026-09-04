#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelShape:
    hidden: int = 4096
    heads: int = 32
    layers: int = 32
    bytes_per_value: int = 2


@dataclass(frozen=True)
class CostModel:
    digital_mac: float = 12.0
    near_cache_mac: float = 3.0
    analog_memory_mac: float = 1.5
    memory_byte: float = 0.08
    analog_write_byte: float = 0.20
    softmax_per_score: float = 4.0


def kv_cache_bytes(tokens: int, shape: ModelShape) -> int:
    return 2 * shape.layers * tokens * shape.hidden * shape.bytes_per_value


def attention_step_counts(context_tokens: int, shape: ModelShape) -> dict[str, int]:
    score_macs = shape.layers * context_tokens * shape.hidden
    value_macs = shape.layers * context_tokens * shape.hidden
    score_count = shape.layers * shape.heads * context_tokens
    kv_read_bytes = 2 * shape.layers * context_tokens * shape.hidden * shape.bytes_per_value
    kv_write_bytes = 2 * shape.layers * shape.hidden * shape.bytes_per_value
    return {
        "score_macs": score_macs,
        "value_macs": value_macs,
        "score_count": score_count,
        "kv_read_bytes": kv_read_bytes,
        "kv_write_bytes": kv_write_bytes,
    }


def attention_energy(context_tokens: int, shape: ModelShape, cost: CostModel, placement: str) -> float:
    counts = attention_step_counts(context_tokens, shape)
    if placement == "digital_cache":
        mac_cost = cost.digital_mac
        write_cost = cost.memory_byte
    elif placement == "near_cache_compute":
        mac_cost = cost.near_cache_mac
        write_cost = cost.memory_byte
    elif placement == "analog_cache_state":
        mac_cost = cost.analog_memory_mac
        write_cost = cost.analog_write_byte
    else:
        raise ValueError(f"unknown placement {placement!r}")

    return (
        (counts["score_macs"] + counts["value_macs"]) * mac_cost
        + counts["kv_read_bytes"] * cost.memory_byte
        + counts["kv_write_bytes"] * write_cost
        + counts["score_count"] * cost.softmax_per_score
    )


def projection_step_energy(shape: ModelShape, digital_mac: float = 12.0) -> float:
    qkv = shape.hidden * 3 * shape.hidden
    output = shape.hidden * shape.hidden
    mlp_up = shape.hidden * 4 * shape.hidden
    mlp_down = 4 * shape.hidden * shape.hidden
    return shape.layers * (qkv + output + mlp_up + mlp_down) * digital_mac


def print_context_sweep() -> None:
    shape = ModelShape()
    cost = CostModel()
    print("attention_kv_cache_model")
    print(f"hidden,{shape.hidden}")
    print(f"heads,{shape.heads}")
    print(f"layers,{shape.layers}")
    print("relative units,not process calibrated")
    print()
    print("context,active_window,kv_cache_mb,kv_read_mb_per_token,digital_cache,near_cache_compute,analog_cache_state,near_cache_vs_digital,analog_cache_vs_digital,attention_digital_to_projection")
    for context in [512, 2048, 8192, 32768]:
        active_windows = sorted({min(context, 512), min(context, 2048), context})
        for active_window in active_windows:
            digital = attention_energy(active_window, shape, cost, "digital_cache")
            near_cache = attention_energy(active_window, shape, cost, "near_cache_compute")
            analog_cache = attention_energy(active_window, shape, cost, "analog_cache_state")
            counts = attention_step_counts(active_window, shape)
            projection = projection_step_energy(shape, cost.digital_mac)
            print(
                f"{context},{active_window},"
                f"{kv_cache_bytes(context, shape) / 1_000_000:.2f},"
                f"{counts['kv_read_bytes'] / 1_000_000:.2f},"
                f"{digital:.2e},{near_cache:.2e},{analog_cache:.2e},"
                f"{near_cache / digital:.4f},"
                f"{analog_cache / digital:.4f},"
                f"{digital / projection:.4f}"
            )


if __name__ == "__main__":
    print_context_sweep()
