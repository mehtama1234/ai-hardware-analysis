from deployment import worker
import deployment.verification_service as service


def test_worker_process_once_empty_queue(tmp_path, monkeypatch):
    monkeypatch.setattr(worker, "JOB_ROOT", tmp_path / "jobs")
    assert worker.process_once() is False


def test_worker_processes_project_compile_job(tmp_path, monkeypatch):
    root = tmp_path / "jobs"
    monkeypatch.setattr(worker, "JOB_ROOT", root)
    monkeypatch.setattr(service, "JOB_ROOT", root)
    service.create_project(service.ProjectRequest(id="p1", name="Project one"))
    collateral = service.add_collateral("p1", service.CollateralRequest(name="counter.sv", kind="rtl", content="module counter(input logic clk); endmodule\n"))
    created = service.create_job(service.JobRequest(kind="project-compile", project_id="p1", artifact_id=collateral["id"]))
    assert worker.process_once(job_timeout_seconds=30) is True
    finished = service.get_job(created["id"])
    assert finished["status"] == "passed"
    assert finished["evidence"]["project_compile"].endswith("project-compile-result.json")
