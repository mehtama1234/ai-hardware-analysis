"""Provider-neutral local model backend contract for verification proposals."""
from __future__ import annotations

from dataclasses import dataclass
import atexit
import json
import os
import select
import shlex
import subprocess
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError

from .agent import AgentProposal, validate_agent_proposal


@dataclass(frozen=True)
class BackendResult:
    backend: str
    status: str
    proposal: AgentProposal | None = None
    error: str | None = None
    raw: dict[str, Any] | None = None


_LOCAL_BATCH_WORKER: subprocess.Popen[str] | None = None
_LOCAL_BATCH_COMMAND: tuple[str, ...] | None = None


def _stop_local_batch_worker() -> None:
    global _LOCAL_BATCH_WORKER, _LOCAL_BATCH_COMMAND
    worker = _LOCAL_BATCH_WORKER
    _LOCAL_BATCH_WORKER = None
    _LOCAL_BATCH_COMMAND = None
    if worker is None:
        return
    if worker.poll() is None:
        worker.kill()
    try:
        worker.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass


atexit.register(_stop_local_batch_worker)


def _get_local_batch_worker(command: tuple[str, ...]) -> subprocess.Popen[str]:
    global _LOCAL_BATCH_WORKER, _LOCAL_BATCH_COMMAND
    if _LOCAL_BATCH_WORKER is not None and _LOCAL_BATCH_COMMAND != command:
        _stop_local_batch_worker()
    if _LOCAL_BATCH_WORKER is None:
        _LOCAL_BATCH_WORKER = subprocess.Popen(
            list(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        _LOCAL_BATCH_COMMAND = command
    return _LOCAL_BATCH_WORKER


def _read_worker_line(worker: subprocess.Popen[str], timeout_seconds: float) -> str | None:
    if worker.stdout is None:
        return None
    ready, _, _ = select.select([worker.stdout], [], [], timeout_seconds)
    if not ready:
        return None
    line = worker.stdout.readline()
    return line if line else None


def _configured_timeout(default: float) -> float:
    raw = os.environ.get("VERIFICATION_LLM_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def invoke_local_backend_batch(requests: list[dict[str, Any]], *, timeout_seconds: float | None = None) -> list[BackendResult]:
    """Invoke one resident JSONL worker so model weights load only once per run."""
    raw = os.environ.get("VERIFICATION_LLM_BATCH_COMMAND", "").strip()
    timeout_seconds = _configured_timeout(300.0) if timeout_seconds is None else timeout_seconds
    if not raw:
        return [BackendResult("local-batch-command", "unconfigured", error="VERIFICATION_LLM_BATCH_COMMAND is not configured") for _ in requests]
    command = tuple(shlex.split(raw))
    try:
        worker = _get_local_batch_worker(command)
        if worker.stdin is None:
            raise OSError("local batch worker stdin is unavailable")
        results = []
        for request in requests:
            worker.stdin.write(json.dumps(request) + "\n")
            worker.stdin.flush()
            line = _read_worker_line(worker, timeout_seconds)
            if line is None:
                _stop_local_batch_worker()
                return results + [BackendResult("local-batch-command", "blocked", error="local batch backend timed out or exited") for _ in requests[len(results):]]
            payload = None
            try:
                payload = json.loads(line)
                results.append(BackendResult("local-batch-command", "available", proposal=validate_agent_proposal(payload), raw=payload))
            except (ValueError, TypeError, json.JSONDecodeError) as error:
                results.append(BackendResult("local-batch-command", "blocked", error=f"local batch backend emitted invalid proposal: {error}", raw=payload if isinstance(payload, dict) else None))
        return results
    except (OSError, ValueError) as error:
        _stop_local_batch_worker()
        return [BackendResult("local-batch-command", "blocked", error=f"local batch backend failed: {type(error).__name__}") for _ in requests]


def invoke_local_backend(request: dict[str, Any], *, timeout_seconds: float | None = None) -> BackendResult:
    """Invoke a configured local command using JSONL stdin/stdout.

    The command must emit one typed proposal JSON object. No shell is used;
    model output remains subject to the same validator as every other agent.
    """
    raw = os.environ.get("VERIFICATION_LLM_COMMAND", "").strip()
    timeout_seconds = _configured_timeout(30.0) if timeout_seconds is None else timeout_seconds
    # A resident worker is also valid for one-request callers such as the
    # diagnosis and repair stages.  Keeping one transport contract avoids
    # silently switching a real model run back to a mock one-shot process.
    if not raw and os.environ.get("VERIFICATION_LLM_BATCH_COMMAND", "").strip():
        results = invoke_local_backend_batch([request], timeout_seconds=timeout_seconds)
        return results[0]
    if not raw:
        return BackendResult("local-command", "unconfigured", error="VERIFICATION_LLM_COMMAND is not configured")
    try:
        completed = subprocess.run(shlex.split(raw), input=json.dumps(request), text=True, capture_output=True, timeout=timeout_seconds, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        return BackendResult("local-command", "blocked", error=f"local backend failed: {type(error).__name__}")
    if completed.returncode:
        return BackendResult("local-command", "blocked", error=f"local backend exit {completed.returncode}")
    try:
        payload = json.loads(completed.stdout)
        return BackendResult("local-command", "available", proposal=validate_agent_proposal(payload), raw=payload)
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        return BackendResult("local-command", "blocked", error=f"local backend emitted invalid proposal: {error}")


def invoke_openai_compatible_backend(request: dict[str, Any], *, timeout_seconds: float | None = None) -> BackendResult:
    """Call a local OpenAI-compatible chat endpoint and validate JSON output."""
    timeout_seconds = _configured_timeout(30.0) if timeout_seconds is None else timeout_seconds
    base_url = os.environ.get("VERIFICATION_LLM_BASE_URL", "").strip().rstrip("/")
    model = os.environ.get("VERIFICATION_LLM_MODEL", "").strip()
    if not base_url or not model:
        return BackendResult("openai-compatible-local", "unconfigured", error="VERIFICATION_LLM_BASE_URL and VERIFICATION_LLM_MODEL are required")
    body = {"model": model, "temperature": 0, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Return exactly one evidence-grounded verification proposal JSON object. Do not claim closure."}, {"role": "user", "content": json.dumps(request, sort_keys=True)}]}
    try:
        response = urlopen(Request(base_url + "/v1/chat/completions", data=json.dumps(body).encode(), headers={"content-type": "application/json"}), timeout=timeout_seconds)
        payload = json.loads(response.read().decode())
        content = payload["choices"][0]["message"]["content"]
        payload = json.loads(content)
        return BackendResult("openai-compatible-local", "available", proposal=validate_agent_proposal(payload), raw=payload)
    except (OSError, URLError, KeyError, IndexError, ValueError, TypeError, json.JSONDecodeError) as error:
        return BackendResult("openai-compatible-local", "blocked", error=f"local OpenAI-compatible backend failed: {type(error).__name__}: {error}")
