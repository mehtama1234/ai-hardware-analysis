#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelShape:
    hidden: int = 4096
    layers: int = 32
    mlp_ratio: int = 4
    bytes_per_value: int = 2


@dataclass(frozen=True)
class TileShape:
    rows: int = 128
    cols: int = 128
    adc_bits: int = 6
    dac_bits: int = 6


@dataclass(frozen=True)
class CostModel:
    analog_mac: float = 1.0
    digital_mac: float = 12.0
    adc_base: float = 18.0
    dac_base: float = 5.0
    digital_accum: float = 0.6
    memory_byte: float = 0.08
    calibration_unit: float = 50_000_000.0


def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def projection_energy(tokens: int, shape: ModelShape, tile: TileShape, cost: CostModel, analog: bool) -> float:
    projections = [
        (shape.hidden, 3 * shape.hidden),
        (shape.hidden, shape.hidden),
        (shape.hidden, shape.mlp_ratio * shape.hidden),
        (shape.mlp_ratio * shape.hidden, shape.hidden),
    ]
    total = 0.0
    for input_dim, output_dim in projections:
        macs = tokens * input_dim * output_dim
        if not analog:
            total += macs * cost.digital_mac
            continue
        row_tiles = ceil_div(input_dim, tile.rows)
        col_tiles = ceil_div(output_dim, tile.cols)
        adc = tokens * output_dim * row_tiles
        dac = tokens * input_dim * col_tiles
        accum = tokens * output_dim * max(0, row_tiles - 1)
        adc_cost = cost.adc_base * (2 ** max(0, tile.adc_bits - 4))
        dac_cost = cost.dac_base * (2 ** max(0, tile.dac_bits - 4))
        total += macs * cost.analog_mac + adc * adc_cost + dac * dac_cost + accum * cost.digital_accum
    return total * shape.layers


def kv_cache_bytes(tokens: int, shape: ModelShape) -> int:
    return 2 * shape.layers * tokens * shape.hidden * shape.bytes_per_value


def attention_cache_energy(active_context: int, generated_tokens: int, batch: int, shape: ModelShape, cost: CostModel) -> float:
    per_token_read = kv_cache_bytes(active_context, shape)
    return per_token_read * generated_tokens * batch * cost.memory_byte


def calibration_penalty(calibration_due: bool, tile_health: float, cost: CostModel) -> float:
    if not calibration_due:
        return 0.0
    return cost.calibration_unit * (1.0 + tile_health)


def estimate_error(tile_health: float, adc_bits: int, batch: int) -> float:
    converter_error = 0.18 / max(1, 2 ** (adc_bits - 3))
    reuse_stress = 0.02 if batch >= 4 else 0.05
    return converter_error + tile_health + reuse_stress


def decide_phase(
    phase: str,
    tokens: int,
    batch: int,
    active_context: int,
    calibration_due: bool,
    tile_health: float,
    shape: ModelShape,
    tile: TileShape,
    cost: CostModel,
) -> dict[str, float | str]:
    work_tokens = tokens * batch
    analog = projection_energy(work_tokens, shape, tile, cost, analog=True)
    digital = projection_energy(work_tokens, shape, tile, cost, analog=False)
    cache = attention_cache_energy(active_context, tokens if phase == "decode" else 1, batch, shape, cost)
    calibration = calibration_penalty(calibration_due, tile_health, cost)
    analog_total = analog + cache + calibration
    digital_total = digital + cache
    ratio = analog_total / digital_total
    error = estimate_error(tile_health, tile.adc_bits, batch)
    decision = "analog"
    reason = "projection reuse pays for boundary cost"
    if error > 0.12:
        decision = "digital"
        reason = "estimated state error is above budget"
    elif ratio > 0.70:
        decision = "digital"
        reason = "analog cost is too close to digital cost"
    elif phase == "decode" and batch < 4 and active_context > 4096:
        decision = "digital"
        reason = "single-request long-context decode is cache-limited"
    elif phase == "decode" and batch >= 4:
        decision = "analog_batched_decode"
        reason = "batch reuse is enough to amortize converters"
    return {
        "phase": phase,
        "tokens": tokens,
        "batch": batch,
        "active_context": active_context,
        "calibration_due": "yes" if calibration_due else "no",
        "tile_health": tile_health,
        "analog_to_digital": ratio,
        "cache_to_analog_projection": cache / max(1.0, analog),
        "estimated_error": error,
        "decision": decision,
        "reason": reason,
    }


def main() -> None:
    shape = ModelShape()
    tile = TileShape(adc_bits=6, dac_bits=6)
    cost = CostModel()
    workloads = [
        ("prefill", 2048, 1, 2048, False, 0.02),
        ("decode", 128, 1, 2048, False, 0.02),
        ("decode", 128, 1, 8192, False, 0.02),
        ("decode", 128, 8, 2048, False, 0.02),
        ("prefill", 2048, 1, 2048, True, 0.08),
        ("decode", 128, 8, 2048, True, 0.08),
    ]
    print("serving_policy")
    print("relative units,not process calibrated")
    print()
    print("phase,tokens,batch,active_context,calibration_due,tile_health,analog_to_digital,cache_to_analog_projection,estimated_error,decision,reason")
    for workload in workloads:
        row = decide_phase(*workload, shape, tile, cost)
        print(
            f"{row['phase']},{row['tokens']},{row['batch']},{row['active_context']},"
            f"{row['calibration_due']},{row['tile_health']:.2f},"
            f"{row['analog_to_digital']:.4f},{row['cache_to_analog_projection']:.4f},"
            f"{row['estimated_error']:.4f},{row['decision']},{row['reason']}"
        )


if __name__ == "__main__":
    main()
