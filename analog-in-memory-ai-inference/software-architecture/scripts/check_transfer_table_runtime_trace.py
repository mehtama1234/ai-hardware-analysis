#!/usr/bin/env python3
"""Verify the all-code compiler/runtime fallback replay."""

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
    trace = json.loads((args.package / "transfer_table_runtime_trace.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    events = trace.get("events", [])
    if len(events) != 16 or [event.get("requested_converter_code") for event in events] != list(range(16)):
        failures.append("runtime trace does not cover converter codes 0 through 15")
    if trace.get("unsupported_code_events") != [0, 2, 3, 4, 5, 6, 7, 9, 11, 12]:
        failures.append("runtime trace unsupported-code events changed")
    if (trace.get("all_routes_fallback") is not True or trace.get("analog_instruction_count") != 0
            or any(event.get("runtime_command") != "RUN_DIGITAL_FALLBACK" for event in events)
            or any(event.get("output_preservation") != "exact_by_digital_fallback_control" for event in events)):
        failures.append("runtime trace contains a non-fallback or non-preserving event")
    boundary = trace.get("claim_boundary", "")
    if "Local compiler/runtime" not in boundary or "not hardware latency" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "all 16 converter codes compile to explicit digital fallback; the 10 missing codes are visible as unsupported events.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
