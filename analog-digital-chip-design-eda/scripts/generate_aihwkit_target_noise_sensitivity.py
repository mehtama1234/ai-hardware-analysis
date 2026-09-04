#!/usr/bin/env python3
"""Run AIHWKIT target converter settings under explicit output-noise values."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_aihwkit_forward_setting_sweep import (  # noqa: E402
    POSITIVE_THRESHOLD,
    attention_cases,
    deep_cases,
    run_matrix,
    run_vector,
)


TARGET = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-upgrade-target.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-target-noise-sensitivity.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-target-noise-sensitivity.md"
NOISE_VALUES = [0.0, 0.001, 0.004, 0.012]


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def configure_target(config, input_bits: int, output_bits: int, out_noise: float) -> None:
    config.forward.inp_res = 1.0 / float(2**input_bits)
    config.forward.out_res = 1.0 / float(2**output_bits)
    config.forward.out_noise = out_noise


def evaluate_noise(input_bits: int, output_bits: int, out_noise: float, cases: list[dict[str, object]]) -> dict[str, object]:
    def configure(config) -> None:
        configure_target(config, input_bits, output_bits, out_noise)

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
    worst = max(rows, key=lambda row: float(row["residual_relative"]))
    return {
        "out_noise": out_noise,
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "passing_rows": sum(1 for row in rows if row["passes_positive_boundary"]),
            "failing_rows": sum(1 for row in rows if not row["passes_positive_boundary"]),
            "max_residual_relative": worst["residual_relative"],
            "worst_fixture": worst["fixture"],
            "worst_candidate": worst["candidate_id"],
            "passes_all_rows": all(row["passes_positive_boundary"] for row in rows),
        },
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    target = payload["target_boundary"]
    lines = [
        "# AIHWKIT Target Noise Sensitivity",
        "",
        "This replay keeps the 10-bit input and 12-bit output target fixed, then adds explicit output noise.",
        "",
        f"- target input bits: `{target['effective_input_bits']}`",
        f"- target output bits: `{target['effective_output_bits']}`",
        f"- rows per noise setting: `{summary['rows_per_noise_setting']}`",
        f"- noise settings: `{summary['noise_settings']}`",
        f"- all-pass noise settings: `{summary['all_pass_noise_settings']}`",
        f"- highest all-pass output noise: `{summary['highest_all_pass_out_noise']}`",
        f"- passes any nonzero noise: `{summary['passes_any_nonzero_noise']}`",
        "",
        "## Noise Summary",
        "",
        "| output noise | passing rows | failing rows | max residual | worst row | pass all |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in payload["noise_settings"]:
        item_summary = item["summary"]
        lines.append(
            f"| {item['out_noise']:.3f} | {item_summary['passing_rows']} | {item_summary['failing_rows']} | "
            f"{item_summary['max_residual_relative']:.6f} | {item_summary['worst_fixture']}/{item_summary['worst_candidate']} | {item_summary['passes_all_rows']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "The converter target solved one problem: it made the input and output bins fine enough. This replay asks a different question: how much output disturbance can the same target tolerate before the model-facing residual crosses the claim boundary again.",
            "",
            "Output noise matters because it is added after the analog sum. At that point the row voltages and conductance products have already collapsed into a column value. A small output disturbance can be harmless when the column value is far from a decision edge, and damaging when two states need to remain separated.",
            "",
            "A zero-noise pass is therefore not enough for hardware. A usable analog boundary needs a nonzero noise budget. If only the zero-noise case passes, the target is fragile. If small nonzero cases pass, the next circuit proof has a concrete noise allowance to try to meet.",
            "",
            "## Refused Claim",
            "",
            payload["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        import aihwkit
    except Exception as exc:
        raise SystemExit(f"AIHWKIT is not importable: {exc}") from exc

    target_payload = load_json(TARGET)
    target = target_payload.get("minimum_passing_aihwkit_target") if isinstance(target_payload.get("minimum_passing_aihwkit_target"), dict) else {}
    input_bits = int(target["effective_input_bits"])
    output_bits = int(target["effective_output_bits"])
    cases = attention_cases() + deep_cases()
    noise_settings = [evaluate_noise(input_bits, output_bits, value, cases) for value in NOISE_VALUES]
    all_pass = [item for item in noise_settings if item["summary"]["passes_all_rows"]]
    highest_all_pass = max((float(item["out_noise"]) for item in all_pass), default=None)
    payload = {
        "result_type": "aihwkit_target_noise_sensitivity",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool": "aihwkit",
        "tool_version": getattr(aihwkit, "__version__", "unknown"),
        "positive_threshold": POSITIVE_THRESHOLD,
        "source_artifacts": {
            "converter_upgrade_target": str(TARGET.relative_to(ROOT)),
        },
        "target_boundary": {
            "effective_input_bits": input_bits,
            "effective_output_bits": output_bits,
            "inp_res": 1.0 / float(2**input_bits),
            "out_res": 1.0 / float(2**output_bits),
        },
        "noise_settings": noise_settings,
        "summary": {
            "rows_per_noise_setting": len(cases),
            "noise_settings": len(noise_settings),
            "all_pass_noise_settings": len(all_pass),
            "highest_all_pass_out_noise": highest_all_pass,
            "passes_any_nonzero_noise": any(float(item["out_noise"]) > 0 and item["summary"]["passes_all_rows"] for item in all_pass),
        },
        "claim_boundary": {
            "allowed": "shows how the 10-bit input and 12-bit output AIHWKIT target behaves under explicit output-noise values",
            "not_allowed": "does not prove measured noise, circuit noise, calibrated silicon, board accuracy, or production readiness",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload)
    print("aihwkit_target_noise_sensitivity")
    print(f"target_bits,{input_bits},{output_bits}")
    print(f"noise_settings,{len(noise_settings)}")
    print(f"all_pass_noise_settings,{len(all_pass)}")
    print(f"highest_all_pass_out_noise,{highest_all_pass}")
    print(f"passes_any_nonzero_noise,{payload['summary']['passes_any_nonzero_noise']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
