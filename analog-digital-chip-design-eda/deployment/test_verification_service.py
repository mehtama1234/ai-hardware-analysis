import json
from pathlib import Path
import zipfile
import deployment.verification_service as service
from fastapi import BackgroundTasks

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
    with zipfile.ZipFile(bundle["bundle_path"]) as archive:
        names = set(archive.namelist())
    assert "multi_design_pilot/runs/latest/pilot-summary.json" in names
    assert "seeded_counter/runs/latest/artifact-manifest.json" in names
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

def test_job_idempotency_rejects_key_payload_collision(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "JOB_ROOT", tmp_path / "jobs")
    service.create_job(service.JobRequest(project_id="p1", idempotency_key="pilot-001", kind="multi-design-pilot"))
    try:
        service.create_job(service.JobRequest(project_id="p1", idempotency_key="pilot-001", kind="project-compile", artifact_id="missing"))
    except Exception as error:
        assert getattr(error, "status_code", None) == 409
    else:
        raise AssertionError("idempotency key collision must be rejected")

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
    assert proof_finished["status"] in {"passed", "failed"}
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
    pov = service.project_proof_of_value(created["id"])
    assert pov["execution"]["status"] == "failed"
    assert pov["coverage"]["percentage"] == 0.0
    bundle = service.get_bundle(created["id"])
    assert bundle["status"] == "failed"
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
