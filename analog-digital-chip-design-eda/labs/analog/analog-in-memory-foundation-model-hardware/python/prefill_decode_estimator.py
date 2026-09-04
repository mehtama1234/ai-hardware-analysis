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


def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def projection_counts(input_dim: int, output_dim: int, tokens: int, tile: TileShape) -> dict[str, float]:
    row_tiles = ceil_div(input_dim, tile.rows)
    col_tiles = ceil_div(output_dim, tile.cols)
    macs = tokens * input_dim * output_dim
    adc = tokens * output_dim * row_tiles
    dac = tokens * input_dim * col_tiles
    accum = tokens * output_dim * max(0, row_tiles - 1)
    return {
        "row_tiles": row_tiles,
        "col_tiles": col_tiles,
        "macs": macs,
        "adc": adc,
        "dac": dac,
        "accum": accum,
    }


def analog_projection_energy(input_dim: int, output_dim: int, tokens: int, tile: TileShape, cost: CostModel) -> float:
    counts = projection_counts(input_dim, output_dim, tokens, tile)
    adc_cost = cost.adc_base * (2 ** max(0, tile.adc_bits - 4))
    dac_cost = cost.dac_base * (2 ** max(0, tile.dac_bits - 4))
    return (
        counts["macs"] * cost.analog_mac
        + counts["adc"] * adc_cost
        + counts["dac"] * dac_cost
        + counts["accum"] * cost.digital_accum
    )


def digital_projection_energy(input_dim: int, output_dim: int, tokens: int, cost: CostModel) -> float:
    return tokens * input_dim * output_dim * cost.digital_mac


def transformer_projection_energy(tokens: int, shape: ModelShape, tile: TileShape, cost: CostModel, analog: bool) -> float:
    projections = [
        (shape.hidden, 3 * shape.hidden),
        (shape.hidden, shape.hidden),
        (shape.hidden, shape.mlp_ratio * shape.hidden),
        (shape.mlp_ratio * shape.hidden, shape.hidden),
    ]
    total = 0.0
    for input_dim, output_dim in projections:
        if analog:
            total += analog_projection_energy(input_dim, output_dim, tokens, tile, cost)
        else:
            total += digital_projection_energy(input_dim, output_dim, tokens, cost)
    return total * shape.layers


def kv_cache_bytes(tokens: int, shape: ModelShape) -> int:
    return 2 * shape.layers * tokens * shape.hidden * shape.bytes_per_value


def phase_report(prompt_tokens: int, generated_tokens: int, batch: int, shape: ModelShape, tile: TileShape, cost: CostModel) -> dict[str, float]:
    prefill_tokens = prompt_tokens * batch
    decode_tokens = generated_tokens * batch
    prefill_analog = transformer_projection_energy(prefill_tokens, shape, tile, cost, analog=True)
    prefill_digital = transformer_projection_energy(prefill_tokens, shape, tile, cost, analog=False)
    decode_analog_projection = transformer_projection_energy(decode_tokens, shape, tile, cost, analog=True)
    decode_digital_projection = transformer_projection_energy(decode_tokens, shape, tile, cost, analog=False)

    # Decode must repeatedly read a larger cache as the generated sequence grows.
    average_context = prompt_tokens + generated_tokens / 2
    decode_cache_energy = generated_tokens * batch * kv_cache_bytes(int(average_context), shape) * cost.memory_byte

    return {
        "prompt_tokens": prompt_tokens,
        "generated_tokens": generated_tokens,
        "batch": batch,
        "kv_cache_mb_end": kv_cache_bytes(prompt_tokens + generated_tokens, shape) / 1_000_000,
        "prefill_analog_to_digital": prefill_analog / prefill_digital,
        "decode_analog_projection_to_digital_projection": decode_analog_projection / decode_digital_projection,
        "decode_cache_to_projection": decode_cache_energy / decode_analog_projection,
        "decode_total_analog_to_digital_projection_only": (decode_analog_projection + decode_cache_energy) / decode_digital_projection,
    }


def print_sweep() -> None:
    shape = ModelShape()
    cost = CostModel()
    print("prefill_decode_energy_estimate")
    print(f"hidden,{shape.hidden}")
    print(f"layers,{shape.layers}")
    print("relative units,not process calibrated")
    print()
    print("prompt,generated,batch,adc_bits,dac_bits,kv_cache_mb_end,prefill_analog_to_digital,decode_analog_projection_to_digital_projection,decode_cache_to_projection,decode_total_analog_to_digital_projection_only")
    for bits in [4, 6, 8]:
        tile = TileShape(adc_bits=bits, dac_bits=bits)
        for prompt, generated, batch in [
            (512, 128, 1),
            (2048, 128, 1),
            (2048, 2048, 1),
            (2048, 128, 8),
        ]:
            row = phase_report(prompt, generated, batch, shape, tile, cost)
            print(
                f"{prompt},{generated},{batch},{bits},{bits},"
                f"{row['kv_cache_mb_end']:.2f},"
                f"{row['prefill_analog_to_digital']:.4f},"
                f"{row['decode_analog_projection_to_digital_projection']:.4f},"
                f"{row['decode_cache_to_projection']:.4f},"
                f"{row['decode_total_analog_to_digital_projection_only']:.4f}"
            )


if __name__ == "__main__":
    print_sweep()
