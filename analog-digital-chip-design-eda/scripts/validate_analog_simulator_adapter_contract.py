#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "sources" / "evidence" / "analog-simulator-adapter-output-schema.json"
STRICT_PAYLOAD = ROOT / "evidence" / "aimc-hardware-lab" / "analog_error_simulation_strict_tool.json"
SKIPPED_STATUS = ROOT / "evidence" / "aimc-simulator-adapters" / "simulator-adapter-status.json"
DRY_RUN_DIR = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run"
OLD_BACKEND = (
    ROOT.parent
    / "analog-in-memory-ai-inference"
    / "software-architecture"
    / "backend"
)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def has_path(payload: dict[str, object], path: str) -> bool:
    current: object = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    if isinstance(current, str):
        return bool(current.strip())
    return current is not None


def validate_contract_shape(contract: dict[str, object]) -> None:
    require(contract.get("required_source_id") == "analog_error_simulation", "contract must target analog_error_simulation")
    for key in [
        "required_top_level_fields",
        "required_error_model_fields",
        "required_accuracy_impact_fields",
        "required_provenance_fields",
        "accepted_tool_name_fragments",
        "claim_rule",
    ]:
        require(key in contract, f"contract missing {key}")


def validate_payload_against_contract(payload: dict[str, object], contract: dict[str, object]) -> list[str]:
    issues: list[str] = []
    for field in contract["required_top_level_fields"]:
        if not has_path(payload, str(field)):
            issues.append(f"missing top-level field {field}")
    for field in contract["required_error_model_fields"]:
        if not has_path(payload, f"error_model.{field}"):
            issues.append(f"missing error_model.{field}")
    for field in contract["required_accuracy_impact_fields"]:
        if not has_path(payload, f"accuracy_impact.{field}"):
            issues.append(f"missing accuracy_impact.{field}")
    for field in contract["required_provenance_fields"]:
        if not has_path(payload, f"provenance.{field}"):
            issues.append(f"missing provenance.{field}")

    provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    error_model = payload.get("error_model") if isinstance(payload.get("error_model"), dict) else {}
    tool_text = f"{provenance.get('tool', '')} {error_model.get('tool', '')}".lower()
    if not any(str(fragment) in tool_text for fragment in contract["accepted_tool_name_fragments"]):
        issues.append("tool name does not match accepted analog simulator fragments")
    return issues


def backend_readiness(payload: dict[str, object]) -> dict[str, object]:
    sys.path.insert(0, str(OLD_BACKEND))
    from evidence_imports import build_tool_readiness_report, validate_imported_evidence

    structural_errors = validate_imported_evidence("analog_error_simulation", payload)
    readiness = build_tool_readiness_report("analog_error_simulation", payload)
    return {
        "structural_errors": structural_errors,
        "tool_ready": readiness["tool_ready"],
        "issues": readiness["issues"],
    }


def main() -> int:
    contract = load_json(CONTRACT)
    validate_contract_shape(contract)

    strict_payload = load_json(STRICT_PAYLOAD)
    strict_issues = validate_payload_against_contract(strict_payload, contract)
    require(not strict_issues, f"strict payload does not satisfy adapter contract: {strict_issues}")
    strict_backend = backend_readiness(strict_payload)
    require(not strict_backend["structural_errors"], f"strict payload failed backend structure: {strict_backend['structural_errors']}")
    require(strict_backend["tool_ready"] is True, f"strict payload failed backend readiness: {strict_backend['issues']}")

    skipped_status = load_json(SKIPPED_STATUS)
    skipped_issues = validate_payload_against_contract(skipped_status, contract)
    require(skipped_issues, "skipped adapter status must not satisfy simulator evidence contract")

    dry_run_paths = [
        DRY_RUN_DIR / "aihwkit-analog-error-simulation.dry-run.json",
        DRY_RUN_DIR / "crosssim-analog-error-simulation.dry-run.json",
    ]
    rejected_dry_runs = 0
    for path in dry_run_paths:
        payload = load_json(path)
        contract_issues = validate_payload_against_contract(payload, contract)
        require(not contract_issues, f"{path.name} should satisfy payload shape contract: {contract_issues}")
        require(payload.get("dry_run") is True, f"{path.name} must mark dry_run=true")
        readiness = backend_readiness(payload)
        require(readiness["tool_ready"] is False, f"{path.name} must not be backend tool-ready")
        require(any("accuracy_impact.pass" in issue for issue in readiness["issues"]), f"{path.name} rejection should depend on pass=false")
        rejected_dry_runs += 1

    print("PASS analog_simulator_adapter_contract")
    print(f"contract,{CONTRACT}")
    print(f"strict_payload,{STRICT_PAYLOAD}")
    print("strict_contract_ready,True")
    print(f"strict_backend_tool_ready,{strict_backend['tool_ready']}")
    print("skipped_status_contract_ready,False")
    print(f"skipped_status_issues,{len(skipped_issues)}")
    print(f"dry_run_payloads_rejected,{rejected_dry_runs}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL analog_simulator_adapter_contract: {exc}", file=sys.stderr)
        raise
