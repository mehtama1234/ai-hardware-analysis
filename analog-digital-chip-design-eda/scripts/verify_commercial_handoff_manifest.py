#!/usr/bin/env python3
"""Verify a commercial handoff manifest and every artifact it inventories."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

REQUIRED_ADVERSARIAL_SCENARIOS = {
    "selection_isolation",
    "project_switch_isolation",
    "missing_waveform",
    "repair_digest",
    "narrow_retest",
    "credential_boundary",
    "coverage_boundary",
    "disconnect_recovery",
}


def verify(manifest_path: Path, root: Path) -> list[str]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = payload.get("manifest_sha256")
    body = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        return ["manifest_sha256 is missing or invalid"]
    if digest != sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest():
        return ["manifest_sha256 does not match manifest content"]
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict) or payload.get("artifact_count") != len(artifacts):
        return ["artifact inventory is missing or count does not match"]
    errors: list[str] = []
    root = root.resolve()
    for raw_path, record in artifacts.items():
        path = str(raw_path)
        candidate = (root / path).resolve()
        if Path(path).is_absolute() or "\\" in path or any(part in {"", ".", ".."} for part in path.split("/")) or root not in candidate.parents:
            errors.append(f"unsafe artifact path: {path}")
            continue
        expected = record.get("sha256") if isinstance(record, dict) else None
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            errors.append(f"invalid artifact digest: {path}")
        elif not candidate.is_file():
            errors.append(f"missing handoff artifact: {path}")
        elif sha256(candidate.read_bytes()).hexdigest() != expected:
            errors.append(f"handoff artifact digest mismatch: {path}")
        elif path == ".artifacts/workbench-adversarial/judge-packet.json":
            packet_errors = verify_adversarial_packet(candidate)
            errors.extend(f"adversarial packet: {error}" for error in packet_errors)
        elif path == ".artifacts/public-reference-replay.json":
            try:
                replay = json.loads(candidate.read_text(encoding="utf-8"))
                if replay.get("replay") is not True or replay.get("pilot_exit_code") != 0 or replay.get("passed_retests") != replay.get("design_count"):
                    errors.append("public reference replay evidence is not a successful matched pilot")
            except (OSError, ValueError, TypeError):
                errors.append("public reference replay evidence is not valid JSON")
        elif path == ".artifacts/customer-pilot-certification.json":
            pilot_errors = verify_customer_pilot_certification(candidate)
            errors.extend(f"customer pilot certification: {error}" for error in pilot_errors)
        elif path == ".artifacts/customer-pilot-scorecard.json":
            scorecard_errors = verify_customer_pilot_scorecard(candidate, root)
            errors.extend(f"customer pilot scorecard: {error}" for error in scorecard_errors)
        elif path == ".artifacts/production-pilot-flight.json":
            flight_errors = verify_production_pilot_flight(candidate)
            errors.extend(f"production pilot flight: {error}" for error in flight_errors)
        elif path == ".artifacts/production-pilot-packet.json":
            packet_errors = verify_production_pilot_packet(candidate, root)
            errors.extend(f"production pilot packet: {error}" for error in packet_errors)
        elif path == ".artifacts/llm-agent-benchmark.json":
            agent_errors = verify_llm_agent_benchmark(candidate)
            errors.extend(f"llm agent benchmark: {error}" for error in agent_errors)
    return errors


def verify_adversarial_packet(path: Path) -> list[str]:
    """Validate digest and semantic scenario coverage for the judge packet."""
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        return [f"cannot parse packet ({error})"]
    digest = packet.get("packet_sha256") if isinstance(packet, dict) else None
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        return ["packet_sha256 is missing or invalid"]
    body = {key: value for key, value in packet.items() if key != "packet_sha256"}
    expected = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    errors = [] if digest == expected else ["packet_sha256 does not match packet content"]
    scenarios = packet.get("scenarios")
    scenario_ids = {item.get("id") for item in scenarios} if isinstance(scenarios, list) and all(isinstance(item, dict) for item in scenarios) else set()
    if scenario_ids != REQUIRED_ADVERSARIAL_SCENARIOS:
        errors.append("scenario coverage does not match the eight-scenario release contract")
    gate = packet.get("deterministic_gate")
    if not isinstance(gate, dict) or gate.get("passed") is not True:
        errors.append("deterministic adversarial gate is not passed")
    return errors


def verify_customer_pilot_certification(path: Path) -> list[str]:
    """Validate the semantic contract for the synthetic customer certification slice."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        return [f"cannot parse certification ({error})"]
    if not isinstance(payload, dict):
        return ["certification payload is not an object"]
    errors: list[str] = []
    if payload.get("schema_version") != "customer-pilot-certification-v1":
        errors.append("schema_version is not customer-pilot-certification-v1")
    projects = payload.get("projects")
    if not isinstance(projects, list) or len(projects) != 3 or payload.get("project_count") != 3:
        errors.append("certification does not contain exactly three projects")
    else:
        for project in projects:
            closure = project.get("closure", {}) if isinstance(project, dict) else {}
            if not isinstance(project, dict) or project.get("requirements", 0) < 1 or project.get("planned_checks", 0) < 1 or project.get("job_status") != "passed":
                errors.append("each project must have requirements, planned checks, and a passed adapter job")
                break
            if not (closure.get("baseline_status") == "failed" and closure.get("retest_status") == "passed" and closure.get("failure_resolved") is True and closure.get("stale_digest_rejected") is True and closure.get("signoff_status") == "approved" and closure.get("signoff_valid") is True):
                errors.append("each project must prove failed baseline, approved matched retest, stale-digest rejection, and valid sign-off")
                break
    adapters = payload.get("adapters")
    adapter_names = {item.get("name") for item in adapters} if isinstance(adapters, list) and all(isinstance(item, dict) for item in adapters) else set()
    required = {"reference-iverilog", "reference-verilator", "reference-yosys", "reference-symbiyosys"}
    if not required.issubset(adapter_names):
        errors.append("required open-source adapter definitions are missing")
    if payload.get("adapter_count", 0) < 4 or payload.get("available_adapters", 0) < 3:
        errors.append("adapter availability evidence is below the certification minimum")
    if payload.get("certified_synthetic_runs") != 3:
        errors.append("certified_synthetic_runs must equal three")
    negatives = payload.get("negative_paths")
    if not isinstance(negatives, dict) or negatives.get("timeout", {}).get("status") != "blocked" or negatives.get("missing_artifact", {}).get("status") != "blocked":
        errors.append("timeout and missing-artifact paths must be explicitly recorded as blocked")
    digest = payload.get("evidence_sha256")
    body = {key: value for key, value in payload.items() if key != "evidence_sha256"}
    expected = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if digest != expected:
        errors.append("evidence_sha256 does not match certification content")
    return errors


def verify_customer_pilot_scorecard(path: Path, root: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        return [f"cannot parse scorecard ({error})"]
    errors: list[str] = []
    if payload.get("schema_version") != "verification-pilot-scorecard-v1":
        errors.append("unexpected scorecard schema")
    if payload.get("pilot", {}).get("sample_size", 0) < 20:
        errors.append("scorecard sample is smaller than 20 matched observations")
    digest = payload.get("scorecard_sha256")
    body = {key: value for key, value in payload.items() if key != "scorecard_sha256"}
    if digest != sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest():
        errors.append("scorecard_sha256 does not match scorecard content")
    for raw_path, expected in (payload.get("evidence_sha256") or {}).items():
        candidate = (root / str(raw_path)).resolve()
        if not candidate.is_file() or sha256(candidate.read_bytes()).hexdigest() != expected:
            errors.append(f"scorecard evidence is missing or changed: {raw_path}")
    return errors


def verify_production_pilot_flight(path: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        return [f"cannot parse flight receipt ({error})"]
    errors: list[str] = []
    if payload.get("schema_version") != "production-pilot-flight-v1":
        errors.append("unexpected flight receipt schema")
    if payload.get("ready_before_restart") != "ready" or payload.get("ready_after_restart") != "ready":
        errors.append("API readiness did not pass before and after restart")
    if payload.get("job_status_before_restart") != "passed" or payload.get("job_status_after_restart") != "passed":
        errors.append("worker simulation did not pass before and after restart")
    if payload.get("project_id_after_restart") != payload.get("project", {}).get("id"):
        errors.append("project identity was not preserved across restart")
    closure = payload.get("closure", {})
    if not (closure.get("failed_baseline_status") == "failed" and closure.get("retest_status") == "passed" and closure.get("failure_resolved") is True and closure.get("stale_digest_rejected") is True):
        errors.append("deployed closure does not prove failed baseline, approved retest, and stale-digest rejection")
    negative = payload.get("negative_paths", {})
    if negative.get("invalid_credential_rejected") is not True or negative.get("cross_tenant_rejected") is not True:
        errors.append("deployed negative paths did not reject invalid credentials and cross-tenant access")
    operational = payload.get("operational_evidence", {})
    if operational.get("job_evidence_after_restart") is not True or operational.get("audit_entries_after_restart", 0) < 1 or operational.get("storage_controls_ready") is not True or operational.get("metrics_exposed") is not True or operational.get("scorecard_endpoint_ready") is not True:
        errors.append("deployed operational evidence is incomplete after restart")
    digest = payload.get("evidence_sha256")
    body = {key: value for key, value in payload.items() if key != "evidence_sha256"}
    if digest != sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest():
        errors.append("evidence_sha256 does not match flight receipt content")
    return errors


def verify_production_pilot_packet(path: Path, root: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        return [f"cannot parse packet ({error})"]
    errors: list[str] = []
    if payload.get("schema_version") != "production-pilot-packet-v1":
        errors.append("unexpected packet schema")
    digest = payload.get("packet_sha256")
    body = {key: value for key, value in payload.items() if key != "packet_sha256"}
    if digest != sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest():
        errors.append("packet_sha256 does not match packet content")
    for name, required in (("flight", "production-pilot-flight.json"), ("scorecard", "customer-pilot-scorecard.json"), ("adversarial", "judge-packet.json"), ("archive_replay", "public-reference-replay.json"), ("commercial_manifest", "commercial-handoff-manifest.json")):
        item = payload.get(name, {})
        candidate = (root / str(item.get("path", ""))).resolve()
        if candidate.name != required or not candidate.is_file() or sha256(candidate.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"{name} evidence binding is missing or changed")
    if payload.get("flight", {}).get("job_status_after_restart") != "passed" or payload.get("scorecard", {}).get("sample_size", 0) < 20 or payload.get("adversarial", {}).get("gate_passed") is not True or payload.get("archive_replay", {}).get("replay") is not True:
        errors.append("packet does not contain passed flight, scorecard, adversarial, and replay gates")
    return errors


def verify_llm_agent_benchmark(path: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        return [f"cannot parse benchmark ({error})"]
    errors: list[str] = []
    if payload.get("schema_version") != "llm-verification-agent-benchmark-v1" or payload.get("backend") != "deterministic-reference":
        errors.append("unexpected provider-neutral benchmark schema")
    metrics = payload.get("metrics", {})
    if payload.get("design_count") != 11 or metrics.get("grounded_proposals") != 11 or metrics.get("unsafe_rejected") != 3 or metrics.get("forbidden_claims_rejected") is not True:
        errors.append("benchmark does not prove 11 grounded proposals and three unsafe trajectory rejections")
    execution = payload.get("reference_execution", {})
    if execution.get("status") != "passed" or execution.get("passed_retests") != 11:
        errors.append("benchmark reference execution does not prove 11 passed retests")
    runs = payload.get("model_runs", {})
    if not isinstance(runs, dict):
        errors.append("model_runs must be an object")
    else:
        for backend, rows in runs.items():
            if not isinstance(rows, list) or len(rows) != 11:
                errors.append(f"model backend {backend} does not have 11 case records")
                continue
            for row in rows:
                if row.get("status") == "available" and row.get("adversarial_review", {}).get("accepted") is not True:
                    errors.append(f"available model result for {row.get('design_id')} was not adversarially accepted")
    digest = payload.get("evidence_sha256")
    body = {key: value for key, value in payload.items() if key != "evidence_sha256"}
    if digest != sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest():
        errors.append("benchmark evidence_sha256 does not match content")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        errors = verify(args.manifest, args.root)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"cannot verify handoff manifest: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"verified commercial handoff: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
