#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelShape:
    hidden: int
    heads: int
    layers: int
    sequence: int
    batch: int
    mlp_ratio: int = 4
    bytes_per_value: int = 2


@dataclass(frozen=True)
class TileShape:
    rows: int
    cols: int
    adc_bits: int
    dac_bits: int


def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def projection_tiles(input_dim: int, output_dim: int, tile: TileShape) -> tuple[int, int, int]:
    row_tiles = ceil_div(input_dim, tile.rows)
    col_tiles = ceil_div(output_dim, tile.cols)
    return row_tiles, col_tiles, row_tiles * col_tiles


def projection_report(name: str, input_dim: int, output_dim: int, tokens: int, tile: TileShape, bytes_per_value: int) -> dict[str, float | int | str]:
    row_tiles, col_tiles, total_tiles = projection_tiles(input_dim, output_dim, tile)
    weight_bytes = input_dim * output_dim * bytes_per_value
    activation_read_bytes = tokens * input_dim * bytes_per_value
    output_write_bytes = tokens * output_dim * bytes_per_value
    adc_conversions = tokens * output_dim * row_tiles
    dac_conversions = tokens * input_dim * col_tiles
    digital_accumulations = tokens * output_dim * max(0, row_tiles - 1)
    return {
        "name": name,
        "input_dim": input_dim,
        "output_dim": output_dim,
        "row_tiles": row_tiles,
        "col_tiles": col_tiles,
        "total_tiles": total_tiles,
        "weight_mb": weight_bytes / 1_000_000,
        "activation_mb": activation_read_bytes / 1_000_000,
        "output_mb": output_write_bytes / 1_000_000,
        "adc_m": adc_conversions / 1_000_000,
        "dac_m": dac_conversions / 1_000_000,
        "digital_accum_m": digital_accumulations / 1_000_000,
    }


def kv_cache_mb(shape: ModelShape, generated_tokens: int) -> float:
    # K and V for every layer and every generated token.
    values = 2 * shape.layers * shape.batch * generated_tokens * shape.hidden
    return values * shape.bytes_per_value / 1_000_000


def print_projection_table(shape: ModelShape, tile: TileShape) -> None:
    tokens = shape.batch * shape.sequence
    reports = [
        projection_report("qkv_projection", shape.hidden, 3 * shape.hidden, tokens, tile, shape.bytes_per_value),
        projection_report("attention_output", shape.hidden, shape.hidden, tokens, tile, shape.bytes_per_value),
        projection_report("mlp_up", shape.hidden, shape.mlp_ratio * shape.hidden, tokens, tile, shape.bytes_per_value),
        projection_report("mlp_down", shape.mlp_ratio * shape.hidden, shape.hidden, tokens, tile, shape.bytes_per_value),
    ]
    print("projection,input_dim,output_dim,row_tiles,col_tiles,total_tiles,weight_mb,activation_mb,output_mb,adc_m,dac_m,digital_accum_m")
    for row in reports:
        print(
            f"{row['name']},{row['input_dim']},{row['output_dim']},"
            f"{row['row_tiles']},{row['col_tiles']},{row['total_tiles']},"
            f"{row['weight_mb']:.2f},{row['activation_mb']:.2f},{row['output_mb']:.2f},"
            f"{row['adc_m']:.2f},{row['dac_m']:.2f},{row['digital_accum_m']:.2f}"
        )


def print_sequence_sweep(shape: ModelShape) -> None:
    print("\nkv_cache_growth")
    print("generated_tokens,kv_cache_mb")
    for generated in [128, 512, 2048, 8192, 32768]:
        print(f"{generated},{kv_cache_mb(shape, generated):.2f}")


def print_tile_sweep(shape: ModelShape) -> None:
    print("\ntile_size_sweep_for_mlp_up")
    print("tile_rows,tile_cols,total_tiles,adc_m,dac_m,digital_accum_m")
    tokens = shape.batch * shape.sequence
    for size in [64, 128, 256, 512]:
        tile = TileShape(rows=size, cols=size, adc_bits=6, dac_bits=6)
        row = projection_report("mlp_up", shape.hidden, shape.mlp_ratio * shape.hidden, tokens, tile, shape.bytes_per_value)
        print(f"{size},{size},{row['total_tiles']},{row['adc_m']:.2f},{row['dac_m']:.2f},{row['digital_accum_m']:.2f}")


def main() -> None:
    shape = ModelShape(hidden=4096, heads=32, layers=32, sequence=2048, batch=1)
    tile = TileShape(rows=128, cols=128, adc_bits=6, dac_bits=6)
    print("model_shape")
    print(f"hidden,{shape.hidden}")
    print(f"layers,{shape.layers}")
    print(f"sequence,{shape.sequence}")
    print(f"batch,{shape.batch}")
    print(f"tile,{tile.rows}x{tile.cols}")
    print()
    print_projection_table(shape, tile)
    print_sequence_sweep(shape)
    print_tile_sweep(shape)


if __name__ == "__main__":
    main()
