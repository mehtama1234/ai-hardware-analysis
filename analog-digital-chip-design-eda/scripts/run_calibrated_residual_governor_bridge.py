#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
PY_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "python"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCE_SUMMARIES = [
    {
        "source_id": "attention_block",
        "target_object": "attention-block.onnx static projection weights",
        "path": OUT_DIR / "calibrated-attention-block-simulator-payload-run-summary.json",
    },
    {
        "source_id": "transformer_mlp_block",
        "target_object": "transformer-mlp-block.onnx fixed-weight MatMuls",
        "path": OUT_DIR / "calibrated-transformer-mlp-block-simulator-payload-run-summary.json",
    },
    {
        "source_id": "deep_transformer_mlp_stack",
        "target_object": "deep-transformer-mlp-stack.onnx 12 fixed-weight MatMuls",
        "path": OUT_DIR / "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json",
    },
]
JSON_OUT = OUT_DIR / "calibrated-residual-governor-bridge.json"
CSV_OUT = MEASURE / "calibrated-residual-governor-requests.csv"
MD_OUT = OUT_DIR / "calibrated-residual-governor-bridge.md"

sys.path.insert(0, str(PY_DIR))
from error_budget_governor_trace import govern  # noqa: E402


def q8(value: float, scale: float = 255.0) -> int:
    return max(0, min(255, round(value * scale)))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def result_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = summary.get("results")
    if not isinstance(rows, list):
        raise ValueError("calibrated simulator summary has no results list")
    return [row for row in rows if isinstance(row, dict)]


def payload_for(result: dict[str, object]) -> dict[str, object] | None:
    payload = result.get("payload")
    if not isinstance(payload, str):
        return None
    path = ROOT / payload
    if not path.exists():
        return None
    return load_json(path)


def bridge_row(source: dict[str, object], result: dict[str, object]) -> dict[str, object]:
    source_id = str(source["source_id"])
    target_object = str(source["target_object"])
    tool = str(result.get("tool", "unknown"))
    status = str(result.get("status", "unknown"))
    payload = payload_for(result)
    accepted = False
    residual = None
    residual_q8 = 255
    candidate_count = 0
    calibration_profile = "missing"
    reason = "missing_payload"

    if payload:
        accuracy = payload.get("accuracy_impact") if isinstance(payload.get("accuracy_impact"), dict) else {}
        error_model = payload.get("error_model") if isinstance(payload.get("error_model"), dict) else {}
        array = error_model.get("array_assumptions") if isinstance(error_model.get("array_assumptions"), dict) else {}
        candidates = array.get("candidate_ids")
        candidate_count = len(candidates) if isinstance(candidates, list) else 0
        calibration_profile = str(payload.get("calibration_profile", "missing"))
        residual = float(error_model.get("final_residual_relative", accuracy.get("estimated_drop", 1.0)))
        residual_q8 = q8(residual)
        accepted = accuracy.get("pass") is True and status == "wrote_payload"
        reason = "accepted_calibrated_payload" if accepted else "payload_not_ready_for_positive_claim"

    sensitivity_q8 = 176 if accepted else 224
    analog_candidate = 1 if accepted else 0
    decision, action, governor_reason, next_error = govern(
        sample_valid=1,
        analog_candidate=analog_candidate,
        residual_q8=residual_q8,
        drift_age=1 if accepted else 4,
        sensitivity_q8=sensitivity_q8,
        cumulative_error_q8=0,
    )
    return {
        "source_id": source_id,
        "target_object": target_object,
        "tool": tool,
        "payload_status": status,
        "calibration_profile": calibration_profile,
        "candidate_count": candidate_count,
        "accepted_as_positive_evidence": accepted,
        "residual_relative": residual,
        "residual_q8": residual_q8,
        "sensitivity_q8": sensitivity_q8,
        "analog_candidate": analog_candidate,
        "governor_decision": decision,
        "governor_action": action,
        "governor_reason": governor_reason,
        "next_cumulative_error_q8": next_error,
        "bridge_reason": reason,
    }


def write_csv(rows: list[dict[str, object]]) -> None:
    MEASURE.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "tool",
        "source_id",
        "target_object",
        "payload_status",
        "calibration_profile",
        "candidate_count",
        "accepted_as_positive_evidence",
        "residual_relative",
        "residual_q8",
        "sensitivity_q8",
        "analog_candidate",
        "governor_decision",
        "governor_action",
        "governor_reason",
        "next_cumulative_error_q8",
        "bridge_reason",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Calibrated Residual Governor Bridge",
        "",
        "This report connects calibrated simulator evidence to the digital governor.",
        "",
        "The object is not the whole transformer. The object is each calibrated fixed-weight subgraph that has a strict simulator payload. Today that means attention-block static projections, one-block transformer-MLP fixed-weight MatMuls, and a deeper three-block transformer-MLP stack. The question is whether each held-out residual is low enough to become a hardware-control request.",
        "",
        "## Evidence Rule",
        "",
        "A simulator payload must pass two checks before it can request analog service:",
        "",
        "1. The payload status must be `wrote_payload`.",
        "2. `accuracy_impact.pass` must be true in the strict payload.",
        "",
        "If either check fails, the row is kept as evidence that the tool ran, but it is not allowed to become an analog candidate.",
        "",
        "## Governor Rows",
        "",
        "| source | tool | accepted | residual | residual q8 | candidate | decision | action | reason |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        residual = row["residual_relative"]
        residual_text = "missing" if residual is None else f"{float(residual):.6g}"
        lines.append(
            f"| {row['source_id']} | {row['tool']} | {int(bool(row['accepted_as_positive_evidence']))} | "
            f"{residual_text} | {row['residual_q8']} | {row['analog_candidate']} | "
            f"{row['governor_decision']} | {row['governor_action']} | {row['governor_reason']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A calibrated simulator result is still not hardware. It is a bounded claim about one software replay. The useful step is to make that bound visible to the controller instead of hiding it in prose.",
            "",
            "The bridge turns residual into `residual_q8`, carries a sensitivity field, and asks the same governor used by the other lab traces. CrossSim becomes an analog candidate for the calibrated attention, one-block MLP, and deep MLP-stack fixtures because its held-out residual passes the strict payload check. AIHWKIT does not become a candidate because it ran but exceeded the local threshold.",
            "",
            "This is the clean control rule: running a simulator is not enough. Low residual on a held-out calibrated replay can ask for analog service. High residual can only ask for review or fallback.",
            "",
            "## Refused Claim",
            "",
            "This does not prove silicon calibration, board power, board latency, analog softmax, pretrained model accuracy, physical signoff, or tapeout readiness.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = []
    sources = []
    for source in SOURCE_SUMMARIES:
        summary = load_json(source["path"])
        source_rows = [bridge_row(source, result) for result in result_rows(summary)]
        rows.extend(source_rows)
        sources.append({
            "source_id": source["source_id"],
            "target_object": source["target_object"],
            "source_summary": str(source["path"].relative_to(ROOT)),
            "rows": len(source_rows),
        })
    if not rows:
        raise SystemExit("no calibrated simulator rows found")
    if not any(row["accepted_as_positive_evidence"] for row in rows):
        raise SystemExit("no calibrated simulator payload is accepted as positive evidence")
    if not any(row["governor_decision"] == 1 for row in rows):
        raise SystemExit("no calibrated simulator payload can request analog service")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(
        json.dumps(
            {
                "result_type": "calibrated_residual_governor_bridge",
                "source_summaries": sources,
                "rows": rows,
                "claim_boundary": {
                    "allowed": "calibrated simulator residuals are converted into governor fields for attention-block static projections, transformer-MLP fixed-weight MatMuls, and a deeper transformer-MLP stack",
                    "not_allowed": "does not prove silicon, board measurements, analog dynamic attention, pretrained accuracy, signoff, or tapeout readiness",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_csv(rows)
    write_markdown(rows)
    print("calibrated_residual_governor_bridge")
    print(f"rows,{len(rows)}")
    print(f"accepted,{sum(1 for row in rows if row['accepted_as_positive_evidence'])}")
    print(f"analog_decisions,{sum(1 for row in rows if row['governor_decision'] == 1)}")
    print(f"json,{JSON_OUT}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
