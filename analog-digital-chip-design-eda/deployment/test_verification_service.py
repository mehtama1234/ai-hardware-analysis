import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
import pytest
from datetime import datetime, timezone
import deployment.verification_service as service
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient


def test_customer_production_mutations_require_operator_role(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    monkeypatch.setenv("VERIFICATION_OPERATOR_ROLE", "verification-operator")
    with pytest.raises(service.HTTPException, match="operator role"):
        service._require_operator_role()


def test_cancel_does_not_override_an_atomic_worker_claim(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    created = service.create_job(service.JobRequest(project_id="cancel-race"))
    service._queue().start(created["id"])
    with pytest.raises(Exception) as error:
        service.cancel_job(created["id"])
    assert getattr(error.value, "status_code", None) == 409
    assert service.get_job(created["id"])["status"] == "queued"

def test_job_lifecycle_persists_status_and_rejects_unknown_kind(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    created = service.create_job(service.JobRequest(project_id="customer_demo"))
    assert created["status"] == "queued"
    assert service.get_job(created["id"])["kind"] == "multi-design-pilot"
    assert service.get_job(created["id"])["project_id"] == "customer_demo"
    assert service.get_job(created["id"])["events"][0]["status"] == "queued"
    assert created["id"] in {job["id"] for job in service.list_jobs()}
    assert created["id"] in {job["id"] for job in service.list_jobs(project_id="customer_demo")}
    assert created["id"] not in {job["id"] for job in service.list_jobs(project_id="other_project")}
    cancelled = service.cancel_job(created["id"])
    assert cancelled["status"] == "cancelled"
    assert [event["status"] for event in cancelled["events"]] == ["queued", "cancelled"]
    assert service.get_project("customer_demo")["id"] == "customer_demo"
    collateral = service.add_collateral("customer_demo", service.CollateralRequest(name="spec.md", kind="specification", content="module spec;"))
    assert collateral["sha256"]
    assert service.list_collateral("customer_demo")[0]["name"] == "spec.md"
    ingested = service.ingest_project_collateral("customer_demo", collateral["id"])
    assert ingested["requirements"] == 0
    search = service.search_project("customer_demo", "module")
    assert search["hits"][0]["snippet"] == "module spec;"
    assert service.plan_project_collateral("customer_demo", collateral["id"])["summary"]["total"] == 0
    generated = service.generate_project_artifacts("customer_demo", collateral["id"])
    assert generated["execution_candidate"] == "procedural"
    assert generated["files"]["uvm"]["status"] == "review_only"
    review = service.repair_project_collateral("customer_demo", collateral["id"], service.RepairRequest(before="module", after="module", rationale="test"))
    assert review["proposal"]["status"] == "review_required"
    ported = service.add_collateral("customer_demo", service.CollateralRequest(name="ports.sv", kind="rtl", content="module ports(input logic data); endmodule\n"))
    service.ingest_project_collateral("customer_demo", ported["id"])
    service.plan_project_collateral("customer_demo", ported["id"])
    generated_ports = service.generate_project_artifacts("customer_demo", ported["id"])
    assert "logic data;" in Path(generated_ports["files"]["uvm"]["path"]).read_text()


def test_agent_proposal_endpoint_persists_grounded_reviewable_record(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_job(service.JobRequest(project_id="agent-project"))
    proposal = service.submit_agent_proposal("agent-project", service.AgentProposalRequest(
        proposal_id="diag-1", kind="diagnosis", source_revision="rtl-1",
        action="inspect counter_q dependency cone", rationale="first divergence is cycle 1",
        evidence=["triage-report.json", "waveform.vcd"],
    ))
    assert proposal["execution_authority"] == "deterministic-only"
    assert proposal["proposal"]["status"] == "proposal"
    assert Path(proposal["proposal_path"]).is_file()


def test_agent_proposal_endpoint_rejects_closure_claim(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_job(service.JobRequest(project_id="agent-project"))
    with pytest.raises(service.HTTPException) as error:
        service.submit_agent_proposal("agent-project", service.AgentProposalRequest(
            proposal_id="bad", kind="diagnosis", source_revision="rtl-1",
            action="close", rationale="looks good", evidence=["report.json"], claims=["proven"],
        ))
    assert error.value.status_code == 422


def test_agentic_closure_endpoint_exposes_verified_claim_boundary(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / ".artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v3-20260913/agentic-hardware-release-manifest.json"
    if not source.is_file():
        pytest.skip("agentic closure artifact is not present in this checkout")
    bundle = tmp_path / "bundle"
    shutil.copytree(source.parent, bundle)
    manifest = bundle / "agentic-hardware-release-manifest.json"
    monkeypatch.setenv("VERIFICATION_AGENTIC_RELEASE_MANIFEST_PATH", str(manifest))
    response = TestClient(service.app).get("/v1/agentic-closure")
    assert response.status_code == 200
    payload = response.json()
    assert payload["release_decision"] == "blocked_pending_human_approval"
    assert payload["analog_authorized"] is False
    assert payload["claims"]["analog_hardware"]["status"] == "unauthorized"


def test_agentic_closure_signoff_is_digest_bound_and_persisted(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / ".artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913/agentic-hardware-release-manifest.json"
    if not source.is_file():
        pytest.skip("agentic closure artifact is not present in this checkout")
    bundle = tmp_path / "bundle"
    shutil.copytree(source.parent, bundle)
    manifest = bundle / "agentic-hardware-release-manifest.json"
    monkeypatch.setenv("VERIFICATION_AGENTIC_RELEASE_MANIFEST_PATH", str(manifest))
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    client = TestClient(service.app)
    stale = client.post("/v1/agentic-closure/signoff", json={"reviewer": "lead", "notes": "stale", "approved": True, "manifest_sha256": "0" * 64})
    assert stale.status_code == 409
    started = datetime.now(timezone.utc).isoformat()
    signed = client.post("/v1/agentic-closure/signoff", json={"reviewer": "lead", "notes": "reviewed evidence", "approved": True, "manifest_sha256": payload["manifest_sha256"], "reviewer_subject": "oidc|lead", "review_started_at": started})
    assert signed.status_code == 200
    assert signed.json()["status"] == "approved"
    assert signed.json()["review_duration_seconds"] >= 0
    assert signed.json()["release_manifest_sha256"]
    current = client.get("/v1/agentic-closure")
    assert current.status_code == 200
    assert current.json()["human_signoff"]["status"] == "approved"
    assert current.json()["human_review_effort"]["status"] == "measured"
    assert current.json()["manifest_sha256"] == signed.json()["release_manifest_sha256"]


def test_agentic_closure_signoff_rebuilds_non_fixture_release(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / ".artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913/agentic-hardware-release-manifest.json"
    if not source.is_file():
        pytest.skip("agentic closure artifact is not present in this checkout")
    bundle = tmp_path / "bundle"
    shutil.copytree(source.parent, bundle)
    summary = bundle / "closure-summary.json"
    closure = json.loads(summary.read_text(encoding="utf-8"))
    closure["approval"]["reviewer"] = "human-reviewer@example.com"
    closure["approval"]["note"] = "Synthetic integration fixture; validates state transition only."
    summary.write_text(json.dumps(closure, indent=2) + "\n", encoding="utf-8")
    manifest = bundle / "agentic-hardware-release-manifest.json"
    rebuilt = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "scripts/build_agentic_hardware_release_manifest.py"), "--closure-summary", str(summary), "--output", str(manifest)], capture_output=True, text=True, check=False)
    assert rebuilt.returncode == 0, rebuilt.stderr
    monkeypatch.setenv("VERIFICATION_AGENTIC_RELEASE_MANIFEST_PATH", str(manifest))
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    started = datetime.now(timezone.utc).isoformat()
    response = TestClient(service.app).post("/v1/agentic-closure/signoff", json={"reviewer": "human-reviewer@example.com", "notes": "Synthetic integration fixture; validates state transition only.", "approved": True, "manifest_sha256": payload["manifest_sha256"], "reviewer_subject": "oidc|human-reviewer", "review_started_at": started})
    assert response.status_code == 200
    current = TestClient(service.app).get("/v1/agentic-closure")
    assert current.status_code == 200
    assert current.json()["release_decision"] == "passed"
    assert current.json()["human_review_effort"]["status"] == "measured"


def test_agentic_closure_signoff_rejects_empty_human_record(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / ".artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913/agentic-hardware-release-manifest.json"
    if not source.is_file():
        pytest.skip("agentic closure artifact is not present in this checkout")
    bundle = tmp_path / "bundle"
    shutil.copytree(source.parent, bundle)
    manifest = bundle / "agentic-hardware-release-manifest.json"
    monkeypatch.setenv("VERIFICATION_AGENTIC_RELEASE_MANIFEST_PATH", str(manifest))
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    response = TestClient(service.app).post("/v1/agentic-closure/signoff", json={"reviewer": " ", "notes": " ", "approved": True, "manifest_sha256": payload["manifest_sha256"]})
    assert response.status_code == 422


def test_registered_customer_adapter_is_executable_and_evidence_bound(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{
        "name": "customer-sim",
        "kind": "simulation",
        "executable": "python3",
        "expected_artifacts": ["simulation/result.json"],
        "timeout_seconds": 30,
    }]))
    created = service.create_job(service.JobRequest(
        kind="customer-adapter",
        project_id="adapter-project",
        adapter_name="customer-sim",
        adapter_args=["-c", "from pathlib import Path; Path('simulation').mkdir(); Path('simulation/result.json').write_text('{\\\"status\\\":\\\"passed\\\"}')"],
    ))
    finished = service.run_job(created["id"])
    assert finished["status"] == "passed"
    assert finished["evidence"]["adapter_result"].endswith("adapter-result.json")
    payload = json.loads(Path(finished["evidence"]["adapter_result"]).read_text())
    assert payload["tool"] == "customer-sim"
    assert payload["status"] == "passed"
    assert payload["artifacts"]
    assert "-c" in payload["command"]
    evidence = service.project_job_evidence(created["id"])
    assert evidence["files"]["adapter-result.json"]["present"] is True
    assert evidence["job"]["adapter_name"] == "customer-sim"
    assert evidence["job"]["adapter_args_count"] == 2
    assert "passed\\\"}')" not in json.dumps(evidence["job"])
    report = service.project_proof_of_value(created["id"])
    assert report["schema_version"] == "verification-adapter-pov-v1"
    assert service.get_job(created["id"])["evidence"]["adapter_pov"].endswith("adapter-proof-of-value-report.json")
    signed = service.signoff_project_job(created["id"], service.SignoffRequest(reviewer="lead", notes="adapter evidence reviewed", approved=True))
    assert signed["status"] == "approved"
    dashboard = service.project_dashboard("adapter-project")
    assert dashboard["terminal_jobs"][0]["adapter_name"] == "customer-sim"
    assert dashboard["terminal_jobs"][0]["adapter_args_count"] == 2
    audit = service.project_audit("adapter-project")
    assert audit["entries"][-1]["adapter_name"] == "customer-sim"
    assert audit["entries"][-1]["adapter_args_count"] == 2
    assert "secret" not in json.dumps(audit)


def test_blocked_customer_adapter_cannot_be_queued(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{"name": "missing", "kind": "simulation", "executable": "definitely-not-installed"}]))
    with pytest.raises(service.HTTPException) as error:
        service.create_job(service.JobRequest(kind="customer-adapter", project_id="adapter-project", adapter_name="missing"))
    assert error.value.status_code == 409


def test_customer_adapter_arguments_are_bounded_before_queueing(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{"name": "customer-sim", "kind": "simulation", "executable": "python3"}]))
    with pytest.raises(service.HTTPException) as error:
        service.create_job(service.JobRequest(kind="customer-adapter", project_id="bounded", adapter_name="customer-sim", adapter_args=["x"] * 65))
    assert error.value.status_code == 400
    assert "at most 64" in error.value.detail


def test_customer_adapter_source_artifact_is_project_scoped(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{"name": "customer-sim", "kind": "simulation", "executable": "python3"}]))
    service.create_project(service.ProjectRequest(id="source-project", name="Source"))
    source = service.add_collateral("source-project", service.CollateralRequest(name="design.sv", kind="rtl", content="module design; endmodule"))
    with pytest.raises(service.HTTPException) as error:
        service.create_job(service.JobRequest(kind="customer-adapter", project_id="other-project", artifact_id=source["id"], adapter_name="customer-sim"))
    assert error.value.status_code == 404


def test_customer_adapter_http_submission_uses_published_contract(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{"name": "customer-sim", "kind": "simulation", "executable": "python3"}]))
    response = TestClient(service.app).post("/v1/jobs", json={
        "kind": "customer-adapter",
        "project_id": "http-adapter",
        "adapter_name": "customer-sim",
        "adapter_args": ["--token", "secret-value"],
    })
    assert response.status_code == 202
    payload = response.json()
    assert payload["kind"] == "customer-adapter"
    assert payload["adapter_name"] == "customer-sim"
    assert payload["adapter_args_count"] == 2
    assert "adapter_args" not in payload
    assert "secret-value" not in response.text
    fetched = TestClient(service.app).get(f"/v1/jobs/{payload['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["adapter_args_count"] == 2
    assert "adapter_args" not in fetched.json()
    assert "secret-value" not in fetched.text
    listed = TestClient(service.app).get("/v1/jobs?project_id=http-adapter")
    assert listed.status_code == 200
    assert listed.json()[0]["adapter_args_count"] == 2
    assert "adapter_args" not in listed.json()[0]
    assert "secret-value" not in listed.text
    dashboard = TestClient(service.app).get("/v1/projects/http-adapter/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["terminal_jobs"] == []


def test_customer_adapter_http_pov_and_signoff_are_hash_bound(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{"name": "customer-sim", "kind": "simulation", "executable": "python3", "expected_artifacts": ["result.json"]}]))
    created = service.create_job(service.JobRequest(kind="customer-adapter", project_id="http-signoff", adapter_name="customer-sim", adapter_args=["-c", "from pathlib import Path; Path('result.json').write_text('{}')"]))
    service.run_job(created["id"])
    client = TestClient(service.app)
    report = client.get(f"/v1/jobs/{created['id']}/proof-of-value")
    assert report.status_code == 200
    assert report.json()["schema_version"] == "verification-adapter-pov-v1"
    signed = client.post(f"/v1/jobs/{created['id']}/signoff", json={"reviewer": "lead", "notes": "adapter report reviewed", "approved": True})
    assert signed.status_code == 200
    assert signed.json()["report_sha256"] == report.json()["report_sha256"]
    assert "report_path" not in signed.json()


def test_blocked_customer_adapter_pov_is_not_signable(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{"name": "customer-sim", "kind": "simulation", "executable": "python3"}]))
    created = service.create_job(service.JobRequest(kind="customer-adapter", project_id="blocked-adapter", adapter_name="customer-sim", adapter_args=["-c", "raise SystemExit(3)"]))
    finished = service.run_job(created["id"])
    assert finished["status"] == "failed"
    # A failed tool run remains reviewable, but the adapter report is still
    # eligible for a human decision; a blocked status is explicitly rejected.
    job = service._read(created["id"])
    job["status"] = "blocked"
    service._write(job)
    report = service.project_proof_of_value(created["id"])
    assert report["status"] == "blocked"
    with pytest.raises(service.HTTPException) as error:
        service.signoff_project_job(created["id"], service.SignoffRequest(reviewer="lead", notes="cannot approve blocked run", approved=True))
    assert error.value.status_code == 409


def test_job_workspace_is_private_and_symlinked_root_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    job = service.create_job(service.JobRequest(project_id="workspace"))
    workspace = service._prepare_job_workspace(job["id"])
    assert workspace.is_dir()
    assert workspace.stat().st_mode & 0o777 == 0o700
    target = tmp_path / "outside"
    target.mkdir()
    symlinked = service._path(job["id"]).parent
    service._path(job["id"]).unlink()
    symlinked.rmdir()
    symlinked.symlink_to(target, target_is_directory=True)
    with pytest.raises(Exception) as error:
        service._prepare_job_workspace(job["id"])
    assert getattr(error.value, "status_code", None) == 409


def test_project_creation_requires_trusted_subject_when_identity_mode_enabled(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "true")
    client = TestClient(service.app)
    missing = client.post("/v1/projects", json={"id": "identity-missing", "name": "Missing"})
    assert missing.status_code == 403
    trusted = client.post("/v1/projects", headers={"X-Identity-Subject": "oidc|creator-1"}, json={"id": "identity-owned", "name": "Owned"})
    assert trusted.status_code == 201
    assert trusted.json()["id"] == "identity-owned"


def test_project_subject_map_denies_cross_tenant_reads(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_project(service.ProjectRequest(id="tenant-a", name="Tenant A"))
    monkeypatch.setenv("VERIFICATION_PROJECT_SUBJECTS", json.dumps({"tenant-a": ["oidc|alice"]}))
    client = TestClient(service.app)
    denied = client.get("/v1/projects/tenant-a", headers={"X-Identity-Subject": "oidc|bob"})
    assert denied.status_code == 403
    allowed = client.get("/v1/projects/tenant-a", headers={"X-Identity-Subject": "oidc|alice"})
    assert allowed.status_code == 200


def test_oidc_bearer_claims_drive_project_identity_context(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_TOKEN", "true")
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "true")
    monkeypatch.setattr(service, "_oidc_verifier", lambda: type("Verifier", (), {"verify": lambda self, token: service.IdentityClaims("oidc|alice", frozenset({"verification-reviewer"}), "https://issuer", "verification")})())
    client = TestClient(service.app)
    created = client.post("/v1/projects", headers={"Authorization": "Bearer valid-token"}, json={"id": "oidc-project", "name": "OIDC Project"})
    assert created.status_code == 201
    missing = client.post("/v1/projects", json={"id": "oidc-missing", "name": "Missing"})
    assert missing.status_code == 401

def test_signoff_receipt_endpoint_reports_digest_validity(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_project(service.ProjectRequest(id="receipt", name="Receipt"))
    rtl = service.add_collateral("receipt", service.CollateralRequest(name="dut.sv", kind="rtl", content="module dut; endmodule\n"))
    tb = service.add_collateral("receipt", service.CollateralRequest(name="tb.sv", kind="testbench", content="module tb; endmodule\n"))
    job = service.create_job(service.JobRequest(kind="project-simulation", project_id="receipt", artifact_id=rtl["id"], testbench_artifact_id=tb["id"]))
    job.update({"status": "passed", "events": [{"status": "queued"}, {"status": "passed"}]})
    service._write(job)
    root = service._path(job["id"]).parent
    (root / "project-simulation-result.json").write_text(json.dumps({"project_id": "receipt", "status": "passed", "rtl_artifact_id": rtl["id"], "testbench_artifact_id": tb["id"], "compile_run": {"status": "passed"}, "simulation_run": {"status": "passed"}}))
    (root / "closure-report.json").write_text("[]")
    service.project_proof_of_value(job["id"])
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "true")
    with pytest.raises(Exception) as missing_subject:
        service.signoff_project_job(job["id"], service.SignoffRequest(reviewer="lead", notes="checked", approved=True))
    assert getattr(missing_subject.value, "status_code", None) == 403
    client = TestClient(service.app)
    spoofed = client.post(f"/v1/jobs/{job['id']}/signoff", json={"reviewer": "lead", "notes": "checked", "approved": True, "reviewer_subject": "spoofed"})
    assert spoofed.status_code == 403
    trusted = client.post(f"/v1/jobs/{job['id']}/signoff", headers={"X-Identity-Subject": "oidc|http-lead"}, json={"reviewer": "lead", "notes": "checked", "approved": True, "reviewer_subject": "spoofed"})
    assert trusted.status_code == 200
    assert trusted.json()["reviewer_subject"] == "oidc|http-lead"
    bound = service.signoff_project_job(job["id"], service.SignoffRequest(reviewer="lead", notes="checked", approved=True, reviewer_subject="oidc|lead-1"))
    assert bound["reviewer_subject"] == "oidc|lead-1"
    receipt = service.signoff_project_job(job["id"], service.SignoffRequest(reviewer="lead", notes="checked", approved=True, reviewer_subject="oidc|lead-1"))
    assert service.get_signoff_project_job(job["id"])["valid"] is True
    (root / "proof-of-value-report.json").write_text(json.dumps({"report_sha256": "tampered"}))
    assert service.get_signoff_project_job(job["id"])["valid"] is False


def test_signoff_requires_asserted_reviewer_role_when_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_project(service.ProjectRequest(id="role", name="Role"))
    rtl = service.add_collateral("role", service.CollateralRequest(name="dut.sv", kind="rtl", content="module dut; endmodule\n"))
    tb = service.add_collateral("role", service.CollateralRequest(name="tb.sv", kind="testbench", content="module tb; endmodule\n"))
    job = service.create_job(service.JobRequest(kind="project-simulation", project_id="role", artifact_id=rtl["id"], testbench_artifact_id=tb["id"]))
    job.update({"status": "passed", "events": [{"status": "passed"}]})
    service._write(job)
    root = service._path(job["id"]).parent
    (root / "project-simulation-result.json").write_text(json.dumps({"project_id": "role", "status": "passed", "rtl_artifact_id": rtl["id"], "testbench_artifact_id": tb["id"], "compile_run": {"status": "passed"}, "simulation_run": {"status": "passed"}}))
    (root / "proof-of-value-report.json").write_text(json.dumps({"report_sha256": "a" * 64}))
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "true")
    monkeypatch.setenv("VERIFICATION_REVIEWER_ROLE", "verification-reviewer")
    client = TestClient(service.app)
    denied = client.post(f"/v1/jobs/{job['id']}/signoff", headers={"X-Identity-Subject": "oidc|reviewer", "X-Identity-Roles": "engineer"}, json={"reviewer": "lead", "notes": "checked", "approved": True})
    assert denied.status_code == 403
    allowed = client.post(f"/v1/jobs/{job['id']}/signoff", headers={"X-Identity-Subject": "oidc|reviewer", "X-Identity-Roles": "engineer, verification-reviewer"}, json={"reviewer": "lead", "notes": "checked", "approved": True})
    assert allowed.status_code == 200

def test_async_run_submission_is_nonblocking_for_queued_job(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    created = service.create_job(service.JobRequest())
    tasks = BackgroundTasks()
    response = service.run_job_async(created["id"], tasks)
    assert response == {"id": created["id"], "status": "accepted", "poll": f"/v1/jobs/{created['id']}"}
    assert tasks.tasks == []
    service._write({**created, "status": "passed"})
    bundle = service.get_bundle(created["id"])
    assert bundle["job_id"] == created["id"]
    assert Path(bundle["bundle_path"]).is_file()
    assert bundle["object_key"] == f"jobs/{created['id']}/evidence-bundle.zip"
    assert len(bundle["bundle_sha256"]) == 64
    assert service._evidence_store().get(bundle["object_key"]).sha256 == bundle["bundle_sha256"]
    with zipfile.ZipFile(bundle["bundle_path"]) as archive:
        names = set(archive.namelist())
    assert "multi_design_pilot/runs/latest/pilot-summary.json" in names
    assert "seeded_counter/runs/latest/artifact-manifest.json" in names
    Path(bundle["bundle_path"]).unlink()
    restored = service.get_bundle(created["id"])
    assert Path(restored["bundle_path"]).is_file()
    assert restored["bundle_sha256"] == bundle["bundle_sha256"]
    downloaded = service.download_bundle(created["id"])
    assert downloaded.media_type == "application/zip"
    assert json.loads((tmp_path / "jobs" / created["id"] / "job.json").read_text())["status"] == "passed"

def test_job_admission_control_rejects_full_backlog(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_MAX_QUEUED_JOBS", "1")
    first = service.create_job(service.JobRequest())
    try:
        service.create_job(service.JobRequest())
    except Exception as error:
        assert getattr(error, "status_code", None) == 429
    else:
        raise AssertionError("expected queue capacity rejection")
    assert service.get_job(first["id"])["status"] == "queued"

def test_job_idempotency_returns_existing_submission(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    first = service.create_job(service.JobRequest(project_id="p1", idempotency_key="pilot-001"))
    second = service.create_job(service.JobRequest(project_id="p1", idempotency_key="pilot-001"))
    assert second["id"] == first["id"]
    assert len(service.list_jobs(project_id="p1")) == 1


def test_job_persists_request_correlation_id(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    token = service._REQUEST_ID.set("pilot-trace-42")
    try:
        created = service.create_job(service.JobRequest(project_id="trace"))
    finally:
        service._REQUEST_ID.reset(token)
    assert created["request_id"] == "pilot-trace-42"
    assert service.get_job(created["id"])["request_id"] == "pilot-trace-42"
    assert service.get_job(created["id"])["events"][0]["request_id"] == "pilot-trace-42"

def test_project_audit_export_is_bounded_and_redacts_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_project(service.ProjectRequest(id="audit", name="Audit"))
    token = service._REQUEST_ID.set("audit-trace-1")
    try:
        created = service.create_job(service.JobRequest(project_id="audit"))
    finally:
        service._REQUEST_ID.reset(token)
    job = service.get_job(created["id"])
    job["events"].append({"status": "failed", "at": "2026-01-01T00:00:00+00:00", "error": "tool failed at /secret/internal.log", "path": "/secret/internal.log"})
    service._write(job)
    export = service.project_audit("audit", limit=1)
    assert export["schema_version"] == "verification-audit-v1"
    assert export["total"] == 2
    assert export["truncated"] is True
    assert export["entries"][0]["request_id"] == "audit-trace-1"
    assert all("path" not in entry for entry in export["entries"])
    full_export = service.project_audit("audit", limit=2)
    assert "tool failed at [PATH]" in {entry["reason"] for entry in full_export["entries"]}
    assert len(export["export_sha256"]) == 64
    job["events"].append({"status": "cancelled", "at": "2026-01-02T00:00:00+00:00"})
    service._write(job)
    changed = service.project_audit("audit", limit=2)
    assert changed["export_sha256"] != export["export_sha256"]


def test_project_audit_http_route_enforces_project_key(monkeypatch, tmp_path):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_SERVICE_API_KEY", "api-secret")
    monkeypatch.setenv("VERIFICATION_PROJECT_KEYS", '{"audit-http":"project-secret"}')
    service.create_project(service.ProjectRequest(id="audit-http", name="Audit HTTP"))
    client = TestClient(service.app)
    allowed = client.get("/v1/projects/audit-http/audit", headers={"X-API-Key": "api-secret", "X-Project-Key": "project-secret", "X-Request-ID": "audit-http-1"})
    assert allowed.status_code == 200
    assert allowed.headers["cache-control"] == "no-store"
    assert allowed.json()["export_sha256"]
    denied = client.get("/v1/projects/audit-http/audit", headers={"X-API-Key": "api-secret", "X-Project-Key": "wrong", "X-Request-ID": "audit-http-2"})
    assert denied.status_code == 403
    assert denied.headers["x-request-id"] == "audit-http-2"


def test_job_routes_and_project_filtered_listing_enforce_owner_project_key(monkeypatch, tmp_path):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    monkeypatch.setenv("VERIFICATION_SERVICE_API_KEY", "api-secret")
    monkeypatch.setenv("VERIFICATION_PROJECT_KEYS", '{"owner-a":"key-a","owner-b":"key-b"}')
    service.create_project(service.ProjectRequest(id="owner-a", name="Owner A"))
    service.create_project(service.ProjectRequest(id="owner-b", name="Owner B"))
    job = service.create_job(service.JobRequest(project_id="owner-a", kind="multi-design-pilot"))
    client = TestClient(service.app)
    headers = {"X-API-Key": "api-secret", "X-Project-Key": "key-a"}
    project_list = client.get("/v1/projects", headers=headers)
    assert project_list.status_code == 200
    assert [project["id"] for project in project_list.json()] == ["owner-a"]
    assert client.get("/v1/jobs?project_id=owner-a", headers=headers).status_code == 200
    assert client.get("/v1/jobs/" + job["id"], headers=headers).status_code == 200
    created = client.post("/v1/jobs", headers=headers, json={"project_id": "owner-a", "kind": "multi-design-pilot"})
    assert created.status_code == 202
    other_job = service.create_job(service.JobRequest(project_id="owner-b", kind="multi-design-pilot"))
    wrong = {"X-API-Key": "api-secret", "X-Project-Key": "key-b"}
    assert client.get("/v1/projects", headers={"X-API-Key": "api-secret"}).status_code == 403
    assert [project["id"] for project in client.get("/v1/projects", headers=wrong).json()] == ["owner-b"]
    assert client.get("/v1/jobs?project_id=owner-a", headers=wrong).status_code == 403
    assert client.get("/v1/jobs/" + job["id"], headers=wrong).status_code == 403
    assert client.post("/v1/jobs", headers=wrong, json={"project_id": "owner-a", "kind": "multi-design-pilot"}).status_code == 403
    compare = client.get(f"/v1/jobs/{job['id']}/compare/{other_job['id']}", headers=headers)
    assert compare.status_code == 403

def test_job_idempotency_rejects_key_payload_collision(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_job(service.JobRequest(project_id="p1", idempotency_key="pilot-001", kind="multi-design-pilot"))
    try:
        service.create_job(service.JobRequest(project_id="p1", idempotency_key="pilot-001", kind="project-compile", artifact_id="missing"))
    except Exception as error:
        assert getattr(error, "status_code", None) == 409
    else:
        raise AssertionError("idempotency key collision must be rejected")

def test_project_dashboard_aggregates_jobs_collateral_and_signoffs(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_project(service.ProjectRequest(id="p1", name="Project one"))
    service.add_collateral("p1", service.CollateralRequest(name="spec.md", kind="specification", content="REQ-RST: reg0 resets to zero"))
    job = service.create_job(service.JobRequest(project_id="p1", idempotency_key="pilot-1"))
    service._write({**job, "status": "passed"})
    dashboard = service.project_dashboard("p1")
    assert dashboard["collateral_count"] == 1
    assert dashboard["jobs"]["passed"] == 1
    assert dashboard["terminal_jobs"][0]["id"] == job["id"]

def test_project_compile_job_runs_uploaded_rtl(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    project = service.create_project(service.ProjectRequest(id="p1", name="Project one"))
    assert project["id"] == "p1"
    collateral = service.add_collateral("p1", service.CollateralRequest(name="counter.sv", kind="rtl", version="r7", content="module counter(input logic clk); endmodule\n"))
    created = service.create_job(service.JobRequest(kind="project-compile", project_id="p1", artifact_id=collateral["id"]))
    finished = service.run_job(created["id"])
    assert finished["status"] == "passed"
    assert finished["evidence"]["project_compile"].endswith("project-compile-result.json")
    lint_job = service.create_job(service.JobRequest(kind="project-lint", project_id="p1", artifact_id=collateral["id"]))
    lint_finished = service.run_job(lint_job["id"])
    assert lint_finished["status"] == "passed"
    assert lint_finished["evidence"]["project_lint"].endswith("project-lint-result.json")
    formal_job = service.create_job(service.JobRequest(kind="project-formal", project_id="p1", artifact_id=collateral["id"]))
    formal_finished = service.run_job(formal_job["id"])
    assert formal_finished["status"] == "passed"
    assert formal_finished["evidence"]["project_formal"].endswith("project-formal-result.json")
    proof_job = service.create_job(service.JobRequest(kind="project-formal-proof", project_id="p1", artifact_id=collateral["id"], formal_signal="clk", formal_expected="0"))
    proof_finished = service.run_job(proof_job["id"])
    assert proof_finished["status"] in {"passed", "failed", "blocked"}
    assert proof_finished["evidence"]["project_formal_proof"].endswith("project-formal-proof-result.json")

def test_project_simulation_job_persists_failure_triage(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_project(service.ProjectRequest(id="p1", name="Project one"))
    rtl = service.add_collateral("p1", service.CollateralRequest(name="counter.sv", kind="rtl", content="module counter(input logic clk, output logic q); always_ff @(posedge clk) q <= 1'b0; endmodule\n"))
    tb = service.add_collateral("p1", service.CollateralRequest(name="counter_tb.sv", kind="testbench", content='''module counter_tb; logic clk=0; logic q; counter dut(.clk(clk),.q(q)); always #5 clk=~clk; initial begin $dumpfile("waveform.vcd"); $dumpvars(0,counter_tb); #7; $display("FAIL cycle=1 signal=q expected=1 actual=%0d",q); #8 $finish; end endmodule\n'''))
    created = service.create_job(service.JobRequest(kind="project-simulation", project_id="p1", artifact_id=rtl["id"], testbench_artifact_id=tb["id"]))
    finished = service.run_job(created["id"])
    assert finished["status"] == "failed"
    assert finished["evidence"]["project_simulation"].endswith("project-simulation-result.json")
    assert finished["evidence_objects"]
    assert all(len(item["sha256"]) == 64 for item in finished["evidence_objects"].values())
    result_path = Path(finished["evidence"]["project_simulation"])
    result_path.unlink()
    recovered_evidence = service.project_job_evidence(created["id"])
    assert recovered_evidence["files"]["project-simulation-result.json"]["present"] is True
    pov = service.project_proof_of_value(created["id"])
    assert pov["execution"]["status"] == "failed"
    assert pov["coverage"]["percentage"] == 0.0
    bundle = service.get_bundle(created["id"])
    assert bundle["status"] == "failed"
    assert len(bundle["bundle_sha256"]) == 64
    with zipfile.ZipFile(bundle["bundle_path"]) as archive:
        names = set(archive.namelist())
    assert "project-simulation-result.json" in names
    assert "verification-ir.json" in names
    assert "diagnosis.json" in names
    review = service.repair_retest_job(created["id"], service.RepairRequest(before="always_ff", after="always_ff", rationale="review selected RTL change"))
    assert review["retest_job"] is None
    approved = service.repair_retest_job(created["id"], service.RepairRequest(before="always_ff", after="always_ff", rationale="review selected RTL change", approved=True))
    assert approved["retest_job"]["kind"] == "project-simulation"
    assert approved["retest_job"]["status"] == "queued"
    retest_finished = service.run_job(approved["retest_job"]["id"])
    comparison = service.compare_project_jobs(created["id"], retest_finished["id"])
    assert comparison["metrics"]["failure_resolved"] is False

def test_project_regression_job_and_pov_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_project(service.ProjectRequest(id="p1", name="Project one"))
    rtl = service.add_collateral("p1", service.CollateralRequest(name="counter.sv", kind="rtl", content="module counter(input logic clk); endmodule\n"))
    tb_text = 'module tb; initial begin $dumpfile("waveform.vcd"); $dumpvars; $display("COVERAGE kind=functional covered=1 total=1"); $finish; end endmodule\n'
    tb1 = service.add_collateral("p1", service.CollateralRequest(name="tb1.sv", kind="testbench", content=tb_text))
    tb2 = service.add_collateral("p1", service.CollateralRequest(name="tb2.sv", kind="testbench", content=tb_text))
    created = service.create_job(service.JobRequest(kind="project-regression", project_id="p1", artifact_id=rtl["id"], testbench_artifact_ids=[tb1["id"], tb2["id"]]))
    finished = service.run_job(created["id"])
    assert finished["status"] == "passed"
    report = service.project_regression_proof_of_value(created["id"])
    assert report["case_count"] == 2
    assert report["coverage"]["percentage"] == 100.0
    signoff = service.signoff_project_job(created["id"], service.SignoffRequest(reviewer="lead", notes="reviewed regression evidence", approved=True))
    assert signoff["status"] == "approved"
    assert signoff["report_sha256"] == report["report_sha256"]
