#!/usr/bin/env python3
"""Export the bounded local qualification evidence as a portable ZIP bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--package", type=Path, default=ROOT / "evidence/local-digital-qualification-v1")
    parser.add_argument("--advantage", type=Path, default=ROOT / "evidence/counterfactual-hybrid-advantage-v2")
    parser.add_argument("--profile-family", type=Path, default=ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-profile-family-replay")
    args = parser.parse_args()
    package_path = args.package.resolve() / "local_digital_qualification_package.json"
    advantage_path = args.advantage.resolve() / "counterfactual_hybrid_advantage_report.json"
    package = json.loads(package_path.read_text())
    files = {
        "qualification-package.json": package_path,
        "counterfactual-advantage.json": advantage_path,
        "end-to-end-manifest.json": ROOT / "evidence/end-to-end-qualification-manifest.json",
        "qualification-handoff.md": ROOT / "END_TO_END_QUALIFICATION_HANDOFF.md",
        "model-to-chip-goal.md": ROOT / "analog-in-memory-ai-inference/software-architecture/end-to-end-goal.md",
    }
    for key, path in list(files.items()):
        if not path.is_file():
            raise SystemExit(f"missing archive input: {path}")
    if not args.profile_family.is_dir():
        raise SystemExit(f"missing profile-family directory: {args.profile_family}")
    for path in sorted(args.profile_family.rglob("*")):
        if path.is_file():
            files[f"profile-family/{path.relative_to(args.profile_family)}"] = path
    for key, source in package["sources"].items():
        path = Path(source["path"])
        files[f"sources/{key}-{path.name}"] = path
    entries = []
    for arcname, path in files.items():
        entries.append({"archive_path": arcname, "source_path": str(path), "sha256": sha256(path)})
    receipt = {"schema_version": "local-qualification-archive-v0.1",
               "result_type": "portable_local_model_to_chip_evidence_bundle",
               "decision": "digital_reference_and_deterministic_fallback_only",
               "analog_authorized": False, "entries": entries,
               "claim_boundary": "Portable local replay and modeled evidence only; no measured analog execution, hardware timing, energy, silicon yield, or production claim."}
    args.output.mkdir(parents=True, exist_ok=False)
    archive_path = args.output / "local-qualification-evidence.zip"
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        for entry in entries:
            archive.write(entry["source_path"], entry["archive_path"])
        archive.writestr("archive-receipt.json", json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        archive.writestr("README.md", "# Local qualification evidence bundle\n\nDecision: **digital reference and deterministic fallback only**. This archive is reviewable local evidence, not a hardware qualification or production release.\n")
    receipt["archive"] = {"path": str(archive_path), "sha256": sha256(archive_path)}
    receipt_path = args.output / "archive-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"archive": str(archive_path), "entries": len(entries), "analog_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
