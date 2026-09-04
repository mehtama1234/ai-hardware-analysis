#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
SOURCE_NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
CANDIDATE_NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_lower_waste_frontend_candidate.spice"
Candidate_subckt = "sky130_lower_waste_frontend_candidate"
CAP_BUDGET = EVIDENCE / "sky130-frontend-preamp-capacitance-budget.json"
GAIN_SWEEP = EVIDENCE / "sky130-extracted-frontend-preamp-gain-sweep.json"
DECK_OUT = SPICE_DIR / "sky130_lower_waste_frontend_preamp_candidate.sp"
CSV_OUT = MEASUREMENTS / "sky130-lower-waste-frontend-preamp-candidate.csv"
OUT_JSON = EVIDENCE / "sky130-lower-waste-frontend-preamp-candidate.json"
OUT_MD = EVIDENCE / "sky130-lower-waste-frontend-preamp-candidate.md"
NGSPICE_TIMEOUT_S = 120


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def cap_totals(text: str) -> dict[str, float]:
    totals = {"sense_p": 0.0, "sense_n": 0.0}
    for line in text.splitlines():
        match = re.match(r"C\d+\s+(\S+)\s+(\S+)\s+([-+0-9.]+)f\b", line.strip())
        if not match:
            continue
        node_a, node_b, value = match.groups()
        value_ff = float(value)
        for node in (node_a, node_b):
            if node in totals:
                totals[node] += value_ff
    return totals


def is_useful_sample_sense_cap(node_a: str, node_b: str) -> bool:
    return set((node_a, node_b)) in ({"sample_p", "sense_p"}, {"sample_n", "sense_n"})


def write_candidate_netlist(scale: float) -> dict[str, Any]:
    text = SOURCE_NETLIST.read_text(encoding="utf-8")
    before = cap_totals(text)
    out_lines: list[str] = []
    scaled_count = 0
    for line in text.splitlines():
        if line.startswith(".subckt sky130_ultra_sense_capacitive_frontend"):
            out_lines.append(line.replace("sky130_ultra_sense_capacitive_frontend", "sky130_lower_waste_frontend_candidate"))
            continue
        match = re.match(r"(C\d+\s+)(\S+)(\s+)(\S+)(\s+)([-+0-9.]+)(f\b.*)", line)
        if match:
            prefix, node_a, gap_a, node_b, gap_b, value, suffix = match.groups()
            touches_sense = node_a in {"sense_p", "sense_n"} or node_b in {"sense_p", "sense_n"}
            if touches_sense and not is_useful_sample_sense_cap(node_a, node_b):
                scaled_value = float(value) * scale
                out_lines.append(f"{prefix}{node_a}{gap_a}{node_b}{gap_b}{scaled_value:.8g}{suffix}")
                scaled_count += 1
                continue
        out_lines.append(line)
    text_out = "\n".join(out_lines).replace(".ends", ".ends sky130_lower_waste_frontend_candidate", 1) + "\n"
    CANDIDATE_NETLIST.write_text(text_out, encoding="utf-8")
    after = cap_totals(text_out)
    return {
        "source_totals_ff": before,
        "candidate_totals_ff": after,
        "scaled_nonuseful_sense_cap_count": scaled_count,
        "nonuseful_sense_cap_scale": scale,
    }


def build_deck(row: dict[str, Any]) -> str:
    diff_v = float(row["input_diff_mv"]) / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Lower-waste frontend preamp candidate.
* This is a scaled extracted-RC experiment, not a drawn layout.

.global VSUBS
.lib "{PDK_LIB}" tt
.include "{CANDIDATE_NETLIST}"
.param vdd=1.8
.param rd=100000
.param itail=20e-6
.param win=8
.param lmin=0.15
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12

VDD vdd 0 {{vdd}}
VSS vss 0 0
VSUB VSUBS 0 0
VSP sp 0 PULSE(0 {vinp:.12f} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {vinn:.12f} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {{vdd}} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)

XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn {Candidate_subckt}
RBIASP sense_p 0 100G
RBIASN sense_n 0 100G

RDP vdd pre_p {{rd}}
RDN vdd pre_n {{rd}}
XPREP pre_p sense_p tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
XPREN pre_n sense_n tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
ITAIL tail 0 {{itail}}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(sense_p)=0.9 v(sense_n)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(tail)=0.25
.tran 20p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.control
set noaskquit
run
.endc
.end
"""


def run_case(row: dict[str, Any], output_margin_target_v: float) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row), encoding="utf-8")
    expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
    try:
        result = subprocess.run(
            ["ngspice", "-b", str(DECK_OUT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=NGSPICE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return {"reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "ngspice_returncode": None, "ngspice_timed_out": True, "measured": False, "sign_preserved": False, "output_margin_pass": False}
    out: dict[str, Any] = {"reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "ngspice_returncode": result.returncode, "ngspice_timed_out": False, "measured": result.returncode == 0}
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1600:]
        out["sign_preserved"] = False
        out["output_margin_pass"] = False
        return out
    sample_diff_v = read_measure(result.stdout, "sample_p_after_v") - read_measure(result.stdout, "sample_n_after_v")
    sense_diff_v = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    preamp_diff_v = read_measure(result.stdout, "pre_n_after_v") - read_measure(result.stdout, "pre_p_after_v")
    measured_sign = 1 if preamp_diff_v > 0 else -1 if preamp_diff_v < 0 else 0
    out.update(
        {
            "sample_diff_v": sample_diff_v,
            "sense_diff_v": sense_diff_v,
            "preamp_output_diff_v": preamp_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(preamp_diff_v) >= output_margin_target_v,
            "sample_to_sense_transfer_ratio": abs(sense_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0,
            "sense_to_preamp_gain_v_per_v": abs(preamp_diff_v) / abs(sense_diff_v) if sense_diff_v else 0.0,
        }
    )
    return out


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Lower-Waste Frontend Preamp Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- scaled nonuseful sense cap count: `{report['scaled_nonuseful_sense_cap_count']}`",
        f"- nonuseful sense cap scale: `{report['nonuseful_sense_cap_scale']:.6f}`",
        f"- source average sense capacitance fF: `{report['source_average_sense_cap_ff']:.6f}`",
        f"- candidate average sense capacitance fF: `{report['candidate_average_sense_cap_ff']:.6f}`",
        f"- target average sense capacitance fF: `{report['target_average_sense_cap_ff']:.6f}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- output margin pass count: `{report['output_margin_pass_count']}`",
        f"- minimum abs preamp output diff V: `{report['minimum_abs_preamp_output_diff_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "This experiment asks one narrow question: if the useful sample-to-sense capacitors stay the same and only the wasted sense-node capacitance is reduced to the budget target, does the same preamp finally receive enough voltage?",
        "",
        "Charge is fixed by the sample event. Voltage is charge divided by capacitance. Reducing capacitance that does not carry signal should raise the sense voltage without changing the intended coupling path.",
        "",
        "## Result",
        "",
        "| input diff mV | sense diff V | preamp output diff V | transfer ratio | sign preserved | margin pass |",
        "|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{float(row['input_diff_mv']):.6f}` | `{row.get('sense_diff_v', 0.0):.9e}` | `{row.get('preamp_output_diff_v', 0.0):.9e}` | `{row.get('sample_to_sense_transfer_ratio', 0.0):.6f}` | `{row.get('sign_preserved')}` | `{row.get('output_margin_pass')}` |"
        )
    lines.extend(["", "## Next Gate", "", report["next_gate"], "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    budget = load(CAP_BUDGET)
    sweep = load(GAIN_SWEEP)
    source_rows = [row for row in load(EVIDENCE / "sky130-ultra-sense-frontend-candidate.json")["rows"] if row["reset_mode"] == "reset_pulse"]
    source_total = float(budget["average_sense_total_cap_ff"])
    target_total = float(budget["required_total_cap_if_useful_coupling_fixed_ff"])
    useful = float(budget["average_useful_sample_to_sense_cap_ff"])
    nonuseful = source_total - useful
    scale = max((target_total - useful) / nonuseful, 0.0)
    netlist_report = write_candidate_netlist(scale)
    output_margin_target_v = float(sweep["output_margin_target_v"])
    rows = [run_case(row, output_margin_target_v) for row in source_rows]
    measured = [row for row in rows if row["measured"]]
    sign_pass_count = sum(1 for row in rows if row["sign_preserved"])
    margin_pass_count = sum(1 for row in rows if row["output_margin_pass"])
    passes = len(measured) == len(rows) and sign_pass_count == len(rows) and margin_pass_count == len(rows)
    min_output = min((abs(row["preamp_output_diff_v"]) for row in measured), default=0.0)
    candidate_avg = sum(netlist_report["candidate_totals_ff"].values()) / 2.0
    return {
        "result_type": "sky130_lower_waste_frontend_preamp_candidate",
        "status": "lower_waste_frontend_preamp_candidate_passed_scaled_rc_not_layout_proven" if passes else "lower_waste_frontend_preamp_candidate_failed_scaled_rc_margin",
        "source_capacitance_budget": rel(CAP_BUDGET),
        "source_gain_sweep": rel(GAIN_SWEEP),
        "source_netlist": rel(SOURCE_NETLIST),
        "candidate_netlist": rel(CANDIDATE_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "source_average_sense_cap_ff": source_total,
        "candidate_average_sense_cap_ff": candidate_avg,
        "target_average_sense_cap_ff": target_total,
        "useful_sample_to_sense_cap_ff": useful,
        "nonuseful_sense_cap_scale": scale,
        "scaled_nonuseful_sense_cap_count": netlist_report["scaled_nonuseful_sense_cap_count"],
        "output_margin_target_v": output_margin_target_v,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "sign_pass_count": sign_pass_count,
        "output_margin_pass_count": margin_pass_count,
        "minimum_abs_preamp_output_diff_v": min_output,
        "rows": rows,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "next_gate": (
            "The scaled-RC candidate reaches the attached-preamp margin target. The next required work is to draw and extract a real lower-waste frontend layout and rerun this same attached-preamp test."
            if passes
            else "The scaled-RC candidate still misses margin. The next required work is to combine lower wasted capacitance with stronger useful coupling or move to an isolation stage."
        ),
        "claim_boundary": {
            "allowed": "tests whether the lower-waste capacitance target would be electrically sufficient in a scaled extracted-RC experiment",
            "not_allowed": "does not prove a drawn layout, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence",
        },
    }


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_lower_waste_frontend_preamp_candidate")
    print(f"status,{report['status']}")
    print(f"candidate_average_sense_cap_ff,{report['candidate_average_sense_cap_ff']:.6f}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"output_margin_pass_count,{report['output_margin_pass_count']}")
    print(f"minimum_abs_preamp_output_diff_v,{report['minimum_abs_preamp_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
