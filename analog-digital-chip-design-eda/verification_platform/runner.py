"""Execution-in-the-loop adapter with reproducible run records."""

from __future__ import annotations

from dataclasses import asdict
import subprocess
import time
import hashlib
from pathlib import Path

from .ledger import ProvenanceLedger, ToolRun, evidence_for


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
    root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    status = "unknown"
    exit_code: int | None = None
    try:
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=timeout_seconds, check=False)
        exit_code = completed.returncode
        (root / "stdout.log").write_text(completed.stdout, encoding="utf-8")
        (root / "stderr.log").write_text(completed.stderr, encoding="utf-8")
        status = "passed" if exit_code == 0 else "failed"
    except FileNotFoundError as exc:
        (root / "stderr.log").write_text(str(exc), encoding="utf-8")
        status = "blocked"
    except subprocess.TimeoutExpired as exc:
        (root / "stdout.log").write_text(exc.stdout or "", encoding="utf-8")
        (root / "stderr.log").write_text((exc.stderr or "") + "\nTIMEOUT\n", encoding="utf-8")
        status = "blocked"
    artifacts = []
    for relative in ["stdout.log", "stderr.log", *(expected_artifacts or [])]:
        artifact = root / relative
        if artifact.is_file():
            artifacts.append(evidence_for(artifact, root=root, kind="tool-output", source_revision=source_revision))
    missing_artifacts = [relative for relative in (expected_artifacts or []) if not (root / relative).is_file()]
    if missing_artifacts and status == "passed":
        status = "blocked"
    stable_id = run_id or hashlib.sha256((tool + "\0" + source_revision + "\0" + "\0".join(command)).encode("utf-8")).hexdigest()[:16]
    run = ToolRun(
        id=f"{tool}-{stable_id}",
        tool=tool,
        command=command,
        status=status,
        exit_code=exit_code,
        source_revision=source_revision,
        artifacts=artifacts,
        metadata={"duration_seconds": round(time.time() - started, 6), "timeout_seconds": timeout_seconds, "missing_artifacts": missing_artifacts},
    )
    run.validate()
    ProvenanceLedger(runs=[run]).write(root / "provenance-ledger.json")
    return run
