#!/usr/bin/env python3
"""Build a conservative release manifest from an agentic closure summary."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--human-signoff", type=Path, help="optional authenticated human signoff receipt")
    args = parser.parse_args()
    closure_path = args.closure_summary.resolve()
    try:
        closure = json.loads(closure_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read closure summary: {error}", file=sys.stderr)
        return 2
    physical = closure.get("physical_handoff") if isinstance(closure.get("physical_handoff"), dict) else {}
    approval = closure.get("approval") if isinstance(closure.get("approval"), dict) else {}
    fixture_approval = approval.get("reviewer") in {"test-fixture-only", "fixture", "test-fixture"}
    digital_status = "proven" if closure.get("status") == "passed" else "review_required"
    physical_status = "proven" if physical.get("status") == "passed" and physical.get("same_run") is True else "unsupported"
    benchmark = {}
    benchmark_path = Path(str(closure.get("benchmark", "")))
    if not benchmark_path.is_absolute():
        benchmark_path = closure_path.parent / benchmark_path
    if benchmark_path.is_file():
        try:
            benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            benchmark = {}
    metrics = benchmark.get("metrics", {}) if isinstance(benchmark.get("metrics"), dict) else {}
    latency_metric = metrics.get("batch_latency")
    if not isinstance(latency_metric, dict):
        legacy_latency = metrics.get("model_latency_summary", {}).get("local-batch-command", {}) if isinstance(metrics.get("model_latency_summary"), dict) else {}
        latency_metric = {**legacy_latency, "basis": "legacy report summary; repeated batch wall-clock value, not per-case latency"}
    primary_review = closure_path.parent / "repair-review" / "repair-review.json"
    held_out_review = closure_path.parent / "held-out-timeout-repair" / "repair-review.json"
    primary = json.loads(primary_review.read_text(encoding="utf-8")) if primary_review.is_file() else {}
    held_out = json.loads(held_out_review.read_text(encoding="utf-8")) if held_out_review.is_file() else {}
    repair_attempts = [primary, held_out]
    repair_successes = sum(item.get("retest", {}).get("status") == "passed" for item in repair_attempts)
    aimc_path = ROOT / "evidence" / "aimc-hardware-lab" / "llm-rtl2gds-handoff-latest.json"
    aimc_boundary = {
        "status": "traceable" if aimc_path.is_file() else "unavailable",
        "path": "evidence/aimc-hardware-lab/llm-rtl2gds-handoff-latest.json",
        "sha256": digest(aimc_path) if aimc_path.is_file() else None,
        "qualification_status": None,
        "same_design_run": None,
        "analog_authorized": False,
        "claim_boundary": "Traceability link only; the AIMC handoff is not analog qualification or measured-hardware evidence.",
    }
    if aimc_path.is_file():
        try:
            aimc = json.loads(aimc_path.read_text(encoding="utf-8"))
            aimc_boundary["qualification_status"] = aimc.get("status")
            aimc_boundary["same_design_run"] = aimc.get("relationship", {}).get("same_design_run")
        except (OSError, json.JSONDecodeError):
            aimc_boundary["status"] = "unavailable"
    signoff = None
    if args.human_signoff:
        signoff_path = args.human_signoff.resolve()
        try:
            candidate = json.loads(signoff_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"cannot read human signoff: {error}", file=sys.stderr)
            return 2
        body = {key: value for key, value in candidate.items() if key != "receipt_sha256"}
        expected_receipt = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        if candidate.get("receipt_sha256") != expected_receipt or candidate.get("closure_sha256") != digest(closure_path):
            print("human signoff is invalid or not bound to the closure summary", file=sys.stderr)
            return 2
        signoff = {"path": str(signoff_path), "sha256": digest(signoff_path), "status": candidate.get("status"), "reviewer": candidate.get("reviewer"), "reviewer_subject": candidate.get("reviewer_subject"), "reviewed_manifest_sha256": candidate.get("manifest_sha256"), "receipt_sha256": candidate.get("receipt_sha256"), "review_started_at": candidate.get("review_started_at"), "review_duration_seconds": candidate.get("review_duration_seconds"), "review_bindings": candidate.get("review_bindings")}
    review_effort_measured = bool(signoff and isinstance(signoff.get("review_duration_seconds"), (int, float)) and signoff.get("review_duration_seconds") >= 0)
    release_decision = "blocked_pending_human_approval"
    if signoff and signoff.get("status") == "rejected":
        release_decision = "blocked_human_rejected"
    elif not signoff and approval.get("status") == "rejected":
        release_decision = "blocked_human_rejected"
    elif signoff and signoff.get("status") == "approved" and closure.get("status") == "passed" and not fixture_approval and physical_status == "proven" and review_effort_measured:
        release_decision = "passed"
    elif signoff and signoff.get("status") == "approved" and closure.get("status") == "passed" and not fixture_approval:
        release_decision = "blocked"
    result = {
        "schema_version": "agentic-hardware-release-manifest-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "closure": {
            "path": closure_path.name,
            "sha256": digest(closure_path),
            "status": closure.get("status"),
            "canonical_source_unchanged": closure.get("canonical_source_unchanged"),
            "approval": {
                "status": approval.get("status", "missing"),
                "reviewer": approval.get("reviewer"),
                "fixture_only": fixture_approval,
            },
        },
        "model_execution": closure.get("model_execution", {"kind": "unknown"}),
        "claims": {
            "digital_verification": {"status": digital_status, "basis": "agentic closure summary and independent checker"},
            "physical_layout": {"status": physical_status, "basis": "same-run OpenLane handoff" if physical_status == "proven" else "no same-run physical evidence"},
            "analog_hardware": {"status": "unauthorized", "basis": "independent converter and measurement gates are not part of this closure"},
            "measured_hardware": {"status": "unsupported", "basis": "no board or silicon measurement in scope"},
        },
        "metrics": {
            "diagnosis": {"cases": metrics.get("model_cases", {}).get("local-batch-command"), "grounded": metrics.get("model_grounded", {}).get("local-batch-command"), "matched": metrics.get("model_diagnosis_match", {}).get("local-batch-command")},
            "repair": {"attempts": len(repair_attempts), "successes": repair_successes, "success_rate": repair_successes / len(repair_attempts) if repair_attempts else None},
            "regression": {"failed_retests": len(repair_attempts) - repair_successes, "rate": (len(repair_attempts) - repair_successes) / len(repair_attempts) if repair_attempts else None},
            "unsupported_claims": {"rejected": metrics.get("unsafe_rejected"), "rate": (metrics.get("unsafe_rejected", 0) / 3) if isinstance(metrics.get("unsafe_rejected"), (int, float)) else None, "adversarial_cases": 3},
            "latency": latency_metric,
            "human_review_effort": (
                {"status": "measured", "duration_seconds": signoff["review_duration_seconds"], "decision": signoff["status"], "basis": "server-recorded interval from reviewer start to authenticated signoff"}
                if signoff and isinstance(signoff.get("review_duration_seconds"), (int, float)) and signoff.get("review_duration_seconds") >= 0
                else {"status": "not_measured", "reason": "no server-recorded human review interval is attached"}
            ),
        },
        "human_signoff": signoff,
        "aimc_boundary": aimc_boundary,
        "release_decision": release_decision,
        "analog_authorized": False,
        "claim_boundary": "Agentic digital verification and local physical evidence only; no analog authorization, measured-hardware claim, commercial signoff, tapeout, or silicon claim.",
    }
    result["manifest_sha256"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "release_decision": result["release_decision"], "analog_authorized": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
