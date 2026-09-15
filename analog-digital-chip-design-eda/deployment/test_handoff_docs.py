from pathlib import Path
import json
import subprocess
import pytest
from deployment.pilot_scorecard import validate_scorecard


ROOT = Path(__file__).resolve().parent


def test_commercial_handoff_is_evidence_bounded():
    handoff = (ROOT / "COMMERCIAL_BETA_HANDOFF.md").read_text(encoding="utf-8")
    assert "218` tests" in handoff
    assert "76` tests" in handoff
    assert "294` combined tests" in handoff
    assert "Playwright gate passes" in handoff
    assert "eight-scenario adversarial preflight" in handoff
    assert "managed database" in handoff
    assert "enterprise identity" in handoff
    assert "signed pilot" in handoff
    assert "collect_pilot_scorecard.py" in (ROOT / "PILOT_MEASUREMENT_PLAN.md").read_text(encoding="utf-8")
    assert "verification-pilot-release-provenance" in handoff
    assert "verification-image-runtime.json" in handoff
    assert "Prometheus scrape configuration" in handoff
    assert "100` tests" not in handoff
    for artifact in ("RECOVERY_RUNBOOK.md", "CUSTOM_ADAPTER_GUIDE.md", "PILOT_MEASUREMENT_PLAN.md", "pilot-scorecard-template.json", "USABILITY_STUDY_PLAN.md", "pilot-usability-study-template.json", "PRODUCTION_MIGRATION_PLAN.md", "observability/verification-pilot-dashboard.json", "observability/verification-customer-production-runtime.schema.json"):
        assert artifact in handoff
        assert (ROOT / artifact).is_file()
    assert "verification-http-log.schema.json" in handoff or (ROOT / "observability" / "verification-http-log.schema.json").is_file()
    assert "verification-customer-production-runtime.schema.json" in handoff
    assert ".github/workflows/verification-pilot.yml" in handoff or "verification-pilot.yml" in handoff
    assert (ROOT.parent / ".artifacts" / "managed-postgres-restore-drill-2026-09-10.json").is_file()
    assert (ROOT.parent / ".artifacts" / "managed-state-repository-smoke.json").is_file()
    assert (ROOT.parent / ".artifacts" / "execution-sandbox-runtime.json").is_file()
    assert (ROOT.parent / ".artifacts" / "verification-image-runtime.json").is_file()
    assert (ROOT.parent / ".artifacts" / "oidc-key-rotation-drill.json").is_file()
    assert (ROOT.parent / ".artifacts" / "customer-production-runtime-preflight.json").is_file()
    assert (ROOT.parent / ".artifacts" / "workbench-browser" / "handoff-signed.png").is_file()
    assert (ROOT.parent / ".artifacts" / "verification-compose-config.yaml").is_file()
    assert (ROOT.parent / ".artifacts" / "verification-production-overlay.yaml").is_file()
    assert (ROOT.parent / ".artifacts" / "registered-adapters-preflight.json").is_file()
    assert (ROOT.parent / "scripts" / "verify_customer_pilot_packet.py").is_file()
    assert (ROOT.parent / "scripts" / "verify_customer_production_runtime.py").is_file()
    assert (ROOT.parent / "scripts" / "preflight_registered_adapters.py").is_file()
    assert (ROOT.parent / ".artifacts" / "adapter-acceptance" / "acceptance-summary.json").is_file()
    assert "OIDC key rotation" in (ROOT / "RECOVERY_RUNBOOK.md").read_text()
    assert "VerificationPilotOidcUnknownKey" in (ROOT / "observability" / "verification-pilot-alert-rules.yaml").read_text()
    manifest = json.loads((ROOT.parent / ".artifacts" / "commercial-handoff-manifest.json").read_text(encoding="utf-8"))
    assert ".github/workflows/verification-pilot.yml" in manifest["artifacts"]


def test_production_checklist_links_operational_artifacts():
    checklist = (ROOT / "PRODUCTION_CHECKLIST.md").read_text(encoding="utf-8")
    assert "RECOVERY_RUNBOOK.md" in checklist
    assert "CUSTOM_ADAPTER_GUIDE.md" in checklist
    assert "PILOT_MEASUREMENT_PLAN.md" in checklist
    assert "PRODUCTION_MIGRATION_PLAN.md" in checklist
    assert "bounded request correlation IDs" in checklist
    assert "centralized production logs, managed alert routing, and SLO ownership" in checklist
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "VERIFICATION_DEPLOYMENT_TIER" in compose
    assert "VERIFICATION_EVIDENCE_STORE_PROVIDER" in compose
    assert "VERIFICATION_EXECUTION_SANDBOX" in compose
    assert "VERIFICATION_REVIEWER_ROLE" in compose
    assert "VERIFICATION_IDENTITY_ISSUER" in compose
    assert "VERIFICATION_IDENTITY_AUDIENCE" in compose
    assert "VERIFICATION_IDENTITY_JWKS_URL" in compose
    assert "VERIFICATION_PROJECT_SUBJECTS" in compose
    assert "managed_state_contract.py" in (ROOT / "PRODUCTION_MIGRATION_PLAN.md").read_text(encoding="utf-8")
    assert "postgres_job_queue.py" in (ROOT / "PRODUCTION_MIGRATION_PLAN.md").read_text(encoding="utf-8")
    assert "postgres_project_store.py" in (ROOT / "PRODUCTION_MIGRATION_PLAN.md").read_text(encoding="utf-8")
    assert "repository_factory.py" in (ROOT / "PRODUCTION_MIGRATION_PLAN.md").read_text(encoding="utf-8")
    assert "S3EvidenceStore" in (ROOT / "PRODUCTION_MIGRATION_PLAN.md").read_text(encoding="utf-8")
    assert "deployment.apply_managed_state_migration" in (ROOT / "README.md").read_text(encoding="utf-8")
    plan = (ROOT / "PILOT_MEASUREMENT_PLAN.md").read_text(encoding="utf-8")
    assert "validate_pilot_scorecard.py" in plan


def test_root_readme_links_commercial_artifacts():
    readme = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    for artifact in ("COMMERCIAL_BETA_HANDOFF.md", "RECOVERY_RUNBOOK.md", "CUSTOM_ADAPTER_GUIDE.md", "PILOT_MEASUREMENT_PLAN.md"):
        assert artifact in readme


def test_deployment_readme_defines_release_evidence_sequence():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for command in ("verify_workbench_browser.py", "verify_workbench_setup.py", "verify_workbench_handoff.py", "verify_workbench_adapter_ux.py", "run_workbench_adversarial_judge.py", "validate_pilot_scorecard.py", "verify_pilot_scorecard_evidence.py", "verify_handoff_upload_contract.py", "validate_usability_study.py"):
        assert command in readme
    assert "verify_verification_image_runtime.py" in readme
    assert "write_verification_release_manifest.py" in readme
    assert "/v1/projects/{project_id}/audit" in readme
    workflow = (ROOT.parent / ".github" / "workflows" / "verification-pilot.yml").read_text(encoding="utf-8")
    assert "build_open_source_pilot_scorecard.py" in workflow
    assert ".artifacts/open-source-pilot-scorecard.json" in workflow
    assert "verify_recovery_snapshot.py" in workflow
    assert "run_managed_state_repository_smoke.py" in workflow
    assert "managed-postgres-restore-drill-2026-09-10.json" in workflow
    assert "ephemeral PostgreSQL" in (ROOT / "PRODUCTION_MIGRATION_PLAN.md").read_text(encoding="utf-8")
    assert "verify_execution_sandbox_runtime.py" in workflow
    assert "run_adapter_acceptance.py" in workflow
    assert "verification-image-runtime.json" in workflow
    assert "managed_restore_drill.py" in (ROOT / "RECOVERY_RUNBOOK.md").read_text(encoding="utf-8")
    assert "postgres_backup_restore.py" in (ROOT / "RECOVERY_RUNBOOK.md").read_text(encoding="utf-8")
    assert (ROOT / "kubernetes" / "verification-backup-cronjob.yaml").is_file()
    assert "recovery-snapshot-verification.json" in workflow
    assert "report_production_readiness.py" in workflow
    assert "production-readiness.json" in workflow
    assert "build_commercial_handoff_manifest.py" in workflow
    assert "commercial-handoff-manifest.json" in workflow
    assert "verify_commercial_handoff_manifest.py" in workflow
    assert "Validate runtime preflight schema" in workflow
    assert "verification-customer-production-runtime.schema.json" in workflow
    assert '"schema_path": "deployment/observability/verification-customer-production-runtime.schema.json"' in workflow
    assert "scripts/verify_customer_production_runtime.py" in workflow
    assert "scripts/run_adapter_acceptance.py" in workflow
    assert "scripts/run_workbench_adversarial_judge.py" in workflow
    assert "scripts/report_production_readiness.py" in workflow
    assert "scripts/build_commercial_handoff_manifest.py" in workflow
    assert "scripts/verify_commercial_handoff_manifest.py" in workflow
    assert "scripts/verify_handoff_upload_contract.py" in workflow
    assert "Verify handoff upload contract" in workflow
    assert "scripts/write_verification_release_manifest.py" in workflow
    assert "scripts/verify_workbench_setup.py" in workflow
    assert "scripts/verify_workbench_handoff.py" in workflow
    assert "Write release provenance manifest" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert ".github/workflows/verification-pilot.yml" in workflow
    assert "deployment/requirements.txt" in workflow
    assert "deployment/Dockerfile" in workflow
    assert "deployment/.env.example" in workflow
    assert "deployment/docker-compose.yml" in workflow
    assert "deployment/kubernetes/production/kustomization.yaml" in workflow
    assert "deployment/kubernetes/verification-pilot.yaml" in workflow
    assert ".artifacts/verification-production-overlay.yaml" in workflow
    assert ".artifacts/verification-compose-config.yaml" in workflow
    assert ".artifacts/unified-hardware-verification-release.json" in workflow
    assert "scripts/build_unified_release_manifest.py" in workflow
    assert "scripts/verify_unified_release_manifest.py" in workflow
    assert "verification_platform/agent.py" in workflow
    assert "verification_platform/reference_agent.py" in workflow
    assert ".artifacts/managed-postgres-restore-drill-2026-09-10.json" in workflow
    assert ".artifacts/managed-state-repository-smoke.json" in workflow
    assert ".artifacts/workbench-adversarial/judge-packet.json" in workflow
    assert ".artifacts/workbench-browser/handoff-signed.png" in workflow
    assert "include-hidden-files: true" in workflow
    assert "Install browser acceptance runtime" in workflow
    assert "verify_workbench_browser.py" in workflow
    assert "verify_workbench_setup.py" in workflow
    assert "verify_workbench_handoff.py" in workflow
    assert "verify_workbench_adapter_ux.py" in workflow
    assert "Require clean release provenance" in workflow
    assert "docker-compose.observability.yml" in workflow
    assert "Validate observability compose overlay" in workflow
    assert "Render customer production Kubernetes overlay" in workflow
    assert "--load-restrictor LoadRestrictionsNone deployment/kubernetes/production" in workflow
    assert "preflight_customer_production_overlay.py" in workflow
    assert "/readyz" in readme
    assert "jsonschema==4.23.0" in (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "playwright==1.48.0" in (ROOT / "requirements.txt").read_text(encoding="utf-8")


def test_scorecard_template_has_traceable_metric_contract():
    scorecard = json.loads((ROOT / "pilot-scorecard-template.json").read_text(encoding="utf-8"))
    assert scorecard["schema_version"] == "verification-pilot-scorecard-v1"
    assert len(scorecard["metrics"]) == 6
    assert all(metric["evidence"] == [] for metric in scorecard["metrics"])
    assert scorecard["review"]["receipt_sha256"] is None
    assert "does not establish exhaustive functional coverage" in scorecard["claim_boundary"]
    assert validate_scorecard(scorecard) == []
    assert validate_scorecard(scorecard, finalized=True)


def test_finalized_scorecard_requires_evidence_and_review():
    scorecard = json.loads((ROOT / "pilot-scorecard-template.json").read_text(encoding="utf-8"))
    scorecard["pilot"]["sample_size"] = 20
    for metric in scorecard["metrics"]:
        metric.update({"baseline_median": 10, "baseline_confidence_95": [9, 11], "workbench_median": 7, "workbench_confidence_95": [6, 8], "evidence": ["run-1"]})
    scorecard["review"].update({"lead_reviewer": "lead", "receipt_sha256": "a" * 64})
    assert validate_scorecard(scorecard, finalized=True) == []


def test_finalized_scorecard_rejects_invalid_confidence_interval():
    scorecard = json.loads((ROOT / "pilot-scorecard-template.json").read_text(encoding="utf-8"))
    scorecard["pilot"]["sample_size"] = 20
    for metric in scorecard["metrics"]:
        metric.update({"baseline_median": 10, "baseline_confidence_95": [9, 11], "workbench_median": 7, "workbench_confidence_95": [8, 6], "evidence": ["run-1"]})
    scorecard["review"].update({"lead_reviewer": "lead", "receipt_sha256": "a" * 64})
    errors = validate_scorecard(scorecard, finalized=True)
    assert len([error for error in errors if "confidence_95" in error]) == 6


@pytest.mark.parametrize("interval", [[float("nan"), 8], [float("inf"), 8], [True, 8]])
def test_finalized_scorecard_rejects_non_finite_or_boolean_interval(interval):
    scorecard = json.loads((ROOT / "pilot-scorecard-template.json").read_text(encoding="utf-8"))
    scorecard["pilot"]["sample_size"] = 20
    for metric in scorecard["metrics"]:
        metric.update({"baseline_median": 10, "baseline_confidence_95": [9, 11], "workbench_median": 7, "workbench_confidence_95": [6, 8], "evidence": ["run-1"]})
    scorecard["metrics"][0]["workbench_confidence_95"] = interval
    scorecard["review"].update({"lead_reviewer": "lead", "receipt_sha256": "a" * 64})
    errors = validate_scorecard(scorecard, finalized=True)
    assert any("workbench_confidence_95" in error for error in errors)


def test_scorecard_cli_exit_codes(tmp_path):
    template = ROOT / "pilot-scorecard-template.json"
    command = ["python3", "scripts/validate_pilot_scorecard.py", str(template)]
    draft = subprocess.run(command, cwd=ROOT.parent, capture_output=True, text=True, check=False)
    finalized = subprocess.run(command + ["--finalized"], cwd=ROOT.parent, capture_output=True, text=True, check=False)
    assert draft.returncode == 0
    assert "valid scorecard" in draft.stdout
    assert finalized.returncode == 1
    assert "ERROR:" in finalized.stdout


def test_production_migration_plan_has_acceptance_boundaries():
    plan = (ROOT / "PRODUCTION_MIGRATION_PLAN.md").read_text(encoding="utf-8")
    for phrase in ("Managed state", "Identity and authorization", "Isolated execution", "Operations", "Customer adapters and pilot", "Acceptance:", "Rollout controls"):
        assert phrase in plan
