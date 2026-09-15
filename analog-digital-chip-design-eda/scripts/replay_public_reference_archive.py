#!/usr/bin/env python3
"""Replay the open-source pilot from a curated public archive."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

from verify_public_reference_archive import verify


def _extract_safe(archive: Path, destination: Path) -> Path:
    with tarfile.open(archive, "r:gz") as bundle:
        root = destination / "public-reference"
        for member in bundle.getmembers():
            target = (destination / member.name).resolve()
            if target != destination.resolve() and destination.resolve() not in target.parents:
                raise ValueError("archive contains unsafe path")
        bundle.extractall(destination)
    return root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    archive = args.archive.resolve()
    errors = verify(archive)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    with tempfile.TemporaryDirectory(prefix="public-reference-replay-") as temp:
        root = _extract_safe(archive, Path(temp))
        run = subprocess.run(["python3", "benchmarks/multi_design_pilot/ci_gate.py"], cwd=root, capture_output=True, text=True)
        summary_path = root / "benchmarks/multi_design_pilot/runs/latest/pilot-summary.json"
        summary = json.loads(summary_path.read_text()) if summary_path.is_file() else {}
        result = {"archive": str(archive), "pilot_exit_code": run.returncode, "design_count": summary.get("design_count"), "failed_designs": summary.get("failed_designs"), "passed_retests": summary.get("passed_retests"), "replay": run.returncode == 0 and summary.get("passed_retests") == summary.get("design_count")}
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
        return 0 if result["replay"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
