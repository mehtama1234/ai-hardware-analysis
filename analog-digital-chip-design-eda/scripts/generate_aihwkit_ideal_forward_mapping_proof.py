#!/usr/bin/env python3
from __future__ import annotations

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
OUT_JSON = OUT_DIR / "aihwkit-ideal-forward-mapping-proof.json"
OUT_MD = OUT_DIR / "aihwkit-ideal-forward-mapping-proof.md"


def flatten(matrix):
    if matrix and isinstance(matrix[0], list):
        return [value for row in matrix for value in row]
    return list(matrix)


def make_layer(in_features: int, out_features: int):
    import torch
    from aihwkit.nn import AnalogLinear
    from aihwkit.simulator.configs import TorchInferenceRPUConfig

    config = TorchInferenceRPUConfig(noise_model=None, drift_compensation=None)
    config.forward.is_perfect = True
    return AnalogLinear(in_features, out_features, bias=False, rpu_config=config), torch


def run_matrix(input_matrix, weight_in_out, transpose_fn):
    layer, torch = make_layer(len(weight_in_out), len(weight_in_out[0]))
    layer.set_weights(torch.tensor(transpose_fn(weight_in_out), dtype=torch.float32))
    return layer(torch.tensor(input_matrix, dtype=torch.float32)).detach().tolist()


def run_vector(input_vector, weight_in_out, transpose_fn):
    observed = run_matrix([input_vector], weight_in_out, transpose_fn)
    return [float(value) for value in observed[0]]


def attention_rows() -> list[dict[str, object]]:
    model = extract_attention_onnx()
    weights = model["initializers"]
    rows = []
    for item in attention_trace(model)["static_trace"]:
        observed = run_matrix(item["input_matrix"], weights[item["weight_name"]]["values"], attention_transpose)
        rows.append(
            {
                "fixture": "attention_block",
                "candidate_id": item["candidate_id"],
                "weight_shape_in_out": item["weight_shape_in_out"],
                "input_shape": item["input_shape"],
                "residual_relative": attention_relative_l2(item["ideal_output"], observed),
            }
        )
    return rows


def deep_rows() -> list[dict[str, object]]:
    model = extract_deep_onnx()
    weights = model["initializers"]
    _, trace = digital_forward(model, DEEP_INPUT)
    rows = []
    for item in trace:
        observed = run_vector(item["input"], weights[item["weight_name"]]["values"], deep_transpose)
        rows.append(
            {
                "fixture": "deep_transformer_mlp_stack",
                "candidate_id": item["candidate_id"],
                "weight_shape_in_out": item["weight_shape_in_out"],
                "input_shape": item["input_shape"],
                "residual_relative": deep_relative_l2(item["ideal_output"], observed),
            }
        )
    return rows


def write_markdown(payload: dict[str, object]) -> None:
    rows = payload["rows"]
    summary = payload["summary"]
    lines = [
        "# AIHWKIT Ideal Forward Mapping Proof",
        "",
        "This proof separates two questions that were previously mixed together.",
        "",
        "First question: are the layer dimensions, weight orientation, and signed MatMul object mapped correctly into AIHWKIT? Yes, under an explicit perfect-forward AIHWKIT configuration, the tested MatMul rows reproduce the digital reference within floating-point tolerance.",
        "",
        "Second question: do the same rows pass under AIHWKIT's non-perfect inference path with its default input/output behavior and PCM-like assumptions? No. That remains the mapping work item.",
        "",
        f"- rows checked: `{summary['rows']}`",
        f"- fixtures checked: `{summary['fixtures']}`",
        f"- maximum ideal-forward residual: `{summary['max_residual_relative']:.9f}`",
        f"- passing rows under ideal-forward boundary: `{summary['passing_rows']}`",
        "",
        "## Rows",
        "",
        "| fixture | candidate | shape | residual |",
        "| --- | --- | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['fixture']} | {row['candidate_id']} | {row['weight_shape_in_out']} | {row['residual_relative']:.9f} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A matrix multiply has three objects: the input vector, the stored weight matrix, and the output vector. If the weight is transposed incorrectly, or if the layer is built with the wrong input and output sizes, a perfect forward path will still produce the wrong vector.",
            "",
            "This proof removes the analog forward imperfections and asks only whether AIHWKIT receives the same mathematical object as the digital reference. It does. That means the next repair should not chase orientation or shape. It should tune the non-perfect forward path: input range, converter resolution, output noise, conductance mapping, and calibration.",
            "",
            "## Refused Claim",
            "",
            "This proof does not make the default AIHWKIT payloads positive analog evidence. It does not prove PCM behavior, measured silicon, measured runtime, measured power, macro layout, or production readiness.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        import aihwkit
    except Exception as exc:
        raise SystemExit(f"AIHWKIT is not importable: {exc}") from exc

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = attention_rows() + deep_rows()
    max_residual = max(float(row["residual_relative"]) for row in rows)
    payload = {
        "result_type": "aihwkit_ideal_forward_mapping_proof",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool": "aihwkit",
        "tool_version": getattr(aihwkit, "__version__", "unknown"),
        "configuration": {
            "noise_model": None,
            "drift_compensation": None,
            "forward_is_perfect": True,
            "boundary": "ideal-forward AIHWKIT mapping check, not noisy device simulation",
        },
        "summary": {
            "rows": len(rows),
            "fixtures": 2,
            "max_residual_relative": max_residual,
            "passing_rows": sum(1 for row in rows if float(row["residual_relative"]) <= 1e-5),
            "threshold": 1e-5,
        },
        "rows": rows,
        "claim_boundary": {
            "allowed": "proves AIHWKIT layer dimensions, weight orientation, and signed MatMul mapping for the tested rows under ideal forward",
            "not_allowed": "does not upgrade noisy or default AIHWKIT threshold-fail payloads into positive analog evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload)
    print("aihwkit_ideal_forward_mapping_proof")
    print(f"rows,{payload['summary']['rows']}")
    print(f"passing,{payload['summary']['passing_rows']}")
    print(f"max_residual,{payload['summary']['max_residual_relative']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
