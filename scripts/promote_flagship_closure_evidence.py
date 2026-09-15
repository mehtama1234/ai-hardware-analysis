#!/usr/bin/env python3
"""Promote the proof-carrying closure reports into a self-contained bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = {
    "simulation": ("repository-fail-to-pass", "repository-task-result.json"),
    "mutation": ("workstream2-mutation-1000", "mutation-closure-report.json"),
    "formal": ("formal-proof-closure", "formal-proof-closure-suite-report.json"),
    "coverage": ("coverage-closure", "coverage-closure-report.json"),
    "security": ("security-policy-campaign", "security-campaign-report.json"),
    "assertion_integrity": ("spec-grounded-assertion-matrix-integrity", "assertion-matrix-result.json"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("aggregate", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    aggregate_path = args.aggregate.resolve()
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    records = {item["name"]: item for item in aggregate.get("components", [])}
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    aggregate_copy = output / "aggregate-report.json"
    shutil.copyfile(aggregate_path, aggregate_copy)
    evidence = {}
    errors = []
    for role, (component, filename) in REQUIRED.items():
        record = records.get(component, {})
        source = Path(record.get("result", {}).get("report", ""))
        if not source.is_file():
            errors.append(f"missing source report for {component}: {source}")
            continue
        destination = output / filename
        shutil.copyfile(source, destination)
        evidence[role] = {
            "component": component,
            "path": filename,
            "sha256": sha256(destination),
            "size_bytes": destination.stat().st_size,
        }
    manifest = {
        "schema_version": "flagship-closure-evidence-bundle-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not errors and aggregate.get("all_passed") is True and set(evidence) == set(REQUIRED) else "blocked",
        "aggregate": {"path": aggregate_copy.name, "sha256": sha256(aggregate_copy), "all_passed": aggregate.get("all_passed")},
        "evidence": evidence,
        "required_roles": sorted(REQUIRED),
        "errors": sorted(errors),
        "claim_boundary": "Repository-owned proof-carrying closure reports for declared local acceptance; not exhaustive proof, silicon signoff, or production release",
    }
    manifest["manifest_sha256"] = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "output": str(output), "roles": sorted(evidence)}, sort_keys=True))
    return 0 if manifest["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
