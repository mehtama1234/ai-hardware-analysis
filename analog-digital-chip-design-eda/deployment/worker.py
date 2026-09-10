"""Durable verification job worker.

Run with ``python -m deployment.worker`` in a separate container/process.  The
SQLite claim is transactional, so restarting a worker cannot duplicate a job
that another worker has already claimed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
import subprocess
import time

from deployment.job_queue import DurableJobQueue
from deployment.verification_service import JOB_ROOT, PILOT, ROOT, _path, _read, _write


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: str | bytes | None) -> str:
    return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")


def process_once(*, stale_after_seconds: float = 900.0, job_timeout_seconds: float = 1800.0) -> bool:
    queue = DurableJobQueue(JOB_ROOT.parent / "jobs.sqlite")
    queue.requeue_stale(max_age_seconds=stale_after_seconds)
    claimed = queue.claim()
    if claimed is None:
        return False
    job_id = claimed["id"]
    try:
        job = _read(job_id)
        job["status"] = "running"
        job["started_at"] = job.get("started_at", _now())
        job.setdefault("events", []).append({"at": _now(), "status": "running", "executor": "worker"})
        _write(job)
        job_dir = _path(job_id).parent
        try:
            result = subprocess.run(
                ["python3", str(PILOT)], cwd=ROOT, capture_output=True, text=True,
                check=False, timeout=job_timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            (job_dir / "stdout.log").write_text(_text(exc.stdout), encoding="utf-8")
            (job_dir / "stderr.log").write_text(_text(exc.stderr) + "\nworker timeout\n", encoding="utf-8")
            job["status"] = "failed"
            job["error"] = f"job exceeded timeout of {job_timeout_seconds} seconds"
            job.setdefault("events", []).append({"at": _now(), "status": "failed", "reason": "timeout"})
            job["finished_at"] = _now()
            job["exit_code"] = None
            _write(job)
            queue.finish(job_id, status="failed")
            return True
        (job_dir / "stdout.log").write_text(result.stdout, encoding="utf-8")
        (job_dir / "stderr.log").write_text(result.stderr, encoding="utf-8")
        job["status"] = "passed" if result.returncode == 0 else "failed"
        job.setdefault("events", []).append({"at": _now(), "status": job["status"], "exit_code": result.returncode})
        job["finished_at"] = _now()
        job["exit_code"] = result.returncode
        job["evidence"] = {
            "pilot_summary": "benchmarks/multi_design_pilot/runs/latest/pilot-summary.json",
            "validation": "benchmarks/multi_design_pilot/runs/latest/clean-checkout-validation.json",
        }
        _write(job)
        queue.finish(job_id, status=job["status"])
    except Exception:
        # Leave a durable terminal state and make the failure visible in the
        # job metadata. The worker can then continue with the next job.
        try:
            job = _read(job_id)
            job["status"] = "failed"
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
