"""Independently validate the historical fix candidate manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("manifest", type=Path); args = parser.parse_args(); manifest = json.loads(args.manifest.read_text(encoding="utf-8")); errors = []
    if manifest.get("schema_version") != "historical-fix-candidate-manifest-v1": errors.append("schema mismatch")
    candidates = manifest.get("candidates", [])
    if manifest.get("candidate_count") != len(candidates): errors.append("candidate count mismatch")
    if len(manifest.get("repositories", [])) < 3: errors.append("fewer than three repositories")
    if len(candidates) < 50: errors.append("fewer than 50 mined candidates")
    development = {tuple(item) for item in manifest.get("development_keys", [])}
    heldout = {tuple(item) for item in manifest.get("heldout_keys", [])}
    observed = {(item.get("repository"), item.get("commit")) for item in candidates}
    if len(heldout) < 15: errors.append("fewer than 15 held-out candidates")
    if development & heldout or development | heldout != observed: errors.append("development/held-out split is not disjoint and complete")
    if any(item.get("validation_status") != "candidate_only" for item in candidates): errors.append("candidate promoted without validation")
    keys = [(item.get("repository"), item.get("commit")) for item in candidates]
    if len(keys) != len(set(keys)): errors.append("duplicate repository/commit candidates")
    unsigned = dict(manifest); recorded = unsigned.pop("manifest_sha256", None)
    if recorded != digest(unsigned): errors.append("manifest digest mismatch")
    result = {"schema_version": "historical-fix-candidate-check-v1", "status": "passed" if not errors else "blocked", "errors": errors, "manifest": str(args.manifest)}; result["check_sha256"] = digest(result); print(json.dumps(result, sort_keys=True)); return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
