#!/usr/bin/env python3
"""Verify the conservative multi-context qualification matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    matrix_path = args.package / "multicontext_matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if matrix.get("context_count") != 3 or len(matrix.get("contexts", [])) != 3:
        failures.append("matrix does not contain three independent context families")
    if matrix.get("contexts", [])[0].get("screen_pass") is not True or matrix.get("contexts", [])[1].get("screen_pass") is not True:
        failures.append("passing original/prior stress stateful receipts were not preserved")
    if matrix.get("contexts", [])[2].get("screen_pass") is not False:
        failures.append("third holdout negative boundary was not preserved")
    if matrix.get("all_contexts_pass") is not False:
        failures.append("conservative matrix incorrectly passed all contexts")
    if matrix.get("decision") != "candidate_profile_not_generalized_full_digital_fallback" or matrix.get("analog_authorized") is not False:
        failures.append("matrix did not enforce full digital fallback")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "the stateful profile passes two context families but fails the third; conservative promotion is denied.",
              "claim_boundary": matrix.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
