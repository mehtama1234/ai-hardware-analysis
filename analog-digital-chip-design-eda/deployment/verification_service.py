"""Dependency-light service wrapper for the reproducible verification pilot.

The service owns job metadata and logs; the existing pilot remains the source
of truth for verification evidence. A single-flight lock prevents concurrent
jobs from sharing the benchmark evidence roots until isolated worker
provisioning is enabled.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hmac
import json
import os
from pathlib import Path
import subprocess
import threading
import uuid
import zipfile
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from deployment.job_queue import DurableJobQueue
from deployment.project_store import ProjectStore

ROOT = Path(__file__).resolve().parents[1]
JOB_ROOT = ROOT / ".artifacts" / "verification-service" / "jobs"
PILOT = ROOT / "benchmarks" / "multi_design_pilot" / "ci_gate.py"
_RUN_LOCK = threading.Lock()
_COUNTERS = {"submitted": 0, "started": 0, "passed": 0, "failed": 0}

def _queue() -> DurableJobQueue:
    return DurableJobQueue(JOB_ROOT.parent / "jobs.sqlite")

def _projects() -> ProjectStore:
    return ProjectStore(JOB_ROOT.parent / "jobs.sqlite")

app = FastAPI(title="Verification Pilot Service", version="v1")

@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    expected = os.environ.get("VERIFICATION_SERVICE_API_KEY")
    key_file = os.environ.get("VERIFICATION_SERVICE_API_KEY_FILE")
    if key_file:
        try:
            expected = Path(key_file).read_text(encoding="utf-8").strip()
        except OSError:
            expected = None
    supplied = request.headers.get("x-api-key", "")
    if expected and request.url.path not in {"/healthz", "/readyz"} and not hmac.compare_digest(supplied, expected):
        return JSONResponse(status_code=401, content={"detail": "invalid or missing API key"})
    return await call_next(request)

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "verification-pilot"}

@app.get("/readyz")
def readyz() -> dict[str, Any]:
    queue_ready = True
    queue_error = None
    try:
        _queue().counts()
    except Exception as error:  # pragma: no cover - filesystem failure is environment-specific
        queue_ready = False
        queue_error = str(error)
    result = {
        "status": "ready" if PILOT.is_file() and queue_ready else "not-ready",
        "pilot_entrypoint": str(PILOT),
        "queue": "ready" if queue_ready else "unavailable",
    }
    if queue_error:
        result["queue_error"] = queue_error
    return result

@app.get("/metrics")
def metrics() -> dict[str, Any]:
    return {"service": "verification-pilot", "jobs": dict(_COUNTERS), "durable_queue": _queue().counts(), "single_flight": True}

@app.get("/metrics/prometheus", response_class=PlainTextResponse)
def prometheus_metrics() -> str:
    counts = _queue().counts()
    lines = ["# TYPE verification_jobs_total counter"]
    for name, value in _COUNTERS.items():
        lines.append(f'verification_jobs_total{{state="{name}"}} {value}')
    lines.append("# TYPE verification_queue_jobs gauge")
    for state, value in sorted(counts.items()):
        lines.append(f'verification_queue_jobs{{state="{state}"}} {value}')
    lines.append("verification_single_flight 1")
    return "\n".join(lines) + "\n"

class JobRequest(BaseModel):
    kind: str = "multi-design-pilot"
    project_id: str = "default"

class ProjectRequest(BaseModel):
    id: str
    name: str

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _job_timeout_seconds() -> float:
    try:
        return max(float(os.environ.get("VERIFICATION_JOB_TIMEOUT_SECONDS", "1800")), 0.1)
    except ValueError:
        return 1800.0

def _max_queued_jobs() -> int:
    try:
        return max(int(os.environ.get("VERIFICATION_MAX_QUEUED_JOBS", "32")), 1)
    except ValueError:
        return 32

def _path(job_id: str) -> Path:
    if not job_id or Path(job_id).name != job_id or "/" in job_id or "\\" in job_id:
        raise HTTPException(status_code=400, detail="invalid job id")
    return JOB_ROOT / job_id / "job.json"

def _read(job_id: str) -> dict[str, Any]:
    path = _path(job_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="job not found")
    return json.loads(path.read_text(encoding="utf-8"))

def _write(job: dict[str, Any]) -> None:
    path = _path(job["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _record(job: dict[str, Any], status: str, **details: Any) -> None:
    job.setdefault("events", []).append({"at": _now(), "status": status, **details})

@app.post("/v1/projects", status_code=201)
def create_project(request: ProjectRequest) -> dict[str, str]:
    if not request.id or not request.id.replace("-", "").replace("_", "").isalnum() or not request.name.strip():
        raise HTTPException(status_code=400, detail="invalid project")
    try:
        return _projects().create(request.id, request.name.strip())
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

@app.get("/v1/projects")
def list_projects() -> list[dict[str, str]]:
    return _projects().list()

@app.get("/v1/projects/{project_id}")
def get_project(project_id: str) -> dict[str, str]:
    try:
        return _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error

@app.post("/v1/jobs", status_code=202)
def create_job(request: JobRequest) -> dict[str, Any]:
    if request.kind != "multi-design-pilot":
        raise HTTPException(status_code=400, detail="unsupported job kind")
    if not request.project_id or not request.project_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="invalid project id")
    queue_counts = _queue().counts()
    backlog = queue_counts.get("queued", 0) + queue_counts.get("running", 0)
    if backlog >= _max_queued_jobs():
        raise HTTPException(status_code=429, detail="verification job capacity is full")
    _projects().ensure(request.project_id)
    job = {"id": uuid.uuid4().hex, "kind": request.kind, "project_id": request.project_id, "status": "queued", "created_at": _now(), "events": []}
    _record(job, "queued")
    _COUNTERS["submitted"] += 1
    _write(job)
    _queue().enqueue(job["id"], project_id=request.project_id, kind=request.kind)
    return job

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    return _read(job_id)

@app.get("/v1/jobs")
def list_jobs(project_id: str | None = None) -> list[dict[str, Any]]:
    if not JOB_ROOT.is_dir():
        return []
    jobs = []
    for path in sorted(JOB_ROOT.glob("*/job.json")):
        try:
            job = json.loads(path.read_text(encoding="utf-8"))
            if project_id is None or job.get("project_id") == project_id:
                jobs.append(job)
        except (OSError, json.JSONDecodeError):
            continue
    return jobs

@app.post("/v1/jobs/{job_id}/run")
def run_job(job_id: str) -> dict[str, Any]:
    job = _read(job_id)
    if job["status"] not in {"queued", "failed"}:
        raise HTTPException(status_code=409, detail=f"job is {job['status']}")
    job["status"], job["started_at"] = "running", _now(); _record(job, "running", executor="api"); _write(job)
    _queue().start(job_id)
    _COUNTERS["started"] += 1
    job_dir = _path(job_id).parent
    with _RUN_LOCK:
        try:
            result = subprocess.run(["python3", str(PILOT)], cwd=ROOT, capture_output=True, text=True, check=False, timeout=_job_timeout_seconds())
            stdout, stderr, exit_code = result.stdout, result.stderr, result.returncode
            timeout_error = None
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            stderr += "\nservice timeout\n"
            exit_code, timeout_error = None, f"job exceeded timeout of {_job_timeout_seconds()} seconds"
    (job_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (job_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    job["status"] = "passed" if exit_code == 0 else "failed"
    _record(job, job["status"], exit_code=exit_code)
    _COUNTERS[job["status"]] += 1
    _queue().finish(job_id, status=job["status"])
    job["finished_at"] = _now(); job["exit_code"] = exit_code
    if timeout_error:
        job["error"] = timeout_error
    job["evidence"] = {"pilot_summary": "benchmarks/multi_design_pilot/runs/latest/pilot-summary.json", "validation": "benchmarks/multi_design_pilot/runs/latest/clean-checkout-validation.json"}
    _write(job)
    return job

@app.post("/v1/jobs/{job_id}/run-async", status_code=202)
def run_job_async(job_id: str, background_tasks: BackgroundTasks) -> dict[str, Any]:
    job = _read(job_id)
    if job["status"] not in {"queued", "failed"}:
        raise HTTPException(status_code=409, detail=f"job is {job['status']}")
    # Durable workers own asynchronous execution. Scheduling an in-process
    # background task here would race a worker claiming the same queue row.
    return {"id": job_id, "status": "accepted", "poll": f"/v1/jobs/{job_id}"}

@app.post("/v1/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict[str, Any]:
    job = _read(job_id)
    if job["status"] != "queued":
        raise HTTPException(status_code=409, detail=f"job is {job['status']}")
    job["status"] = "cancelled"
    job["cancelled_at"] = _now()
    _record(job, "cancelled")
    _write(job)
    _queue().cancel(job_id)
    return job

@app.get("/v1/jobs/{job_id}/bundle")
def get_bundle(job_id: str) -> dict[str, Any]:
    job = _read(job_id)
    if job["status"] != "passed":
        raise HTTPException(status_code=409, detail="evidence bundle is unavailable until the job passes")
    bundle_path = _path(job_id).parent / "evidence-bundle.zip"
    evidence_root = ROOT / "benchmarks"
    wanted = [
        Path("multi_design_pilot/runs/latest/pilot-summary.json"),
        Path("multi_design_pilot/runs/latest/pilot-release-manifest.json"),
        Path("multi_design_pilot/runs/latest/session-ledger.json"),
        Path("multi_design_pilot/runs/latest/clean-checkout-validation.json"),
    ]
    for name in ("seeded_counter", "seeded_fifo", "seeded_regblock", "register_peripheral", "seeded_handshake"):
        wanted.extend([Path(name) / "runs/latest/artifact-manifest.json", Path(name) / "runs/retest/artifact-manifest.json"])
    included: list[str] = []
    missing: list[str] = []
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in wanted:
            source = evidence_root / relative
            if source.is_file():
                archive.write(source, relative.as_posix())
                included.append(relative.as_posix())
            else:
                missing.append(relative.as_posix())
    return {"job_id": job_id, "status": job["status"], "evidence": job.get("evidence", {}), "job_metadata": str(_path(job_id)), "bundle_path": str(bundle_path), "bundle_files": len(included), "missing_files": missing}

@app.get("/v1/jobs/{job_id}/bundle/download")
def download_bundle(job_id: str) -> FileResponse:
    bundle = get_bundle(job_id)
    return FileResponse(bundle["bundle_path"], media_type="application/zip", filename=f"verification-{job_id}.zip")
