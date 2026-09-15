#!/usr/bin/env python3
"""Exercise the customer workflow through the local Compose API and worker."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8080"
KEY = "production-pilot-flight-key"
COMPOSE = ["docker", "compose", "-p", "production-pilot-flight", "-f", "deployment/docker-compose.yml"]


def api(method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(BASE + path, data=data, method=method, headers={"x-api-key": KEY, "content-type": "application/json"})
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


def expected_error(method: str, path: str, payload: dict | None, status: int, *, key: str = KEY) -> bool:
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(BASE + path, data=data, method=method, headers={"x-api-key": key, "content-type": "application/json"})
    try:
        urlopen(request, timeout=10)
    except HTTPError as error:
        return error.code == status
    return False


def wait_ready() -> dict:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            return api("GET", "/readyz")
        except Exception:
            time.sleep(1)
    raise RuntimeError("deployed API did not become ready")


def main() -> int:
    env = {**os.environ, "VERIFICATION_SERVICE_API_KEY": KEY, "VERIFICATION_DEPLOYMENT_TIER": "pilot"}
    subprocess.run(COMPOSE + ["up", "-d", "--build"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    try:
        api_container = subprocess.run(COMPOSE + ["ps", "-q", "verification-pilot"], cwd=ROOT, env=env, check=True, capture_output=True, text=True).stdout.strip()
        if not api_container:
            raise RuntimeError("Compose API container id is unavailable")
        # Seed the shared evidence volume so the deployed scorecard endpoint
        # reads the same certified observations as the handoff packet.
        subprocess.run(["docker", "cp", str(ROOT / ".artifacts/customer-pilot-scorecard.json"), f"{api_container}:/app/.artifacts/open-source-pilot-scorecard.json"], check=True, capture_output=True, text=True)
        subprocess.run(["docker", "cp", str(ROOT / ".artifacts/customer-pilot-scorecard"), f"{api_container}:/app/.artifacts/customer-pilot-scorecard"], check=True, capture_output=True, text=True)
        ready = wait_ready()
        run_token = uuid.uuid4().hex[:10]
        project_id = "flight-api-customer-" + run_token
        second_project_id = "flight-api-second-" + run_token
        project = api("POST", "/v1/projects", {"id": project_id, "name": "Deployed API Customer"})
        second = api("POST", "/v1/projects", {"id": second_project_id, "name": "Second Isolated Customer"})
        rtl = api("POST", f"/v1/projects/{project_id}/collateral", {"name": "dut.sv", "kind": "rtl", "content": "module dut(output wire done); assign done = 1'b1; endmodule\n"})
        tb = api("POST", f"/v1/projects/{project_id}/collateral", {"name": "tb.sv", "kind": "testbench", "content": "module tb; wire done; dut d(done); initial begin $dumpfile(\"waveform.vcd\"); $dumpvars(0,tb); #1; if (!done) $display(\"FAIL\"); else $display(\"PASS\"); $finish; end endmodule\n"})
        job = api("POST", "/v1/jobs", {"kind": "project-simulation", "project_id": project_id, "artifact_id": rtl["id"], "testbench_artifact_id": tb["id"], "idempotency_key": "flight-simulation-001"})
        deadline = time.monotonic() + 60
        terminal = None
        while time.monotonic() < deadline:
            observed = api("GET", f"/v1/jobs/{job['id']}")
            if observed.get("status") in {"passed", "failed", "blocked"}:
                terminal = observed
                break
            time.sleep(1)
        if terminal is None or terminal.get("status") != "passed":
            raise RuntimeError(f"deployed simulation did not pass: {terminal}")
        faulty = api("POST", f"/v1/projects/{project_id}/collateral", {"name": "faulty.sv", "kind": "rtl", "content": "module dut(output wire done); assign done = 1'b0; endmodule\n"})
        faulty_tb = api("POST", f"/v1/projects/{project_id}/collateral", {"name": "faulty-tb.sv", "kind": "testbench", "content": "module tb; wire done; dut d(done); initial begin $dumpfile(\"waveform.vcd\"); $dumpvars(0,tb); #1; if (done !== 1'b1) $display(\"FAIL cycle=1 signal=done expected=1 actual=0\"); else $display(\"PASS\"); $finish; end endmodule\n"})
        failed_job = api("POST", "/v1/jobs", {"kind": "project-simulation", "project_id": project_id, "artifact_id": faulty["id"], "testbench_artifact_id": faulty_tb["id"], "idempotency_key": "flight-failing-simulation-001"})
        deadline = time.monotonic() + 60
        failed_terminal = None
        while time.monotonic() < deadline:
            observed = api("GET", f"/v1/jobs/{failed_job['id']}")
            if observed.get("status") in {"passed", "failed", "blocked"}:
                failed_terminal = observed
                break
            time.sleep(1)
        if failed_terminal is None or failed_terminal.get("status") != "failed":
            raise RuntimeError(f"deployed failing simulation did not fail: {failed_terminal}")
        repair = {"before": "assign done = 1'b0", "after": "assign done = 1'b1", "rationale": "Correct the observed failing output"}
        proposal_response = api("POST", f"/v1/projects/{project_id}/collateral/{faulty['id']}/repair", repair)
        proposal = proposal_response["proposal"]
        stale_rejected = expected_error("POST", f"/v1/jobs/{failed_job['id']}/repair-retest", {**repair, "approved": True, "proposal_sha256": "0" * 64}, 409)
        approved = api("POST", f"/v1/jobs/{failed_job['id']}/repair-retest", {**repair, "approved": True, "proposal_sha256": proposal["proposal_sha256"]})
        retest_id = approved["retest_job"]["id"]
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            retest = api("GET", f"/v1/jobs/{retest_id}")
            if retest.get("status") in {"passed", "failed", "blocked"}:
                break
            time.sleep(1)
        comparison = api("GET", f"/v1/jobs/{failed_job['id']}/compare/{retest_id}")
        invalid_credential_rejected = expected_error("GET", "/v1/projects", None, 401, key="wrong-key")
        cross_tenant_rejected = expected_error("POST", f"/v1/projects/{second_project_id}/collateral/{faulty['id']}/repair", repair, 404)
        dashboard_before = api("GET", f"/v1/projects/{project_id}/dashboard")
        subprocess.run(COMPOSE + ["restart"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
        ready_after = wait_ready()
        project_after = api("GET", f"/v1/projects/{project_id}")
        job_after = api("GET", f"/v1/jobs/{job['id']}")
        evidence_after = api("GET", f"/v1/jobs/{failed_job['id']}/evidence")
        audit_after = api("GET", f"/v1/projects/{project_id}/audit")
        storage_after = api("GET", "/v1/storage/controls")
        metrics_payload = api("GET", "/metrics")
        scorecard_endpoint = api("GET", "/v1/pilot/scorecard")
        result = {"schema_version": "production-pilot-flight-v1", "project": project, "second_project": second, "collateral": [{"id": rtl["id"], "sha256": rtl["sha256"]}, {"id": tb["id"], "sha256": tb["sha256"]}], "job_id": job["id"], "job_status_before_restart": terminal["status"], "job_status_after_restart": job_after["status"], "dashboard_jobs_before_restart": dashboard_before["jobs"], "closure": {"failed_baseline_status": failed_terminal["status"], "proposal_sha256": proposal["proposal_sha256"], "stale_digest_rejected": stale_rejected, "retest_status": retest.get("status"), "failure_resolved": comparison.get("metrics", {}).get("failure_resolved"), "comparison_sha256": comparison.get("comparison_sha256")}, "negative_paths": {"invalid_credential_rejected": invalid_credential_rejected, "cross_tenant_rejected": cross_tenant_rejected}, "operational_evidence": {"job_evidence_after_restart": evidence_after.get("job", {}).get("status") == "failed" and bool(evidence_after.get("files")), "audit_entries_after_restart": audit_after.get("total", 0), "storage_controls_ready": storage_after.get("ready") is True, "metrics_exposed": isinstance(metrics_payload, dict), "scorecard_endpoint_ready": isinstance(scorecard_endpoint, dict) and scorecard_endpoint.get("pilot", {}).get("sample_size", 0) >= 20}, "ready_before_restart": ready["status"], "ready_after_restart": ready_after["status"], "project_id_after_restart": project_after["id"], "claim_boundary": "Local Compose API and worker pilot only; this does not establish HA, managed dependencies, customer identity, or production readiness."}
        result["evidence_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        output = ROOT / ".artifacts" / "production-pilot-flight.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
        return 0
    finally:
        subprocess.run(COMPOSE + ["down"], cwd=ROOT, env=env, check=False, capture_output=True, text=True)


if __name__ == "__main__":
    raise SystemExit(main())
