"""Execution-in-the-loop adapter with reproducible run records."""

from __future__ import annotations

from dataclasses import asdict
import subprocess
import time
import hashlib
import os
import signal
import math
import resource
import shutil
from pathlib import Path

from .ledger import ProvenanceLedger, ToolRun, evidence_for

MAX_LOG_BYTES = 2 * 1024 * 1024
_SECRET_FLAGS = {"--api-key", "--token", "--password", "--secret", "--license-key"}

def _bound_log(value: str) -> tuple[str, bool]:
    encoded = (value or "").encode("utf-8", errors="replace")
    if len(encoded) <= MAX_LOG_BYTES:
        return value or "", False
    return encoded[:MAX_LOG_BYTES].decode("utf-8", errors="ignore") + "\n[output truncated]\n", True

def _redact_command(command: list[str]) -> list[str]:
    redacted: list[str] = []
    redact_next = False
    for argument in command:
        if redact_next:
            redacted.append("[REDACTED]")
            redact_next = False
            continue
        if argument in _SECRET_FLAGS:
            redacted.append(argument)
            redact_next = True
            continue
        if any(argument.startswith(flag + "=") for flag in _SECRET_FLAGS) or any(argument.upper().startswith(name + "=") for name in ("API_KEY", "TOKEN", "PASSWORD", "LICENSE_KEY")):
            redacted.append(argument.split("=", 1)[0] + "=[REDACTED]")
        else:
            redacted.append(argument)
    return redacted


def _execution_limits(timeout_seconds: float):
    """Return a POSIX child setup that bounds CPU time and single-file size."""
    cpu_seconds = max(1, int(math.ceil(timeout_seconds)))
    try:
        file_bytes = max(1, int(os.environ.get("VERIFICATION_JOB_MAX_FILE_BYTES", str(512 * 1024 * 1024))))
    except ValueError:
        file_bytes = 512 * 1024 * 1024

    def apply_limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))

    return apply_limits, {"cpu_seconds": cpu_seconds, "max_file_bytes": file_bytes}


def _sandbox_command(command: list[str]) -> tuple[list[str], dict[str, object]]:
    """Wrap a tool in Linux namespaces when production isolation is enabled."""
    mode = os.environ.get("VERIFICATION_EXECUTION_SANDBOX", "pilot").strip().lower()
    if mode in {"", "pilot", "none", "disabled"}:
        return command, {"mode": mode or "pilot", "enforced": False}
    if mode != "isolated":
        raise ValueError("VERIFICATION_EXECUTION_SANDBOX must be pilot or isolated")
    if os.name != "posix":
        raise RuntimeError("isolated execution requires POSIX user, PID, mount, and network namespaces")
    unshare = shutil.which("unshare")
    if not unshare:
        raise RuntimeError("isolated execution requires the unshare executable")
    wrapped = [unshare, "--user", "--map-root-user", "--mount", "--pid", "--fork", "--net", "--mount-proc", "--", *command]
    return wrapped, {"mode": "isolated", "enforced": True, "backend": "linux-unshare", "network": "private", "pid": "private", "mount": "private", "user": "mapped"}


def _workspace_violations(root: Path) -> list[str]:
    """Return symlinked workspace entries that must never become evidence."""
    violations: list[str] = []
    for entry in root.rglob("*"):
        if entry.is_symlink():
            violations.append(str(entry.relative_to(root)))
    return sorted(violations)


def _workspace_size(root: Path) -> int:
    total = 0
    for entry in root.rglob("*"):
        if entry.is_symlink() or not entry.is_file():
            continue
        try:
            total += entry.stat().st_size
        except OSError:
            continue
    return total


def run_command(
    command: list[str],
    *,
    tool: str,
    run_root: str | Path,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
    expected_artifacts: list[str] | None = None,
    run_id: str | None = None,
) -> ToolRun:
    """Run one tool without a shell and persist stdout/stderr plus a run record."""
    if not command or any(not isinstance(arg, str) or not arg for arg in command):
        raise ValueError("command must be a non-empty list of non-empty strings")
    root = Path(run_root)
    if root.is_symlink():
        raise ValueError("run root must not be a symlink")
    root.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except OSError as exc:
        raise ValueError("run root permissions unavailable") from exc
    expected = list(expected_artifacts or [])
    root_resolved = root.resolve()
    for relative in expected:
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError("expected artifacts must be non-empty relative paths")
        try:
            (root / relative).resolve().relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError("expected artifacts must stay inside the run root") from exc
    started = time.time()
    status = "unknown"
    exit_code: int | None = None
    stdout_truncated = False
    stderr_truncated = False
    try:
        preexec_fn = None
        execution_limits = {}
        if os.name == "posix":
            preexec_fn, execution_limits = _execution_limits(timeout_seconds)
        launch_command, isolation = _sandbox_command(command)
        process = subprocess.Popen(launch_command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True, preexec_fn=preexec_fn)
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            # Kill the whole tool process group. EDA wrappers can leave child
            # processes behind if only the direct process is terminated.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
            stdout, stdout_truncated = _bound_log(stdout or exc.stdout or "")
            stderr, stderr_truncated = _bound_log(stderr or exc.stderr or "")
            (root / "stdout.log").write_text(stdout, encoding="utf-8")
            (root / "stderr.log").write_text(stderr + "\nTIMEOUT\n", encoding="utf-8")
            status = "blocked"
        else:
            exit_code = process.returncode
            stdout, stdout_truncated = _bound_log(stdout)
            stderr, stderr_truncated = _bound_log(stderr)
            (root / "stdout.log").write_text(stdout, encoding="utf-8")
            (root / "stderr.log").write_text(stderr, encoding="utf-8")
            status = "passed" if exit_code == 0 else "failed"
    except FileNotFoundError as exc:
        (root / "stderr.log").write_text(str(exc), encoding="utf-8")
        status = "blocked"
    workspace_violations = _workspace_violations(root)
    try:
        max_workspace_bytes = max(1, int(os.environ.get("VERIFICATION_JOB_MAX_WORKSPACE_BYTES", str(2 * 1024 * 1024 * 1024))))
    except ValueError:
        max_workspace_bytes = 2 * 1024 * 1024 * 1024
    workspace_bytes = _workspace_size(root)
    if workspace_bytes > max_workspace_bytes:
        workspace_violations.append(f"workspace-quota-exceeded:{workspace_bytes}>{max_workspace_bytes}")
    if workspace_violations:
        status = "blocked"
    artifacts = []
    for relative in ["stdout.log", "stderr.log", *expected]:
        artifact = root / relative
        if artifact.is_file():
            artifacts.append(evidence_for(artifact, root=root, kind="tool-output", source_revision=source_revision))
    missing_artifacts = [relative for relative in expected if not (root / relative).is_file()]
    if missing_artifacts and status == "passed":
        status = "blocked"
    stable_id = run_id or hashlib.sha256((tool + "\0" + source_revision + "\0" + "\0".join(command)).encode("utf-8")).hexdigest()[:16]
    run = ToolRun(
        id=f"{tool}-{stable_id}",
        tool=tool,
        command=_redact_command(command),
        status=status,
        exit_code=exit_code,
        source_revision=source_revision,
        artifacts=artifacts,
        metadata={"duration_seconds": round(time.time() - started, 6), "timeout_seconds": timeout_seconds, "missing_artifacts": missing_artifacts, "workspace_violations": workspace_violations, "workspace_bytes": workspace_bytes, "max_workspace_bytes": max_workspace_bytes, "max_log_bytes": MAX_LOG_BYTES, "stdout_truncated": stdout_truncated, "stderr_truncated": stderr_truncated, "execution_limits": execution_limits, "isolation": isolation},
    )
    run.validate()
    ProvenanceLedger(runs=[run]).write(root / "provenance-ledger.json")
    return run
