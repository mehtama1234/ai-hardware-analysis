"""Verify exact proposal approval creates a linked retest."""

from deployment import verification_service as service
from deployment import worker


def test_exact_repair_hash_is_required_for_workbench_retest(tmp_path, monkeypatch):
    jobs = tmp_path / "jobs"
    monkeypatch.setattr(service, "JOB_ROOT", jobs)
    monkeypatch.setattr(worker, "JOB_ROOT", jobs)
    project = service.create_project(service.ProjectRequest(id="repair", name="Repair"))
    rtl = service.add_collateral(project["id"], service.CollateralRequest(name="dut.sv", kind="rtl", content="module dut(output wire done); assign done = 1'b0; endmodule\n"))
    tb = service.add_collateral(project["id"], service.CollateralRequest(name="tb.sv", kind="testbench", content=(
        "module tb; wire done; dut d(done); initial begin $dumpfile(\"waveform.vcd\"); $dumpvars(0,tb); #1; "
        "if (done !== 1'b1) $display(\"FAIL cycle=1 signal=done expected=1 actual=0\"); else $display(\"PASS\"); $finish; end endmodule\n")))
    baseline = service.create_job(service.JobRequest(kind="project-simulation", project_id=project["id"], artifact_id=rtl["id"], testbench_artifact_id=tb["id"]))
    assert worker.process_once(job_timeout_seconds=30)
    assert service.get_job(baseline["id"])["status"] == "failed"
    preview = service.repair_retest_job(baseline["id"], service.RepairRequest(before="assign done = 1'b0", after="assign done = 1'b1", rationale="Fix observed failing output"))
    proposal = preview["proposal"]
    assert proposal["status"] == "review_required" and proposal["occurrences"] == 1
    try:
        service.repair_retest_job(baseline["id"], service.RepairRequest(before=proposal["before"], after=proposal["after"], rationale=proposal["rationale"], proposal_sha256="0" * 64, approved=True))
    except Exception as error:
        assert getattr(error, "status_code", None) == 409
    else:
        raise AssertionError("changed proposal must be rejected")
    approved = service.repair_retest_job(baseline["id"], service.RepairRequest(before=proposal["before"], after=proposal["after"], rationale=proposal["rationale"], proposal_sha256=proposal["proposal_sha256"], approved=True))
    assert approved["retest_job"]["lineage"]["baseline_job_id"] == baseline["id"]
    assert approved["retest_job"]["lineage"]["proposal_sha256"] == proposal["proposal_sha256"]
    retest_id = approved["retest_job"]["id"]
    assert worker.process_once(job_timeout_seconds=30)
    assert service.get_job(retest_id)["status"] == "passed"
    comparison = service.compare_project_jobs(baseline["id"], retest_id)
    assert comparison["metrics"]["failure_resolved"] is True
