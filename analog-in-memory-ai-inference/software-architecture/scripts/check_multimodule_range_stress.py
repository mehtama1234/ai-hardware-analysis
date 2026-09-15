#!/usr/bin/env python3
"""Verify the strongest per-module range candidate on disjoint stress inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    report_path = args.run / "stress_validation_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if report.get("profile") != {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14,
                                  "bound_multiplier": 1.0, "range_multipliers": [1.0, 1.0, 1.25]}:
        failures.append("strongest range-stress profile is not pinned")
    full = report.get("results", {}).get("full_three_module", {})
    if full.get("screen_pass") is not False or full.get("quality", {}).get("teacher_forced_argmax_agreement") != 0.9726027397260274:
        failures.append("full route did not preserve the negative range-stress boundary")
    attn = report.get("results", {}).get("attn_only", {})
    if attn.get("screen_pass") is not True:
        failures.append("attn-only range candidate did not preserve its isolated pass")
    if report.get("analog_authorized") is not False:
        failures.append("range-stress run authorized analog execution")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "single-module range allocation improves the stress candidate but does not make the full route pass.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
