#!/usr/bin/env python3
"""Run the first synthetic-customer onboarding and adapter-certification slice."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import deployment.verification_service as service
import deployment.worker as worker
from deployment.adapter_registry import discover_registered_adapters
from deployment.signoff_service import verify_signoff, write_signoff
from scripts.collect_pilot_scorecard import collect


def main() -> int:
    registry = [
        {"name": "reference-iverilog", "kind": "simulation", "executable": "iverilog", "version": "system"},
        {"name": "reference-verilator", "kind": "simulation", "executable": "verilator", "version": "system"},
        {"name": "reference-yosys", "kind": "formal", "executable": "yosys", "version": "system"},
        {"name": "reference-symbiyosys", "kind": "formal", "executable": "sby", "version": "system"},
        {"name": "synthetic-runner", "kind": "pilot", "executable": "python3", "expected_artifacts": ["result.json"], "timeout_seconds": 30},
        {"name": "synthetic-timeout", "kind": "pilot", "executable": "python3", "expected_artifacts": ["result.json"], "timeout_seconds": 1},
        {"name": "synthetic-missing-artifact", "kind": "pilot", "executable": "python3", "expected_artifacts": ["result.json"], "timeout_seconds": 30},
    ]
    os.environ["VERIFICATION_EDA_ADAPTERS"] = json.dumps(registry)
    projects = (("customer-alpha", "Counter integration"), ("customer-beta", "Register integration"), ("customer-gamma", "Protocol integration"))
    with tempfile.TemporaryDirectory(prefix="customer-pilot-") as temp:
        service.JOB_ROOT = Path(temp) / "jobs"
        worker.JOB_ROOT = service.JOB_ROOT
        service._REPOSITORY_CACHE.clear()
        records = []
        for project_id, name in projects:
            service.create_project(service.ProjectRequest(id=project_id, name=name))
            requirement_id = "REQ_" + project_id.replace("-", "_").upper()
            spec = service.add_collateral(project_id, service.CollateralRequest(name="spec.md", kind="specification", content=f"# {name}\n{requirement_id}: verify the supplied behavior.\n"))
            rtl = service.add_collateral(project_id, service.CollateralRequest(name="design.sv", kind="rtl", content="module design(input logic clk); endmodule\n"))
            ingested = service.ingest_project_collateral(project_id, spec["id"])
            rtl_ingested = service.ingest_project_collateral(project_id, rtl["id"])
            spec_plan = service.plan_project_collateral(project_id, spec["id"])
            rtl_plan = service.plan_project_collateral(project_id, rtl["id"])
            spec_generated = service.generate_project_artifacts(project_id, spec["id"])
            rtl_generated = service.generate_project_artifacts(project_id, rtl["id"])
            job = service.create_job(service.JobRequest(kind="customer-adapter", project_id=project_id, adapter_name="synthetic-runner", adapter_args=["-c", "import json; open('result.json','w').write(json.dumps({'status':'passed','project':'" + project_id + "'}))"]))
            finished = service.run_job(job["id"])
            # Exercise the real simulation closure path with a deliberately failing baseline.
            faulty_rtl = service.add_collateral(project_id, service.CollateralRequest(name="faulty.sv", kind="rtl", content="module dut(output wire done); assign done = 1'b0; endmodule\n"))
            tb = service.add_collateral(project_id, service.CollateralRequest(name="tb.sv", kind="testbench", content='module tb; wire done; dut d(done); initial begin $dumpfile("waveform.vcd"); $dumpvars(0,tb); #1; if (done !== 1\'b1) $display("FAIL cycle=1 signal=done expected=1 actual=0"); else $display("PASS"); $finish; end endmodule\n'))
            baseline = service.create_job(service.JobRequest(kind="project-simulation", project_id=project_id, artifact_id=faulty_rtl["id"], testbench_artifact_id=tb["id"]))
            worker.process_once(job_timeout_seconds=30)
            baseline = service.get_job(baseline["id"])
            preview = service.repair_retest_job(baseline["id"], service.RepairRequest(before="assign done = 1'b0", after="assign done = 1'b1", rationale="Correct the observed failing output"))
            proposal = preview["proposal"]
            stale_rejection = False
            try:
                service.repair_retest_job(baseline["id"], service.RepairRequest(before=proposal["before"], after=proposal["after"], rationale=proposal["rationale"], proposal_sha256="0" * 64, approved=True))
            except Exception as error:
                stale_rejection = getattr(error, "status_code", None) == 409
            approved = service.repair_retest_job(baseline["id"], service.RepairRequest(before=proposal["before"], after=proposal["after"], rationale=proposal["rationale"], proposal_sha256=proposal["proposal_sha256"], approved=True))
            retest_id = approved["retest_job"]["id"]
            worker.process_once(job_timeout_seconds=30)
            retest = service.get_job(retest_id)
            comparison = service.compare_project_jobs(baseline["id"], retest_id)
            pov = service.project_proof_of_value(retest_id)
            signoff_path = write_signoff(service._path(retest_id).parent / "baseline-comparison.json", reviewer="pilot-verification-lead", notes="Reviewed baseline failure, exact repair, and identical-scope retest.", approved=True, reviewer_subject="synthetic|pilot-lead")
            records.append({"project_id": project_id, "collateral": [{"id": spec["id"], "sha256": spec["sha256"]}, {"id": rtl["id"], "sha256": rtl["sha256"]}], "requirements": ingested.get("requirements", 0) + rtl_ingested.get("requirements", 0), "planned_checks": spec_plan["summary"]["total"] + rtl_plan["summary"]["total"], "generated_artifacts": {"spec": spec_generated["execution_candidate"], "rtl": rtl_generated["execution_candidate"]}, "job_id": job["id"], "job_status": finished["status"], "evidence": finished.get("evidence", {}), "closure": {"baseline_job_id": baseline["id"], "baseline_status": baseline["status"], "proposal_sha256": proposal["proposal_sha256"], "stale_digest_rejected": stale_rejection, "retest_job_id": retest_id, "retest_status": retest["status"], "failure_resolved": comparison["metrics"]["failure_resolved"], "comparison_sha256": comparison["comparison_sha256"], "pov_report_sha256": pov["report_sha256"], "signoff_status": "approved", "signoff_valid": verify_signoff(signoff_path)}})
        adapters = [{"name": item.name, "kind": item.kind, "available": item.available, "status": item.status} for item in discover_registered_adapters()]
        timeout_job = service.create_job(service.JobRequest(kind="customer-adapter", project_id="customer-alpha", adapter_name="synthetic-timeout", adapter_args=["-c", "import time; time.sleep(2)"]))
        timeout_result = service.run_job(timeout_job["id"])
        missing_job = service.create_job(service.JobRequest(kind="customer-adapter", project_id="customer-alpha", adapter_name="synthetic-missing-artifact", adapter_args=["-c", "pass"]))
        missing_result = service.run_job(missing_job["id"])
        result = {"schema_version": "customer-pilot-certification-v1", "projects": records, "project_count": len(records), "adapters": adapters, "adapter_count": len(adapters), "available_adapters": sum(item["available"] for item in adapters), "certified_synthetic_runs": sum(item["job_status"] == "passed" for item in records), "claim_boundary": "Synthetic onboarding and adapter contract rehearsal; not customer production or silicon qualification."}
        result["negative_paths"] = {"timeout": {"job_id": timeout_job["id"], "status": timeout_result["status"]}, "missing_artifact": {"job_id": missing_job["id"], "status": missing_result["status"]}}
    scorecard_root = Path(".artifacts/customer-pilot-scorecard")
    scorecard_root.mkdir(parents=True, exist_ok=True)
    baseline_rows, workbench_rows = [], []
    categories = ("simulation", "lint", "formal", "regression")
    for index in range(24):
        category = categories[index % len(categories)]
        common = {"failure_id": f"synthetic-{index:02d}", "category": category, "root_cause_actionable": True, "evidence_complete": True, "closure_integrity": True}
        baseline_rows.append({**common, "triage_seconds": 120 + index, "reproduction_seconds": 90 + index, "manual_actions": 12})
        workbench_rows.append({**common, "triage_seconds": 30 + index, "reproduction_seconds": 20 + index, "manual_actions": 4, "blocked_or_timeout": index < 3})
    baseline_path = scorecard_root / "baseline-observations.json"
    workbench_path = scorecard_root / "workbench-observations.json"
    baseline_path.write_text(json.dumps(baseline_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    workbench_path.write_text(json.dumps(workbench_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    scorecard_path = Path(".artifacts/customer-pilot-scorecard.json")
    scorecard = collect(baseline_path, workbench_path, output=scorecard_path, customer="synthetic-customer-cohort", project="customer-pilot-certification")
    result["scorecard"] = {"path": str(scorecard_path), "sha256": hashlib.sha256(scorecard_path.read_bytes()).hexdigest(), "sample_size": scorecard["pilot"]["sample_size"]}
    result["evidence_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = Path(".artifacts/customer-pilot-certification.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    closures = [record.get("closure", {}) for record in result["projects"]]
    negatives = result.get("negative_paths", {})
    return 0 if result["project_count"] == 3 and result["certified_synthetic_runs"] == 3 and negatives.get("timeout", {}).get("status") == "blocked" and negatives.get("missing_artifact", {}).get("status") == "blocked" and all(item.get("baseline_status") == "failed" and item.get("retest_status") == "passed" and item.get("failure_resolved") is True and item.get("stale_digest_rejected") is True and item.get("signoff_valid") is True for item in closures) else 1


if __name__ == "__main__":
    raise SystemExit(main())
