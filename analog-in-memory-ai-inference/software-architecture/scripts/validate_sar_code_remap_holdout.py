#!/usr/bin/env python3
"""Fit a SAR code remap on calibration references and test fixed holdouts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED = [0, 2, 4, 6, 7]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def codes(path: Path) -> list[int]:
    data: dict[str, Any] = json.loads(path.read_text())
    rows = data.get("conversions", data.get("results", []))
    values = []
    for row in rows:
        value = row.get("decoded_code", row.get("final_code", row.get("code")))
        if value is not None:
            values.append(int(value))
    if len(values) != len(EXPECTED):
        raise ValueError(f"{path}: expected {len(EXPECTED)} decoded conversions, found {len(values)}")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("holdout", type=Path, nargs="+")
    args = parser.parse_args()
    calibration_codes = codes(args.calibration)
    if len(set(calibration_codes)) != len(EXPECTED) or not all(a < b for a, b in zip(calibration_codes, calibration_codes[1:])):
        raise SystemExit("calibration case must be strictly monotonic and one-to-one")
    remap = {str(observed): expected for observed, expected in zip(calibration_codes, EXPECTED)}
    rows = []
    for path in args.holdout:
        observed = codes(path)
        mapped = [remap.get(str(value)) for value in observed]
        in_domain = all(value is not None for value in mapped)
        unique = len(set(observed)) == len(observed)
        exact = mapped == EXPECTED
        rows.append({"artifact": str(path), "source_sha256": sha256(path),
                     "observed_codes": observed, "mapped_codes": mapped,
                     "one_to_one_observed": unique, "all_codes_in_calibration_domain": in_domain,
                     "exact_expected_map": exact,
                     "status": "passed" if exact else "rejected_holdout"})
    result = {
        "schema_version": "sar-code-remap-holdout-v0.1",
        "result_type": "fixed_calibration_remap_holdout_validation",
        "calibration": {"artifact": str(args.calibration), "source_sha256": sha256(args.calibration),
                         "observed_codes": calibration_codes, "expected_codes": EXPECTED,
                         "fitted_remap": remap},
        "holdouts": rows,
        "passed_holdouts": sum(row["exact_expected_map"] for row in rows),
        "total_holdouts": len(rows),
        "promotion_allowed": bool(rows) and all(row["exact_expected_map"] for row in rows),
        "next_gate": "Collect additional calibration references per converter/tile and repeat on disjoint mismatch seeds; any collision or unmapped code rejects promotion.",
        "claim_boundary": "Fixed digital remap validation across schematic receipts only; no analog error correction, yield, noise, energy, layout, or hardware claim.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "passed_holdouts": result["passed_holdouts"],
                      "total_holdouts": result["total_holdouts"], "promotion_allowed": result["promotion_allowed"]}))


if __name__ == "__main__":
    main()
