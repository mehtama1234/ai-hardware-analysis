"""Exercise the open-source worker through a real project PoV."""

import json
from pathlib import Path

from deployment import verification_service as service
from deployment import worker


def test_worker_executes_bound_simulation_and_produces_run_report(tmp_path, monkeypatch):
    jobs = tmp_path / "jobs"
    monkeypatch.setattr(service, "JOB_ROOT", jobs)
    monkeypatch.setattr(worker, "JOB_ROOT", jobs)
    project = service.create_project(service.ProjectRequest(id="e2e", name="E2E"))
    rtl = service.add_collateral(
        project["id"],
        service.CollateralRequest(
            name="counter.sv",
            kind="rtl",
            content="module counter(output wire done); assign done = 1'b1; endmodule\n",
        ),
    )
    tb = service.add_collateral(
        project["id"],
        service.CollateralRequest(
            name="counter_tb.sv",
            kind="testbench",
            content=(
                "module counter_tb; wire done; counter dut(done); "
                "initial begin $dumpfile(\"waveform.vcd\"); $dumpvars(0,counter_tb); "
                "#1; if (!done) $fatal(1, \"FAILED\"); "
                "$display(\"COVERAGE functional 1/1\"); $finish; end endmodule\n"
            ),
        ),
    )
    job = service.create_job(
        service.JobRequest(
            kind="project-simulation",
            project_id=project["id"],
            artifact_id=rtl["id"],
            testbench_artifact_id=tb["id"],
            idempotency_key="e2e-simulation",
        )
    )
    assert worker.process_once(job_timeout_seconds=30)
    finished = service.get_job(job["id"])
    assert finished["status"] == "passed", finished
    assert finished["artifact_id"] == rtl["id"]
    assert finished["testbench_artifact_id"] == tb["id"]
    assert [event["status"] for event in finished["events"]] == ["queued", "running", "passed"]

    report = service.project_proof_of_value(job["id"])
    assert report["project_id"] == project["id"]
    assert report["execution"]["status"] == "passed"
    assert report["coverage"]["percentage"] == 100.0
    assert report["claim_boundary"].startswith("simulation execution evidence")
    report_path = jobs / job["id"] / "proof-of-value-report.json"
    assert json.loads(report_path.read_text())["report_sha256"] == report["report_sha256"]
    evidence = service.project_job_evidence(job["id"])
    assert evidence["job"]["artifact_id"] == rtl["id"]
    assert evidence["artifacts"]["rtl"]["sha256"] == rtl["sha256"]
    assert "module counter" in evidence["artifacts"]["rtl"]["content"]
    assert evidence["waveform"]["present"] is True
    assert "done" in evidence["waveform"]["signals"]
    assert "COVERAGE functional 1/1" in evidence["files"]["simulation/stdout.log"]["text"]


def test_evidence_view_preserves_execution_failure_reason(tmp_path, monkeypatch):
    jobs = tmp_path / "jobs"
    monkeypatch.setattr(service, "JOB_ROOT", jobs)
    job = service.create_job(service.JobRequest(project_id="timeout", kind="multi-design-pilot"))
    job["status"] = "failed"
    job["error"] = "job exceeded timeout of 0.1 seconds"
    service._write(job)
    evidence = service.project_job_evidence(job["id"])
    assert evidence["job"]["error"] == "job exceeded timeout of 0.1 seconds"
