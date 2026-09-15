#!/usr/bin/env python3
"""Export bounded local RTL-to-GDS evidence into a portable archive."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def choose(root: Path, pattern: str) -> Path:
    matches = sorted(root.glob(pattern))
    if not matches:
        raise SystemExit(f"missing physical evidence: {root / pattern}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--aimc-run", type=Path, required=True)
    parser.add_argument("--register-run", type=Path, required=True)
    args = parser.parse_args()
    aimc = args.aimc_run.resolve(); register = args.register_run.resolve()
    sources = {
        "aimc_bridge.json": ROOT / "analog-digital-chip-design-eda/evidence/aimc-hardware-lab/verified-rtl2gds-bridge-latest.json",
        "register_handoff.json": ROOT / "analog-digital-chip-design-eda/evidence/register-peripheral/model-repair-rtl2gds-handoff-20260913.json",
        "aimc_prep_manifest.json": ROOT / "analog-digital-chip-design-eda/labs/eda/aimc-multi-clock-control-subsystem-openlane-prep/openlane-vsrc-aligned-manifest.json",
    }
    selected = {
        "aimc": {
            "run": aimc,
            "files": {
                "metrics.csv": aimc / "reports/metrics.csv",
                "lvs.rpt": choose(aimc, "reports/signoff/*lvs.rpt"),
                "xor.rpt": choose(aimc, "reports/signoff/*xor.rpt"),
                "drc.rpt": aimc / "reports/signoff/drc.rpt",
                "antenna.rpt": choose(aimc, "reports/signoff/*antenna_violators.rpt"),
                "gds": choose(aimc, "results/final/gds/*.gds"),
                "lef": choose(aimc, "results/final/lef/*.lef"),
                "lib": choose(aimc, "results/final/lib/*.lib"),
                "sdc": choose(aimc, "results/final/sdc/*.sdc"),
                "spef": choose(aimc, "results/final/spef/*.spef"),
                "sdf": choose(aimc, "results/final/sdf/*.sdf"),
            },
        },
        "register": {
            "run": register,
            "files": {
                "metrics.csv": register / "reports/metrics.csv",
                "lvs.rpt": choose(register, "reports/signoff/*lvs.rpt"),
                "xor.rpt": choose(register, "reports/signoff/*xor.rpt"),
                "drc.rpt": register / "reports/signoff/drc.rpt",
                "antenna.rpt": choose(register, "reports/signoff/*antenna_violators.rpt"),
                "gds": choose(register, "results/final/gds/*.gds"),
                "lef": choose(register, "results/final/lef/*.lef"),
                "lib": choose(register, "results/final/lib/*.lib"),
                "sdc": choose(register, "results/final/sdc/*.sdc"),
                "spef": choose(register, "results/final/spef/*.spef"),
                "sdf": choose(register, "results/final/sdf/*.sdf"),
            },
        },
    }
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False); archive_path = output / "flagship-physical-evidence.zip"
    entries = []
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        for name, source in sources.items():
            archive.write(source, f"receipts/{name}")
            entries.append({"archive_path": f"receipts/{name}", "sha256": sha256(source), "size_bytes": source.stat().st_size})
        for design, data in selected.items():
            for label, source in data["files"].items():
                if not source.is_file(): raise SystemExit(f"missing physical evidence: {source}")
                arcname = f"{design}/{label}/{source.name}"
                archive.write(source, arcname)
                entries.append({"archive_path": arcname, "sha256": sha256(source), "size_bytes": source.stat().st_size})
        receipt = {"schema_version": "flagship-physical-evidence-archive-v1", "generated_at": datetime.now(timezone.utc).isoformat(), "status": "passed", "designs": sorted(selected), "entries": entries, "claim_boundary": "Portable local OpenLane implementation evidence only; not commercial EDA signoff, foundry tapeout, analog qualification, measured hardware, silicon correctness, or production readiness."}
        receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        archive.writestr("archive-receipt.json", json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    outer = dict(receipt); outer["archive"] = {"path": archive_path.name, "sha256": sha256(archive_path), "size_bytes": archive_path.stat().st_size}
    (output / "archive-receipt.json").write_text(json.dumps(outer, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "archive": str(archive_path), "entries": len(entries), "bytes": archive_path.stat().st_size}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
