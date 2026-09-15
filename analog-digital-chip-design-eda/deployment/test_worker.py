from deployment import worker
import deployment.verification_service as service
import json
from pathlib import Path


def test_worker_process_once_empty_queue(tmp_path, monkeypatch):
    monkeypatch.setattr(worker, "JOB_ROOT", tmp_path / "jobs")
    assert worker.process_once() is False


def test_worker_processes_project_compile_job(tmp_path, monkeypatch):
    root = tmp_path / "jobs"
    monkeypatch.setattr(worker, "JOB_ROOT", root)
    monkeypatch.setattr(service, "JOB_ROOT", root)
    service.create_project(service.ProjectRequest(id="p1", name="Project one"))
    collateral = service.add_collateral("p1", service.CollateralRequest(name="counter.sv", kind="rtl", content="module counter(input logic clk); endmodule\n"))
    token = service._REQUEST_ID.set("worker-trace-7")
    try:
        created = service.create_job(service.JobRequest(kind="project-compile", project_id="p1", artifact_id=collateral["id"]))
    finally:
        service._REQUEST_ID.reset(token)
    assert worker.process_once(job_timeout_seconds=30) is True
    finished = service.get_job(created["id"])
    assert finished["status"] == "passed"
    assert finished["evidence"]["project_compile"].endswith("project-compile-result.json")
    assert all(event["request_id"] == "worker-trace-7" for event in finished["events"])


def test_worker_persists_bounded_redacted_exception(tmp_path, monkeypatch):
    root = tmp_path / "jobs"
    monkeypatch.setattr(worker, "JOB_ROOT", root)
    monkeypatch.setattr(service, "JOB_ROOT", root)
    created = service.create_job(service.JobRequest(project_id="p1"))
    monkeypatch.setattr(worker, "_prepare_job_workspace", lambda _job_id: (_ for _ in ()).throw(RuntimeError("adapter failed at /srv/customer/secret.log")))
    assert worker.process_once() is True
    finished = service.get_job(created["id"])
    assert finished["status"] == "failed"
    assert "[PATH]" in finished["error"]
    assert "/srv/customer" not in finished["error"]
    assert finished["events"][-1]["reason"] == "worker_exception"


def test_worker_executes_registered_customer_adapter(tmp_path, monkeypatch):
    root = tmp_path / "jobs"
    monkeypatch.setattr(worker, "JOB_ROOT", root)
    monkeypatch.setattr(service, "JOB_ROOT", root)
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", json.dumps([{
        "name": "customer-regression",
        "kind": "regression",
        "executable": "python3",
        "expected_artifacts": ["results/summary.json"],
        "timeout_seconds": 30,
    }]))
    created = service.create_job(service.JobRequest(
        kind="customer-adapter",
        project_id="worker-adapter",
        adapter_name="customer-regression",
        adapter_args=["-c", "from pathlib import Path; Path('results').mkdir(); Path('results/summary.json').write_text('{}')"],
    ))
    assert worker.process_once(job_timeout_seconds=30) is True
    finished = service.get_job(created["id"])
    assert finished["status"] == "passed"
    assert finished["evidence"]["adapter_result"].endswith("adapter-result.json")
    assert Path(finished["evidence"]["adapter_result"]).is_file()
