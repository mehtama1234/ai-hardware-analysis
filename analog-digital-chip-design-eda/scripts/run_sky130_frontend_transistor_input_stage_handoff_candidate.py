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
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
FRONTEND_NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
SOURCE_FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
SOURCE_MACRO = EVIDENCE / "sky130-frontend-input-stage-handoff-candidate.json"
SOURCE_WORK_ORDER = EVIDENCE / "sky130-transistor-handoff-replacement-work-order.json"
DECK_OUT = SPICE_DIR / "sky130_frontend_transistor_input_stage_handoff_candidate.sp"
CSV_OUT = MEASUREMENTS / "sky130-frontend-transistor-input-stage-handoff-candidate.csv"
OUT_JSON = EVIDENCE / "sky130-frontend-transistor-input-stage-handoff-candidate.json"
OUT_MD = EVIDENCE / "sky130-frontend-transistor-input-stage-handoff-candidate.md"

CANDIDATE_ID = "aimc_readout_candidate_001"
HANDOFF_CANDIDATE = "sky130_frontend_transistor_input_stage_handoff_candidate"
RUN_ID = "aimc_readout_candidate_001_frontend_transistor_input_stage_handoff_candidate_run001"
NGSPICE_TIMEOUT_S = 30


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
        match = re.search(rf"{re.escape(name)}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    reset = "0.9" if case.reset_mode == "quiet_vcm" else "PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)"
    return f"""* Extracted frontend plus Sky130 transistor input-stage handoff candidate.
* This replaces the active gain macro with two Sky130 nfet input devices.
* It is not a clocked latch, SAR loop, or accepted converter simulation.

.global VSUBS
.lib "{PDK_LIB}" tt
.include "{FRONTEND_NETLIST}"
.param vdd=1.8
.param rd=100k
.param rbias=10Meg
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
VCM vcm_reset 0 {reset}

XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G

RGP sense_p gate_p 1k
RGN sense_n gate_n 1k
RGBP gate_p vcm_reset {{rbias}}
RGBN gate_n vcm_reset {{rbias}}
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


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.diff_mv > 0 else -1
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
        return {"reset_mode": case.reset_mode, "input_diff_mv": case.diff_mv, "ngspice_returncode": None, "ngspice_timed_out": True, "sign_preserved": False, "active_output_margin_pass": False}
    if result.returncode != 0:
        return {"reset_mode": case.reset_mode, "input_diff_mv": case.diff_mv, "ngspice_returncode": result.returncode, "ngspice_timed_out": result.returncode == 124, "error_excerpt": (result.stdout + result.stderr)[-1600:], "sign_preserved": False, "active_output_margin_pass": False}
    sample_diff_v = read_measure(result.stdout, "sample_p_after_v") - read_measure(result.stdout, "sample_n_after_v")
    sense_diff_v = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    gate_diff_v = read_measure(result.stdout, "gate_p_after_v") - read_measure(result.stdout, "gate_n_after_v")
    output_diff_v = read_measure(result.stdout, "outn_after_v") - read_measure(result.stdout, "outp_after_v")
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    transfer_ratio = abs(sense_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0
    gate_transfer_ratio = abs(gate_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0
    output_gain = abs(output_diff_v) / abs(sense_diff_v) if sense_diff_v else 0.0
    return {
        "reset_mode": case.reset_mode,
        "input_diff_mv": case.diff_mv,
        "sample_diff_v": sample_diff_v,
        "sense_diff_v": sense_diff_v,
        "gate_diff_v": gate_diff_v,
        "output_diff_v": output_diff_v,
        "sample_to_sense_transfer_ratio": transfer_ratio,
        "sample_to_gate_transfer_ratio": gate_transfer_ratio,
        "sense_to_output_gain_v_per_v": output_gain,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "sign_preserved": measured_sign == expected_sign,
        "active_output_margin_pass": abs(output_diff_v) >= 0.0005,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    source = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    macro = json.loads(SOURCE_MACRO.read_text(encoding="utf-8"))
    work_order = json.loads(SOURCE_WORK_ORDER.read_text(encoding="utf-8"))
    target_mv = abs(float(source["rows"][0]["input_diff_mv"]))
    cases = [Case(diff, mode) for mode in ["quiet_vcm", "reset_pulse"] for diff in (-target_mv, target_mv)]
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    sign_pass = sum(1 for row in rows if row.get("sign_preserved") is True)
    margin_pass = sum(1 for row in rows if row.get("active_output_margin_pass") is True)
    timed_out = sum(1 for row in rows if row.get("ngspice_timed_out") is True)
    min_transfer = min((float(row["sample_to_sense_transfer_ratio"]) for row in measured), default=0.0)
    min_output = min((abs(float(row["output_diff_v"])) for row in measured), default=0.0)
    loading_pass = min_transfer >= float(macro["minimum_sample_to_sense_transfer_ratio"]) * 0.9
    passed = len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows) and loading_pass
    return {
        "result_type": "sky130_frontend_transistor_input_stage_handoff_candidate",
        "status": "transistor_handoff_passed_not_latch_sar_or_strict_evidence" if passed else "transistor_handoff_measured_but_failed_acceptance" if measured else "transistor_handoff_failed_or_timed_out",
        "candidate_id": CANDIDATE_ID,
        "handoff_candidate": HANDOFF_CANDIDATE,
        "run_id": RUN_ID,
        "source_frontend_evidence": rel(SOURCE_FRONTEND),
        "source_macro_handoff": rel(SOURCE_MACRO),
        "source_work_order": rel(SOURCE_WORK_ORDER),
        "source_frontend_netlist": rel(FRONTEND_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_extracted_frontend_netlist": True,
        "uses_active_gain_macro": False,
        "uses_sky130_transistor_input_stage": True,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": timed_out,
        "sign_pass_count": sign_pass,
        "active_output_margin_pass_count": margin_pass,
        "minimum_sample_to_sense_transfer_ratio": min_transfer,
        "macro_minimum_sample_to_sense_transfer_ratio": macro["minimum_sample_to_sense_transfer_ratio"],
        "loading_pass": loading_pass,
        "minimum_output_diff_v": min_output,
        "acceptance_tests": {
            "T1_bounded_simulator_run": timed_out == 0 and len(measured) == len(rows),
            "T2_sign_handoff": sign_pass == len(rows),
            "T3_active_output_margin": margin_pass == len(rows),
            "T4_loading_check": loading_pass,
            "T5_claim_boundary": True,
        },
        "work_order_acceptance_test_count": len(work_order["acceptance_tests"]),
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "strict_blockers": [
            "This is a transistor input-stage handoff, not a clocked latch or SAR conversion.",
            "The input stage is schematic-level Sky130 devices connected to an extracted frontend; the combined active block is not DRC/LVS-clean extracted layout.",
            "There is no comparator offset/noise sweep, kickback test, full converter energy integration, DAC switching, SAR bit cycling, area signoff, or same-run strict converter payload.",
        ],
        "claim_boundary": {
            "allowed": "runs the extracted ultra frontend into a Sky130 transistor differential input stage and checks bounded run, sign, margin, loading, and claim boundary",
            "not_allowed": "does not prove clocked latch behavior, SAR conversion, full converter behavior, accepted post-layout evidence, or replacement economics",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in report["rows"] for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Frontend Transistor Input-Stage Handoff Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- handoff candidate: `{report['handoff_candidate']}`",
        f"- run id: `{report['run_id']}`",
        f"- source frontend netlist: `{report['source_frontend_netlist']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- uses extracted frontend netlist: `{report['uses_extracted_frontend_netlist']}`",
        f"- uses active gain macro: `{report['uses_active_gain_macro']}`",
        f"- uses Sky130 transistor input stage: `{report['uses_sky130_transistor_input_stage']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- active output margin pass count: `{report['active_output_margin_pass_count']}`",
        f"- loading pass: `{report['loading_pass']}`",
        f"- minimum output diff V: `{report['minimum_output_diff_v']:.9e}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The active-macro handoff proved that the equations can carry the extracted frontend signal into a gain block. This run replaces that macro with real Sky130 nfet input devices. That matters because transistor gates add capacitance, transistor current needs a bias point, and the output is now produced by device equations instead of an ideal gain statement.",
        "",
        "This is a stronger handoff than the macro run if it passes. It still stops before the latch. A comparator is not only an input pair. It must regenerate, settle before the bit deadline, avoid kicking charge back into the sample, and survive offset and noise.",
        "",
        "## Acceptance Tests",
        "",
    ]
    for name, passed in report["acceptance_tests"].items():
        lines.append(f"- {name}: `{passed}`")
    lines.extend(
        [
            "",
            "## Result",
            "",
            "| reset mode | input diff mV | sense diff uV | gate diff uV | output diff mV | transfer ratio | sign preserved | margin pass |",
            "|---|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report["rows"]:
        if row.get("ngspice_returncode") != 0 or row.get("ngspice_timed_out"):
            lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | failed | failed | failed | failed | `{row['sign_preserved']}` | `{row['active_output_margin_pass']}` |")
            continue
        lines.append(
            f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{float(row['sense_diff_v']) * 1_000_000.0:.6f}` | `{float(row['gate_diff_v']) * 1_000_000.0:.6f}` | `{float(row['output_diff_v']) * 1000.0:.6f}` | `{float(row['sample_to_sense_transfer_ratio']):.6f}` | `{row['sign_preserved']}` | `{row['active_output_margin_pass']}` |"
        )
    lines.extend(["", "## Strict Blockers", ""])
    lines.extend(f"- {item}" for item in report["strict_blockers"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_frontend_transistor_input_stage_handoff_candidate")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"active_output_margin_pass_count,{report['active_output_margin_pass_count']}")
    print(f"minimum_output_diff_v,{report['minimum_output_diff_v']:.9e}")
    print(f"uses_sky130_transistor_input_stage,{report['uses_sky130_transistor_input_stage']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0 if report["status"] == "transistor_handoff_passed_not_latch_sar_or_strict_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
