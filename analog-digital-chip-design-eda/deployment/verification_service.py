"""Dependency-light service wrapper for the reproducible verification pilot.

The service owns job metadata and logs; the existing pilot remains the source
of truth for verification evidence. A single-flight lock prevents concurrent
jobs from sharing the benchmark evidence roots until isolated worker
provisioning is enabled.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
import zipfile
import re
from contextvars import ContextVar
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from deployment.job_queue import DurableJobQueue
from deployment.project_store import ProjectStore
from deployment.collateral_store import CollateralStore, MAX_CONTENT_BYTES
from deployment.collateral_ingest import ingest_artifact
from verification_platform.retrieval import build_retrieval_index, retrieve
from verification_platform.agent import validate_agent_proposal
from deployment.planning_service import plan_persisted_ir
from deployment.generation_service import generate_persisted_plan
from deployment.project_execution import compile_project_rtl, formal_preflight_project_rtl, lint_project_rtl, prove_project_invariant, simulate_project, simulate_project_regression
from deployment.repair_service import propose_repair
from deployment.project_pov import write_project_pov
from deployment.project_comparison import write_comparison
from deployment.project_regression_pov import write_regression_pov
from verification_platform.capabilities import discover_capabilities
from deployment.signoff_service import verify_signoff, write_signoff
from deployment.adapter_registry import discover_registered_adapters
from deployment.adapter_execution import execute_registered_adapter, validate_adapter_args
from deployment.repository_factory import build_repositories
from deployment.production_config import load_deployment_config
from deployment.oidc_identity import IdentityClaims, OIDCIdentityVerifier
from deployment.pilot_scorecard import validate_scorecard

ROOT = Path(__file__).resolve().parents[1]
JOB_ROOT = ROOT / ".artifacts" / "verification-service" / "jobs"
PILOT = ROOT / "benchmarks" / "multi_design_pilot" / "ci_gate.py"
_RUN_LOCK = threading.Lock()
_COUNTERS = {"submitted": 0, "started": 0, "passed": 0, "failed": 0}
_HTTP_COUNTERS = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0, "request_id_generated": 0}
_HTTP_DURATION = {"2xx": 0.0, "3xx": 0.0, "4xx": 0.0, "5xx": 0.0}
_REQUEST_ID = ContextVar("verification_request_id", default=None)
_PROJECT_KEY_HEADER = ContextVar("verification_project_key", default=None)
_OIDC_CLAIMS = ContextVar("verification_oidc_claims", default=None)
EVIDENCE_STORE_CONTRACT = "evidence-store-v1"
EVIDENCE_STORE_PROVIDER = os.environ.get("VERIFICATION_EVIDENCE_STORE_PROVIDER", "filesystem-pilot")

_REPOSITORY_CACHE: dict[tuple[str, str, str], object] = {}
_OIDC_VERIFIER_CACHE: dict[tuple[str, str, str], OIDCIdentityVerifier] = {}


def _repositories():
    tier = os.environ.get("VERIFICATION_DEPLOYMENT_TIER", "pilot")
    dsn = os.environ.get("VERIFICATION_DATABASE_URL", "")
    key = (tier, dsn, str(JOB_ROOT.parent))
    if key not in _REPOSITORY_CACHE:
        _REPOSITORY_CACHE[key] = build_repositories(JOB_ROOT.parent / "jobs.sqlite", JOB_ROOT.parent / "collateral", migrate=tier == "customer-production")
    return _REPOSITORY_CACHE[key]


def _queue() -> DurableJobQueue:
    return _repositories().queue

def _projects() -> ProjectStore:
    return _repositories().projects

def _collateral() -> CollateralStore:
    return _repositories().collateral


def _evidence_store():
    return _repositories().evidence

def _evidence_store_provider_ready() -> bool:
    # The pilot provider is implemented locally. Managed providers must retain
    # the same contract before being advertised as ready.
    return EVIDENCE_STORE_PROVIDER == "filesystem-pilot"

def _project_keys() -> dict[str, str]:
    raw = os.environ.get("VERIFICATION_PROJECT_KEYS", "")
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) and all(isinstance(key, str) and isinstance(item, str) for key, item in value.items()) else {}


def _project_subjects() -> dict[str, set[str]]:
    raw = os.environ.get("VERIFICATION_PROJECT_SUBJECTS", "")
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(value, dict):
        return {}
    return {str(project): {str(subject) for subject in subjects if str(subject).strip()} for project, subjects in value.items() if isinstance(subjects, list)}


def _oidc_verifier() -> OIDCIdentityVerifier:
    key = (os.environ.get("VERIFICATION_IDENTITY_ISSUER", ""), os.environ.get("VERIFICATION_IDENTITY_AUDIENCE", ""), os.environ.get("VERIFICATION_IDENTITY_JWKS_URL", ""))
    if key not in _OIDC_VERIFIER_CACHE:
        _OIDC_VERIFIER_CACHE[key] = OIDCIdentityVerifier(*key)
    return _OIDC_VERIFIER_CACHE[key]

WORKBENCH_ASSETS = {"verification-workbench.js", "verification-workbench-setup.js"}

class AgenticClosureSignoffRequest(BaseModel):
    reviewer: str
    notes: str
    approved: bool = False
    manifest_sha256: str
    reviewer_subject: str | None = None
    review_started_at: str | None = None

app = FastAPI(title="Verification Pilot Service", version="v1")
_REQUEST_LOGGER = logging.getLogger("verification.request")


def _log_request(request: Request, request_id: str, status_code: int, started: float) -> None:
    _REQUEST_LOGGER.info(json.dumps({
        "event": "http_request",
        "schema_version": "verification-http-log-v1",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "duration_ms": round(max(time.monotonic() - started, 0.0) * 1000, 3),
    }, sort_keys=True, separators=(",", ":")))

def _apply_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' http: https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
    # Verification evidence and audit exports contain proprietary design data.
    # Never allow a browser, proxy, or shared cache to retain them.
    if getattr(response, "headers", None) is not None:
        response.headers.setdefault("Cache-Control", "no-store")
    return response

@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Set conservative browser policy headers on API and workbench responses."""
    response = await call_next(request)
    return _apply_security_headers(response)

def _correlation_id(value: str) -> tuple[str, bool]:
    supplied = value.strip()
    valid = bool(supplied and re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", supplied))
    return (supplied if valid else uuid.uuid4().hex), valid

@app.middleware("http")
async def request_id_header(request: Request, call_next):
    request_id, valid_supplied = _correlation_id(request.headers.get("X-Request-ID", ""))
    if not valid_supplied:
        _HTTP_COUNTERS["request_id_generated"] += 1
    token = _REQUEST_ID.set(request_id)
    started = time.monotonic()
    response = None
    try:
        response = await call_next(request)
    except Exception:
        _HTTP_COUNTERS["5xx"] += 1
        _HTTP_DURATION["5xx"] += max(time.monotonic() - started, 0.0)
        _log_request(request, request_id, 500, started)
        raise
    finally:
        _REQUEST_ID.reset(token)
    status_code = response.status_code if response is not None else 500
    bucket = f"{status_code // 100}xx"
    if bucket in _HTTP_COUNTERS:
        _HTTP_COUNTERS[bucket] += 1
        _HTTP_DURATION[bucket] += max(time.monotonic() - started, 0.0)
    if response is None:
        raise RuntimeError("request dispatch returned no response")
    response.headers["X-Request-ID"] = request_id
    _log_request(request, request_id, response.status_code, started)
    return response

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
    method = getattr(request, "method", "GET")
    path = getattr(getattr(request, "url", None), "path", "")
    public_ui = method == "GET" and (path in {"/workbench", "/workbench/", "/workbench/verification-workbench.html"} or path in {"/workbench/" + name for name in WORKBENCH_ASSETS})
    if expected and not public_ui and path not in {"/healthz", "/readyz"} and not hmac.compare_digest(supplied, expected):
        response = JSONResponse(status_code=401, content={"detail": "invalid or missing API key"})
        request_id, generated = _correlation_id(request.headers.get("X-Request-ID", ""))
        if generated:
            _HTTP_COUNTERS["request_id_generated"] += 1
        response.headers["X-Request-ID"] = request_id
        return _apply_security_headers(response)
    token_required = os.environ.get("VERIFICATION_REQUIRE_IDENTITY_TOKEN", "0").lower() in {"1", "true", "yes"}
    authorization = request.headers.get("Authorization", "")
    bearer = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
    claims_token = None
    if token_required or bearer:
        if not bearer:
            return _apply_security_headers(JSONResponse(status_code=401, content={"detail": "OIDC bearer token is required"}))
        try:
            claims = _oidc_verifier().verify(bearer)
        except Exception:
            return _apply_security_headers(JSONResponse(status_code=401, content={"detail": "invalid OIDC bearer token"}))
        claims_token = _OIDC_CLAIMS.set(claims)
    project_keys = _project_keys()
    parts = path.strip("/").split("/")
    protected_project = None
    if parts[:2] == ["v1", "projects"] and len(parts) >= 3:
        protected_project = parts[2]
    elif parts[:2] == ["v1", "jobs"] and len(parts) >= 5 and parts[3] == "compare":
        # Comparison reads two persisted jobs. Authenticate both owners and
        # reject a cross-project pair before the route can inspect either.
        owners = []
        for job_id in (parts[2], parts[4]):
            try:
                job_path = JOB_ROOT / job_id / "job.json"
                if job_path.is_file():
                    owners.append(json.loads(job_path.read_text(encoding="utf-8")).get("project_id"))
            except (OSError, json.JSONDecodeError):
                pass
        if owners and len(set(owners)) != 1:
            protected_project = "__cross_project_pair__"
        elif owners:
            protected_project = owners[0]
    elif parts[:2] == ["v1", "jobs"] and len(parts) >= 3:
        # Job endpoints do not repeat the project in their URL. Resolve the
        # persisted owner before dispatch so a project key cannot read or
        # mutate another project's run by guessing its job ID.
        try:
            job_path = JOB_ROOT / parts[2] / "job.json"
            if job_path.is_file():
                protected_project = json.loads(job_path.read_text(encoding="utf-8")).get("project_id")
        except (OSError, json.JSONDecodeError):
            protected_project = None
    elif path == "/v1/jobs":
        protected_project = getattr(getattr(request, "query_params", None), "get", lambda _key: None)("project_id")
    if project_keys and protected_project:
        required = "__cross_project_pair__" if protected_project == "__cross_project_pair__" else project_keys.get(protected_project)
        if required and not hmac.compare_digest(request.headers.get("x-project-key", ""), required):
            response = JSONResponse(status_code=403, content={"detail": "invalid or missing project key"})
            request_id, generated = _correlation_id(request.headers.get("X-Request-ID", ""))
            if generated:
                _HTTP_COUNTERS["request_id_generated"] += 1
            response.headers["X-Request-ID"] = request_id
            if claims_token is not None:
                _OIDC_CLAIMS.reset(claims_token)
            return _apply_security_headers(response)
    subjects = _project_subjects()
    if subjects and protected_project and protected_project in subjects:
        subject = _identity_subject(request)
        if not subject or subject not in subjects[protected_project]:
            if claims_token is not None:
                _OIDC_CLAIMS.reset(claims_token)
            return _apply_security_headers(JSONResponse(status_code=403, content={"detail": "identity is not authorized for this project"}))
    # Preserve the header for body-scoped routes such as POST /v1/jobs, where
    # the project ID arrives in JSON rather than the URL.
    project_token = _PROJECT_KEY_HEADER.set(request.headers.get("x-project-key"))
    try:
        return await call_next(request)
    finally:
        _PROJECT_KEY_HEADER.reset(project_token)
        if claims_token is not None:
            _OIDC_CLAIMS.reset(claims_token)

def _enforce_project_key(project_id: str) -> None:
    """Enforce the scoped key on routes whose project is in the request body."""
    required = _project_keys().get(project_id)
    supplied = _PROJECT_KEY_HEADER.get()
    # Direct Python calls are used by the pilot's deterministic unit tests and
    # have no HTTP header context; HTTP requests always set the context above.
    if required and supplied is not None and not hmac.compare_digest(supplied, required):
        raise HTTPException(status_code=403, detail="invalid or missing project key")
    subjects = _project_subjects()
    if project_id in subjects:
        subject = _identity_subject(None)
        if not subject or subject not in subjects[project_id]:
            raise HTTPException(status_code=403, detail="identity is not authorized for this project")

@app.get("/workbench")
@app.get("/workbench/")
def workbench_page():
    from fastapi.responses import RedirectResponse
    # A trailing slash ensures all assets resolve under the public UI allowlist.
    return RedirectResponse("/workbench/verification-workbench.html")

@app.get("/workbench/verification-workbench.html")
def workbench_html():
    return FileResponse(ROOT / "site" / "verification-workbench.html")

@app.get("/workbench/{asset}")
def workbench_asset(asset: str):
    if asset not in WORKBENCH_ASSETS:
        raise HTTPException(status_code=404, detail="unknown workbench asset")
    return FileResponse(ROOT / "site" / asset, media_type="text/javascript")

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "verification-pilot"}

@app.get("/readyz")
def readyz() -> dict[str, Any]:
    deployment = load_deployment_config()
    queue_ready = True
    queue_error = None
    try:
        _queue().counts()
    except Exception as error:  # pragma: no cover - filesystem failure is environment-specific
        queue_ready = False
        queue_error = str(error)
    storage_ready = True
    storage_error = None
    probe = JOB_ROOT.parent / ".readyz-storage-probe"
    try:
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("ready\n", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as error:  # pragma: no cover - filesystem failure is environment-specific
        storage_ready = False
        storage_error = str(error)
    provider_ready = _evidence_store_provider_ready()
    storage_controls = {"ready": True, "provider": EVIDENCE_STORE_PROVIDER, "managed_controls_required": deployment.tier == "customer-production"}
    if deployment.tier == "customer-production" and provider_ready:
        try:
            storage_controls = _repositories().evidence.control_probe()
        except Exception as error:  # pragma: no cover - provider-specific
            storage_controls = {"ready": False, "provider": EVIDENCE_STORE_PROVIDER, "missing": [f"control probe unavailable ({type(error).__name__})"]}
    adapter_config_ready = True
    adapter_config_error = None
    try:
        discover_registered_adapters()
    except ValueError as error:
        adapter_config_ready = False
        adapter_config_error = str(error)
    identity_required = os.environ.get("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "0").lower() in {"1", "true", "yes"}
    result = {
        "status": "ready" if PILOT.is_file() and queue_ready and storage_ready and provider_ready and adapter_config_ready and deployment.ready and storage_controls.get("ready", False) else "not-ready",
        "deployment": deployment.tier,
        "deployment_config": deployment.as_dict(),
        "storage_controls": storage_controls,
        "pilot_entrypoint": str(PILOT),
        "queue": "ready" if queue_ready else "unavailable",
        "storage": "ready" if storage_ready else "unavailable",
        "storage_provider": EVIDENCE_STORE_PROVIDER,
        "storage_contract": EVIDENCE_STORE_CONTRACT,
        "adapter_config": "ready" if adapter_config_ready else "invalid",
        "identity_mode": "oidc-subject-required" if identity_required else "api-key-pilot",
        "identity_subject_required": identity_required,
    }
    if not provider_ready:
        result["storage_provider_error"] = "configured provider is not implemented in this pilot image"
    if not storage_controls.get("ready", False):
        result["storage_controls_error"] = "managed evidence bucket controls are not ready"
    if adapter_config_error:
        result["adapter_config_error"] = adapter_config_error
    if not deployment.ready:
        result["deployment_config_error"] = "missing production declarations: " + ", ".join(deployment.missing)
    if queue_error:
        result["queue_error"] = queue_error
    if storage_error:
        result["storage_error"] = storage_error
    return result

@app.get("/metrics")
def metrics() -> dict[str, Any]:
    return {"service": "verification-pilot", "jobs": dict(_COUNTERS), "http": dict(_HTTP_COUNTERS), "durable_queue": _queue().counts(), "single_flight": True}

@app.get("/v1/readiness")
def release_readiness() -> dict[str, Any]:
    """Expose the signed release-readiness summary without serving raw files."""
    configured = os.environ.get("VERIFICATION_READINESS_REPORT_PATH", str(ROOT / ".artifacts" / "production-readiness.json"))
    report_path = Path(configured).resolve()
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail=f"readiness report unavailable: {type(error).__name__}") from error
    if report.get("schema_version") != "verification-production-readiness-v1":
        raise HTTPException(status_code=503, detail="readiness report has an unsupported schema")
    fields = {"schema_version", "checklist", "checklist_sha256", "readiness_sha256", "control_count", "verified_count", "open_count", "open_controls", "pilot_controls_verified", "customer_production_ready", "claim_boundary"}
    return {key: report[key] for key in fields if key in report}


@app.get("/v1/agentic-closure")
def agentic_closure_readiness() -> dict[str, Any]:
    """Expose the verified agentic closure/release state without raw RTL."""
    configured = os.environ.get(
        "VERIFICATION_AGENTIC_RELEASE_MANIFEST_PATH",
        str(ROOT / ".artifacts" / "agentic-hardware-release-manifest.json"),
    )
    manifest_path = Path(configured).resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail=f"agentic closure manifest unavailable: {type(error).__name__}") from error
    if manifest.get("schema_version") != "agentic-hardware-release-manifest-v1":
        raise HTTPException(status_code=503, detail="agentic closure manifest has an unsupported schema")
    stored = manifest.get("manifest_sha256")
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if stored != expected or manifest.get("analog_authorized") is not False:
        raise HTTPException(status_code=503, detail="agentic closure manifest failed integrity or authorization checks")
    signoff_path = manifest_path.parent / "agentic-human-signoff.json"
    human_signoff = None
    if signoff_path.is_file():
        try:
            candidate = json.loads(signoff_path.read_text(encoding="utf-8"))
            reviewed_manifest = manifest.get("human_signoff") or {}
            reviewed_digest = reviewed_manifest.get("reviewed_manifest_sha256", stored)
            if candidate.get("closure_sha256") == manifest.get("closure", {}).get("sha256") and candidate.get("manifest_sha256") == reviewed_digest:
                human_signoff = {key: candidate.get(key) for key in ("status", "reviewer", "reviewer_subject", "notes", "created_at", "review_started_at", "review_duration_seconds", "review_bindings", "receipt_sha256")}
        except (OSError, json.JSONDecodeError):
            human_signoff = None
    return {
        "schema_version": manifest["schema_version"],
        "manifest_sha256": stored,
        "release_decision": manifest.get("release_decision"),
        "claims": manifest.get("claims", {}),
        "approval": manifest.get("closure", {}).get("approval", {}),
        "human_signoff": human_signoff,
        "human_review_effort": manifest.get("metrics", {}).get("human_review_effort", {"status": "not_measured"}),
        "analog_authorized": False,
        "claim_boundary": manifest.get("claim_boundary"),
    }

@app.post("/v1/agentic-closure/signoff")
def agentic_closure_signoff(request: AgenticClosureSignoffRequest, http_request: Request) -> dict[str, Any]:
    """Record an authenticated human decision without rewriting closure evidence."""
    _require_operator_role()
    if not request.reviewer.strip() or not request.notes.strip():
        raise HTTPException(status_code=422, detail="reviewer and notes must be non-empty")
    configured = os.environ.get(
        "VERIFICATION_AGENTIC_RELEASE_MANIFEST_PATH",
        str(ROOT / ".artifacts" / "agentic-hardware-release-manifest.json"),
    )
    manifest_path = Path(configured).resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail=f"agentic closure manifest unavailable: {type(error).__name__}") from error
    stored = manifest.get("manifest_sha256")
    if request.manifest_sha256 != stored:
        raise HTTPException(status_code=409, detail="manifest digest is stale")
    if manifest.get("analog_authorized") is not False:
        raise HTTPException(status_code=409, detail="analog authorization state is invalid")
    subject = _identity_subject(http_request, request.reviewer_subject)
    if os.environ.get("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "0").lower() in {"1", "true", "yes"} and not subject:
        raise HTTPException(status_code=403, detail="trusted identity subject is required for sign-off")
    required_role = os.environ.get("VERIFICATION_REVIEWER_ROLE", "").strip()
    if required_role and required_role not in _identity_roles(http_request):
        raise HTTPException(status_code=403, detail="trusted reviewer role is required for sign-off")
    review_started_at = request.review_started_at
    review_duration_seconds = None
    if review_started_at:
        try:
            started = datetime.fromisoformat(review_started_at.replace("Z", "+00:00"))
            if started.tzinfo is None:
                raise ValueError("review start must include timezone")
            review_duration_seconds = round((datetime.now(timezone.utc) - started.astimezone(timezone.utc)).total_seconds(), 3)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=f"invalid review_started_at: {error}") from error
        if review_duration_seconds < 0 or review_duration_seconds > 86400:
            raise HTTPException(status_code=422, detail="review_started_at must be within the previous 24 hours")
    receipt = {
        "schema_version": "agentic-human-signoff-v1",
        "status": "approved" if request.approved else "rejected",
        "reviewer": request.reviewer,
        "reviewer_subject": subject,
        "notes": request.notes,
        "manifest_sha256": stored,
        "closure_sha256": manifest.get("closure", {}).get("sha256"),
        "created_at": _now(),
        "review_bindings": {
            "primary": {key: (manifest.get("closure", {}).get("approval") or {}).get(key) for key in ("proposal_sha256", "source_sha256", "scope_sha256")},
            "held_out": {key: (manifest.get("closure", {}).get("held_out", {}).get("approval") or {}).get(key) for key in ("proposal_sha256", "source_sha256", "scope_sha256")},
        },
    }
    if review_started_at:
        receipt["review_started_at"] = review_started_at
        receipt["review_duration_seconds"] = review_duration_seconds
    receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    receipt_path = manifest_path.parent / "agentic-human-signoff.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    closure_path = manifest_path.parent / str(manifest.get("closure", {}).get("path", ""))
    if not closure_path.is_file():
        raise HTTPException(status_code=503, detail="agentic closure summary is unavailable")
    next_manifest = manifest_path.with_name(f".{manifest_path.name}.{uuid.uuid4().hex}.next")
    rebuilt = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_agentic_hardware_release_manifest.py"), "--closure-summary", str(closure_path), "--output", str(next_manifest), "--human-signoff", str(receipt_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if rebuilt.returncode != 0:
        try:
            next_manifest.unlink(missing_ok=True)
        except OSError:
            pass
        raise HTTPException(status_code=503, detail="release manifest could not consume signoff receipt")
    os.replace(next_manifest, manifest_path)
    updated = json.loads(manifest_path.read_text(encoding="utf-8"))
    response = dict(receipt)
    response["release_manifest_sha256"] = updated.get("manifest_sha256")
    return response

@app.get("/v1/pilot/scorecard")
def pilot_scorecard_summary() -> dict[str, Any]:
    """Expose scorecard status and metric summaries without raw observations."""
    configured = os.environ.get("VERIFICATION_SCORECARD_PATH", str(ROOT / ".artifacts" / "open-source-pilot-scorecard.json"))
    scorecard_path = Path(configured).resolve()
    try:
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail=f"scorecard unavailable: {type(error).__name__}") from error
    errors = validate_scorecard(scorecard, finalized=False)
    if errors:
        raise HTTPException(status_code=503, detail="scorecard failed schema validation")
    pilot = scorecard.get("pilot", {}) if isinstance(scorecard.get("pilot"), dict) else {}
    review = scorecard.get("review", {}) if isinstance(scorecard.get("review"), dict) else {}
    try:
        sample_size = int(pilot.get("sample_size", 0) or 0)
    except (TypeError, ValueError):
        sample_size = 0
    metrics = []
    for metric in scorecard.get("metrics", []):
        if not isinstance(metric, dict):
            continue
        metrics.append({key: metric.get(key) for key in ("name", "unit", "baseline_median", "workbench_median", "baseline_confidence_95", "workbench_confidence_95") if key in metric} | {"evidence_count": len(metric.get("evidence", [])) if isinstance(metric.get("evidence"), list) else 0})
    return {"schema_version": scorecard["schema_version"], "scorecard_sha256": scorecard.get("scorecard_sha256"), "pilot": {key: (sample_size if key == "sample_size" else pilot.get(key)) for key in ("customer", "project", "sample_size", "baseline_window", "workbench_window")}, "metrics": metrics, "finalized": bool(sample_size >= 20 and review.get("receipt_sha256")), "claim_boundary": scorecard.get("claim_boundary", "Scorecard evidence remains bounded to supplied observations.")}

@app.get("/metrics/prometheus", response_class=PlainTextResponse)
def prometheus_metrics() -> str:
    counts = _queue().counts()
    lines = ["# TYPE verification_jobs_total counter"]
    for name, value in _COUNTERS.items():
        lines.append(f'verification_jobs_total{{state="{name}"}} {value}')
    lines.append("# TYPE verification_queue_jobs gauge")
    for state, value in sorted(counts.items()):
        lines.append(f'verification_queue_jobs{{state="{state}"}} {value}')
    lines.append(f"verification_queue_capacity {_max_queued_jobs()}")
    backup_path = Path(os.environ.get("VERIFICATION_BACKUP_MANIFEST_PATH", str(JOB_ROOT.parent / "backups")))
    manifests = sorted(backup_path.glob("*.manifest.json")) if backup_path.is_dir() else ([backup_path] if backup_path.is_file() else [])
    last_success = 0.0
    if manifests:
        try:
            created = json.loads(manifests[-1].read_text(encoding="utf-8")).get("created_at", "")
            last_success = datetime.fromisoformat(str(created).replace("Z", "+00:00")).timestamp()
        except (OSError, ValueError, json.JSONDecodeError, TypeError):
            last_success = 0.0
    try:
        rpo_seconds = max(int(os.environ.get("VERIFICATION_DR_RPO_MINUTES", "60")), 1) * 60
    except ValueError:
        rpo_seconds = 3600
    lines.append(f"verification_backup_last_success_timestamp {last_success:.3f}")
    lines.append(f"verification_backup_age_seconds {max(time.time() - last_success, 0.0):.3f}")
    lines.append(f"verification_backup_rpo_seconds {rpo_seconds}")
    lines.append("verification_single_flight 1")
    lines.append("# TYPE verification_http_responses_total counter")
    for bucket in ("2xx", "3xx", "4xx", "5xx"):
        lines.append(f'verification_http_responses_total{{class="{bucket}"}} {_HTTP_COUNTERS[bucket]}')
    lines.append("# TYPE verification_http_request_duration_seconds_sum counter")
    for bucket in ("2xx", "3xx", "4xx", "5xx"):
        lines.append(f'verification_http_request_duration_seconds_sum{{class="{bucket}"}} {_HTTP_DURATION[bucket]:.6f}')
    lines.append("# TYPE verification_http_request_duration_seconds_count counter")
    for bucket in ("2xx", "3xx", "4xx", "5xx"):
        lines.append(f'verification_http_request_duration_seconds_count{{class="{bucket}"}} {_HTTP_COUNTERS[bucket]}')
    lines.append(f'verification_request_id_generated_total {_HTTP_COUNTERS["request_id_generated"]}')
    if _OIDC_VERIFIER_CACHE:
        oidc_metrics = next(iter(_OIDC_VERIFIER_CACHE.values())).metrics()
        lines.append(f'verification_oidc_jwks_refresh_total {oidc_metrics["jwks_refresh_total"]}')
        lines.append(f'verification_oidc_jwks_unknown_kid_total {oidc_metrics["jwks_unknown_kid_total"]}')
        lines.append(f'verification_oidc_cached_keys {oidc_metrics["cached_key_count"]}')
    try:
        adapters = discover_registered_adapters()
    except ValueError:
        adapters = []
    lines.append("# TYPE verification_eda_adapter_available gauge")
    for adapter in adapters:
        lines.append(f'verification_eda_adapter_available{{name="{adapter.name}",kind="{adapter.kind}"}} {1 if adapter.available else 0}')
    lines.append("# TYPE verification_readiness gauge")
    lines.append(f"verification_readiness {1 if readyz().get('status') == 'ready' else 0}")
    return "\n".join(lines) + "\n"

@app.get("/v1/capabilities")
def capabilities() -> dict[str, Any]:
    discovered = discover_capabilities()
    try:
        adapters = discover_registered_adapters()
    except ValueError as error:
        raise HTTPException(status_code=503, detail=f"invalid EDA adapter configuration: {error}") from error
    return {"schema_version": "verification-capabilities-v1", "capabilities": [{"tool": item.tool, "executable": item.executable, "available": item.available, "status": item.status} for item in discovered], "available": sum(item.available for item in discovered), "blocked": sum(not item.available for item in discovered), "eda_adapters": [{"name": item.name, "kind": item.kind, "executable": item.executable, "version": item.version, "available": item.available, "status": item.status, "expected_artifacts": list(item.expected_artifacts), "timeout_seconds": item.timeout_seconds} for item in adapters]}


@app.get("/v1/storage/controls")
def storage_controls() -> dict[str, Any]:
    """Expose evidence-provider retention controls for deployment preflight."""
    if EVIDENCE_STORE_PROVIDER == "filesystem-pilot":
        return {"provider": EVIDENCE_STORE_PROVIDER, "ready": True, "managed_controls_required": True, "claim_boundary": "Local pilot storage has no managed versioning, encryption, or retention policy."}
    try:
        result = _evidence_store().control_probe()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"evidence provider controls unavailable: {type(error).__name__}") from error
    return {"provider": EVIDENCE_STORE_PROVIDER, **result, "managed_controls_required": True}

@app.get("/v1/contract")
def platform_contract() -> dict[str, Any]:
    """Machine-readable workflow and evidence guarantees for integrations."""
    return {
        "schema_version": "verification-platform-contract-v1",
        "workflow": ["ingest", "plan", "generate", "queue", "execute", "inspect", "repair_review", "retest", "compare", "signoff", "audit_export"],
        "agent_proposals": {
            "endpoint": "/v1/projects/{project_id}/agent-proposals",
            "kinds": ["plan", "check", "diagnosis", "repair", "next_action"],
            "required_fields": ["proposal_id", "kind", "source_revision", "action", "rationale", "evidence"],
            "statuses": ["proposal", "review_required"],
            "execution_authority": "deterministic-only",
            "claim_boundary": "Agent output is a grounded proposal; tools and human approval own execution and closure.",
        },
        "job_kinds": ["project-compile", "project-lint", "project-simulation", "project-regression", "project-formal", "project-formal-proof", "customer-adapter"],
        "customer_adapter_job": {
            "required_fields": ["project_id", "adapter_name", "adapter_args"],
            "optional_fields": ["artifact_id", "idempotency_key"],
            "preflight": ["registered_name", "available_executable", "project_scoped_source_artifact"],
            "evidence": "adapter-result.json plus bounded logs, provenance ledger, and expected artifacts",
            "argument_limits": {"max_count": 64, "max_argument_bytes": 4096, "max_total_bytes": 65536},
            "claim_boundary": "Adapter output remains tool evidence and requires human review before customer signoff.",
        },
        "evidence_guarantees": ["artifact_sha256", "request_id", "durable_events", "bounded_logs", "claim_boundary", "hash_bound_signoff", "agentic_release_self_digest"],
        "claim_boundaries": ["simulation_is_not_exhaustive_coverage", "bounded_formal_is_bound_limited", "generated_artifacts_are_review_only_until_approved"],
        "execution_safety": {
            "shell": "disabled",
            "timeout_process_group_cleanup": True,
            "posix_cpu_and_file_limits": True,
            "workspace_mode": os.environ.get("VERIFICATION_EXECUTION_WORKSPACE", "pilot-private"),
            "symlink_outputs": "blocked",
            "network_policy": os.environ.get("VERIFICATION_EXECUTION_NETWORK_POLICY", "pilot-container-policy"),
            "customer_production_requirements": [
                "disposable workspace",
                "deny-by-default network policy",
                "per-job namespace and read-only source mounts",
                "managed PostgreSQL or queue/database",
                "versioned object storage with retention",
                "enterprise OIDC and project subject mapping",
                "managed logs and alert routing",
                "named SLO owner",
                "non-empty customer EDA adapter registry",
            ],
        },
        "customer_production_requirements": {
            "required_environment": [
                "VERIFICATION_DATABASE_URL",
                "VERIFICATION_EVIDENCE_STORE_PROVIDER",
                "VERIFICATION_EVIDENCE_STORE_BUCKET",
                "VERIFICATION_REQUIRE_IDENTITY_TOKEN",
                "VERIFICATION_PROJECT_SUBJECTS",
                "VERIFICATION_EDA_ADAPTERS",
                "VERIFICATION_LOGS_ENDPOINT",
                "VERIFICATION_ALERTMANAGER_ENDPOINT",
                "VERIFICATION_SLO_OWNER",
            ],
            "runtime_evidence": [
                "managed-state migration and restore rehearsal",
                "object-store control probe",
                "credential-free execution sandbox probe",
                "customer adapter acceptance matrix",
                "centralized alert and SLO ownership confirmation",
            ],
            "runtime_preflight_schema": "verification-customer-production-runtime-v1",
            "runtime_preflight_schema_path": "deployment/observability/verification-customer-production-runtime.schema.json",
            "claim_boundary": "Declarations are necessary for readiness; provider drills and signed customer pilot results remain separate evidence.",
        },
        "storage_contract": EVIDENCE_STORE_CONTRACT,
        "observability_contract": "deployment/observability/verification-pilot-dashboard.json",
        "request_log_schema": "deployment/observability/verification-http-log.schema.json",
        "readiness_report_tool": "scripts/report_production_readiness.py",
        "handoff_manifest_tool": "scripts/build_commercial_handoff_manifest.py",
        "handoff_manifest_verifier": "scripts/verify_commercial_handoff_manifest.py",
        "deployment_config_contract": "deployment/production_config.py",
        "managed_state_contract": "deployment/managed_state_contract.py",
        "capabilities_endpoint": "/v1/capabilities",
        "readiness_endpoint": "/v1/readiness",
        "pilot_scorecard_endpoint": "/v1/pilot/scorecard",
        "agentic_closure_endpoint": "/v1/agentic-closure",
        "agentic_closure_signoff_endpoint": "/v1/agentic-closure/signoff",
        "storage_controls_endpoint": "/v1/storage/controls",
    }

class JobRequest(BaseModel):
    kind: str = "multi-design-pilot"
    project_id: str = "default"
    artifact_id: str | None = None
    testbench_artifact_id: str | None = None
    testbench_artifact_ids: list[str] = []
    formal_signal: str | None = None
    formal_expected: str | None = None
    formal_sequence: int = 3
    adapter_name: str | None = None
    adapter_args: list[str] = []
    idempotency_key: str | None = None

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
    proposal_sha256: str | None = None

class AgentProposalRequest(BaseModel):
    proposal_id: str
    kind: str
    source_revision: str
    action: str
    rationale: str
    evidence: list[str]
    status: str = "proposal"
    claims: list[str] = []

class SignoffRequest(BaseModel):
    reviewer: str
    notes: str
    approved: bool = False
    reviewer_subject: str | None = None

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _job_timeout_seconds() -> float:
    try:
        return max(float(os.environ.get("VERIFICATION_JOB_TIMEOUT_SECONDS", "1800")), 0.1)
    except ValueError:
        return 1800.0


def _identity_roles(http_request: Request | None) -> set[str]:
    """Read normalized roles asserted by the identity-aware ingress."""
    claims = _OIDC_CLAIMS.get()
    if claims is not None:
        return set(claims.roles)
    if http_request is None:
        return set()
    return {role.strip() for role in http_request.headers.get("X-Identity-Roles", "").split(",") if role.strip()}


def _identity_subject(http_request: Request | None, fallback: str | None = None) -> str | None:
    claims = _OIDC_CLAIMS.get()
    if claims is not None:
        return claims.subject
    return http_request.headers.get("X-Identity-Subject") if http_request is not None else fallback


def _public_job(job: dict[str, Any]) -> dict[str, Any]:
    """Return job metadata safe for API callers; adapter arguments are secret-bearing."""
    public = dict(job)
    if "adapter_args" in public:
        raw = public.pop("adapter_args")
        public["adapter_args_count"] = len(raw) if isinstance(raw, list) else 0
    return public


def _public_signoff(receipt: dict[str, Any]) -> dict[str, Any]:
    """Expose signoff metadata without leaking server filesystem paths."""
    public = dict(receipt)
    public.pop("report_path", None)
    return public


def _require_operator_role() -> None:
    """Require the configured operator role for customer-production writes."""
    if os.environ.get("VERIFICATION_DEPLOYMENT_TIER", "pilot").strip().lower() != "customer-production":
        return
    required = os.environ.get("VERIFICATION_OPERATOR_ROLE", "").strip()
    if not required or required not in _identity_roles(None):
        raise HTTPException(status_code=403, detail="trusted operator role is required")

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

def _prepare_job_workspace(job_id: str) -> Path:
    """Create and harden one job's private workspace before tool execution."""
    job_dir = _path(job_id).parent
    if job_dir.is_symlink():
        raise HTTPException(status_code=409, detail="job workspace must not be a symlink")
    job_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(job_dir, 0o700)
    except OSError as error:
        raise HTTPException(status_code=503, detail="job workspace permissions unavailable") from error
    return job_dir

def _write(job: dict[str, Any]) -> None:
    path = _path(job["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _publish_job_artifacts(job_id: str, job_dir: Path) -> dict[str, dict[str, object]]:
    """Publish local run outputs through the selected immutable evidence store."""
    published: dict[str, dict[str, object]] = {}
    if not job_dir.is_dir():
        return published
    for source in sorted(job_dir.rglob("*")):
        if not source.is_file() or source.name == "evidence-bundle.zip":
            continue
        relative = source.relative_to(job_dir).as_posix()
        stored = _evidence_store().put(f"jobs/{job_id}/artifacts/{relative}", source.read_bytes())
        published[relative] = {"object_key": stored.key, "sha256": stored.sha256, "bytes": len(stored.content)}
    return published


def _materialize_bundle(job_id: str, bundle_path: Path) -> bool:
    """Restore a bundle from immutable evidence storage after local loss."""
    if bundle_path.is_file():
        return True
    stored = _evidence_store().get(f"jobs/{job_id}/evidence-bundle.zip")
    if stored is None:
        return False
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = bundle_path.with_name(bundle_path.name + ".restore.tmp")
    temporary.write_bytes(stored.content)
    temporary.chmod(0o600)
    temporary.replace(bundle_path)
    return True

def _audit_reason(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"(?:[A-Za-z]:)?/[^\s,;]+", "[PATH]", str(value))
    return text[:500]

def _record(job: dict[str, Any], status: str, **details: Any) -> None:
    event = {"at": _now(), "status": status, **details}
    if job.get("request_id"):
        event["request_id"] = job["request_id"]
    job.setdefault("events", []).append(event)

@app.post("/v1/projects", status_code=201)
def create_project(request: ProjectRequest, http_request: Request = None) -> dict[str, str]:
    _require_operator_role()
    if not request.id or not request.id.replace("-", "").replace("_", "").isalnum() or not request.name.strip():
        raise HTTPException(status_code=400, detail="invalid project")
    identity_required = os.environ.get("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "0").lower() in {"1", "true", "yes"}
    subject = _identity_subject(http_request)
    if identity_required and not subject:
        raise HTTPException(status_code=403, detail="trusted identity subject is required to create a project")
    try:
        return _projects().create(request.id, request.name.strip())
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

@app.get("/v1/projects")
def list_projects(http_request: Request = None) -> list[dict[str, str]]:
    projects = _projects().list()
    configured = _project_keys()
    if not configured or http_request is None:
        return projects
    supplied = http_request.headers.get("X-Project-Key", "")
    allowed = {project_id for project_id, key in configured.items() if hmac.compare_digest(supplied, key)}
    if not allowed:
        raise HTTPException(status_code=403, detail="valid project key is required to list projects")
    return [project for project in projects if project["id"] in allowed]

@app.get("/v1/projects/{project_id}")
def get_project(project_id: str) -> dict[str, str]:
    try:
        return _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error

@app.get("/v1/projects/{project_id}/dashboard")
def project_dashboard(project_id: str) -> dict[str, Any]:
    try:
        project = _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error
    jobs = _list_jobs_raw(project_id=project_id)
    terminal = [job for job in jobs if job.get("status") in {"passed", "failed"}]
    signed = []
    for job in terminal:
        signoff = _path(job["id"]).parent / "pilot-signoff.json"
        if signoff.is_file():
            try:
                record = json.loads(signoff.read_text(encoding="utf-8"))
                record["valid"] = verify_signoff(signoff)
                signed.append(record)
            except json.JSONDecodeError:
                continue
    return {"project": project, "collateral_count": len(_collateral().list(project_id)), "jobs": {"total": len(jobs), "queued": sum(job.get("status") == "queued" for job in jobs), "running": sum(job.get("status") == "running" for job in jobs), "passed": sum(job.get("status") == "passed" for job in jobs), "failed": sum(job.get("status") == "failed" for job in jobs)}, "terminal_jobs": [{"id": job["id"], "kind": job["kind"], "status": job["status"], "adapter_name": job.get("adapter_name"), "adapter_args_count": len(job.get("adapter_args", [])) if isinstance(job.get("adapter_args"), list) else 0, "evidence": job.get("evidence", {})} for job in terminal], "signoffs": signed}

@app.post("/v1/projects/{project_id}/collateral", status_code=201)
def add_collateral(project_id: str, request: CollateralRequest) -> dict[str, object]:
    _require_operator_role()
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
    _require_operator_role()
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
    _require_operator_role()
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

@app.post("/v1/projects/{project_id}/agent-proposals")
def submit_agent_proposal(project_id: str, request: AgentProposalRequest) -> dict[str, Any]:
    """Persist a grounded model proposal without granting execution authority."""
    _require_operator_role()
    try:
        _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error
    try:
        proposal = validate_agent_proposal(request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=f"invalid agent proposal: {error}") from error
    destination = JOB_ROOT.parent / "proposals" / project_id
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f"{proposal.proposal_sha256}.json"
    output.write_text(json.dumps(proposal.record(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"project_id": project_id, "proposal": proposal.record(), "proposal_path": str(output), "execution_authority": "deterministic-only"}

@app.post("/v1/projects/{project_id}/collateral/{artifact_id}/generate")
def generate_project_artifacts(project_id: str, artifact_id: str) -> dict[str, Any]:
    _require_operator_role()
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
    _require_operator_role()
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
    _require_operator_role()
    job = _read(job_id)
    if job.get("kind") != "project-simulation" or job.get("status") != "failed":
        raise HTTPException(status_code=409, detail="a failed project-simulation job is required")
    # Approval may only apply to the exact proposal the reviewer inspected.
    # Keep accepting old clients without a digest for compatibility, while
    # the workbench always supplies it.
    if request.approved and request.proposal_sha256:
        preview = repair_project_collateral(str(job["project_id"]), str(job["artifact_id"]), request.model_copy(update={"approved": False}))
        expected = preview.get("proposal", {}).get("proposal_sha256")
        if expected != request.proposal_sha256:
            raise HTTPException(status_code=409, detail="repair proposal changed; review the current diff again")
    result = repair_project_collateral(str(job["project_id"]), str(job["artifact_id"]), request)
    if "repaired_artifact" not in result:
        return {"source_job_id": job_id, "proposal": result["proposal"], "retest_job": None}
    retest = create_job(JobRequest(kind="project-simulation", project_id=str(job["project_id"]), artifact_id=str(result["repaired_artifact"]["id"]), testbench_artifact_id=str(job["testbench_artifact_id"]), idempotency_key=f"retest-{job_id}-{result['proposal']['proposal_sha256']}"))
    retest["lineage"] = {"baseline_job_id": job_id, "proposal_sha256": result["proposal"]["proposal_sha256"], "source_artifact_id": str(job["artifact_id"]), "repaired_artifact_id": str(result["repaired_artifact"]["id"])}
    _write(retest)
    return {"source_job_id": job_id, "proposal": result["proposal"], "repaired_artifact": result["repaired_artifact"], "retest_job": retest}

@app.get("/v1/jobs/{job_id}/proof-of-value")
def project_proof_of_value(job_id: str) -> dict[str, Any]:
    job = _read(job_id)
    if job.get("kind") == "customer-adapter":
        if job.get("status") not in {"passed", "failed", "blocked"}:
            raise HTTPException(status_code=409, detail="a terminal customer-adapter job is required")
        try:
            result_path = _path(job_id).parent / "adapter-result.json"
            if not result_path.is_file():
                raise OSError("adapter result is unavailable")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            report = {"schema_version": "verification-adapter-pov-v1", "job_id": job_id, "project_id": job["project_id"], "adapter_name": job.get("adapter_name"), "status": job["status"], "execution": {"tool": result.get("tool"), "status": result.get("status"), "exit_code": result.get("exit_code"), "artifact_count": len(result.get("artifacts", [])) if isinstance(result.get("artifacts"), list) else 0}, "claim_boundary": "Adapter evidence records one tool execution; it is not exhaustive verification or customer production qualification."}
            report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            report_path = _path(job_id).parent / "adapter-proof-of-value-report.json"
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            job.setdefault("evidence", {})["adapter_pov"] = str(report_path)
            _write(job)
            return report
        except (OSError, ValueError, json.JSONDecodeError) as error:
            raise HTTPException(status_code=422, detail=f"adapter proof-of-value generation failed: {error}") from error
    if job.get("kind") != "project-simulation" or job.get("status") not in {"passed", "failed"}:
        raise HTTPException(status_code=409, detail="a terminal project-simulation job is required")
    try:
        report_path = write_project_pov(_path(job_id).parent)
        return json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"proof-of-value generation failed: {error}") from error

@app.get("/v1/jobs/{job_id}/evidence")
def project_job_evidence(job_id: str) -> dict[str, Any]:
    """Return a bounded, run-scoped evidence view for the workbench.

    The browser never receives arbitrary filesystem paths. Text is deliberately
    capped because the endpoint is for investigation context, while the
    immutable bundle remains the complete handoff artifact.
    """
    job = _read(job_id)
    root = _path(job_id).parent
    allowed = {
        "adapter-result.json",
        "adapter-proof-of-value-report.json",
        "project-simulation-result.json", "project-compile-result.json",
        "project-lint-result.json", "project-formal-result.json",
        "project-formal-proof-result.json", "project-regression-result.json",
        "diagnosis.json", "closure-report.json", "verification-ir.json",
        "functional-coverage.json", "artifact-manifest.json",
        "simulation/stdout.log", "simulation/stderr.log",
    }
    files: dict[str, Any] = {}
    for relative in sorted(allowed):
        path = root / relative
        if not path.is_file():
            stored = _evidence_store().get(f"jobs/{job_id}/artifacts/{relative}")
            if stored is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_name(path.name + ".restore.tmp")
                temporary.write_bytes(stored.content)
                temporary.chmod(0o600)
                temporary.replace(path)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            files[relative] = {"present": True, "bytes": path.stat().st_size, "text": text[:20000], "truncated": len(text) > 20000}
        except OSError:
            files[relative] = {"present": False, "reason": "unreadable"}
    artifacts: dict[str, Any] = {}
    store = _collateral()
    for role, artifact_id in (("rtl", job.get("artifact_id")), ("testbench", job.get("testbench_artifact_id"))):
        if not artifact_id:
            continue
        try:
            record = store.get(str(artifact_id))
            if record.get("project_id") != job.get("project_id"):
                continue
            source = (store.root / str(record["path"])).read_text(encoding="utf-8", errors="replace")
            artifacts[role] = {"id": record["id"], "name": record["name"], "kind": record["kind"], "version": record["version"], "sha256": record["sha256"], "content": source[:30000], "truncated": len(source) > 30000}
        except (KeyError, OSError, UnicodeError):
            artifacts[role] = {"id": str(artifact_id), "available": False}
    waveform_path = root / "simulation" / "waveform.vcd"
    if not waveform_path.is_file():
        stored = _evidence_store().get(f"jobs/{job_id}/artifacts/simulation/waveform.vcd")
        if stored is not None:
            waveform_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = waveform_path.with_name(waveform_path.name + ".restore.tmp")
            temporary.write_bytes(stored.content)
            temporary.chmod(0o600)
            temporary.replace(waveform_path)
    waveform: dict[str, Any] = {"present": waveform_path.is_file(), "path": "simulation/waveform.vcd"}
    if waveform_path.is_file():
        try:
            waveform_text = waveform_path.read_text(encoding="utf-8", errors="replace")
            waveform["bytes"] = waveform_path.stat().st_size
            waveform["signals"] = sorted(set(match.group(1) for match in re.finditer(r"\$var\s+\S+\s+\S+\s+\S+\s+(\S+)\s+\$end", waveform_text)))[:200]
            waveform["excerpt"] = waveform_text[:12000]
            waveform["truncated"] = len(waveform_text) > 12000
        except OSError:
            waveform["present"] = False
            waveform["reason"] = "unreadable"
    return {"job": {"id": job["id"], "project_id": job["project_id"], "kind": job["kind"], "status": job["status"], "error": job.get("error"), "artifact_id": job.get("artifact_id"), "testbench_artifact_id": job.get("testbench_artifact_id"), "adapter_name": job.get("adapter_name"), "adapter_args_count": len(job.get("adapter_args", [])) if isinstance(job.get("adapter_args"), list) else 0, "events": job.get("events", []), "evidence": job.get("evidence", {})}, "artifacts": artifacts, "files": files, "waveform": waveform}

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

@app.get("/v1/jobs/{job_id}/regression-proof-of-value")
def project_regression_proof_of_value(job_id: str) -> dict[str, Any]:
    job = _read(job_id)
    if job.get("kind") != "project-regression" or job.get("status") not in {"passed", "failed"}:
        raise HTTPException(status_code=409, detail="a terminal project-regression job is required")
    try:
        path = write_regression_pov(_path(job_id).parent)
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"regression proof-of-value generation failed: {error}") from error

def signoff_project_job(job_id: str, request: SignoffRequest, http_request: Request | None = None) -> dict[str, Any]:
    job = _read(job_id)
    if job.get("kind") == "project-simulation":
        if job.get("status") not in {"passed", "failed"}:
            raise HTTPException(status_code=409, detail="a terminal project-simulation job is required")
        report_path = _path(job_id).parent / "proof-of-value-report.json"
        if not report_path.is_file():
            write_project_pov(_path(job_id).parent)
    elif job.get("kind") == "project-regression":
        if job.get("status") not in {"passed", "failed"}:
            raise HTTPException(status_code=409, detail="a terminal project-regression job is required")
        report_path = _path(job_id).parent / "regression-proof-of-value-report.json"
        if not report_path.is_file():
            write_regression_pov(_path(job_id).parent)
    elif job.get("kind") == "customer-adapter":
        if job.get("status") not in {"passed", "failed"}:
            raise HTTPException(status_code=409, detail="a terminal customer-adapter job is required")
        report_path = _path(job_id).parent / "adapter-proof-of-value-report.json"
        if not report_path.is_file():
            project_proof_of_value(job_id)
    else:
        raise HTTPException(status_code=409, detail="project simulation, regression, or customer-adapter job is required")
    try:
        # In HTTP mode only the trusted identity middleware/header is
        # authoritative. A JSON body field is accepted for direct pilot
        # service calls, but cannot spoof an enterprise subject over HTTP.
        subject = _identity_subject(http_request, request.reviewer_subject)
        if os.environ.get("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "0").lower() in {"1", "true", "yes"} and not subject:
            raise HTTPException(status_code=403, detail="trusted identity subject is required for sign-off")
        required_role = os.environ.get("VERIFICATION_REVIEWER_ROLE", "").strip()
        if required_role and required_role not in _identity_roles(http_request):
            if http_request is not None:
                raise HTTPException(status_code=403, detail="trusted reviewer role is required for sign-off")
            raise HTTPException(status_code=403, detail="reviewer role is required for sign-off")
        signoff_path = write_signoff(report_path, reviewer=request.reviewer, notes=request.notes, approved=request.approved, reviewer_subject=subject)
        return json.loads(signoff_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"sign-off failed: {error}") from error

@app.post("/v1/jobs/{job_id}/signoff")
def signoff_project_job_http(job_id: str, request: SignoffRequest, http_request: Request) -> dict[str, Any]:
    return _public_signoff(signoff_project_job(job_id, request, http_request))

@app.get("/v1/jobs/{job_id}/signoff")
def get_signoff_project_job(job_id: str) -> dict[str, Any]:
    _read(job_id)
    signoff_path = _path(job_id).parent / "pilot-signoff.json"
    if not signoff_path.is_file():
        raise HTTPException(status_code=404, detail="no sign-off receipt recorded")
    try:
        record = json.loads(signoff_path.read_text(encoding="utf-8"))
        record["valid"] = verify_signoff(signoff_path)
        return _public_signoff(record)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"sign-off receipt unavailable: {error}") from error

@app.post("/v1/jobs", status_code=202)
def create_job(request: JobRequest) -> dict[str, Any]:
    _require_operator_role()
    if request.kind not in {"multi-design-pilot", "customer-adapter", "project-compile", "project-lint", "project-formal", "project-formal-proof", "project-simulation", "project-regression"}:
        raise HTTPException(status_code=400, detail="unsupported job kind")
    if not request.project_id or not request.project_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="invalid project id")
    _enforce_project_key(request.project_id)
    if request.idempotency_key is not None and (not request.idempotency_key.strip() or len(request.idempotency_key) > 128):
        raise HTTPException(status_code=400, detail="invalid idempotency key")
    request_fingerprint = hashlib.sha256(json.dumps(request.model_dump(exclude={"idempotency_key"}), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if request.idempotency_key:
        for existing in _list_jobs_raw(project_id=request.project_id):
            if existing.get("idempotency_key") == request.idempotency_key:
                if existing.get("request_fingerprint") != request_fingerprint:
                    raise HTTPException(status_code=409, detail="idempotency key is already bound to a different request")
                return _public_job(existing)
    if request.kind == "customer-adapter":
        if not request.adapter_name:
            raise HTTPException(status_code=400, detail="adapter_name is required for customer-adapter")
        try:
            registered = {item.name: item for item in discover_registered_adapters()}
        except ValueError as error:
            raise HTTPException(status_code=503, detail=f"invalid EDA adapter configuration: {error}") from error
        adapter = registered.get(request.adapter_name)
        if adapter is None:
            raise HTTPException(status_code=404, detail="adapter is not registered")
        if not adapter.available:
            raise HTTPException(status_code=409, detail="adapter executable is blocked or unavailable")
        try:
            validate_adapter_args(request.adapter_args)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        if request.artifact_id:
            try:
                source_record = _collateral().get(request.artifact_id)
            except KeyError as error:
                raise HTTPException(status_code=404, detail="collateral not found") from error
            if source_record["project_id"] != request.project_id:
                raise HTTPException(status_code=404, detail="collateral not found")
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
    job = {"id": uuid.uuid4().hex, "kind": request.kind, "project_id": request.project_id, "artifact_id": request.artifact_id, "testbench_artifact_id": request.testbench_artifact_id, "testbench_artifact_ids": request.testbench_artifact_ids, "formal_signal": request.formal_signal, "formal_expected": request.formal_expected, "formal_sequence": request.formal_sequence, "adapter_name": request.adapter_name, "adapter_args": request.adapter_args, "idempotency_key": request.idempotency_key, "request_fingerprint": request_fingerprint, "status": "queued", "created_at": _now(), "events": []}
    if _REQUEST_ID.get():
        job["request_id"] = _REQUEST_ID.get()
    _record(job, "queued")
    _COUNTERS["submitted"] += 1
    _write(job)
    _queue().enqueue(job["id"], project_id=request.project_id, kind=request.kind, payload={"artifact_id": request.artifact_id, "testbench_artifact_id": request.testbench_artifact_id, "testbench_artifact_ids": request.testbench_artifact_ids, "formal_signal": request.formal_signal, "formal_expected": request.formal_expected, "formal_sequence": request.formal_sequence} if request.artifact_id else {})
    return _public_job(job)

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    return _public_job(_read(job_id))

def _list_jobs_raw(project_id: str | None = None) -> list[dict[str, Any]]:
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


@app.get("/v1/jobs")
def list_jobs(project_id: str | None = None) -> list[dict[str, Any]]:
    return [_public_job(job) for job in _list_jobs_raw(project_id=project_id)]

@app.get("/v1/projects/{project_id}/audit")
def project_audit(project_id: str, limit: int = 500) -> dict[str, Any]:
    """Return a bounded, project-scoped audit export without arbitrary paths."""
    try:
        _projects().get(project_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error
    bounded_limit = min(max(int(limit), 1), 2000)
    entries: list[dict[str, Any]] = []
    for job in _list_jobs_raw(project_id=project_id):
        for index, event in enumerate(job.get("events", []), 1):
            entries.append({
                "job_id": job["id"],
                "project_id": project_id,
                "kind": job.get("kind"),
                "adapter_name": job.get("adapter_name"),
                "adapter_args_count": len(job.get("adapter_args", [])) if isinstance(job.get("adapter_args"), list) else 0,
                "event_index": index,
                "at": event.get("at") or event.get("timestamp") or event.get("created_at"),
                "status": event.get("status") or event.get("event"),
                "request_id": event.get("request_id") or job.get("request_id"),
                "executor": event.get("executor"),
                "reason": _audit_reason(event.get("reason") or event.get("error")),
            })
    entries.sort(key=lambda item: (item.get("at") or "", item["job_id"], item["event_index"]))
    selected = entries[:bounded_limit]
    digest = hashlib.sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"schema_version": "verification-audit-v1", "project_id": project_id, "total": len(entries), "entries": selected, "truncated": len(entries) > bounded_limit, "export_sha256": digest}

@app.post("/v1/jobs/{job_id}/run")
def run_job(job_id: str) -> dict[str, Any]:
    _require_operator_role()
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
            elif job["kind"] == "customer-adapter":
                source_revision = "unknown"
                if job.get("artifact_id"):
                    source_revision = str(_collateral().get(str(job["artifact_id"]))["version"])
                result_data = execute_registered_adapter(name=str(job["adapter_name"]), args=list(job.get("adapter_args", [])), run_root=job_dir, source_revision=source_revision)
                stdout = (job_dir / "stdout.log").read_text(encoding="utf-8") if (job_dir / "stdout.log").is_file() else ""
                stderr = (job_dir / "stderr.log").read_text(encoding="utf-8") if (job_dir / "stderr.log").is_file() else ""
                exit_code = int(result_data.get("exit_code") or 0) if result_data.get("status") == "passed" else 1
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
    job["evidence_objects"] = _publish_job_artifacts(job_id, job_dir)
    reported_status = result_data.get("status") if isinstance(result_data, dict) else None
    job["status"] = reported_status if reported_status in {"passed", "failed", "blocked"} else ("passed" if exit_code == 0 else "failed")
    if job["status"] == "blocked" and not job.get("error"):
        job["error"] = "execution did not produce terminal evidence before the configured timeout or artifact boundary"
    _record(job, job["status"], exit_code=exit_code)
    if job["status"] in _COUNTERS:
        _COUNTERS[job["status"]] += 1
    _queue().finish(job_id, status=job["status"])
    job["finished_at"] = _now(); job["exit_code"] = exit_code
    if timeout_error:
        job["error"] = timeout_error
    job["evidence"] = ({"adapter_result": str(job_dir / "adapter-result.json")} if job["kind"] == "customer-adapter" else {"project_compile": str(job_dir / "project-compile-result.json")} if job["kind"] == "project-compile" else {"project_lint": str(job_dir / "project-lint-result.json")} if job["kind"] == "project-lint" else {"project_formal": str(job_dir / "project-formal-result.json")} if job["kind"] == "project-formal" else {"project_formal_proof": str(job_dir / "project-formal-proof-result.json")} if job["kind"] == "project-formal-proof" else {"project_simulation": str(job_dir / "project-simulation-result.json")} if job["kind"] == "project-simulation" else {"project_regression": str(job_dir / "project-regression-result.json")} if job["kind"] == "project-regression" else {"pilot_summary": "benchmarks/multi_design_pilot/runs/latest/pilot-summary.json", "validation": "benchmarks/multi_design_pilot/runs/latest/clean-checkout-validation.json"})
    _write(job)
    return _public_job(job)

@app.post("/v1/jobs/{job_id}/run-async", status_code=202)
def run_job_async(job_id: str, background_tasks: BackgroundTasks) -> dict[str, Any]:
    _require_operator_role()
    job = _read(job_id)
    if job["status"] not in {"queued", "failed"}:
        raise HTTPException(status_code=409, detail=f"job is {job['status']}")
    # Durable workers own asynchronous execution. Scheduling an in-process
    # background task here would race a worker claiming the same queue row.
    return {"id": job_id, "status": "accepted", "poll": f"/v1/jobs/{job_id}"}

@app.post("/v1/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict[str, Any]:
    _require_operator_role()
    job = _read(job_id)
    if job["status"] != "queued":
        raise HTTPException(status_code=409, detail=f"job is {job['status']}")
    # Atomically win cancellation against a worker claim before mutating the
    # JSON record. If the worker claimed first, it owns execution and the API
    # must not present a false cancelled state.
    queued = _queue().cancel(job_id)
    if queued.get("status") != "cancelled":
        raise HTTPException(status_code=409, detail=f"job is {queued.get('status', 'running')}")
    job["status"] = "cancelled"
    job["cancelled_at"] = _now()
    _record(job, "cancelled")
    _write(job)
    return _public_job(job)

@app.get("/v1/jobs/{job_id}/bundle")
def get_bundle(job_id: str) -> dict[str, Any]:
    job = _read(job_id)
    if job["kind"] in {"customer-adapter", "project-compile", "project-lint", "project-formal", "project-formal-proof", "project-simulation", "project-regression"}:
        if job["status"] not in {"passed", "failed"}:
            raise HTTPException(status_code=409, detail="project evidence bundle requires a terminal job")
        bundle_path = _path(job_id).parent / "evidence-bundle.zip"
        included: list[str] = []
        if _materialize_bundle(job_id, bundle_path):
            with zipfile.ZipFile(bundle_path) as archive:
                included = archive.namelist()
        else:
            with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for source in sorted(_path(job_id).parent.rglob("*")):
                    if source.is_file() and source.name != bundle_path.name:
                        archive.write(source, source.relative_to(_path(job_id).parent).as_posix())
                        included.append(source.relative_to(_path(job_id).parent).as_posix())
        stored = _evidence_store().put(f"jobs/{job_id}/evidence-bundle.zip", bundle_path.read_bytes())
        return {"job_id": job_id, "status": job["status"], "evidence": job.get("evidence", {}), "job_metadata": str(_path(job_id)), "bundle_path": str(bundle_path), "object_key": stored.key, "bundle_sha256": stored.sha256, "bundle_files": len(included), "files": included, "missing_files": []}
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
    if _materialize_bundle(job_id, bundle_path):
        with zipfile.ZipFile(bundle_path) as archive:
            included = archive.namelist()
        missing = [relative.as_posix() for relative in wanted if relative.as_posix() not in included]
    else:
        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for relative in wanted:
                source = evidence_root / relative
                if source.is_file():
                    archive.write(source, relative.as_posix())
                    included.append(relative.as_posix())
                else:
                    missing.append(relative.as_posix())
    stored = _evidence_store().put(f"jobs/{job_id}/evidence-bundle.zip", bundle_path.read_bytes())
    return {"job_id": job_id, "status": job["status"], "evidence": job.get("evidence", {}), "job_metadata": str(_path(job_id)), "bundle_path": str(bundle_path), "object_key": stored.key, "bundle_sha256": stored.sha256, "bundle_files": len(included), "files": included, "missing_files": missing}

@app.get("/v1/jobs/{job_id}/bundle/download")
def download_bundle(job_id: str) -> FileResponse:
    bundle = get_bundle(job_id)
    return FileResponse(bundle["bundle_path"], media_type="application/zip", filename=f"verification-{job_id}.zip")
