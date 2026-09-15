#!/usr/bin/env python3
"""Turn a saved FS A/B receipt into a compact online-schedule audit.

This is a reporting tool only.  It never changes a receipt or upgrades the
qualification decision; it makes the state, trial, and retained-control
relationship visible at each conversion boundary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def rail(v: float, *, tol: float = 0.08) -> str:
    if abs(v) <= tol:
        return "LOW"
    if abs(v - 1.8) <= tol:
        return "HIGH"
    return "MID"


def summarize(name: str, case: dict) -> list[str]:
    report = case.get("report") or {}
    rows = [f"### {name}", "", "| conversion | final code | retained bits | raw decision V | state rails | trial P rails | retained P rails |", "|---:|---:|---|---|---|---|---|"]
    for conv in report.get("conversions", []):
        probe = conv.get("sequential_control_probe", {})
        state = ",".join(rail(float(v)) for v in conv.get("sequential_state_v", [])) or "—"
        trial = ",".join(rail(float(v)) for v in probe.get("trial_gate_p_v", [])) or "—"
        retained = ",".join(rail(float(v)) for v in probe.get("retain_gate_p_v", [])) or "—"
        bits = "".join(str(int(v)) for v in conv.get("retained_bits", [])) or "—"
        raw = ",".join(f"{float(v):.3f}" for v in probe.get("raw_dec_v", [])) or "—"
        rows.append(f"| {conv.get('conversion_number', '?')} | {conv.get('final_code', '?')} | `{bits}` | `{raw}` | `{state}` | `{trial}` | `{retained}` |")
    if len(rows) == 4:
        rows.append("| — | — | — | — | — | — | — |")
    rows.extend(["", f"Claim boundary: {report.get('claim_boundary', 'not provided')}", ""])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.receipt.read_text(encoding="utf-8"))
    lines = ["# Online schedule audit", "", f"Receipt: `{args.receipt}`", "", f"Status: `{data.get('status', 'unknown')}`", ""]
    cases = data.get("cases", {})
    if cases:
        for name in ("fixed", "two_control", "fixed_state"):
            if name in cases:
                lines.extend(summarize(name, cases[name]))
    else:
        lines.extend(summarize(data.get("result_type", "single receipt"), {"report": data}))
    lines.extend(["## Interpretation", "", "This table classifies saved probe voltages at the conversion boundary. It does not prove timing margin, PVT robustness, mismatch tolerance, energy, or analog authorization.", ""])
    output = "\n".join(lines)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
