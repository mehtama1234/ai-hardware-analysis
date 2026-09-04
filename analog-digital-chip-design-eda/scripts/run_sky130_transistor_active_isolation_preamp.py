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
SOURCE_MACRO = EVIDENCE / "sky130-offset-calibrated-active-isolation-preamp.json"
DECK_OUT = SPICE_DIR / "sky130_transistor_active_isolation_preamp.sp"
CSV_OUT = MEASUREMENTS / "sky130-transistor-active-isolation-preamp.csv"
OUT_JSON = EVIDENCE / "sky130-transistor-active-isolation-preamp.json"
OUT_MD = EVIDENCE / "sky130-transistor-active-isolation-preamp.md"
NGSPICE_TIMEOUT_S = 120
OUTPUT_TARGET_V = 0.0005


SETTINGS = [
    {"name": "tiny_iso_pair_2ua", "wiso": 0.42, "iso_tail_a": 2e-6, "iso_rd_ohm": 220_000.0, "pre_w": 8.0, "pre_tail_a": 20e-6, "pre_rd_ohm": 100_000.0},
    {"name": "small_iso_pair_4ua", "wiso": 1.0, "iso_tail_a": 4e-6, "iso_rd_ohm": 180_000.0, "pre_w": 8.0, "pre_tail_a": 20e-6, "pre_rd_ohm": 100_000.0},
    {"name": "medium_iso_pair_8ua", "wiso": 2.0, "iso_tail_a": 8e-6, "iso_rd_ohm": 120_000.0, "pre_w": 8.0, "pre_tail_a": 20e-6, "pre_rd_ohm": 100_000.0},
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


def frontend_rows() -> list[dict[str, Any]]:
    frontend = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    rows = [row for row in frontend["rows"] if row["reset_mode"] == "reset_pulse"]
    zero = dict(rows[0])
    zero["input_diff_mv"] = 0.0
    return [zero] + rows


def build_deck(row: dict[str, Any], setting: dict[str, Any]) -> str:
    diff_v = float(row["input_diff_mv"]) / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Sky130 transistor active isolation before preamp.
* This replaces the ideal active-isolation macro with a small differential pair.
* It is schematic transistor evidence, not layout or accepted converter evidence.

.global VSUBS
.lib "{PDK_LIB}" tt
.include "{FRONTEND_NETLIST}"
.param vdd=1.8
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

XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p 0 100G
RBIASN sense_n 0 100G

RISO_P vdd iso_p {setting['iso_rd_ohm']:.12g}
RISO_N vdd iso_n {setting['iso_rd_ohm']:.12g}
XISO_P iso_p sense_p iso_tail 0 sky130_fd_pr__nfet_01v8 W={setting['wiso']:.12g} L={{lmin}}
XISO_N iso_n sense_n iso_tail 0 sky130_fd_pr__nfet_01v8 W={setting['wiso']:.12g} L={{lmin}}
IISO_TAIL iso_tail 0 {setting['iso_tail_a']:.12g}
CISO_P iso_p 0 2f
CISO_N iso_n 0 2f

RDP vdd pre_p {setting['pre_rd_ohm']:.12g}
RDN vdd pre_n {setting['pre_rd_ohm']:.12g}
XPREP pre_p iso_p pre_tail 0 sky130_fd_pr__nfet_01v8 W={setting['pre_w']:.12g} L={{lmin}}
XPREN pre_n iso_n pre_tail 0 sky130_fd_pr__nfet_01v8 W={setting['pre_w']:.12g} L={{lmin}}
IPRE_TAIL pre_tail 0 {setting['pre_tail_a']:.12g}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(sense_p)=0.9 v(sense_n)=0.9 v(iso_p)=1.2 v(iso_n)=1.2 v(iso_tail)=0.25 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail)=0.25
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


def run_case(row: dict[str, Any], setting: dict[str, Any]) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row, setting), encoding="utf-8")
    expected_sign = 0 if float(row["input_diff_mv"]) == 0.0 else 1 if float(row["input_diff_mv"]) > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {**setting, "input_diff_mv": row["input_diff_mv"], "measured": False, "ngspice_timed_out": True, "ngspice_returncode": None}
    out: dict[str, Any] = {**setting, "input_diff_mv": row["input_diff_mv"], "expected_sign": expected_sign, "measured": result.returncode == 0, "ngspice_timed_out": False, "ngspice_returncode": result.returncode}
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1600:]
        return out
    sample_diff_v = read_measure(result.stdout, "sample_p_after_v") - read_measure(result.stdout, "sample_n_after_v")
    sense_diff_v = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    iso_diff_v = read_measure(result.stdout, "iso_n_after_v") - read_measure(result.stdout, "iso_p_after_v")
    preamp_diff_v = read_measure(result.stdout, "pre_n_after_v") - read_measure(result.stdout, "pre_p_after_v")
    out.update(
        {
            "sample_diff_v": sample_diff_v,
            "sense_diff_v": sense_diff_v,
            "isolation_output_diff_v": iso_diff_v,
            "preamp_output_diff_v": preamp_diff_v,
            "sample_to_sense_transfer_ratio": abs(sense_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0,
            "sense_to_isolation_gain_v_per_v": abs(iso_diff_v) / abs(sense_diff_v) if sense_diff_v else 0.0,
            "isolation_to_preamp_gain_v_per_v": abs(preamp_diff_v) / abs(iso_diff_v) if iso_diff_v else 0.0,
        }
    )
    return out


def summarize(setting_rows: list[dict[str, Any]]) -> dict[str, Any]:
    zero = next((row for row in setting_rows if row["measured"] and float(row["input_diff_mv"]) == 0.0), None)
    zero_output = float(zero["preamp_output_diff_v"]) if zero else 0.0
    signal_rows = [row for row in setting_rows if float(row["input_diff_mv"]) != 0.0]
    for row in signal_rows:
        if not row["measured"]:
            row["corrected_sign_preserved"] = False
            row["corrected_output_margin_pass"] = False
            continue
        corrected = float(row["preamp_output_diff_v"]) - zero_output
        measured_sign = 1 if corrected > 0 else -1 if corrected < 0 else 0
        row["zero_input_preamp_output_diff_v"] = zero_output
        row["corrected_preamp_output_diff_v"] = corrected
        row["corrected_measured_sign"] = measured_sign
        row["corrected_sign_preserved"] = measured_sign == row["expected_sign"]
        row["corrected_output_margin_pass"] = abs(corrected) >= OUTPUT_TARGET_V
    measured_signal = [row for row in signal_rows if row["measured"]]
    return {
        "name": setting_rows[0]["name"],
        "wiso": setting_rows[0]["wiso"],
        "iso_tail_a": setting_rows[0]["iso_tail_a"],
        "iso_rd_ohm": setting_rows[0]["iso_rd_ohm"],
        "zero_input_preamp_output_diff_v": zero_output,
        "case_count": len(signal_rows),
        "measured_case_count": len(measured_signal),
        "timed_out_case_count": sum(1 for row in signal_rows if row["ngspice_timed_out"]),
        "corrected_sign_pass_count": sum(1 for row in signal_rows if row.get("corrected_sign_preserved")),
        "corrected_margin_pass_count": sum(1 for row in signal_rows if row.get("corrected_output_margin_pass")),
        "minimum_abs_corrected_preamp_output_diff_v": min((abs(row["corrected_preamp_output_diff_v"]) for row in measured_signal), default=0.0),
        "minimum_sample_to_sense_transfer_ratio": min((row["sample_to_sense_transfer_ratio"] for row in measured_signal), default=0.0),
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    macro = json.loads(SOURCE_MACRO.read_text(encoding="utf-8"))
    all_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for setting in SETTINGS:
        setting_rows = [run_case(row, setting) for row in frontend_rows()]
        summaries.append(summarize(setting_rows))
        all_rows.extend(row for row in setting_rows if float(row["input_diff_mv"]) != 0.0)
    passing = [item for item in summaries if item["measured_case_count"] == item["case_count"] and item["corrected_sign_pass_count"] == item["case_count"] and item["corrected_margin_pass_count"] == item["case_count"]]
    best = max(summaries, key=lambda item: (item["corrected_margin_pass_count"], item["corrected_sign_pass_count"], item["minimum_abs_corrected_preamp_output_diff_v"]))
    return {
        "result_type": "sky130_transistor_active_isolation_preamp",
        "status": "transistor_active_isolation_preamp_passed_schematic_not_layout_or_strict" if passing else "transistor_active_isolation_preamp_failed_schematic",
        "source_offset_calibrated_macro": rel(SOURCE_MACRO),
        "source_frontend_netlist": rel(FRONTEND_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "output_margin_target_v": OUTPUT_TARGET_V,
        "macro_first_passing_setting": macro["first_passing_setting"],
        "setting_count": len(summaries),
        "case_count": len(all_rows),
        "measured_case_count": sum(1 for row in all_rows if row["measured"]),
        "timed_out_case_count": sum(1 for row in all_rows if row["ngspice_timed_out"]),
        "passing_setting_count": len(passing),
        "first_passing_setting": passing[0]["name"] if passing else None,
        "best_setting": best,
        "setting_summaries": summaries,
        "rows": all_rows,
        "uses_extracted_frontend_netlist": True,
        "uses_sky130_transistor_isolation_pair": True,
        "uses_offset_calibration": True,
        "uses_sky130_preamp": True,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "tests small Sky130 transistor differential-pair isolation stages before the existing preamp with zero-input offset subtraction",
            "not_allowed": "does not prove layout, DRC/LVS, offset stability, noise, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence",
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
        "# Sky130 Transistor Active Isolation Preamp",
        "",
        f"- status: `{report['status']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- first passing setting: `{report['first_passing_setting']}`",
        f"- best setting: `{report['best_setting']['name']}`",
        f"- best minimum abs corrected preamp output diff V: `{report['best_setting']['minimum_abs_corrected_preamp_output_diff_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The ideal macro proved the shape of the answer: read the frontend lightly, subtract the zero-input offset, and ask whether both signs still exceed the margin. This run replaces that ideal gain block with a small Sky130 differential pair.",
        "",
        "The important test is not whether the transistor pair produces any gain. It must do all three jobs together: keep the frontend sense ratio high, leave a calibratable zero point, and create corrected output margin for both signs.",
        "",
        "## Setting Summary",
        "",
        "| setting | iso width | iso tail uA | zero output mV | measured | corrected sign pass | corrected margin pass | min corrected output mV | min sense ratio |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['name']}` | `{item['wiso']:.3f}` | `{item['iso_tail_a'] * 1e6:.3f}` | `{item['zero_input_preamp_output_diff_v'] * 1000.0:.6f}` | `{item['measured_case_count']}` | `{item['corrected_sign_pass_count']}` | `{item['corrected_margin_pass_count']}` | `{item['minimum_abs_corrected_preamp_output_diff_v'] * 1000.0:.6f}` | `{item['minimum_sample_to_sense_transfer_ratio']:.6f}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_transistor_active_isolation_preamp")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"first_passing_setting,{report['first_passing_setting']}")
    print(f"best_setting,{report['best_setting']['name']}")
    print(f"best_minimum_abs_corrected_preamp_output_diff_v,{report['best_setting']['minimum_abs_corrected_preamp_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
