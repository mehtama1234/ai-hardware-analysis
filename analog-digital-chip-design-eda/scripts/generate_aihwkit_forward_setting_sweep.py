#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


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
OUT_JSON = OUT_DIR / "aihwkit-forward-setting-sweep.json"
OUT_MD = OUT_DIR / "aihwkit-forward-setting-sweep.md"
POSITIVE_THRESHOLD = 0.15


def base_config():
    from aihwkit.simulator.configs import TorchInferenceRPUConfig

    return TorchInferenceRPUConfig(noise_model=None, drift_compensation=None)


def make_layer(in_features: int, out_features: int, configure: Callable[[object], None]):
    import torch
    from aihwkit.nn import AnalogLinear

    config = base_config()
    configure(config)
    return AnalogLinear(in_features, out_features, bias=False, rpu_config=config), torch, config


def run_matrix(input_matrix, weight_in_out, transpose_fn, configure):
    layer, torch, _ = make_layer(len(weight_in_out), len(weight_in_out[0]), configure)
    layer.set_weights(torch.tensor(transpose_fn(weight_in_out), dtype=torch.float32))
    return layer(torch.tensor(input_matrix, dtype=torch.float32)).detach().tolist()


def run_vector(input_vector, weight_in_out, transpose_fn, configure):
    observed = run_matrix([input_vector], weight_in_out, transpose_fn, configure)
    return [float(value) for value in observed[0]]


def attention_cases() -> list[dict[str, object]]:
    model = extract_attention_onnx()
    weights = model["initializers"]
    cases = []
    for item in attention_trace(model)["static_trace"]:
        cases.append(
            {
                "fixture": "attention_block",
                "candidate_id": item["candidate_id"],
                "weight_shape_in_out": item["weight_shape_in_out"],
                "input": item["input_matrix"],
                "ideal": item["ideal_output"],
                "weight": weights[item["weight_name"]]["values"],
                "transpose": attention_transpose,
                "relative_l2": attention_relative_l2,
                "mode": "matrix",
            }
        )
    return cases


def deep_cases() -> list[dict[str, object]]:
    model = extract_deep_onnx()
    weights = model["initializers"]
    _, trace = digital_forward(model, DEEP_INPUT)
    cases = []
    for item in trace:
        cases.append(
            {
                "fixture": "deep_transformer_mlp_stack",
                "candidate_id": item["candidate_id"],
                "weight_shape_in_out": item["weight_shape_in_out"],
                "input": item["input"],
                "ideal": item["ideal_output"],
                "weight": weights[item["weight_name"]]["values"],
                "transpose": deep_transpose,
                "relative_l2": deep_relative_l2,
                "mode": "vector",
            }
        )
    return cases


def configure_default(config) -> None:
    return None


def configure_no_output_noise(config) -> None:
    config.forward.out_noise = 0.0


def configure_fine_resolution(config) -> None:
    config.forward.out_noise = 0.0
    config.forward.inp_res = 1.0 / 1024.0
    config.forward.out_res = 1.0 / 4096.0


def configure_fine_resolution_large_bounds(config) -> None:
    config.forward.out_noise = 0.0
    config.forward.inp_res = 1.0 / 4096.0
    config.forward.out_res = 1.0 / 16384.0
    config.forward.inp_bound = 10.0
    config.forward.out_bound = 100.0


def configure_ideal_resolution(config) -> None:
    config.forward.out_noise = 0.0
    config.forward.inp_res = -1.0
    config.forward.out_res = -1.0


CONFIGS = [
    {
        "id": "baseline_nonperfect_no_noise_model",
        "description": "AIHWKIT non-perfect forward path with noise_model=None and drift_compensation=None; leaves default input/output resolution and output noise.",
        "configure": configure_default,
    },
    {
        "id": "no_output_noise",
        "description": "Same non-perfect path, but output noise is set to zero.",
        "configure": configure_no_output_noise,
    },
    {
        "id": "fine_resolution_no_output_noise",
        "description": "Output noise is zero and input/output converter resolution is tightened.",
        "configure": configure_fine_resolution,
    },
    {
        "id": "fine_resolution_large_bounds",
        "description": "Output noise is zero, converter resolution is tightened, and input/output bounds are widened.",
        "configure": configure_fine_resolution_large_bounds,
    },
    {
        "id": "ideal_resolution_no_output_noise",
        "description": "Output noise is zero and input/output resolution limits are disabled while the forward path stays non-perfect.",
        "configure": configure_ideal_resolution,
    },
]


def evaluate_config(config_item: dict[str, object], cases: list[dict[str, object]]) -> dict[str, object]:
    configure = config_item["configure"]
    rows = []
    for case in cases:
        if case["mode"] == "matrix":
            observed = run_matrix(case["input"], case["weight"], case["transpose"], configure)
        else:
            observed = run_vector(case["input"], case["weight"], case["transpose"], configure)
        residual = case["relative_l2"](case["ideal"], observed)
        rows.append(
            {
                "fixture": case["fixture"],
                "candidate_id": case["candidate_id"],
                "weight_shape_in_out": case["weight_shape_in_out"],
                "residual_relative": residual,
                "passes_positive_boundary": residual <= POSITIVE_THRESHOLD,
            }
        )
    max_row = max(rows, key=lambda row: float(row["residual_relative"]))
    return {
        "id": config_item["id"],
        "description": config_item["description"],
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "passing_rows": sum(1 for row in rows if row["passes_positive_boundary"]),
            "failing_rows": sum(1 for row in rows if not row["passes_positive_boundary"]),
            "max_residual_relative": max_row["residual_relative"],
            "worst_fixture": max_row["fixture"],
            "worst_candidate": max_row["candidate_id"],
            "passes_all_rows": all(row["passes_positive_boundary"] for row in rows),
        },
    }


def write_markdown(payload: dict[str, object]) -> None:
    lines = [
        "# AIHWKIT Forward Setting Sweep",
        "",
        "This sweep asks which AIHWKIT non-perfect forward settings move the same MatMul rows across the positive residual boundary.",
        "",
        "It does not change the importer threshold. It changes only the simulator-side forward assumptions and records the result.",
        "",
        f"- rows checked per setting: `{payload['summary']['rows_per_setting']}`",
        f"- settings checked: `{payload['summary']['settings']}`",
        f"- best passing setting: `{payload['summary']['best_passing_setting']}`",
        f"- best max residual: `{payload['summary']['best_max_residual_relative']:.9f}`",
        "",
        "## Setting Summary",
        "",
        "| setting | passing rows | failing rows | max residual | worst row | pass all |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for setting in payload["settings"]:
        summary = setting["summary"]
        lines.append(
            f"| {setting['id']} | {summary['passing_rows']} | {summary['failing_rows']} | "
            f"{summary['max_residual_relative']:.6f} | {summary['worst_fixture']}/{summary['worst_candidate']} | {summary['passes_all_rows']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "The matrix object was already proven correct under ideal forward. This sweep keeps that object fixed and changes how the analog forward path limits the signal.",
            "",
            "Output noise is the largest visible lever in this local test. Removing it makes the attention rows pass, and tighter converter resolution makes both attention and deep-stack rows much closer to the digital reference. Disabling input/output resolution limits drives the residual near floating-point tolerance while still using the AIHWKIT analog layer path.",
            "",
            "That gives the next real design question: which of these simulator-side assumptions corresponds to a physically defensible analog tile? The answer cannot be claimed from this sweep alone; it needs a device, converter, and calibration story.",
            "",
            "## Refused Claim",
            "",
            "This sweep does not prove measured silicon, measured board runtime, measured power, PCM device accuracy, macro layout, or production readiness. It does not allow the importer threshold to be weakened.",
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
    cases = attention_cases() + deep_cases()
    settings = [evaluate_config(item, cases) for item in CONFIGS]
    passing = [item for item in settings if item["summary"]["passes_all_rows"]]
    best = min(settings, key=lambda item: float(item["summary"]["max_residual_relative"]))
    best_passing = min(passing, key=lambda item: float(item["summary"]["max_residual_relative"])) if passing else None
    payload = {
        "result_type": "aihwkit_forward_setting_sweep",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool": "aihwkit",
        "tool_version": getattr(aihwkit, "__version__", "unknown"),
        "positive_threshold": POSITIVE_THRESHOLD,
        "summary": {
            "rows_per_setting": len(cases),
            "settings": len(settings),
            "passing_settings": len(passing),
            "best_setting": best["id"],
            "best_max_residual_relative": best["summary"]["max_residual_relative"],
            "best_passing_setting": best_passing["id"] if best_passing else None,
        },
        "settings": settings,
        "claim_boundary": {
            "allowed": "compares bounded AIHWKIT forward settings on the same fixed MatMul rows",
            "not_allowed": "does not prove a physically accepted device model or measured hardware",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload)
    print("aihwkit_forward_setting_sweep")
    print(f"settings,{payload['summary']['settings']}")
    print(f"rows_per_setting,{payload['summary']['rows_per_setting']}")
    print(f"passing_settings,{payload['summary']['passing_settings']}")
    print(f"best_passing,{payload['summary']['best_passing_setting']}")
    print(f"best_max_residual,{payload['summary']['best_max_residual_relative']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
