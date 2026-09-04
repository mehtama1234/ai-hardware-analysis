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
SOURCE_ASSISTED = EVIDENCE / "sky130-extracted-frontend-to-transistor-gate-startup.json"
DECK_OUT = SPICE_DIR / "sky130_extracted_frontend_gate_coupling_sweep.sp"
CSV_OUT = MEASUREMENTS / "sky130-extracted-frontend-gate-coupling-sweep.csv"
OUT_JSON = EVIDENCE / "sky130-extracted-frontend-gate-coupling-sweep.json"
OUT_MD = EVIDENCE / "sky130-extracted-frontend-gate-coupling-sweep.md"
NGSPICE_TIMEOUT_S = 12

SWEEP_SETTINGS = [
    (3e5, 5e4),
    (1e6, 5e4),
    (1e6, 1e5),
    (3e6, 1e5),
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


def spice_res(value: float) -> str:
    if value >= 1e6:
        return f"{value / 1e6:g}Meg"
    if value >= 1e3:
        return f"{value / 1e3:g}k"
    return f"{value:g}"


def build_deck(row: dict[str, Any], sense_to_gate_ohm: float, prebias_ohm: float) -> str:
    diff_v = float(row["input_diff_mv"]) / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    expected_sense_p = 0.9 + float(row["sense_diff_after_v"]) / 2.0
    expected_sense_n = 0.9 - float(row["sense_diff_after_v"]) / 2.0
    return f"""* Extracted frontend gate-coupling sweep.
* Sweeps sense-to-gate loading and weak startup assist.

.global VSUBS
.lib "{PDK_LIB}" tt
.include "{FRONTEND_NETLIST}"
.param vdd=1.8
.param rd=100k
.param rtail=45k
.param wn=8.0
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
RGP sense_p gate_p {spice_res(sense_to_gate_ohm)}
RGN sense_n gate_n {spice_res(sense_to_gate_ohm)}
VGPRE gate_p_pre 0 PWL(0 0.9 0.60n 0.9 1.50n {expected_sense_p:.12f} 3n {expected_sense_p:.12f})
VGNRE gate_n_pre 0 PWL(0 0.9 0.60n 0.9 1.50n {expected_sense_n:.12f} 3n {expected_sense_n:.12f})
RPREP gate_p_pre gate_p {spice_res(prebias_ohm)}
RPREN gate_n_pre gate_n {spice_res(prebias_ohm)}

RDP vdd outp {{rd}}
RDN vdd outn {{rd}}
XINP outp gate_p tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XINN outn gate_n tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
RTAIL tail 0 {{rtail}}
COUTP outp 0 2f
COUTN outn 0 2f

.ic v(sense_p)=0.9 v(sense_n)=0.9 v(gate_p)=0.9 v(gate_n)=0.9 v(outp)=1.0 v(outn)=1.0 v(tail)=0.25
.tran 20p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran gate_p_after_v FIND v(gate_p) AT=2.60n
.measure tran gate_n_after_v FIND v(gate_n) AT=2.60n
.measure tran outp_after_v FIND v(outp) AT=2.60n
.measure tran outn_after_v FIND v(outn) AT=2.60n
.control
set noaskquit
run
.endc
.end
"""


def run_case(row: dict[str, Any], sense_to_gate_ohm: float, prebias_ohm: float) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row, sense_to_gate_ohm, prebias_ohm), encoding="utf-8")
    expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
    try:
        result = subprocess.run(
            ["timeout", f"{NGSPICE_TIMEOUT_S}s", "ngspice", "-b", str(DECK_OUT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=NGSPICE_TIMEOUT_S + 5,
        )
    except subprocess.TimeoutExpired:
        return {
            "reset_mode": row["reset_mode"],
            "input_diff_mv": row["input_diff_mv"],
            "sense_to_gate_ohm": sense_to_gate_ohm,
            "prebias_ohm": prebias_ohm,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "measured": False,
            "sign_preserved": False,
            "output_margin_pass": False,
        }
    out: dict[str, Any] = {
        "reset_mode": row["reset_mode"],
        "input_diff_mv": row["input_diff_mv"],
        "source_sense_diff_v": row["sense_diff_after_v"],
        "sense_to_gate_ohm": sense_to_gate_ohm,
        "prebias_ohm": prebias_ohm,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": result.returncode == 124,
        "measured": result.returncode == 0,
    }
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        out["sign_preserved"] = False
        out["output_margin_pass"] = False
        return out
    sample_diff_v = read_measure(result.stdout, "sample_p_after_v") - read_measure(result.stdout, "sample_n_after_v")
    sense_diff_v = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    gate_diff_v = read_measure(result.stdout, "gate_p_after_v") - read_measure(result.stdout, "gate_n_after_v")
    output_diff_v = read_measure(result.stdout, "outn_after_v") - read_measure(result.stdout, "outp_after_v")
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    out.update(
        {
            "sample_diff_v": sample_diff_v,
            "sense_diff_v": sense_diff_v,
            "gate_diff_v": gate_diff_v,
            "output_diff_v": output_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(output_diff_v) >= 0.0005,
            "sample_to_sense_transfer_ratio": abs(sense_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0,
            "sense_to_gate_transfer_ratio": abs(gate_diff_v) / abs(sense_diff_v) if sense_diff_v else 0.0,
            "gate_to_output_gain_v_per_v": abs(output_diff_v) / abs(gate_diff_v) if gate_diff_v else 0.0,
        }
    )
    return out


def summarize_setting(rows: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [row for row in rows if row["measured"]]
    return {
        "sense_to_gate_ohm": rows[0]["sense_to_gate_ohm"],
        "prebias_ohm": rows[0]["prebias_ohm"],
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "sign_pass_count": sum(1 for row in rows if row["sign_preserved"]),
        "output_margin_pass_count": sum(1 for row in rows if row["output_margin_pass"]),
        "minimum_abs_output_diff_v": min((abs(row["output_diff_v"]) for row in measured), default=0.0),
        "minimum_sense_to_gate_transfer_ratio": min((row["sense_to_gate_transfer_ratio"] for row in measured), default=0.0),
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    if not FRONTEND_NETLIST.exists():
        raise FileNotFoundError(FRONTEND_NETLIST)
    frontend = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    assisted = json.loads(SOURCE_ASSISTED.read_text(encoding="utf-8"))
    source_rows = [row for row in frontend["rows"] if row["reset_mode"] == "reset_pulse"]
    rows: list[dict[str, Any]] = []
    setting_summaries: list[dict[str, Any]] = []
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    for sense_to_gate_ohm, prebias_ohm in SWEEP_SETTINGS:
        setting_rows = [run_case(row, sense_to_gate_ohm, prebias_ohm) for row in source_rows]
        rows.extend(setting_rows)
        setting_summaries.append(summarize_setting(setting_rows))
    pass_settings = [
        item
        for item in setting_summaries
        if item["measured_case_count"] == item["case_count"]
        and item["sign_pass_count"] == item["case_count"]
        and item["output_margin_pass_count"] == item["case_count"]
    ]
    best_by_margin = max(setting_summaries, key=lambda item: (item["output_margin_pass_count"], item["sign_pass_count"], item["minimum_abs_output_diff_v"]))
    best_by_sign = max(setting_summaries, key=lambda item: (item["sign_pass_count"], item["output_margin_pass_count"], item["minimum_abs_output_diff_v"]))
    return {
        "result_type": "sky130_extracted_frontend_gate_coupling_sweep",
        "status": "gate_coupling_sweep_found_passing_assisted_setting_not_full_handoff" if pass_settings else "gate_coupling_sweep_found_no_passing_assisted_setting",
        "source_frontend_evidence": rel(SOURCE_FRONTEND),
        "source_assisted_gate_startup": rel(SOURCE_ASSISTED),
        "source_frontend_netlist": rel(FRONTEND_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_extracted_frontend_netlist": True,
        "uses_sky130_transistor_input_stage": True,
        "uses_assisted_gate_startup": True,
        "uses_full_free_gate_handoff": False,
        "sweep_settings": [{"sense_to_gate_ohm": item[0], "prebias_ohm": item[1]} for item in SWEEP_SETTINGS],
        "setting_count": len(setting_summaries),
        "case_count": len(rows),
        "measured_case_count": sum(1 for row in rows if row["measured"]),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "passing_setting_count": len(pass_settings),
        "best_by_margin": best_by_margin,
        "best_by_sign": best_by_sign,
        "setting_summaries": setting_summaries,
        "rows": rows,
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "sweeps assisted sense-to-gate coupling and gate prebias strength to localize why the loaded extracted frontend fails the transistor gate handoff",
            "not_allowed": "does not prove full free gate handoff, latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Extracted Frontend Gate Coupling Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- uses extracted frontend netlist: `{report['uses_extracted_frontend_netlist']}`",
        f"- uses Sky130 transistor input stage: `{report['uses_sky130_transistor_input_stage']}`",
        f"- uses assisted gate startup: `{report['uses_assisted_gate_startup']}`",
        f"- uses full free gate handoff: `{report['uses_full_free_gate_handoff']}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A tiny sampled voltage is not only a number. It is charge sitting on small capacitances. When a transistor gate is attached, the same charge sees a new electrical object. The voltage can shrink, move, or flip because the gate path and bias path now share the node.",
        "",
        "This sweep changes two resistances. The sense-to-gate resistance controls how hard the frontend is loaded by the transistor input. The prebias resistance controls how hard the startup guide pulls the gate toward the previously measured sense voltage. If one setting passed both polarities, the next move would be to remove the guide gradually. If no setting passes, the frontend needs a buffer, a stronger differential sense node, or a cleaner port topology before latch work is meaningful.",
        "",
        "## Setting Summary",
        "",
        "| sense-to-gate ohm | prebias ohm | measured | sign pass | margin pass | min output mV | min sense-to-gate |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['sense_to_gate_ohm']:.0f}` | `{item['prebias_ohm']:.0f}` | `{item['measured_case_count']}` | `{item['sign_pass_count']}` | `{item['output_margin_pass_count']}` | `{item['minimum_abs_output_diff_v'] * 1000.0:.6f}` | `{item['minimum_sense_to_gate_transfer_ratio']:.6f}` |"
        )
    lines.extend(
        [
            "",
            "## Best Observed Setting",
            "",
            f"- by margin: sense-to-gate `{report['best_by_margin']['sense_to_gate_ohm']:.0f}` ohm, prebias `{report['best_by_margin']['prebias_ohm']:.0f}` ohm, sign passes `{report['best_by_margin']['sign_pass_count']}`, margin passes `{report['best_by_margin']['output_margin_pass_count']}`",
            f"- by sign: sense-to-gate `{report['best_by_sign']['sense_to_gate_ohm']:.0f}` ohm, prebias `{report['best_by_sign']['prebias_ohm']:.0f}` ohm, sign passes `{report['best_by_sign']['sign_pass_count']}`, margin passes `{report['best_by_sign']['output_margin_pass_count']}`",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_extracted_frontend_gate_coupling_sweep")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
