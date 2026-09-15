#!/usr/bin/env python3
"""Replay the second held-out OpenLane historical fix in an isolated Python harness."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


UPSTREAM = Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT = "1c6d170484b830c650860153ac6407c17f626a84"
PARENT = "7f0486c949c21042e0a670dd77d2d654ad189483"
SOURCE_PATH = "scripts/config/tcl.py"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def show(revision: str) -> bytes:
    return subprocess.run(["git", "-C", str(UPSTREAM), "show", f"{revision}:{SOURCE_PATH}"], capture_output=True, check=True).stdout


def exercise(source: bytes, root: Path) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=True)
    module_path = root / "tcl.py"
    module_path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("openlane_tcl_replay", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load historical config module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pdk = root / "pdk"
    scl = root / "scl"
    pdk.mkdir()
    scl.mkdir()
    (pdk / "libs").write_text("pdk library marker\n", encoding="utf-8")
    (scl / "libs").write_text("scl library marker\n", encoding="utf-8")
    state = module.State({
        "PDKPATH": str(pdk),
        "SCLPATH": str(scl),
        "DESIGN_DIR": str(root / "design"),
        "PDK": "sky130",
        "STD_CELL_LIBRARY": "sky130_fd_sc_hd",
    })
    return {
        "pdk_dir": module.process_string("pdk_dir::libs", state),
        "scl_dir": module.process_string("scl_dir::libs", state),
        "expected_pdk": str(pdk / "libs"),
        "expected_scl": str(scl / "libs"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    parent_source = show(f"{COMMIT}^")
    fixed_source = show(COMMIT)
    (output / "parent-tcl.py").write_bytes(parent_source)
    (output / "fixed-tcl.py").write_bytes(fixed_source)
    with tempfile.TemporaryDirectory(prefix="heldout-openlane-config-") as td:
        root = Path(td)
        parent = exercise(parent_source, root / "parent")
        fixed = exercise(fixed_source, root / "fixed")
    snapshots = {
        "parent-tcl.py": {"path": "parent-tcl.py", "sha256": hashlib.sha256(parent_source).hexdigest(), "size_bytes": len(parent_source)},
        "fixed-tcl.py": {"path": "fixed-tcl.py", "sha256": hashlib.sha256(fixed_source).hexdigest(), "size_bytes": len(fixed_source)},
    }
    report = {
        "schema_version": "heldout-openlane-config-path-replay-v1",
        "repository": "OpenLane",
        "commit": COMMIT,
        "parent": PARENT,
        "subject": "Fix processing of pdk_dir:: and scl_dir:: in JSON",
        "source_path": SOURCE_PATH,
        "source_snapshots": snapshots,
        "parent_result": parent,
        "fixed_result": fixed,
        "status": "passed" if parent["pdk_dir"] != parent["expected_pdk"] and parent["scl_dir"] != parent["expected_scl"] and fixed["pdk_dir"] == fixed["expected_pdk"] and fixed["scl_dir"] == fixed["expected_scl"] else "blocked",
        "claim_boundary": "one upstream OpenLane held-out configuration-path regression reconstructed in an isolated Python harness; not an agent repair, complete OpenLane qualification, or model-generalization result",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report["report_sha256"] = digest(report)
    (output / "replay-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
