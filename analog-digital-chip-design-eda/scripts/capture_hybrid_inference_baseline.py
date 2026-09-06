#!/usr/bin/env python3
"""Record scoped source hashes and bounded checks without regenerating evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
BACKEND = REPO / "analog-in-memory-ai-inference/software-architecture/backend"
SCOPES = [ROOT.name, "analog-in-memory-ai-inference"]


def run(command: list[str], cwd: Path, timeout: int = 60) -> dict:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                timeout=timeout, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return {"command": command, "cwd": str(cwd), "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr, "timed_out": False}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "cwd": str(cwd), "returncode": None,
                "error": str(exc), "timed_out": isinstance(exc, subprocess.TimeoutExpired)}


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / "evidence/aimc-hardware-lab/recovery-baselines" / stamp
    files = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *SCOPES],
        cwd=REPO).decode().split("\0")
    manifest = []
    for name in sorted(set(filter(None, files))):
        if "/recovery-baselines/" in name:
            continue
        path = REPO / name
        if path.is_symlink():
            manifest.append({"path": name, "symlink": os.readlink(path)})
        elif path.is_file():
            with path.open("rb") as stream:
                hasher = hashlib.sha256()
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    hasher.update(block)
                digest = hasher.hexdigest()
            manifest.append({"path": name, "bytes": path.stat().st_size, "sha256": digest})
        else:
            manifest.append({"path": name, "missing": True})
    snapshot = {
        "created_at": stamp, "scope": SCOPES,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "git_status": subprocess.check_output(
            ["git", "status", "--porcelain=v1", "--", *SCOPES], cwd=REPO, text=True),
        "files": manifest,
        "boundary": "Hashes of non-ignored scoped files; not a backup, atomic snapshot, or hardware qualification. Prior baseline directories excluded.",
        "tool_paths": {name: shutil.which(name) for name in
                       ["ngspice", "yosys", "iverilog", "magic", "klayout", "netgen", "xschem", "openlane"]},
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "manifest.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    commands = [
        ("portfolio", [sys.executable, "scripts/validate_aimc_workload_portfolio.py"], ROOT),
        ("project", [sys.executable, "scripts/validate_project.py"], ROOT),
        ("measured_evidence_boundary", [str(BACKEND / ".venv/bin/python"), "scripts/check_measured_evidence_readiness.py"], BACKEND),
        ("ngspice_version", ["ngspice", "--version"], ROOT),
        ("yosys_version", ["yosys", "-V"], ROOT),
        ("simulator_imports", [str(Path.home() / "eda-tools/aimc-simulators-venv/bin/python"), "-c",
          "import aihwkit, simulator; import importlib.metadata as m; print('aihwkit', m.version('aihwkit')); print('crosssim_module', simulator.__file__)"], ROOT),
    ]
    results = {}
    for name, command, cwd in commands:
        result = run(command, cwd)
        results[name] = result
        (output / f"{name}.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"{name}: {result['returncode']}", flush=True)
    summary = {"checks": {name: result["returncode"] == 0 for name, result in results.items()},
               "file_count": len(manifest), "manifest": "manifest.json",
               "boundary": "Fresh software checks and tool probes only; no circuit rerun or acceptance promotion."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"baseline: {output}")
    return 0 if all(summary["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
