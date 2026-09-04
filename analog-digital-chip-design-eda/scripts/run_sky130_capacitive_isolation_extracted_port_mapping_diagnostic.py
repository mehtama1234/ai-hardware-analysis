#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
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
OUT_JSON = EVIDENCE / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.json"
OUT_MD = EVIDENCE / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.md"
OUT_CSV = MEASUREMENTS / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.csv"
DECK_OUT = SPICE_DIR / "sky130_capacitive_isolation_extracted_port_mapping_diagnostic.sp"
NGSPICE_TIMEOUT_S = 80


@dataclass(frozen=True)
class Case:
    mapping: str
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


def instance(mapping: str) -> str:
    if mapping == "normal":
        return "XFRONT vss vdd sp gp clk gn sn sky130_capacitive_isolation_frontend"
    if mapping == "swap_latch_gates":
        return "XFRONT vss vdd sp gn clk gp sn sky130_capacitive_isolation_frontend"
    if mapping == "swap_samples":
        return "XFRONT vss vdd sn gp clk gn sp sky130_capacitive_isolation_frontend"
    raise ValueError(mapping)


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Extracted capacitive-isolation frontend port-mapping diagnostic.

.include "{MODEL}"
.include "{EXTRACTED}"
.param vdd=1.8
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}
VDD vdd 0 {{vdd}}
VSS vss 0 0
VBIAS vcm 0 0.9
VCLK clk 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VSP sp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
{instance(case.mapping)}
RBIASP gp vcm 100G
RBIASN gn vcm 100G
.tran 2p 3n
.measure tran sp_before_v FIND v(sp) AT=0.90n
.measure tran sn_before_v FIND v(sn) AT=0.90n
.measure tran sp_after_v FIND v(sp) AT=2.60n
.measure tran sn_after_v FIND v(sn) AT=2.60n
.measure tran gp_before_v FIND v(gp) AT=0.90n
.measure tran gn_before_v FIND v(gn) AT=0.90n
.measure tran gp_after_v FIND v(gp) AT=2.60n
.measure tran gn_after_v FIND v(gn) AT=2.60n
.measure tran gp_after_v FIND v(gp) AT=2.60n
.measure tran gn_after_v FIND v(gn) AT=2.60n
.control
run
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.diff_mv > 0 else -1
    result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    if result.returncode != 0:
        return {"mapping": case.mapping, "input_diff_mv": case.diff_mv, "expected_sign": expected_sign, "ngspice_returncode": result.returncode, "error_excerpt": (result.stdout + result.stderr)[-1200:], "sign_preserved": False}
    sp_before = read_measure(result.stdout, "sp_before_v")
    sn_before = read_measure(result.stdout, "sn_before_v")
    sp_after = read_measure(result.stdout, "sp_after_v")
    sn_after = read_measure(result.stdout, "sn_after_v")
    gp_before = read_measure(result.stdout, "gp_before_v")
    gn_before = read_measure(result.stdout, "gn_before_v")
    gp_after = read_measure(result.stdout, "gp_after_v")
    gn_after = read_measure(result.stdout, "gn_after_v")
    gate_before = gp_before - gn_before
    gate_after = gp_after - gn_after
    measured_sign = 1 if gate_after > 0 else -1 if gate_after < 0 else 0
    return {
        "mapping": case.mapping,
        "input_diff_mv": case.diff_mv,
        "expected_sign": expected_sign,
        "sample_diff_before_v": sp_before - sn_before,
        "sample_diff_after_v": sp_after - sn_after,
        "gate_diff_before_v": gate_before,
        "gate_diff_after_v": gate_after,
        "gp_after_v": gp_after,
        "gn_after_v": gn_after,
        "measured_gate_sign": measured_sign,
        "sign_preserved": measured_sign == expected_sign,
        "ngspice_returncode": result.returncode,
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
        "# Sky130 Capacitive Isolation Extracted Port-Mapping Diagnostic",
        "",
        f"- status: `{report['status']}`",
        f"- rows: `{report['row_count']}`",
        f"- mappings with both signs preserved: `{', '.join(report['mappings_with_both_signs_preserved']) or 'none'}`",
        f"- extracted frontend: `{report['extracted_frontend_netlist']}`",
        "",
        "## First Principle",
        "",
        "Before blaming the latch, check what the extracted frontend hands to the latch. A comparator can only decide correctly if the sign of the sampled difference reaches the latch input with the same sign or with a known intentional inversion.",
        "",
        "This diagnostic removes the latch. It drives the extracted frontend with a positive and negative sample difference, then measures `gp - gn`. If a mapping gives the same sign for both inputs, the physical connection is not a valid differential handoff.",
        "",
        "## Results",
        "",
        "| mapping | input diff mV | gate diff before V | gate diff after V | expected sign | measured sign | sign preserved |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(f"| `{row['mapping']}` | `{row['input_diff_mv']:.6f}` | `{row.get('gate_diff_before_v', 0):.9e}` | `{row.get('gate_diff_after_v', 0):.9e}` | `{row['expected_sign']}` | `{row.get('measured_gate_sign')}` | `{row['sign_preserved']}` |")
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    confirm = json.loads(CONFIRM.read_text(encoding="utf-8"))
    target_mv = float(confirm["target_combined_offset_noise_mv"])
    mappings = ["normal", "swap_latch_gates", "swap_samples"]
    rows = [run_case(Case(mapping, diff)) for mapping in mappings for diff in (-target_mv, target_mv)]
    by_mapping: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_mapping.setdefault(str(row["mapping"]), []).append(row)
    passing_mappings = [name for name, items in by_mapping.items() if len(items) == 2 and all(item.get("sign_preserved") for item in items)]
    report = {
        "result_type": "sky130_capacitive_isolation_extracted_port_mapping_diagnostic",
        "status": "port_mapping_found_that_preserves_both_signs" if passing_mappings else "no_port_mapping_preserves_both_signs",
        "source_rerun": "evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-post-layout-both-polarity.json",
        "extracted_frontend_netlist": rel(EXTRACTED),
        "model_include": rel(MODEL),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(OUT_CSV),
        "row_count": len(rows),
        "mappings_tested": mappings,
        "mappings_with_both_signs_preserved": passing_mappings,
        "rows": rows,
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "diagnoses whether the extracted frontend port mapping preserves sampled differential sign before the latch",
            "not_allowed": "does not prove latch resolution, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted converter replacement",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(report)
    print("sky130_capacitive_isolation_extracted_port_mapping_diagnostic")
    print(f"status,{report['status']}")
    print(f"passing_mappings,{','.join(passing_mappings) or 'none'}")
    print(f"rows,{len(rows)}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
