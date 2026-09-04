#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CANDIDATE = EVIDENCE / "candidate-post-layout"
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_capacitive_isolation_frontend_extracted.spice"
MODEL = CANDIDATE / "models" / "sky130-capacitive-isolation-ngspice.includes"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
PORT_MAPPING = EVIDENCE / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.json"
OUT_JSON = EVIDENCE / "sky130-capacitive-isolation-extracted-coupling-strength-sweep.json"
OUT_MD = EVIDENCE / "sky130-capacitive-isolation-extracted-coupling-strength-sweep.md"
OUT_CSV = MEASUREMENTS / "sky130-capacitive-isolation-extracted-coupling-strength-sweep.csv"


@dataclass(frozen=True)
class Case:
    added_cap_f: float
    diff_mv: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"missing measurement {name}")
    return values[-1]


def capacitance_totals_f() -> dict[str, float]:
    text = EXTRACTED.read_text(encoding="utf-8")
    totals = {"latch_gate_p": 0.0, "latch_gate_n": 0.0}
    for line in text.splitlines():
        match = re.match(r"C\d+\s+(\S+)\s+(\S+)\s+([-+0-9.]+)f\b", line.strip())
        if not match:
            continue
        node_a, node_b, value_ff = match.groups()
        value_f = float(value_ff) * 1e-15
        for node in (node_a, node_b):
            if node in totals:
                totals[node] += value_f
    return totals


def baseline_gate_diff_by_sign() -> dict[int, float]:
    data = json.loads(PORT_MAPPING.read_text(encoding="utf-8"))
    rows = [row for row in data["rows"] if row["mapping"] == "normal"]
    return {int(row["expected_sign"]): float(row["gate_diff_after_v"]) for row in rows}


def run_case(case: Case, totals: dict[str, float], baseline: dict[int, float]) -> dict[str, Any]:
    expected_sign = 1 if case.diff_mv > 0 else -1
    sample_diff = case.diff_mv / 1000.0
    added_cap = case.added_cap_f
    p_total = totals["latch_gate_p"] + added_cap
    n_total = totals["latch_gate_n"] + added_cap
    added_delta = added_cap * ((sample_diff / 2.0) / p_total + (sample_diff / 2.0) / n_total)
    gate_diff = baseline[expected_sign] + added_delta
    measured_sign = 1 if gate_diff > 0 else -1 if gate_diff < 0 else 0
    return {
        "added_cap_f": case.added_cap_f,
        "added_cap_ff": case.added_cap_f * 1e15,
        "input_diff_mv": case.diff_mv,
        "expected_sign": expected_sign,
        "sample_diff_after_v": sample_diff,
        "baseline_gate_diff_after_v": baseline[expected_sign],
        "added_coupling_delta_v": added_delta,
        "gate_diff_after_v": gate_diff,
        "measured_gate_sign": measured_sign,
        "sign_preserved": measured_sign == expected_sign,
        "method": "measured_baseline_plus_extracted_capacitive_divider",
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Capacitive Isolation Extracted Coupling-Strength Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- tested added capacitor fF: `{', '.join(str(v) for v in report['tested_added_cap_ff'])}`",
        f"- first passing added capacitor fF: `{report['first_passing_added_cap_ff']}`",
        f"- row count: `{report['row_count']}`",
        "",
        "## First Principle",
        "",
        "The extracted frontend has fixed capacitance from latch gates to clock, supply, ground, and substrate. A tiny intended sample-to-gate signal can lose if those fixed paths move the latch inputs more than the sampled difference does.",
        "",
        "This sweep keeps the extracted RC cell in the path and adds a controlled symmetric sample-to-gate capacitor. It asks how much stronger the intended differential coupling must be before both signs reach the latch-gate nodes correctly.",
        "",
        "It uses the measured normal-mapping extracted-RC sign error as the baseline, then applies the added capacitor through the extracted latch-gate capacitance totals. The added capacitors are a design diagnostic, not a physical layout edit.",
        "",
        "## Results",
        "",
        "| added cap fF | input diff mV | baseline gate diff V | added coupling delta V | gate diff after V | expected sign | measured sign | sign preserved |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(f"| `{row['added_cap_ff']:.3f}` | `{row['input_diff_mv']:.6f}` | `{row['baseline_gate_diff_after_v']:.9e}` | `{row['added_coupling_delta_v']:.9e}` | `{row['gate_diff_after_v']:.9e}` | `{row['expected_sign']}` | `{row.get('measured_gate_sign')}` | `{row['sign_preserved']}` |")
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    confirm = json.loads(CONFIRM.read_text(encoding="utf-8"))
    target_mv = float(confirm["target_combined_offset_noise_mv"])
    cap_values = [0.0, 0.1e-15, 0.2e-15, 0.5e-15, 1.0e-15, 2.0e-15, 5.0e-15, 10.0e-15, 20.0e-15, 50.0e-15, 100.0e-15, 200.0e-15]
    totals = capacitance_totals_f()
    baseline = baseline_gate_diff_by_sign()
    rows = [run_case(Case(cap, diff), totals, baseline) for cap in cap_values for diff in (-target_mv, target_mv)]
    passing_caps = []
    for cap in cap_values:
        items = [row for row in rows if row["added_cap_f"] == cap]
        if len(items) == 2 and all(row.get("sign_preserved") for row in items):
            passing_caps.append(cap)
    report = {
        "result_type": "sky130_capacitive_isolation_extracted_coupling_strength_sweep",
        "status": "added_coupling_strength_found_for_both_signs" if passing_caps else "no_added_coupling_strength_preserves_both_signs",
        "source_port_mapping_diagnostic": "evidence/aimc-simulator-adapters/sky130-capacitive-isolation-extracted-port-mapping-diagnostic.json",
        "extracted_frontend_netlist": rel(EXTRACTED),
        "model_include": rel(MODEL),
        "csv": rel(OUT_CSV),
        "latch_gate_total_capacitance_ff": {name: value * 1e15 for name, value in totals.items()},
        "baseline_gate_diff_by_expected_sign_v": baseline,
        "tested_added_cap_ff": [cap * 1e15 for cap in cap_values],
        "first_passing_added_cap_ff": passing_caps[0] * 1e15 if passing_caps else None,
        "row_count": len(rows),
        "rows": rows,
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "finds the extra symmetric sample-to-gate coupling needed for the extracted frontend to preserve differential sign",
            "not_allowed": "does not modify the physical layout, does not prove latch resolution, does not prove noise, does not run DRC/LVS, and does not write accepted evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(report)
    print("sky130_capacitive_isolation_extracted_coupling_strength_sweep")
    print(f"status,{report['status']}")
    print(f"first_passing_added_cap_ff,{report['first_passing_added_cap_ff']}")
    print(f"rows,{len(rows)}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
