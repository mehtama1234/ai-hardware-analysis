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
FRONTEND_NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
SOURCE_FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
ACTIVE_TARGET = EVIDENCE / "sky130-active-isolation-preamp-target.json"
DECK_OUT = SPICE_DIR / "sky130_active_isolation_preamp_candidate.sp"
CSV_OUT = MEASUREMENTS / "sky130-active-isolation-preamp-candidate.csv"
OUT_JSON = EVIDENCE / "sky130-active-isolation-preamp-candidate.json"
OUT_MD = EVIDENCE / "sky130-active-isolation-preamp-candidate.md"
NGSPICE_TIMEOUT_S = 90


SETTINGS = [
    {"name": "unity_noninverting_low_cin", "iso_gain": 1.0, "polarity": 1.0, "input_cap_f": 0.05e-15, "bias_current_a": 2e-6},
    {"name": "unity_inverting_low_cin", "iso_gain": 1.0, "polarity": -1.0, "input_cap_f": 0.05e-15, "bias_current_a": 2e-6},
    {"name": "gain4_inverting_low_cin", "iso_gain": 4.0, "polarity": -1.0, "input_cap_f": 0.05e-15, "bias_current_a": 8e-6},
    {"name": "gain12_inverting_low_cin", "iso_gain": 12.0, "polarity": -1.0, "input_cap_f": 0.05e-15, "bias_current_a": 24e-6},
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def build_deck(row: dict[str, Any], setting: dict[str, Any]) -> str:
    diff_v = float(row["input_diff_mv"]) / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    gain_half = float(setting["iso_gain"]) * float(setting["polarity"]) / 2.0
    return f"""* Active isolation preamp candidate.
* The isolation block is an ideal differential voltage-gain macro with explicit input capacitance and bias-current accounting.
* It is a feasibility target for a future transistor circuit, not accepted converter evidence.

.global VSUBS
.lib "{PDK_LIB}" tt
.include "{FRONTEND_NETLIST}"
.param vdd=1.8
.param rd=100000
.param itail=20e-6
.param win=8
.param lmin=0.15
.param iso_cin={setting['input_cap_f']:.12g}
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12

VDD vdd 0 {{vdd}}
VSS vss 0 0
VSUB VSUBS 0 0
VSP sp 0 PULSE(0 {vinp:.12f} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {vinn:.12f} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {{vdd}} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)
VISO_CM iso_cm 0 0.9

XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p 0 100G
RBIASN sense_n 0 100G
CINP sense_p 0 {{iso_cin}}
CINN sense_n 0 {{iso_cin}}

EISOP iso_p iso_cm sense_p sense_n {gain_half:.12g}
EISON iso_n iso_cm sense_n sense_p {gain_half:.12g}
CISOP iso_p 0 2f
CISON iso_n 0 2f

RDP vdd pre_p {{rd}}
RDN vdd pre_n {{rd}}
XPREP pre_p iso_p tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
XPREN pre_n iso_n tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
ITAIL tail 0 {{itail}}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(sense_p)=0.9 v(sense_n)=0.9 v(iso_p)=0.9 v(iso_n)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(tail)=0.25
.tran 20p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran iso_p_after_v FIND v(iso_p) AT=2.60n
.measure tran iso_n_after_v FIND v(iso_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.control
set noaskquit
run
.endc
.end
"""


def run_case(row: dict[str, Any], setting: dict[str, Any], output_target_v: float) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row, setting), encoding="utf-8")
    expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {**setting, "reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "ngspice_returncode": None, "ngspice_timed_out": True, "measured": False, "sign_preserved": False, "output_margin_pass": False}
    out: dict[str, Any] = {**setting, "reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "ngspice_returncode": result.returncode, "ngspice_timed_out": False, "measured": result.returncode == 0}
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1600:]
        out["sign_preserved"] = False
        out["output_margin_pass"] = False
        return out
    sample_diff_v = read_measure(result.stdout, "sample_p_after_v") - read_measure(result.stdout, "sample_n_after_v")
    sense_diff_v = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    iso_diff_v = read_measure(result.stdout, "iso_p_after_v") - read_measure(result.stdout, "iso_n_after_v")
    preamp_diff_v = read_measure(result.stdout, "pre_n_after_v") - read_measure(result.stdout, "pre_p_after_v")
    measured_sign = 1 if preamp_diff_v > 0 else -1 if preamp_diff_v < 0 else 0
    out.update(
        {
            "sample_diff_v": sample_diff_v,
            "sense_diff_v": sense_diff_v,
            "isolation_output_diff_v": iso_diff_v,
            "preamp_output_diff_v": preamp_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(preamp_diff_v) >= output_target_v,
            "sample_to_sense_transfer_ratio": abs(sense_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0,
            "sense_to_isolation_gain_v_per_v": abs(iso_diff_v) / abs(sense_diff_v) if sense_diff_v else 0.0,
            "isolation_to_preamp_gain_v_per_v": abs(preamp_diff_v) / abs(iso_diff_v) if iso_diff_v else 0.0,
        }
    )
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [row for row in rows if row["measured"]]
    return {
        "name": rows[0]["name"],
        "iso_gain": rows[0]["iso_gain"],
        "polarity": rows[0]["polarity"],
        "input_cap_f": rows[0]["input_cap_f"],
        "bias_current_a": rows[0]["bias_current_a"],
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "sign_pass_count": sum(1 for row in rows if row["sign_preserved"]),
        "output_margin_pass_count": sum(1 for row in rows if row["output_margin_pass"]),
        "minimum_abs_preamp_output_diff_v": min((abs(row["preamp_output_diff_v"]) for row in measured), default=0.0),
        "minimum_sample_to_sense_transfer_ratio": min((row["sample_to_sense_transfer_ratio"] for row in measured), default=0.0),
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    target = json.loads(ACTIVE_TARGET.read_text(encoding="utf-8"))
    frontend = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    source_rows = [row for row in frontend["rows"] if row["reset_mode"] == "reset_pulse"]
    output_target_v = float(target["output_margin_target_v"])
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    for setting in SETTINGS:
        setting_rows = [run_case(row, setting, output_target_v) for row in source_rows]
        rows.extend(setting_rows)
        summaries.append(summarize(setting_rows))
    passing = [item for item in summaries if item["measured_case_count"] == item["case_count"] and item["sign_pass_count"] == item["case_count"] and item["output_margin_pass_count"] == item["case_count"]]
    best = max(summaries, key=lambda item: (item["output_margin_pass_count"], item["minimum_abs_preamp_output_diff_v"]))
    return {
        "result_type": "sky130_active_isolation_preamp_candidate",
        "status": "active_isolation_macro_candidate_passed_not_transistor_layout_or_strict" if passing else "active_isolation_macro_candidate_failed_margin_or_runability",
        "source_active_isolation_target": rel(ACTIVE_TARGET),
        "source_frontend_evidence": rel(SOURCE_FRONTEND),
        "source_frontend_netlist": rel(FRONTEND_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "output_margin_target_v": output_target_v,
        "setting_count": len(summaries),
        "case_count": len(rows),
        "measured_case_count": sum(1 for row in rows if row["measured"]),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "passing_setting_count": len(passing),
        "first_passing_setting": passing[0]["name"] if passing else None,
        "best_setting": best,
        "setting_summaries": summaries,
        "rows": rows,
        "uses_extracted_frontend_netlist": True,
        "uses_ideal_active_isolation_macro": True,
        "uses_sky130_preamp": True,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "sweeps an ideal low-input-capacitance active isolation macro in front of the Sky130 preamp to identify the gain and input-capacitance target",
            "not_allowed": "does not prove a transistor isolation circuit, drawn layout, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Active Isolation Preamp Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- first passing setting: `{report['first_passing_setting']}`",
        f"- best setting: `{report['best_setting']['name']}`",
        f"- best minimum abs preamp output diff V: `{report['best_setting']['minimum_abs_preamp_output_diff_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The passive frontend cannot push enough voltage into the preamp. The active-isolation idea is to read the frontend with a very small capacitance, make a larger differential voltage, and then let the existing preamp do its normal job.",
        "",
        "This candidate is deliberately a macro. It answers the next design question before transistor sizing: how much isolated differential gain is enough, and does low input capacitance keep the frontend signal alive?",
        "",
        "## Setting Summary",
        "",
        "| setting | isolation gain | polarity | input cap fF | bias current uA | measured | sign pass | margin pass | min sense ratio | min output mV |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['name']}` | `{item['iso_gain']:.3f}` | `{item['polarity']:.0f}` | `{item['input_cap_f'] * 1e15:.3f}` | `{item['bias_current_a'] * 1e6:.3f}` | `{item['measured_case_count']}` | `{item['sign_pass_count']}` | `{item['output_margin_pass_count']}` | `{item['minimum_sample_to_sense_transfer_ratio']:.6f}` | `{item['minimum_abs_preamp_output_diff_v'] * 1000.0:.6f}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_active_isolation_preamp_candidate")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"first_passing_setting,{report['first_passing_setting']}")
    print(f"best_setting,{report['best_setting']['name']}")
    print(f"best_minimum_abs_preamp_output_diff_v,{report['best_setting']['minimum_abs_preamp_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
