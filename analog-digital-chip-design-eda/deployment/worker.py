"""Durable verification job worker.

Run with ``python -m deployment.worker`` in a separate container/process.  The
SQLite claim is transactional, so restarting a worker cannot duplicate a job
that another worker has already claimed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
import re
import subprocess
import time

from deployment.verification_service import JOB_ROOT, PILOT, ROOT, _path, _prepare_job_workspace, _read, _publish_job_artifacts, _write, _repositories
from deployment.project_execution import compile_project_rtl, formal_preflight_project_rtl, lint_project_rtl, prove_project_invariant, simulate_project, simulate_project_regression
from deployment.adapter_execution import execute_registered_adapter


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: str | bytes | None) -> str:
    return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")


def _safe_error(error: Exception) -> str:
    message = re.sub(r"(?:[A-Za-z]:)?/[^\s,;]+", "[PATH]", str(error))
    return f"{type(error).__name__}: {message[:500]}"


def _event(job: dict, status: str, **details: object) -> dict:
    event = {"at": _now(), "status": status, **details}
    if job.get("request_id"):
        event["request_id"] = job["request_id"]
    return event


def process_once(*, stale_after_seconds: float = 900.0, job_timeout_seconds: float = 1800.0) -> bool:
    repositories = _repositories()
    queue = repositories.queue
    store = repositories.collateral
    queue.requeue_stale(max_age_seconds=stale_after_seconds)
    claimed = queue.claim()
    if claimed is None:
        return False
    job_id = claimed["id"]
    try:
        job = _read(job_id)
        job["status"] = "running"
        job["started_at"] = job.get("started_at", _now())
        job.setdefault("events", []).append(_event(job, "running", executor="worker"))
        _write(job)
        job_dir = _prepare_job_workspace(job_id)
        try:
            if job["kind"] == "project-compile":
                record = store.get(str(job["artifact_id"]))
                result_data = compile_project_rtl(record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=job_timeout_seconds)
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                return_code = result_data["exit_code"]
            elif job["kind"] == "project-lint":
                record = store.get(str(job["artifact_id"]))
                result_data = lint_project_rtl(record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=job_timeout_seconds)
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                return_code = result_data["exit_code"]
            elif job["kind"] == "project-formal":
                record = store.get(str(job["artifact_id"]))
                result_data = formal_preflight_project_rtl(record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=job_timeout_seconds)
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                return_code = result_data["exit_code"]
            elif job["kind"] == "project-formal-proof":
                record = store.get(str(job["artifact_id"]))
                result_data = prove_project_invariant(record, signal=str(job["formal_signal"]), expected_value=str(job["formal_expected"]), sequence=int(job["formal_sequence"]), collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=job_timeout_seconds)
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                return_code = 0 if result_data["status"] == "passed" else 1
            elif job["kind"] == "project-simulation":
                rtl_record = store.get(str(job["artifact_id"]))
                tb_record = store.get(str(job["testbench_artifact_id"]))
                result_data = simulate_project(rtl_record, tb_record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, source_revision=str(rtl_record["version"]), timeout_seconds=job_timeout_seconds)
                stdout = (job_dir / "simulation" / "stdout.log").read_text(encoding="utf-8") if (job_dir / "simulation" / "stdout.log").is_file() else ""
                stderr = (job_dir / "simulation" / "stderr.log").read_text(encoding="utf-8") if (job_dir / "simulation" / "stderr.log").is_file() else ""
                return_code = 0 if result_data["status"] == "passed" else 1
            elif job["kind"] == "project-regression":
                rtl_record = store.get(str(job["artifact_id"]))
                tb_records = [store.get(str(item)) for item in job["testbench_artifact_ids"]]
                result_data = simulate_project_regression(rtl_record, tb_records, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, source_revision=str(rtl_record["version"]), timeout_seconds=job_timeout_seconds)
                stdout, stderr, return_code = "", "", 0 if result_data["status"] == "passed" else 1
            elif job["kind"] == "customer-adapter":
                source_revision = "unknown"
                if job.get("artifact_id"):
                    source_revision = str(store.get(str(job["artifact_id"]))["version"])
                result_data = execute_registered_adapter(name=str(job["adapter_name"]), args=list(job.get("adapter_args", [])), run_root=job_dir, source_revision=source_revision)
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                return_code = int(result_data.get("exit_code") or 0) if result_data.get("status") == "passed" else 1
            else:
                result = subprocess.run(
                    ["python3", str(PILOT)], cwd=ROOT, capture_output=True, text=True,
                    check=False, timeout=job_timeout_seconds,
                )
                stdout, stderr, return_code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            (job_dir / "stdout.log").write_text(_text(exc.stdout), encoding="utf-8")
            (job_dir / "stderr.log").write_text(_text(exc.stderr) + "\nworker timeout\n", encoding="utf-8")
            job["status"] = "failed"
            job["error"] = f"job exceeded timeout of {job_timeout_seconds} seconds"
            job.setdefault("events", []).append(_event(job, "failed", reason="timeout"))
            job["finished_at"] = _now()
            job["exit_code"] = None
            _write(job)
            queue.finish(job_id, status="failed")
            return True
        (job_dir / "stdout.log").write_text(stdout, encoding="utf-8")
        (job_dir / "stderr.log").write_text(stderr, encoding="utf-8")
        job["evidence_objects"] = _publish_job_artifacts(job_id, job_dir)
        reported_status = result_data.get("status") if isinstance(result_data, dict) else None
        job["status"] = reported_status if reported_status in {"passed", "failed", "blocked"} else ("passed" if return_code == 0 else "failed")
        if job["status"] == "blocked" and not job.get("error"):
            job["error"] = "execution did not produce terminal evidence before the configured timeout or artifact boundary"
        job.setdefault("events", []).append(_event(job, job["status"], exit_code=return_code))
        job["finished_at"] = _now()
        job["exit_code"] = return_code
        job["evidence"] = ({"adapter_result": str(job_dir / "adapter-result.json")} if job["kind"] == "customer-adapter" else {"project_compile": str(job_dir / "project-compile-result.json")} if job["kind"] == "project-compile" else {"project_lint": str(job_dir / "project-lint-result.json")} if job["kind"] == "project-lint" else {"project_formal": str(job_dir / "project-formal-result.json")} if job["kind"] == "project-formal" else {"project_formal_proof": str(job_dir / "project-formal-proof-result.json")} if job["kind"] == "project-formal-proof" else {"project_simulation": str(job_dir / "project-simulation-result.json")} if job["kind"] == "project-simulation" else {"project_regression": str(job_dir / "project-regression-result.json")} if job["kind"] == "project-regression" else {
            "pilot_summary": "benchmarks/multi_design_pilot/runs/latest/pilot-summary.json",
            "validation": "benchmarks/multi_design_pilot/runs/latest/clean-checkout-validation.json",
        })
        _write(job)
        queue.finish(job_id, status=job["status"])
    except Exception as error:
        # Leave a durable terminal state and make the failure visible in the
        # job metadata. The worker can then continue with the next job.
        try:
            job = _read(job_id)
            job["status"] = "failed"
            job["error"] = f"worker execution failed: {_safe_error(error)}"
            job.setdefault("events", []).append(_event(job, "failed", reason="worker_exception"))
            job["finished_at"] = _now()
            _write(job)
        finally:
            queue.finish(job_id, status="failed")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Run durable verification jobs")
    parser.add_argument("--once", action="store_true", help="process at most one job and exit")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--stale-after-seconds", type=float, default=900.0)
    parser.add_argument("--job-timeout-seconds", type=float, default=float(os.environ.get("VERIFICATION_WORKER_TIMEOUT_SECONDS", "1800")))
    args = parser.parse_args()
    while True:
        processed = process_once(stale_after_seconds=args.stale_after_seconds, job_timeout_seconds=args.job_timeout_seconds)
        if args.once:
            return
        if not processed:
            time.sleep(max(args.poll_seconds, 0.1))


if __name__ == "__main__":
    main()
