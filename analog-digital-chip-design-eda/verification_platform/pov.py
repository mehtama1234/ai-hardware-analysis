"""Reproducible proof-of-value report aggregation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .claims import Claim, claim_status
from .coverage import rank_coverage_gaps
from .ledger import sha256_file
from .artifacts import verify_artifact_manifest
from .actions import recommend_next_action


def build_pov_report(run_root: str | Path, *, claims: list[Claim] | None = None, observed_evidence_kinds: set[str] | None = None, mixed_signal_manifest: str | Path | dict[str, Any] | None = None) -> dict[str, Any]:
    """Aggregate emitted benchmark artifacts without inferring unsupported claims."""
    root = Path(run_root)

    def load(name: str, default: Any) -> Any:
        path = root / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

    requirements = load("specification-ir.json", {}).get("requirements", [])
    plans = load("verification-plan.json", [])
    closure = load("closure-report.json", [])
    triage = load("triage-report.json", {})
    coverage = load("functional-coverage.json", {})
    capabilities = load("tool-capabilities.json", [])
    verification_ir = load("verification-ir.json", {})
    tool_runs = verification_ir.get("tool_runs", [])
    artifact_manifest = load("artifact-manifest.json", {})
    planning = load("planning-summary.json", {})
    generated = {name: (root / name).is_file() for name in ("generated_checks.sv", "procedural_checks.sv", "uvm-counter-agent.sv")}
    generated_hashes = {name: sha256_file(root / name) for name, exists in generated.items() if exists}
    statuses = {item.get("status", "unknown") for item in closure}
    coverage_percentage = round(100.0 * coverage.get("covered", 0) / coverage["total"], 4) if isinstance(coverage.get("total"), int) and coverage.get("total", 0) > 0 else None
    report: dict[str, Any] = {
        "schema_version": "pov-report-v1",
        "requirements": {"total": len(requirements), "planned_checks": len(plans), "unplanned": max(0, len(requirements) - len(plans)), "planning_queue": planning.get("unplanned", [])},
        "closure": {"total": len(closure), "failed": sum(item.get("status") == "failed" for item in closure), "proven": sum(item.get("status") == "proven" for item in closure), "open": sum(item.get("status") == "open" for item in closure)},
        "triage": {"status": triage.get("status", "missing"), "has_first_divergence": "first_divergence" in triage, "has_root_cause": "root_cause" in triage},
        "coverage": {"kind": coverage.get("kind", "missing"), "covered": coverage.get("covered", 0), "total": coverage.get("total", 0), "percentage": coverage_percentage, "next_actions": rank_coverage_gaps([coverage]) if coverage else []},
        "toolchain": {"total": len(capabilities), "available": sum(item.get("status") == "available" for item in capabilities), "blocked": sum(item.get("status") == "blocked" for item in capabilities), "capabilities": capabilities},
        "execution": {"tool_runs": len(tool_runs), "passed": sum(run.get("status") == "passed" for run in tool_runs), "failed": sum(run.get("status") == "failed" for run in tool_runs), "blocked": sum(run.get("status") == "blocked" for run in tool_runs), "duration_seconds": round(sum(run.get("metadata", {}).get("duration_seconds", 0.0) for run in tool_runs), 6), "tools": sorted({run.get("tool") for run in tool_runs if run.get("tool")}), "proof_results": {result: sum(run.get("metadata", {}).get("proof_result") == result for run in tool_runs) for result in ("proven", "counterexample", "unknown")}},
        "generation": {"artifacts": generated, "sha256": generated_hashes, "emitted_count": sum(generated.values()), "procedural_executable": generated["procedural_checks.sv"], "sva_reviewable": generated["generated_checks.sv"], "uvm_reviewable": generated["uvm-counter-agent.sv"]},
        "artifact_integrity": verify_artifact_manifest(root, artifact_manifest) if artifact_manifest else {"valid": False, "reason": "manifest missing"},
        "claim_boundary": "Counts and statuses reflect only artifacts present under this run root.",
        "claims": [{"text": claim.text, "domain": claim.domain, "status": claim_status(claim, observed_evidence_kinds or set())} for claim in (claims or [])],
    }
    if mixed_signal_manifest is not None:
        manifest = mixed_signal_manifest if isinstance(mixed_signal_manifest, dict) else json.loads(Path(mixed_signal_manifest).read_text(encoding="utf-8"))
        report["mixed_signal"] = {
            "manifest_sha256": manifest.get("manifest_sha256"),
            "artifact_count": len(manifest.get("artifacts", [])),
            "observed_evidence_kinds": manifest.get("observed_evidence_kinds", []),
            "claims": manifest.get("claims", []),
        }
    report["closure"]["observed_statuses"] = sorted(statuses)
    report["next_action"] = recommend_next_action(report)
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"))
    report["report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report


def write_pov_report(run_root: str | Path, *, mixed_signal_manifest: str | Path | dict[str, Any] | None = None) -> Path:
    root = Path(run_root)
    report = build_pov_report(root, mixed_signal_manifest=mixed_signal_manifest)
    output = root / "proof-of-value-report.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def verify_pov_digest(report: dict[str, Any]) -> bool:
    """Verify a PoV report's self-digest without trusting its stored value."""
    stored = report.get("report_sha256")
    if not isinstance(stored, str):
        return False
    payload = {key: value for key, value in report.items() if key != "report_sha256"}
    computed = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return computed == stored
