#!/usr/bin/env python3
"""Run the CPU checkpoint from a clean snapshot of the current source tree.

The normal isolated runner intentionally operates on the current worktree.  This
wrapper creates a temporary Git repository containing the exact current source
snapshot (including uncommitted and untracked files), commits that snapshot,
asserts a clean checkout, and runs the same evidence regression there.  It does
not alter the user's repository or its history.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CURRICULUM = REPO / "gpu-mode-curriculum"


def run(command: list[str], cwd: Path, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=1800,
                        help="checkpoint timeout in seconds (default: 1800)")
    parser.add_argument("--keep", action="store_true",
                        help="keep the temporary checkout and print its path")
    args = parser.parse_args()

    started = datetime.now(timezone.utc).isoformat()
    temp_root = Path(tempfile.mkdtemp(prefix="gpumode-fresh-checkout-"))
    checkout = temp_root / "ai-hardware-analysis"
    try:
        # Copy the complete source snapshot, including files not yet tracked by
        # Git.  VCS metadata, bytecode caches, and local virtual environments are
        # deliberately excluded from the reproduction input.
        shutil.copytree(
            REPO,
            checkout,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".venv", "venv", "venv-*", "*.pyc",
            ),
        )
        init = run(["git", "init", "-q"], checkout)
        if init.returncode:
            raise RuntimeError(init.stderr.strip() or "git init failed")
        for command in (["git", "config", "user.email", "gpumode-reproduction@example.invalid"],
                        ["git", "config", "user.name", "GPUMODE reproduction"]):
            result = run(command, checkout)
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or "git config failed")
        added = run(["git", "add", "-A"], checkout)
        if added.returncode:
            raise RuntimeError(added.stderr.strip() or "git add failed")
        committed = run(["git", "commit", "-qm", "fresh-checkout reproduction snapshot"], checkout)
        if committed.returncode:
            raise RuntimeError(committed.stderr.strip() or "git commit failed")
        status = run(["git", "status", "--porcelain"], checkout)
        if status.returncode or status.stdout.strip():
            raise RuntimeError("snapshot checkout is not clean")
        revision = run(["git", "rev-parse", "HEAD"], checkout)
        snapshot_revision = revision.stdout.strip()

        command = [sys.executable, "gpu-mode-curriculum/scripts/run_advanced_evidence_regression.py"]
        print(f"running clean snapshot {snapshot_revision}", flush=True)
        result = subprocess.run(command, cwd=checkout, text=True, capture_output=True,
                                timeout=args.timeout, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        report_path = checkout / "gpu-mode-curriculum/advanced-lab-phase/executable-checkpoint.json"
        checkpoint = json.loads(report_path.read_text()) if report_path.exists() else {}
        report = {
            "started_at": started,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if result.returncode == 0 and checkpoint.get("status") == "checkpoint_passed" else "failed",
            "snapshot_revision": snapshot_revision,
            "snapshot_clean": True,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "checkpoint_status": checkpoint.get("status"),
            "checkpoint_sha256": __import__("hashlib").sha256(report_path.read_bytes()).hexdigest() if report_path.exists() else None,
            "checkout": str(checkout),
            "scope": "fresh clean Git snapshot reproduction; does not accept GPU execution or the complete curriculum",
        }
        output = CURRICULUM / "advanced-lab-phase/fresh-checkout-reproduction.json"
        output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        print(json.dumps({k: report[k] for k in ("status", "snapshot_revision", "snapshot_clean", "checkpoint_status")}, indent=2))
        return 0 if report["status"] == "passed" else 1
    except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        output = CURRICULUM / "advanced-lab-phase/fresh-checkout-reproduction.json"
        output.write_text(json.dumps({
            "started_at": started,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "error": str(exc),
            "checkout": str(checkout),
            "scope": "fresh clean Git snapshot reproduction; does not accept GPU execution or the complete curriculum",
        }, indent=2) + "\n")
        print(f"fresh checkout reproduction failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if not args.keep:
            shutil.rmtree(temp_root, ignore_errors=True)
        else:
            print(f"kept checkout: {checkout}")


if __name__ == "__main__":
    raise SystemExit(main())
