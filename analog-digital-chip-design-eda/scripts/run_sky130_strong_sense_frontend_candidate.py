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
CELL = LAB / "layout-workbench" / "cells" / "sky130_strong_sense_capacitive_frontend.mag"
EXT = LAB / "layout-workbench" / "cells" / "sky130_strong_sense_capacitive_frontend.ext"
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_strong_sense_capacitive_frontend_extracted.spice"
TCL = LAB / "layout-workbench" / "extracted" / "extract-sky130_strong_sense_capacitive_frontend-smoke.tcl"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
TARGET = EVIDENCE / "sky130-balanced-frontend-sense-gain-target.json"
BASE = EVIDENCE / "sky130-balanced-frontend-starter-extraction.json"
OUT_JSON = EVIDENCE / "sky130-strong-sense-frontend-candidate.json"
OUT_MD = EVIDENCE / "sky130-strong-sense-frontend-candidate.md"
OUT_CSV = MEASUREMENTS / "sky130-strong-sense-frontend-candidate.csv"
DECK_OUT = SPICE_DIR / "sky130_strong_sense_frontend_candidate.sp"
NGSPICE_TIMEOUT_S = 40


@dataclass(frozen=True)
class Case:
    diff_mv: float
    reset_mode: str


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


def parse_ports(text: str) -> list[str]:
    lines = text.splitlines()
    subckt_name = EXTRACTED.stem.removesuffix("_extracted")
    for index, line in enumerate(lines):
        if line.startswith(f".subckt {subckt_name}"):
            port_text = line
            next_index = index + 1
            while next_index < len(lines) and lines[next_index].startswith("+"):
                port_text += " " + lines[next_index][1:].strip()
                next_index += 1
            return port_text.split()[2:]
    return []


def capacitance_summary(text: str) -> dict[str, Any]:
    nodes = ["sample_p", "sense_p", "clk_sample", "vcm_reset", "clk_latch", "sense_n", "sample_n"]
    totals = {node: 0.0 for node in nodes}
    direct = {"sample_p_to_sense_p_ff": 0.0, "sample_n_to_sense_n_ff": 0.0}
    for line in text.splitlines():
        match = re.match(r"C\d+\s+(\S+)\s+(\S+)\s+([-+0-9.]+)f\b", line.strip())
        if not match:
            continue
        node_a, node_b, value = match.groups()
        value_ff = float(value)
        for node in (node_a, node_b):
            if node in totals:
                totals[node] += value_ff
        pair = tuple(sorted((node_a, node_b)))
        if pair == tuple(sorted(("sample_p", "sense_p"))):
            direct["sample_p_to_sense_p_ff"] += value_ff
        if pair == tuple(sorted(("sample_n", "sense_n"))):
            direct["sample_n_to_sense_n_ff"] += value_ff
    return {"totals_ff": totals, "direct_ff": direct, "sense_delta_ff": abs(totals["sense_p"] - totals["sense_n"])}


def file_record(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "present": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0}


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    reset = "0.9" if case.reset_mode == "quiet_vcm" else "PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)"
    return f"""* Strong sample-to-sense extracted frontend candidate diagnostic.

.include "{EXTRACTED}"
.param vdd=1.8
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}
VDD vdd 0 {{vdd}}
VSS vss 0 0
VSP sp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {{vdd}} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 {reset}
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn {EXTRACTED.stem.removesuffix("_extracted")}
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G
.tran 2p 3n
.measure tran sp_after_v FIND v(sp) AT=2.60n
.measure tran sn_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.control
run
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.diff_mv > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"input_diff_mv": case.diff_mv, "reset_mode": case.reset_mode, "expected_sign": expected_sign, "ngspice_timed_out": True, "sign_preserved": False}
    if result.returncode != 0:
        return {"input_diff_mv": case.diff_mv, "reset_mode": case.reset_mode, "expected_sign": expected_sign, "ngspice_returncode": result.returncode, "error_excerpt": (result.stdout + result.stderr)[-1200:], "sign_preserved": False}
    sample_diff = read_measure(result.stdout, "sp_after_v") - read_measure(result.stdout, "sn_after_v")
    sense_diff = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    measured_sign = 1 if sense_diff > 0 else -1 if sense_diff < 0 else 0
    return {
        "input_diff_mv": case.diff_mv,
        "reset_mode": case.reset_mode,
        "expected_sign": expected_sign,
        "sample_diff_after_v": sample_diff,
        "sense_diff_after_v": sense_diff,
        "sample_to_sense_transfer_ratio": abs(sense_diff) / abs(sample_diff) if sample_diff else 0.0,
        "measured_sense_sign": measured_sign,
        "sign_preserved": measured_sign == expected_sign,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
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
        "# Sky130 Strong Sense Frontend Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- direct sample-to-sense capacitance fF: `{report['direct_sample_to_sense_capacitance_ff']:.6f}`",
        f"- direct coupling improvement over balanced starter: `{report['direct_coupling_improvement_x']:.2f}x`",
        f"- minimum sample-to-sense transfer ratio: `{report['minimum_sample_to_sense_transfer_ratio']:.6f}`",
        f"- required transfer target: `{report['target_sample_to_sense_transfer_ratio']:.6f}`",
        f"- passing sign cases: `{report['passing_sign_case_count']}` of `{report['case_count']}`",
        "",
        "## First Principle",
        "",
        "The last target said the frontend needed a bigger sense-node signal, not merely a cleaner sign. This candidate moves the sample and sense conductors closer together on both sides, then extracts the actual capacitance.",
        "",
        "The useful question is not whether the drawing looks more symmetric. The useful question is whether the extracted circuit sends more of the sampled voltage difference to the sense nodes while preserving both signs.",
        "",
        "## Physical Result",
        "",
        "| quantity | value |",
        "|---|---:|",
        f"| `sense_p` total capacitance | `{report['capacitance_totals_ff']['sense_p']:.6f} fF` |",
        f"| `sense_n` total capacitance | `{report['capacitance_totals_ff']['sense_n']:.6f} fF` |",
        f"| sense capacitance delta | `{report['sense_capacitance_delta_ff']:.6f} fF` |",
        f"| sample_p to sense_p | `{report['direct_capacitance_ff']['sample_p_to_sense_p_ff']:.6f} fF` |",
        f"| sample_n to sense_n | `{report['direct_capacitance_ff']['sample_n_to_sense_n_ff']:.6f} fF` |",
        "",
        "## Transient Result",
        "",
        "| reset mode | input diff mV | sense diff after V | transfer ratio | sign preserved |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row.get('sense_diff_after_v', 0):.9e}` | `{row.get('sample_to_sense_transfer_ratio', 0):.6f}` | `{row['sign_preserved']}` |")
    lines.extend(["", "## Next Gate", "", report["next_gate"], "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    confirm = json.loads(CONFIRM.read_text(encoding="utf-8"))
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    text = EXTRACTED.read_text(encoding="utf-8") if EXTRACTED.is_file() else ""
    caps = capacitance_summary(text)
    target_mv = float(confirm["target_combined_offset_noise_mv"])
    cases = [Case(diff, mode) for mode in ["quiet_vcm", "reset_pulse"] for diff in (-target_mv, target_mv)]
    rows = [run_case(case) for case in cases]
    passing = sum(1 for row in rows if row.get("sign_preserved") is True)
    transfers = [row.get("sample_to_sense_transfer_ratio", 0.0) for row in rows if row.get("ngspice_returncode") == 0]
    direct_cap = min(caps["direct_ff"].values())
    base_direct = min(
        cap for key, cap in {
            "sample_p_to_sense_p_ff": 0.08784,
            "sample_n_to_sense_n_ff": 0.08784,
        }.items()
    )
    transfer_min = min(transfers) if transfers else 0.0
    target_ratio = float(target["target_sample_to_sense_transfer_ratio"])
    report = {
        "result_type": "sky130_strong_sense_frontend_candidate",
        "status": "strong_sense_candidate_improves_coupling_but_transfer_still_below_latch_target" if passing == len(rows) and transfer_min < target_ratio else "strong_sense_candidate_characterized",
        "source_sense_gain_target": "evidence/aimc-simulator-adapters/sky130-balanced-frontend-sense-gain-target.json",
        "source_balanced_starter_extraction": "evidence/aimc-simulator-adapters/sky130-balanced-frontend-starter-extraction.json",
        "files": {
            "magic_cell": file_record(CELL),
            "magic_ext": file_record(EXT),
            "extracted_spice": file_record(EXTRACTED),
            "extraction_tcl": file_record(TCL),
        },
        "extracted_ports": parse_ports(text),
        "capacitance_totals_ff": caps["totals_ff"],
        "direct_capacitance_ff": caps["direct_ff"],
        "sense_capacitance_delta_ff": caps["sense_delta_ff"],
        "direct_sample_to_sense_capacitance_ff": direct_cap,
        "baseline_direct_sample_to_sense_capacitance_ff": base_direct,
        "direct_coupling_improvement_x": direct_cap / base_direct if base_direct else 0.0,
        "baseline_sense_capacitance_delta_ff": base["sense_capacitance_delta_ff"],
        "minimum_sample_to_sense_transfer_ratio": transfer_min,
        "target_sample_to_sense_transfer_ratio": target_ratio,
        "remaining_transfer_improvement_x": target_ratio / transfer_min if transfer_min else None,
        "case_count": len(rows),
        "passing_sign_case_count": passing,
        "rows": rows,
        "csv": rel(OUT_CSV),
        "generated_deck": rel(DECK_OUT),
        "next_gate": "The direct coupling improved, but the measured transfer is still below the latch target. The next physical change should either reduce sense-node wasted capacitance or add a measured preamp/buffer before rerunning latch resolution.",
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "extracts and measures a stronger sample-to-sense frontend candidate against the sense-gain target",
            "not_allowed": "does not prove latch resolution, active reset devices, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(report)
    print("sky130_strong_sense_frontend_candidate")
    print(f"status,{report['status']}")
    print(f"direct_coupling_improvement_x,{report['direct_coupling_improvement_x']:.2f}")
    print(f"minimum_sample_to_sense_transfer_ratio,{transfer_min:.6f}")
    print(f"remaining_transfer_improvement_x,{report['remaining_transfer_improvement_x']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
