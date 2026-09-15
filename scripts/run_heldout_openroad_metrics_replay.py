#!/usr/bin/env python3
"""Replay the held-out OpenROAD elapsed-time artifact-extension fix."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


UPSTREAM = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
COMMIT = "31fdacec42065f1f83470a178a318be4b1e998c1"
PARENT = "3fde4a2c234251b9fe9ff735b072a3c0c1f65b5a"
SOURCE = "flow/util/genElapsedTime.py"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def show(revision: str) -> bytes:
    return subprocess.run(["git", "-C", str(UPSTREAM), "show", f"{revision}:{SOURCE}"], capture_output=True, check=True).stdout


def exercise(source: bytes, root: Path) -> dict[str, object]:
    module_path = root / "genElapsedTime.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("gen_elapsed_replay", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load historical metrics module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    log = root / "logs" / "route.log"
    log.parent.mkdir(parents=True)
    log.write_text("Elapsed time: 0:01.00[h:]min:sec. CPU time: user 0.1 sys 0.0 (99%). Peak memory: 1024KB.\n", encoding="utf-8")
    result_dir = root / "results"
    result_dir.mkdir()
    for ext in (".v", ".rtlil", ".odb", ".def", ".spef", ".gds", ".sdc"):
        (result_dir / f"route{ext}").write_bytes(f"artifact {ext}\n".encode())
    hashes = module.get_hashes(log)
    return {"extensions": [ext for ext, _ in hashes], "hashes": hashes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    parent_source = show(f"{COMMIT}^")
    fixed_source = show(COMMIT)
    (output / "parent-genElapsedTime.py").write_bytes(parent_source)
    (output / "fixed-genElapsedTime.py").write_bytes(fixed_source)
    with tempfile.TemporaryDirectory(prefix="heldout-openroad-metrics-") as td:
        parent = exercise(parent_source, Path(td) / "parent")
        fixed = exercise(fixed_source, Path(td) / "fixed")
    expected_added = [".def", ".spef", ".gds"]
    report = {
        "schema_version": "heldout-openroad-metrics-replay-v1",
        "repository": "OpenROAD-flow-scripts",
        "commit": COMMIT,
        "parent": PARENT,
        "subject": "fix: address maliberty review nits on #4232",
        "source": SOURCE,
        "source_snapshots": {
            "parent": {"path": "parent-genElapsedTime.py", "sha256": hashlib.sha256(parent_source).hexdigest(), "size_bytes": len(parent_source)},
            "fixed": {"path": "fixed-genElapsedTime.py", "sha256": hashlib.sha256(fixed_source).hexdigest(), "size_bytes": len(fixed_source)},
        },
        "contract": {"artifacts_present": [".v", ".rtlil", ".odb", ".def", ".spef", ".gds", ".sdc"], "expected_new_extensions": expected_added},
        "parent_result": parent,
        "fixed_result": fixed,
        "status": "passed" if all(ext not in parent["extensions"] for ext in expected_added) and all(ext in fixed["extensions"] for ext in expected_added) else "blocked",
        "claim_boundary": "one upstream OpenROAD elapsed-time artifact-extension contract replayed with synthetic files; not physical signoff, flow correctness, agent repair, or model-generalization evidence",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report["report_sha256"] = digest(report)
    (output / "replay-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
