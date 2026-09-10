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
from deployment.collateral_store import CollateralStore, MAX_CONTENT_BYTES
from deployment.collateral_ingest import ingest_artifact
from verification_platform.retrieval import build_retrieval_index, retrieve
from deployment.planning_service import plan_persisted_ir
from deployment.generation_service import generate_persisted_plan
from deployment.project_execution import compile_project_rtl, formal_preflight_project_rtl, lint_project_rtl, prove_project_invariant, simulate_project, simulate_project_regression
from deployment.repair_service import propose_repair
from deployment.project_pov import write_project_pov
from deployment.project_comparison import write_comparison
from verification_platform.capabilities import discover_capabilities

ROOT = Path(__file__).resolve().parents[1]
JOB_ROOT = ROOT / ".artifacts" / "verification-service" / "jobs"
PILOT = ROOT / "benchmarks" / "multi_design_pilot" / "ci_gate.py"
_RUN_LOCK = threading.Lock()
_COUNTERS = {"submitted": 0, "started": 0, "passed": 0, "failed": 0}

def _queue() -> DurableJobQueue:
    return DurableJobQueue(JOB_ROOT.parent / "jobs.sqlite")

def _projects() -> ProjectStore:
    return ProjectStore(JOB_ROOT.parent / "jobs.sqlite")

def _collateral() -> CollateralStore:
    return CollateralStore(JOB_ROOT.parent / "jobs.sqlite", JOB_ROOT.parent / "collateral")

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

@app.get("/v1/capabilities")
def capabilities() -> dict[str, Any]:
    discovered = discover_capabilities()
    return {"schema_version": "verification-capabilities-v1", "capabilities": [{"tool": item.tool, "executable": item.executable, "available": item.available, "status": item.status} for item in discovered], "available": sum(item.available for item in discovered), "blocked": sum(not item.available for item in discovered)}

class JobRequest(BaseModel):
    kind: str = "multi-design-pilot"
    project_id: str = "default"
    artifact_id: str | None = None
    testbench_artifact_id: str | None = None
    testbench_artifact_ids: list[str] = []
    formal_signal: str | None = None
    formal_expected: str | None = None
    formal_sequence: int = 3

class ProjectRequest(BaseModel):
    id: str
    name: str

class CollateralRequest(BaseModel):
    name: str
    kind: str
    version: str = "1"
    content: str

class RepairRequest(BaseModel):
    before: str
    after: str
    rationale: str
    approved: bool = False

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

@app.post("/v1/projects/{project_id}/collateral", status_code=201)
def add_collateral(project_id: str, request: CollateralRequest) -> dict[str, object]:
    try:
        _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error
    if not request.name.strip() or not request.kind.strip() or not request.version.strip():
        raise HTTPException(status_code=400, detail="invalid collateral metadata")
    if len(request.content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise HTTPException(status_code=413, detail="collateral exceeds 1 MB limit")
    try:
        return _collateral().add(project_id, request.name.strip(), request.kind.strip(), request.version.strip(), request.content)
    except ValueError as error:
        raise HTTPException(status_code=413, detail=str(error)) from error

@app.get("/v1/projects/{project_id}/collateral")
def list_collateral(project_id: str) -> list[dict[str, object]]:
    try:
        _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error
    return _collateral().list(project_id)

@app.post("/v1/projects/{project_id}/collateral/{artifact_id}/ingest")
def ingest_project_collateral(project_id: str, artifact_id: str) -> dict[str, Any]:
    try:
        record = _collateral().get(artifact_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="collateral not found") from error
    if record["project_id"] != project_id:
        raise HTTPException(status_code=404, detail="collateral not found")
    try:
        return ingest_artifact(record, artifact_root=JOB_ROOT.parent / "collateral", output_root=JOB_ROOT.parent / "ir")
    except (OSError, UnicodeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=f"collateral ingestion failed: {error}") from error

@app.get("/v1/projects/{project_id}/search")
def search_project(project_id: str, q: str = "", limit: int = 5) -> dict[str, Any]:
    if not q.strip() or limit < 1 or limit > 20:
        raise HTTPException(status_code=400, detail="invalid search query")
    try:
        _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error
    records = _collateral().list(project_id)
    root = JOB_ROOT.parent / "collateral"
    paths = [root / str(record["path"]) for record in records]
    if not paths:
        return {"project_id": project_id, "query": q, "hits": [], "source_count": 0}
    index = build_retrieval_index(paths, root=root, source_revision="project-collateral")
    return {"project_id": project_id, "query": q, "hits": retrieve(index, q, limit=limit), "source_count": len(paths), "index_sha256": index["index_sha256"]}

@app.post("/v1/projects/{project_id}/collateral/{artifact_id}/plan")
def plan_project_collateral(project_id: str, artifact_id: str) -> dict[str, Any]:
    try:
        record = _collateral().get(artifact_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="collateral not found") from error
    if record["project_id"] != project_id:
        raise HTTPException(status_code=404, detail="collateral not found")
    ir_path = JOB_ROOT.parent / "ir" / project_id / "ir" / f"{artifact_id}.json"
    if not ir_path.is_file():
        raise HTTPException(status_code=409, detail="collateral must be ingested before planning")
    try:
        return plan_persisted_ir(ir_path, output_root=JOB_ROOT.parent / "ir", project_id=project_id, artifact_id=artifact_id)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"planning failed: {error}") from error

@app.post("/v1/projects/{project_id}/collateral/{artifact_id}/generate")
def generate_project_artifacts(project_id: str, artifact_id: str) -> dict[str, Any]:
    try:
        record = _collateral().get(artifact_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="collateral not found") from error
    if record["project_id"] != project_id:
        raise HTTPException(status_code=404, detail="collateral not found")
    plan_path = JOB_ROOT.parent / "ir" / project_id / "plans" / f"{artifact_id}.json"
    if not plan_path.is_file():
        raise HTTPException(status_code=409, detail="collateral must be planned before generation")
    try:
        ir_path = JOB_ROOT.parent / "ir" / project_id / "ir" / f"{artifact_id}.json"
        ir_payload = json.loads(ir_path.read_text(encoding="utf-8")) if ir_path.is_file() else {}
        signals = [str(item["name"]) for item in ir_payload.get("checks", []) if item.get("type") == "port" and str(item.get("name", "")).isidentifier()]
        return generate_persisted_plan(
            plan_path,
            output_root=JOB_ROOT.parent / "ir",
            project_id=project_id,
            artifact_id=artifact_id,
            signals=signals or None,
        )
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"artifact generation failed: {error}") from error

@app.post("/v1/projects/{project_id}/collateral/{artifact_id}/repair")
def repair_project_collateral(project_id: str, artifact_id: str, request: RepairRequest) -> dict[str, Any]:
    try:
        record = _collateral().get(artifact_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="collateral not found") from error
    if record["project_id"] != project_id:
        raise HTTPException(status_code=404, detail="collateral not found")
    try:
        proposal, repaired_content = propose_repair(record, collateral_root=JOB_ROOT.parent / "collateral", before=request.before, after=request.after, rationale=request.rationale, approved=request.approved)
    except (OSError, UnicodeError) as error:
        raise HTTPException(status_code=422, detail=f"repair proposal failed: {error}") from error
    if repaired_content is None:
        return {"project_id": project_id, "source_artifact_id": artifact_id, "proposal": proposal}
    repaired = _collateral().add(project_id, str(record["name"]), str(record["kind"]), f"repair-of-{record['version']}", repaired_content)
    return {"project_id": project_id, "source_artifact_id": artifact_id, "proposal": proposal, "repaired_artifact": repaired}

@app.post("/v1/jobs/{job_id}/repair-retest", status_code=202)
def repair_retest_job(job_id: str, request: RepairRequest) -> dict[str, Any]:
    job = _read(job_id)
    if job.get("kind") != "project-simulation" or job.get("status") != "failed":
        raise HTTPException(status_code=409, detail="a failed project-simulation job is required")
    result = repair_project_collateral(str(job["project_id"]), str(job["artifact_id"]), request)
    if "repaired_artifact" not in result:
        return {"source_job_id": job_id, "proposal": result["proposal"], "retest_job": None}
    retest = create_job(JobRequest(kind="project-simulation", project_id=str(job["project_id"]), artifact_id=str(result["repaired_artifact"]["id"]), testbench_artifact_id=str(job["testbench_artifact_id"])))
    return {"source_job_id": job_id, "proposal": result["proposal"], "repaired_artifact": result["repaired_artifact"], "retest_job": retest}

@app.get("/v1/jobs/{job_id}/proof-of-value")
def project_proof_of_value(job_id: str) -> dict[str, Any]:
    job = _read(job_id)
    if job.get("kind") != "project-simulation" or job.get("status") not in {"passed", "failed"}:
        raise HTTPException(status_code=409, detail="a terminal project-simulation job is required")
    try:
        report_path = write_project_pov(_path(job_id).parent)
        return json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"proof-of-value generation failed: {error}") from error

@app.get("/v1/jobs/{baseline_job_id}/compare/{retest_job_id}")
def compare_project_jobs(baseline_job_id: str, retest_job_id: str) -> dict[str, Any]:
    baseline = _read(baseline_job_id)
    retest = _read(retest_job_id)
    if baseline.get("kind") != "project-simulation" or retest.get("kind") != "project-simulation":
        raise HTTPException(status_code=409, detail="both jobs must be project-simulation jobs")
    if baseline.get("status") not in {"passed", "failed"} or retest.get("status") not in {"passed", "failed"}:
        raise HTTPException(status_code=409, detail="both jobs must be terminal")
    if baseline.get("project_id") != retest.get("project_id"):
        raise HTTPException(status_code=409, detail="jobs must belong to the same project")
    try:
        path = write_comparison(_path(baseline_job_id).parent, _path(retest_job_id).parent)
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"comparison failed: {error}") from error

@app.post("/v1/jobs", status_code=202)
def create_job(request: JobRequest) -> dict[str, Any]:
    if request.kind not in {"multi-design-pilot", "project-compile", "project-lint", "project-formal", "project-formal-proof", "project-simulation", "project-regression"}:
        raise HTTPException(status_code=400, detail="unsupported job kind")
    if not request.project_id or not request.project_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="invalid project id")
    if request.kind in {"project-compile", "project-lint", "project-formal", "project-formal-proof"}:
        if not request.artifact_id:
            raise HTTPException(status_code=400, detail="artifact_id is required for project-compile")
        try:
            record = _collateral().get(request.artifact_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="collateral not found") from error
        if record["project_id"] != request.project_id:
            raise HTTPException(status_code=404, detail="collateral not found")
        if request.kind == "project-formal-proof" and (not request.formal_signal or not request.formal_expected or request.formal_sequence < 1):
            raise HTTPException(status_code=400, detail="formal_signal, formal_expected, and positive formal_sequence are required")
    if request.kind == "project-simulation":
        if not request.artifact_id or not request.testbench_artifact_id:
            raise HTTPException(status_code=400, detail="artifact_id and testbench_artifact_id are required for project-simulation")
        try:
            rtl_record = _collateral().get(request.artifact_id)
            tb_record = _collateral().get(request.testbench_artifact_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="collateral not found") from error
        if rtl_record["project_id"] != request.project_id or tb_record["project_id"] != request.project_id:
            raise HTTPException(status_code=404, detail="collateral not found")
    if request.kind == "project-regression":
        if not request.artifact_id or not request.testbench_artifact_ids:
            raise HTTPException(status_code=400, detail="artifact_id and testbench_artifact_ids are required for project-regression")
        try:
            rtl_record = _collateral().get(request.artifact_id)
            tb_records = [_collateral().get(item) for item in request.testbench_artifact_ids]
        except KeyError as error:
            raise HTTPException(status_code=404, detail="collateral not found") from error
        if rtl_record["project_id"] != request.project_id or any(record["project_id"] != request.project_id for record in tb_records):
            raise HTTPException(status_code=404, detail="collateral not found")
    queue_counts = _queue().counts()
    backlog = queue_counts.get("queued", 0) + queue_counts.get("running", 0)
    if backlog >= _max_queued_jobs():
        raise HTTPException(status_code=429, detail="verification job capacity is full")
    _projects().ensure(request.project_id)
    job = {"id": uuid.uuid4().hex, "kind": request.kind, "project_id": request.project_id, "artifact_id": request.artifact_id, "testbench_artifact_id": request.testbench_artifact_id, "testbench_artifact_ids": request.testbench_artifact_ids, "formal_signal": request.formal_signal, "formal_expected": request.formal_expected, "formal_sequence": request.formal_sequence, "status": "queued", "created_at": _now(), "events": []}
    _record(job, "queued")
    _COUNTERS["submitted"] += 1
    _write(job)
    _queue().enqueue(job["id"], project_id=request.project_id, kind=request.kind, payload={"artifact_id": request.artifact_id, "testbench_artifact_id": request.testbench_artifact_id, "testbench_artifact_ids": request.testbench_artifact_ids, "formal_signal": request.formal_signal, "formal_expected": request.formal_expected, "formal_sequence": request.formal_sequence} if request.artifact_id else {})
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
            if job["kind"] == "project-compile":
                record = _collateral().get(str(job["artifact_id"]))
                result_data = compile_project_rtl(record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=_job_timeout_seconds())
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                exit_code = result_data["exit_code"]
            elif job["kind"] == "project-lint":
                record = _collateral().get(str(job["artifact_id"]))
                result_data = lint_project_rtl(record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=_job_timeout_seconds())
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                exit_code = result_data["exit_code"]
            elif job["kind"] == "project-formal":
                record = _collateral().get(str(job["artifact_id"]))
                result_data = formal_preflight_project_rtl(record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=_job_timeout_seconds())
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                exit_code = result_data["exit_code"]
            elif job["kind"] == "project-formal-proof":
                record = _collateral().get(str(job["artifact_id"]))
                result_data = prove_project_invariant(record, signal=str(job["formal_signal"]), expected_value=str(job["formal_expected"]), sequence=int(job["formal_sequence"]), collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, timeout_seconds=_job_timeout_seconds())
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                exit_code = 0 if result_data["status"] == "passed" else 1
            elif job["kind"] == "project-simulation":
                rtl_record = _collateral().get(str(job["artifact_id"]))
                tb_record = _collateral().get(str(job["testbench_artifact_id"]))
                result_data = simulate_project(rtl_record, tb_record, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, source_revision=str(rtl_record["version"]), timeout_seconds=_job_timeout_seconds())
                stdout = (job_dir / "simulation" / "stdout.log").read_text(encoding="utf-8") if (job_dir / "simulation" / "stdout.log").is_file() else ""
                stderr = (job_dir / "simulation" / "stderr.log").read_text(encoding="utf-8") if (job_dir / "simulation" / "stderr.log").is_file() else ""
                exit_code = 0 if result_data["status"] == "passed" else 1
            elif job["kind"] == "project-regression":
                store = _collateral()
                rtl_record = store.get(str(job["artifact_id"]))
                tb_records = [store.get(str(item)) for item in job["testbench_artifact_ids"]]
                result_data = simulate_project_regression(rtl_record, tb_records, collateral_root=JOB_ROOT.parent / "collateral", run_root=job_dir, source_revision=str(rtl_record["version"]), timeout_seconds=_job_timeout_seconds())
                stdout, stderr, exit_code = "", "", 0 if result_data["status"] == "passed" else 1
            else:
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
    job["evidence"] = ({"project_compile": str(job_dir / "project-compile-result.json")} if job["kind"] == "project-compile" else {"project_lint": str(job_dir / "project-lint-result.json")} if job["kind"] == "project-lint" else {"project_formal": str(job_dir / "project-formal-result.json")} if job["kind"] == "project-formal" else {"project_formal_proof": str(job_dir / "project-formal-proof-result.json")} if job["kind"] == "project-formal-proof" else {"project_simulation": str(job_dir / "project-simulation-result.json")} if job["kind"] == "project-simulation" else {"project_regression": str(job_dir / "project-regression-result.json")} if job["kind"] == "project-regression" else {"pilot_summary": "benchmarks/multi_design_pilot/runs/latest/pilot-summary.json", "validation": "benchmarks/multi_design_pilot/runs/latest/clean-checkout-validation.json"})
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
    if job["kind"] in {"project-compile", "project-lint", "project-formal", "project-formal-proof", "project-simulation", "project-regression"}:
        if job["status"] not in {"passed", "failed"}:
            raise HTTPException(status_code=409, detail="project evidence bundle requires a terminal job")
        bundle_path = _path(job_id).parent / "evidence-bundle.zip"
        included: list[str] = []
        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(_path(job_id).parent.rglob("*")):
                if source.is_file() and source.name != bundle_path.name:
                    archive.write(source, source.relative_to(_path(job_id).parent).as_posix())
                    included.append(source.relative_to(_path(job_id).parent).as_posix())
        return {"job_id": job_id, "status": job["status"], "evidence": job.get("evidence", {}), "job_metadata": str(_path(job_id)), "bundle_path": str(bundle_path), "bundle_files": len(included), "missing_files": []}
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
