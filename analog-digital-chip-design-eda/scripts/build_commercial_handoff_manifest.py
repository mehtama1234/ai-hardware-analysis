#!/usr/bin/env python3
"""Build a content-addressed inventory for a controlled pilot handoff."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


ARTIFACTS = (
    ".github/workflows/verification-pilot.yml",
    "deployment/README.md",
    "deployment/requirements.txt",
    "deployment/Dockerfile",
    "deployment/.env.example",
    "deployment/docker-compose.yml",
    "deployment/kubernetes/README.md",
    "deployment/kubernetes/kustomization.yaml",
    "deployment/kubernetes/base/kustomization.yaml",
    "deployment/kubernetes/production/kustomization.yaml",
    "deployment/kubernetes/production/deployment-production-patch.yaml",
    "deployment/kubernetes/verification-pilot.yaml",
    "deployment/kubernetes/verification-backup-cronjob.yaml",
    "deployment/kubernetes/verification-production-config.example.yaml",
    "deployment/PRODUCTION_CHECKLIST.md",
    "deployment/PRODUCTION_MIGRATION_PLAN.md",
    "deployment/RECOVERY_RUNBOOK.md",
    "deployment/CUSTOM_ADAPTER_GUIDE.md",
    "deployment/adapter_execution.py",
    "deployment/adapter_registry.py",
    "deployment/PILOT_MEASUREMENT_PLAN.md",
    "deployment/USABILITY_STUDY_PLAN.md",
    "deployment/pilot-usability-study-template.json",
    "deployment/observability/verification-pilot-dashboard.json",
    "deployment/observability/verification-pilot-alert-rules.yaml",
    "deployment/observability/prometheus.yml",
    "deployment/observability/docker-compose.observability.yml",
    "deployment/observability/verification-http-log.schema.json",
    "deployment/observability/verification-customer-production-runtime.schema.json",
    ".artifacts/managed-postgres-restore-drill-2026-09-10.json",
    ".artifacts/managed-state-repository-smoke.json",
    ".artifacts/execution-sandbox-runtime.json",
    ".artifacts/verification-image-runtime.json",
    ".artifacts/verification-release-manifest.json",
    ".artifacts/oidc-key-rotation-drill.json",
    ".artifacts/customer-production-runtime-preflight.json",
    ".artifacts/verification-production-overlay.yaml",
    ".artifacts/verification-compose-config.yaml",
    ".artifacts/unified-hardware-verification-release.json",
    "scripts/verify_customer_pilot_packet.py",
    "scripts/verify_customer_production_runtime.py",
    "scripts/preflight_registered_adapters.py",
    "scripts/run_adapter_acceptance.py",
    "scripts/run_workbench_adversarial_judge.py",
    "scripts/report_production_readiness.py",
    "scripts/build_commercial_handoff_manifest.py",
    "scripts/verify_commercial_handoff_manifest.py",
    "scripts/verify_handoff_upload_contract.py",
    "scripts/build_unified_release_manifest.py",
    "scripts/verify_unified_release_manifest.py",
    "scripts/write_verification_release_manifest.py",
    "scripts/verify_workbench_browser.py",
    "scripts/verify_workbench_setup.py",
    "scripts/verify_workbench_handoff.py",
    "scripts/verify_workbench_adapter_ux.py",
    "scripts/validate_pilot_scorecard.py",
    "scripts/collect_pilot_scorecard.py",
    "scripts/verify_pilot_scorecard_evidence.py",
    "verification_platform/adapter.py",
    "verification_platform/agent.py",
    "verification_platform/reference_agent.py",
    "verification_platform/closure_lab.py",
    "scripts/run_reference_agent.py",
    "scripts/plan_next_test.py",
    "scripts/run_closure_lab.py",
    "PUBLIC_REFERENCE_RELEASE.md",
    "deployment/CUSTOMER_PILOT_CERTIFICATION_GOAL.md",
    "deployment/PRODUCTION_PILOT_FLIGHT_GOAL.md",
    "docs/roadmaps/llm-execution-loop-goal.md",
    "docs/roadmaps/llm-model-evaluation-runbook.md",
    "site/verification-workbench.html",
    "site/verification-workbench.js",
    ".artifacts/workbench-adversarial/judge-packet.json",
    ".artifacts/workbench-browser/handoff-signed.png",
    ".artifacts/adapter-acceptance/acceptance-summary.json",
    ".artifacts/registered-adapters-preflight.json",
    "benchmarks/multi_design_pilot/runs/latest/pilot-summary.json",
    "benchmarks/multi_design_pilot/runs/latest/session-ledger.json",
    "benchmarks/multi_design_pilot/runs/latest/pilot-release-manifest.json",
    "benchmarks/multi_design_pilot/fault-taxonomy.json",
    "scripts/build_public_reference_archive.py",
    "scripts/verify_public_reference_archive.py",
    "scripts/replay_public_reference_archive.py",
    "scripts/run_customer_pilot_certification.py",
    "scripts/run_customer_pilot_certification_gate.py",
    "scripts/run_production_pilot_flight.py",
    "scripts/build_production_pilot_packet.py",
    "scripts/run_llm_agent_benchmark.py",
    "scripts/run_agentic_hardware_closure.py",
    "scripts/attest_colab_benchmark.py",
    "scripts/check_agentic_hardware_closure.py",
    "scripts/build_agentic_hardware_release_manifest.py",
    "scripts/check_agentic_hardware_release_manifest.py",
    "scripts/verify_llm_model_evaluation.py",
    "scripts/mock_llm_backend.py",
    "scripts/hf_llm_backend.py",
    "scripts/hf_llm_batch_backend.py",
    ".artifacts/llm-agent-benchmark-batch-mock.json",
    ".artifacts/llm-agent-benchmark-smollm-runtime.json",
    "verification_platform/llm_backend.py",
    "verification_platform/test_llm_backend.py",
    "verification_platform/adversarial.py",
    "verification_platform/test_adversarial.py",
    "verification_platform/test_llm_evaluation_gate.py",
    "tests/test_mock_llm_backend.py",
    ".artifacts/customer-pilot-certification.json",
    ".artifacts/production-pilot-flight-runtime.json",
    ".artifacts/production-pilot-flight.json",
    ".artifacts/llm-agent-benchmark.json",
    ".artifacts/llm-agent-benchmark-mock.json",
    ".artifacts/customer-pilot-scorecard.json",
    ".artifacts/customer-pilot-scorecard/baseline-observations.json",
    ".artifacts/customer-pilot-scorecard/workbench-observations.json",
    ".artifacts/public-reference-release.tar.gz",
    ".artifacts/public-reference-release.tar.gz.json",
    ".artifacts/public-reference-replay.json",
)


def build_manifest(root: Path, *, readiness: Path | None = None, scorecard: Path | None = None, recovery: Path | None = None) -> dict[str, object]:
    root = root.resolve()
    paths = list(ARTIFACTS) + [str(path) for path in (readiness, scorecard, recovery) if path]
    files: dict[str, dict[str, object]] = {}
    for raw in paths:
        path = Path(raw)
        candidate = path if path.is_absolute() else root / path
        candidate = candidate.resolve()
        if root not in candidate.parents or not candidate.is_file():
            raise ValueError(f"required handoff artifact is missing or outside root: {raw}")
        data = candidate.read_bytes()
        key = str(candidate.relative_to(root))
        files[key] = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
    readiness_data = None
    if readiness:
        readiness_data = json.loads(Path(readiness).read_text(encoding="utf-8"))
    result = {"schema_version": "verification-commercial-handoff-v1", "artifact_count": len(files), "artifacts": files, "customer_production_ready": bool(readiness_data and readiness_data.get("customer_production_ready")), "claim_boundary": "This inventory proves which pilot artifacts were handed off; it does not convert an open-source pilot into enterprise production or a signed customer result."}
    result["manifest_sha256"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--readiness", type=Path)
    parser.add_argument("--scorecard", type=Path)
    parser.add_argument("--recovery", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        manifest = build_manifest(args.root, readiness=args.readiness, scorecard=args.scorecard, recovery=args.recovery)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"cannot build handoff manifest: {error}", file=sys.stderr)
        return 2
    payload = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
