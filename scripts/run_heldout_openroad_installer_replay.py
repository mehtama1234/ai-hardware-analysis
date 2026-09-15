#!/usr/bin/env python3
"""Replay a held-out OpenROAD dependency-installer path regression safely."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


UPSTREAM = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
COMMIT = "83e9302b0fce4745d7e14f58145849513169c94a"
PARENT = "fa7ad82cb6f2cc75ef43dfad75ba950cc62b5c64"
SOURCE = "etc/DependencyInstaller.sh"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def show(revision: str) -> bytes:
    return subprocess.run(["git", "-C", str(UPSTREAM), "show", f"{revision}:{SOURCE}"], capture_output=True, check=True).stdout


def harness(source: bytes, root: Path, output: Path, *, fixed: bool) -> dict[str, object]:
    text = source.decode()
    marker = "_installPipSystem()"
    prefix = text.split(marker, 1)[0]
    if fixed:
        # The corrected prefix captures an absolute script directory.  Keep
        # the historical function body and stub all side effects.
        body = prefix
    else:
        body = prefix
    body += "\n"
    body += "id() { echo 1000; }\n"
    body += "pip3() { printf '%s\\n' \"$*\"; }\n"
    body += "_installPipCommon\n"
    script = root / "etc" / "DependencyInstaller.sh"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(body, encoding="utf-8")
    (root / "requirements-common_lock.txt").write_text("root marker\n", encoding="utf-8")
    (root / "etc" / "requirements-common_lock.txt").write_text("etc marker\n", encoding="utf-8")
    completed = subprocess.run(["bash", script.name], cwd=script.parent, capture_output=True, text=True, check=False)
    argument = completed.stdout.strip().split("-r ", 1)[-1] if "-r " in completed.stdout else ""
    return {"returncode": completed.returncode, "pip_invocation": completed.stdout.strip(), "resolved_lockfile": argument, "stderr": completed.stderr}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    parent_source = show(f"{COMMIT}^")
    fixed_source = show(COMMIT)
    (output / "parent-DependencyInstaller.sh").write_bytes(parent_source)
    (output / "fixed-DependencyInstaller.sh").write_bytes(fixed_source)
    with tempfile.TemporaryDirectory(prefix="heldout-openroad-installer-") as td:
        parent = harness(parent_source, Path(td) / "parent", output, fixed=False)
        fixed = harness(fixed_source, Path(td) / "fixed", output, fixed=True)
    expected_parent = "/parent/requirements-common_lock.txt"
    expected_fixed = "/fixed/etc/requirements-common_lock.txt"
    report = {
        "schema_version": "heldout-openroad-installer-replay-v1",
        "repository": "OpenROAD-flow-scripts",
        "commit": COMMIT,
        "parent": PARENT,
        "subject": "fix(installer): resolve lockfile path before cd changes cwd",
        "source": SOURCE,
        "source_snapshots": {
            "parent": {"path": "parent-DependencyInstaller.sh", "sha256": hashlib.sha256(parent_source).hexdigest(), "size_bytes": len(parent_source)},
            "fixed": {"path": "fixed-DependencyInstaller.sh", "sha256": hashlib.sha256(fixed_source).hexdigest(), "size_bytes": len(fixed_source)},
        },
        "contract": {"expected_parent_lockfile_suffix": expected_parent, "expected_fixed_lockfile_suffix": expected_fixed, "package_installation_performed": False},
        "parent_result": parent,
        "fixed_result": fixed,
        "status": "passed" if parent["returncode"] == 0 and fixed["returncode"] == 0 and parent["resolved_lockfile"].endswith(expected_parent) and fixed["resolved_lockfile"].endswith(expected_fixed) else "blocked",
        "claim_boundary": "one upstream OpenROAD-flow-scripts installer-path regression reconstructed with a stubbed pip command; no package installation, no full flow signoff, no agent repair, and no model-generalization claim",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report["report_sha256"] = digest(report)
    (output / "replay-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
