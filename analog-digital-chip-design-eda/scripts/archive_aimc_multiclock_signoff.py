#!/usr/bin/env python3
"""Build a portable archive from a verified AIMC signoff manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
DEFAULT_PACKAGE = HERE / "labs/eda/aimc-multi-clock-control-subsystem-openlane-prep"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
                        default=DEFAULT_PACKAGE / "openlane-vsrc-aligned-manifest.json")
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    run_dir = Path(manifest["run_dir"])
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    source_files = [
        "config.json", "config.tcl", "constraint.sdc", "pin_order.cfg",
        "vsrc_sources.md", "fanout-eco-comparison.md",
    ]
    source_files.extend([args.manifest.name, Path(manifest["summary"]["path"]).name])
    source_files.extend(f"src/{path.name}" for path in (args.package / "src").glob("*.v"))
    source_files.extend(f"src/{path.name}" for path in (args.package / "src").glob("*.sdc"))
    source_files.extend(f"src/{path.name}" for path in (args.package / "src").glob("*.loc"))
    report_files = [
        "reports/metrics.csv", "reports/manufacturability.rpt",
        "reports/signoff/34-rcx_sta.checks.rpt",
        "logs/signoff/35-irdrop.log", "logs/signoff/35-irdrop.warnings",
        "reports/signoff/35-irdrop-VPWR.rpt", "reports/signoff/35-irdrop-VGND.rpt",
    ]
    artifact_files = [Path(record["path"]) for record in manifest["artifacts"].values()]

    with tempfile.TemporaryDirectory(prefix="aimc-signoff-archive-") as staging_name:
        staging = Path(staging_name) / "aimc-multiclock-signoff"
        staging.mkdir()
        copied: list[dict[str, str]] = []

        def copy_file(source: Path, relative: str, allow_empty: bool = False) -> None:
            if not source.is_file() or (not allow_empty and source.stat().st_size == 0):
                raise FileNotFoundError(source)
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append({"path": relative, "sha256": digest(destination)})

        for relative in source_files:
            copy_file(args.package / relative, f"source/{relative}")
        for relative in report_files:
            report_name = relative.removeprefix("reports/")
            copy_file(run_dir / relative, f"reports/{report_name}", relative.endswith("35-irdrop.warnings"))
        for artifact in artifact_files:
            copy_file(artifact, f"final/{artifact.parent.name}/{artifact.name}")

        archive_manifest = {
            "schema_version": "aimc-multiclock-signoff-archive-v0.1",
            "source_manifest": str(args.manifest),
            "run_dir": str(run_dir),
            "claim_boundary": manifest["claim_boundary"],
            "release_decision": manifest["release_decision"],
            "files": sorted(copied, key=lambda item: item["path"]),
        }
        (staging / "archive-manifest.json").write_text(
            json.dumps(archive_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        with tarfile.open(output, "w:gz") as archive:
            archive.add(staging, arcname=staging.name)

    print(json.dumps({"status": "passed", "archive": str(output),
                      "files": len(copied), "bytes": output.stat().st_size}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
