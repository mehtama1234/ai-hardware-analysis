#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = SIM_EVIDENCE / "aihwkit-residual-diagnostic.json"
OUT_MD = SIM_EVIDENCE / "aihwkit-residual-diagnostic.md"

PAYLOADS = [
    ("small_fixture", SIM_EVIDENCE / "aihwkit-analog-error-simulation.json"),
    ("workload_shape", SIM_EVIDENCE / "aihwkit-workload-analog-error-simulation.json"),
    ("tensor_shape", SIM_EVIDENCE / "aihwkit-tensor-shape-analog-error-simulation.json"),
    ("trained_weight_tiny_mlp", SIM_EVIDENCE / "aihwkit-trained-weight-analog-error-simulation.json"),
    ("projection_stack", SIM_EVIDENCE / "aihwkit-projection-stack-analog-error-simulation.json"),
    ("transformer_mlp_block", SIM_EVIDENCE / "aihwkit-transformer-mlp-block-analog-error-simulation.json"),
    ("calibrated_transformer_mlp_block", SIM_EVIDENCE / "aihwkit-calibrated-transformer-mlp-block-analog-error-simulation.json"),
    ("calibrated_deep_transformer_mlp_stack", SIM_EVIDENCE / "aihwkit-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json"),
    ("attention_block", SIM_EVIDENCE / "aihwkit-attention-block-analog-error-simulation.json"),
    ("calibrated_attention_block", SIM_EVIDENCE / "aihwkit-calibrated-attention-block-analog-error-simulation.json"),
]


def load_payload(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_rows(payload: dict[str, object], fixture: str) -> list[dict[str, object]]:
    error_model = payload.get("error_model") if isinstance(payload.get("error_model"), dict) else {}
    rows = error_model.get("per_candidate_results") if isinstance(error_model.get("per_candidate_results"), list) else []
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        residual = row.get("simulator_residual_relative")
        if not isinstance(residual, (int, float)):
            continue
        out.append(
            {
                "fixture": fixture,
                "candidate_id": row.get("candidate_id", "unknown"),
                "weight_shape": row.get("weight_shape_in_out") or row.get("declared_shape") or "unknown",
                "residual_relative": float(residual),
                "over_threshold": float(residual) > 0.15,
            }
        )
    return out


def payload_summary(fixture: str, path: Path, payload: dict[str, object]) -> dict[str, object]:
    if not payload:
        return {
            "fixture": fixture,
            "path": str(path.relative_to(ROOT)),
            "status": "missing",
            "pass": False,
            "estimated_drop": None,
            "candidate_count": 0,
            "over_threshold_candidates": 0,
            "worst_candidate": None,
        }
    accuracy = payload.get("accuracy_impact") if isinstance(payload.get("accuracy_impact"), dict) else {}
    rows = candidate_rows(payload, fixture)
    worst = max(rows, key=lambda row: row["residual_relative"]) if rows else None
    return {
        "fixture": fixture,
        "path": str(path.relative_to(ROOT)),
        "status": "pass" if accuracy.get("pass") is True else "threshold_fail",
        "pass": accuracy.get("pass") is True,
        "estimated_drop": accuracy.get("estimated_drop"),
        "metric": accuracy.get("metric"),
        "candidate_count": len(rows),
        "over_threshold_candidates": sum(1 for row in rows if row["over_threshold"]),
        "worst_candidate": worst,
        "claim_boundary": accuracy.get("boundary"),
    }


def diagnosis(summary: dict[str, object]) -> str:
    if summary["status"] == "missing":
        return "payload is missing"
    if summary["pass"]:
        return "inside the current positive residual boundary"
    count = int(summary["over_threshold_candidates"])
    if count == 0:
        return "final or aggregate residual failed even though no individual candidate exceeded the threshold"
    return f"{count} candidate rows exceed the positive residual boundary"


def write_markdown(summaries: list[dict[str, object]], worst_rows: list[dict[str, object]]) -> None:
    passing = sum(1 for item in summaries if item["pass"])
    failing = sum(1 for item in summaries if item["status"] == "threshold_fail")
    lines = [
        "# AIHWKIT Residual Diagnostic",
        "",
        "This report explains why AIHWKIT is run evidence but not broad positive simulator evidence yet.",
        "",
        f"- payloads checked: `{len(summaries)}`",
        f"- passing payloads: `{passing}`",
        f"- threshold-fail payloads: `{failing}`",
        "",
        "## Fixture Summary",
        "",
        "| fixture | status | estimated drop | candidates | over threshold | diagnosis |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in summaries:
        drop = item["estimated_drop"]
        drop_text = "missing" if drop is None else f"{float(drop):.6f}"
        lines.append(
            f"| {item['fixture']} | {item['status']} | {drop_text} | {item['candidate_count']} | "
            f"{item['over_threshold_candidates']} | {diagnosis(item)} |"
        )
    lines.extend(
        [
            "",
            "## Worst Candidate Rows",
            "",
            "| fixture | candidate | shape | residual |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in worst_rows[:12]:
        lines.append(
            f"| {row['fixture']} | {row['candidate_id']} | {row['weight_shape']} | {row['residual_relative']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "AIHWKIT is not failing because the importer is too strict. It is failing because several fixed-weight MatMul rows produce output vectors that move too far from the digital reference under the current AIHWKIT mapping.",
            "",
            "The object to repair is the mapping from a signed weight matrix and input vector into the analog layer. Scaling, conductance range, noise settings, calibration, and output correction all change that mapping. The guarded threshold should not be changed to make the result look better.",
            "",
            "A useful next experiment changes one mapping assumption, reruns the same held-out payloads, and checks whether the worst candidate rows move under the threshold without weakening the evidence rule.",
            "",
            "## Refused Claim",
            "",
            "This diagnostic does not turn threshold-fail AIHWKIT payloads into positive analog placement evidence. It does not prove calibrated silicon, measured board runtime, measured power, macro layout, or production readiness.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    summaries = []
    rows = []
    for fixture, path in PAYLOADS:
        payload = load_payload(path)
        summaries.append(payload_summary(fixture, path, payload))
        rows.extend(candidate_rows(payload, fixture))
    worst_rows = sorted(rows, key=lambda row: row["residual_relative"], reverse=True)
    payload = {
        "result_type": "aihwkit_residual_diagnostic",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "threshold": 0.15,
        "summaries": summaries,
        "worst_candidate_rows": worst_rows[:20],
        "summary": {
            "payloads": len(summaries),
            "passing_payloads": sum(1 for item in summaries if item["pass"]),
            "threshold_fail_payloads": sum(1 for item in summaries if item["status"] == "threshold_fail"),
            "worst_residual_relative": worst_rows[0]["residual_relative"] if worst_rows else None,
            "worst_candidate": worst_rows[0]["candidate_id"] if worst_rows else None,
            "worst_fixture": worst_rows[0]["fixture"] if worst_rows else None,
        },
        "claim_boundary": {
            "allowed": "ranks AIHWKIT residual failures so mapping changes can be targeted",
            "not_allowed": "does not upgrade threshold-fail AIHWKIT payloads into positive analog evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summaries, worst_rows)
    print("aihwkit_residual_diagnostic")
    print(f"payloads,{payload['summary']['payloads']}")
    print(f"passing,{payload['summary']['passing_payloads']}")
    print(f"threshold_fail,{payload['summary']['threshold_fail_payloads']}")
    print(f"worst,{payload['summary']['worst_fixture']},{payload['summary']['worst_candidate']},{payload['summary']['worst_residual_relative']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
