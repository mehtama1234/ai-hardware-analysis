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
