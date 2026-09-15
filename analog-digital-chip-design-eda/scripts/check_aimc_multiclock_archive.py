#!/usr/bin/env python3
"""Independently verify an AIMC multi-clock signoff archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path


REQUIRED = {
    "source/config.tcl",
    "source/openlane-vsrc-aligned-manifest.json",
    "source/openlane-vsrc-aligned-metrics-summary.md",
    "source/vsrc_sources.md",
    "source/fanout-eco-comparison.md",
    "reports/metrics.csv",
    "reports/manufacturability.rpt",
    "reports/signoff/34-rcx_sta.checks.rpt",
    "reports/logs/signoff/35-irdrop.log",
    "final/def/aimc_multi_clock_control_subsystem.def",
    "final/gds/aimc_multi_clock_control_subsystem.gds",
    "final/lef/aimc_multi_clock_control_subsystem.lef",
    "final/lib/aimc_multi_clock_control_subsystem.lib",
    "final/sdc/aimc_multi_clock_control_subsystem.sdc",
    "final/sdf/aimc_multi_clock_control_subsystem.sdf",
    "final/spef/aimc_multi_clock_control_subsystem.spef",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="aimc-archive-check-") as temp_name:
        root = Path(temp_name)
        with tarfile.open(args.archive, "r:gz") as archive:
            archive.extractall(root, filter="data")
        candidates = list(root.glob("*/archive-manifest.json"))
        if len(candidates) != 1:
            raise ValueError("archive must contain exactly one archive-manifest.json")
        package = candidates[0].parent
        manifest = json.loads(candidates[0].read_text(encoding="utf-8"))
        paths = {item["path"] for item in manifest["files"]}
        missing = REQUIRED - paths
        if missing:
            raise ValueError(f"missing required archive files: {sorted(missing)}")
        for item in manifest["files"]:
            path = package / item["path"]
            if not path.is_file() or digest(path) != item["sha256"]:
                raise ValueError(f"hash mismatch or missing file: {item['path']}")
        if manifest["release_decision"] != "implementation_and_local_signoff_evidence_only":
            raise ValueError("archive claim boundary was weakened")
        print(json.dumps({"status": "passed", "files": len(manifest["files"]),
                          "claim_boundary": "local implementation/signoff evidence only"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, ValueError, json.JSONDecodeError, tarfile.TarError) as exc:
        raise SystemExit(f"FAIL {exc}")
