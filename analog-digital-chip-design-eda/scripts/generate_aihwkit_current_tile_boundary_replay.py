#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_attention_block_aimc_simulator_payloads import (  # noqa: E402
    attention_trace,
    extract_onnx as extract_attention_onnx,
    relative_l2 as attention_relative_l2,
    transpose as attention_transpose,
)
from run_calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads import (  # noqa: E402
    INPUT as DEEP_INPUT,
    digital_forward,
    extract_onnx as extract_deep_onnx,
    relative_l2 as deep_relative_l2,
    transpose as deep_transpose,
)


OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
TILE_CSV = LAB / "tile-operating-point.csv"
OUT_JSON = OUT_DIR / "aihwkit-current-tile-boundary-replay.json"
OUT_MD = OUT_DIR / "aihwkit-current-tile-boundary-replay.md"
POSITIVE_THRESHOLD = 0.15


def load_tile() -> dict[str, str]:
    with TILE_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"empty tile operating point: {TILE_CSV}")
    return rows[0]


def configure_tile_boundary(config, dac_bits: int, adc_bits: int) -> None:
    # AIHWKIT uses negative resolution for ideal, so positive values keep finite converter bins.
    config.forward.out_noise = 0.0
    config.forward.inp_res = 1.0 / float((2**dac_bits) - 1)
    config.forward.out_res = 1.0 / float((2**adc_bits) - 1)


def make_layer(in_features: int, out_features: int, dac_bits: int, adc_bits: int):
    import torch
    from aihwkit.nn import AnalogLinear
    from aihwkit.simulator.configs import TorchInferenceRPUConfig

    config = TorchInferenceRPUConfig(noise_model=None, drift_compensation=None)
    configure_tile_boundary(config, dac_bits, adc_bits)
    return AnalogLinear(in_features, out_features, bias=False, rpu_config=config), torch


def run_matrix(input_matrix, weight_in_out, transpose_fn, dac_bits: int, adc_bits: int):
    layer, torch = make_layer(len(weight_in_out), len(weight_in_out[0]), dac_bits, adc_bits)
    layer.set_weights(torch.tensor(transpose_fn(weight_in_out), dtype=torch.float32))
    return layer(torch.tensor(input_matrix, dtype=torch.float32)).detach().tolist()


def run_vector(input_vector, weight_in_out, transpose_fn, dac_bits: int, adc_bits: int):
    observed = run_matrix([input_vector], weight_in_out, transpose_fn, dac_bits, adc_bits)
    return [float(value) for value in observed[0]]


def attention_rows(dac_bits: int, adc_bits: int) -> list[dict[str, object]]:
    model = extract_attention_onnx()
    weights = model["initializers"]
    rows = []
    for item in attention_trace(model)["static_trace"]:
        observed = run_matrix(item["input_matrix"], weights[item["weight_name"]]["values"], attention_transpose, dac_bits, adc_bits)
        residual = attention_relative_l2(item["ideal_output"], observed)
        rows.append(
            {
                "fixture": "attention_block",
                "candidate_id": item["candidate_id"],
                "weight_shape_in_out": item["weight_shape_in_out"],
                "residual_relative": residual,
                "passes_positive_boundary": residual <= POSITIVE_THRESHOLD,
            }
        )
    return rows


def deep_rows(dac_bits: int, adc_bits: int) -> list[dict[str, object]]:
    model = extract_deep_onnx()
    weights = model["initializers"]
    _, trace = digital_forward(model, DEEP_INPUT)
    rows = []
    for item in trace:
        observed = run_vector(item["input"], weights[item["weight_name"]]["values"], deep_transpose, dac_bits, adc_bits)
        residual = deep_relative_l2(item["ideal_output"], observed)
        rows.append(
            {
                "fixture": "deep_transformer_mlp_stack",
                "candidate_id": item["candidate_id"],
                "weight_shape_in_out": item["weight_shape_in_out"],
                "residual_relative": residual,
                "passes_positive_boundary": residual <= POSITIVE_THRESHOLD,
            }
        )
    return rows


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    tile = payload["tile_boundary"]
    lines = [
        "# AIHWKIT Current Tile Boundary Replay",
        "",
        "This replay runs AIHWKIT with the current local tile converter boundary instead of a stronger sweep setting.",
        "",
        f"- tile DAC bits: `{tile['dac_bits']}`",
        f"- tile ADC bits: `{tile['adc_bits']}`",
        f"- rows checked: `{summary['rows']}`",
        f"- passing rows: `{summary['passing_rows']}`",
        f"- failing rows: `{summary['failing_rows']}`",
        f"- max residual: `{summary['max_residual_relative']:.6f}`",
        f"- worst row: `{summary['worst_fixture']}/{summary['worst_candidate']}`",
        "",
        "## Rows",
        "",
        "| fixture | candidate | shape | residual | pass |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['fixture']} | {row['candidate_id']} | {row['weight_shape_in_out']} | {row['residual_relative']:.6f} | {row['passes_positive_boundary']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A tile boundary is a promise about finite decisions. A 4-bit DAC has only sixteen input levels. A 6-bit ADC has only sixty-four output levels. If the model row needs finer distinctions than those bins preserve, the analog result moves away from the digital reference.",
            "",
            "This replay keeps the strict residual threshold and asks what the current tile boundary does. It is the honest counterpart to the stronger forward-setting sweep.",
            "",
            "## Refused Claim",
            "",
            "This replay does not prove measured silicon, measured board runtime, measured power, macro layout, PCM device accuracy, or production readiness. It does not turn failing rows into placement evidence.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        import aihwkit
    except Exception as exc:
        raise SystemExit(f"AIHWKIT is not importable: {exc}") from exc

    tile = load_tile()
    dac_bits = int(float(tile["dac_bits"]))
    adc_bits = int(float(tile["adc_bits"]))
    rows = attention_rows(dac_bits, adc_bits) + deep_rows(dac_bits, adc_bits)
    worst = max(rows, key=lambda row: float(row["residual_relative"]))
    payload = {
        "result_type": "aihwkit_current_tile_boundary_replay",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool": "aihwkit",
        "tool_version": getattr(aihwkit, "__version__", "unknown"),
        "positive_threshold": POSITIVE_THRESHOLD,
        "source_artifacts": {
            "tile_operating_point": str(TILE_CSV.relative_to(ROOT)),
        },
        "tile_boundary": {
            "dac_bits": dac_bits,
            "adc_bits": adc_bits,
            "inp_res": 1.0 / float((2**dac_bits) - 1),
            "out_res": 1.0 / float((2**adc_bits) - 1),
            "out_noise": 0.0,
            "boundary": "current local converter boundary with output noise held at zero to isolate finite converter bins",
        },
        "summary": {
            "rows": len(rows),
            "passing_rows": sum(1 for row in rows if row["passes_positive_boundary"]),
            "failing_rows": sum(1 for row in rows if not row["passes_positive_boundary"]),
            "max_residual_relative": worst["residual_relative"],
            "worst_fixture": worst["fixture"],
            "worst_candidate": worst["candidate_id"],
            "passes_all_rows": all(row["passes_positive_boundary"] for row in rows),
        },
        "rows": rows,
        "claim_boundary": {
            "allowed": "shows AIHWKIT residual under the current local 4-bit DAC and 6-bit ADC tile boundary",
            "not_allowed": "does not prove measured hardware or allow threshold-fail rows to support positive placement",
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload)
    print("aihwkit_current_tile_boundary_replay")
    print(f"tile_bits,{dac_bits},{adc_bits}")
    print(f"rows,{payload['summary']['rows']}")
    print(f"passing,{payload['summary']['passing_rows']}")
    print(f"failing,{payload['summary']['failing_rows']}")
    print(f"max_residual,{payload['summary']['max_residual_relative']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
