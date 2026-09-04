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
FRONTEND_NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
SOURCE_FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
WORK_ORDER = EVIDENCE / "first-real-converter-combined-active-handoff-work-order.json"
DECK_OUT = SPICE_DIR / "sky130_frontend_input_stage_handoff_candidate.sp"
CSV_OUT = MEASUREMENTS / "sky130-frontend-input-stage-handoff-candidate.csv"
OUT_JSON = EVIDENCE / "sky130-frontend-input-stage-handoff-candidate.json"
OUT_MD = EVIDENCE / "sky130-frontend-input-stage-handoff-candidate.md"

CANDIDATE_ID = "aimc_readout_candidate_001"
HANDOFF_CANDIDATE = "sky130_frontend_input_stage_handoff_candidate"
RUN_ID = "aimc_readout_candidate_001_frontend_input_stage_handoff_candidate_run001"
GAIN_V_PER_V = 9.201769060682565
LOAD_CAP_F = 2.0e-15
NGSPICE_TIMEOUT_S = 20


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
    return f"""* Combined extracted frontend plus bounded active-gain handoff candidate.
* The frontend is the Magic-extracted ultra-sense capacitance network.
* The active input stage is represented by a bounded voltage-controlled gain macro using measured local gain.
* This is a same-deck handoff run, not a Sky130 transistor input-stage proof.

.global VSUBS
.include "{FRONTEND_NETLIST}"
.param gain={GAIN_V_PER_V:.12f}
.param vcm=0.9
.param vdd=1.8

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

VOUTPCM outp_cm 0 {{vcm}}
VOUTNCM outn_cm 0 {{vcm}}
EOUTP outp outp_cm sense_n sense_p {GAIN_V_PER_V / 2.0:.12f}
EOUTN outn outn_cm sense_p sense_n {GAIN_V_PER_V / 2.0:.12f}
COUTP outp 0 {LOAD_CAP_F:.3e}
COUTN outn 0 {LOAD_CAP_F:.3e}
ROUTP outp 0 100G
ROUTN outn 0 100G

.tran 2p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran outp_after_v FIND v(outp) AT=2.60n
.measure tran outn_after_v FIND v(outn) AT=2.60n
.control
run
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.diff_mv > 0 else -1
    try:
        result = subprocess.run(["timeout", f"{NGSPICE_TIMEOUT_S}s", "ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S + 5)
    except subprocess.TimeoutExpired:
        return {"reset_mode": case.reset_mode, "input_diff_mv": case.diff_mv, "ngspice_returncode": None, "ngspice_timed_out": True, "sign_preserved": False, "active_output_margin_pass": False}
    if result.returncode != 0:
        return {"reset_mode": case.reset_mode, "input_diff_mv": case.diff_mv, "ngspice_returncode": result.returncode, "ngspice_timed_out": result.returncode == 124, "error_excerpt": (result.stdout + result.stderr)[-1200:], "sign_preserved": False, "active_output_margin_pass": False}
    sample_diff_v = read_measure(result.stdout, "sample_p_after_v") - read_measure(result.stdout, "sample_n_after_v")
    sense_diff_v = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    output_diff_v = read_measure(result.stdout, "outn_after_v") - read_measure(result.stdout, "outp_after_v")
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    transfer_ratio = abs(sense_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0
    output_gain = abs(output_diff_v) / abs(sense_diff_v) if sense_diff_v else 0.0
    return {
        "reset_mode": case.reset_mode,
        "input_diff_mv": case.diff_mv,
        "sample_diff_v": sample_diff_v,
        "sense_diff_v": sense_diff_v,
        "output_diff_v": output_diff_v,
        "sample_to_sense_transfer_ratio": transfer_ratio,
        "sense_to_output_gain_v_per_v": output_gain,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "sign_preserved": measured_sign == expected_sign,
        "active_output_margin_pass": abs(output_diff_v) >= 0.0005,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
    }


def build_report() -> dict[str, Any]:
    source = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    work_order = json.loads(WORK_ORDER.read_text(encoding="utf-8"))
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
    loading_pass = min_transfer >= float(source["minimum_sample_to_sense_transfer_ratio"]) * 0.9
    passed = len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows) and loading_pass
    return {
        "result_type": "sky130_frontend_input_stage_handoff_candidate",
        "status": "active_macro_handoff_passed_not_sky130_transistor_or_strict_evidence" if passed else "active_macro_handoff_failed",
        "candidate_id": CANDIDATE_ID,
        "handoff_candidate": HANDOFF_CANDIDATE,
        "run_id": RUN_ID,
        "source_frontend_evidence": rel(SOURCE_FRONTEND),
        "source_work_order": rel(WORK_ORDER),
        "source_frontend_netlist": rel(FRONTEND_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "active_gain_source": "measured local Sky130 comparator input-stage gain, represented here as a bounded gain macro",
        "active_gain_v_per_v": GAIN_V_PER_V,
        "uses_extracted_frontend_netlist": True,
        "uses_active_gain_macro": True,
        "uses_sky130_transistor_input_stage": False,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": timed_out,
        "sign_pass_count": sign_pass,
        "active_output_margin_pass_count": margin_pass,
        "minimum_sample_to_sense_transfer_ratio": min_transfer,
        "source_minimum_sample_to_sense_transfer_ratio": source["minimum_sample_to_sense_transfer_ratio"],
        "loading_pass": loading_pass,
        "minimum_output_diff_v": min_output,
        "acceptance_tests": {
            "A1_bounded_simulator_run": timed_out == 0 and len(measured) == len(rows),
            "A2_sign_handoff": sign_pass == len(rows),
            "A3_active_output_margin": margin_pass == len(rows),
            "A4_loading_check": loading_pass,
            "A5_claim_boundary": True,
        },
        "work_order_acceptance_test_count": len(work_order["acceptance_tests"]),
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "strict_blockers": [
            "The active input stage is represented by a bounded gain macro, not a Sky130 transistor input-stage netlist.",
            "The run proves same-deck frontend-to-active-macro handoff, not transistor operating point, offset, noise, or latch resolution.",
            "There is no SAR loop, DAC switching, full energy integration, DRC/LVS area, or same-run strict converter payload.",
        ],
        "claim_boundary": {
            "allowed": "runs the extracted ultra frontend and an active gain macro in one deck and checks bounded run, sign, output margin, loading, and claim boundary",
            "not_allowed": "does not prove Sky130 transistor input-stage handoff, clocked latch behavior, full converter behavior, accepted post-layout evidence, or replacement economics",
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
        "# Sky130 Frontend Input-Stage Handoff Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- handoff candidate: `{report['handoff_candidate']}`",
        f"- run id: `{report['run_id']}`",
        f"- source frontend netlist: `{report['source_frontend_netlist']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- active gain V/V: `{report['active_gain_v_per_v']:.6f}`",
        f"- uses extracted frontend netlist: `{report['uses_extracted_frontend_netlist']}`",
        f"- uses active gain macro: `{report['uses_active_gain_macro']}`",
        f"- uses Sky130 transistor input stage: `{report['uses_sky130_transistor_input_stage']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
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
        "A handoff is real only when the output of one block becomes the input of the next block in the same circuit equations. This deck includes the extracted ultra frontend and an active gain element together. The frontend stores and moves charge. The active element turns the resulting signed sense voltage into a larger signed output voltage.",
        "",
        "This closes the same-deck handoff at the active-macro level. It still does not close the transistor handoff. The macro uses the measured local input-stage gain, but it does not load the frontend like a real Sky130 input pair, and it does not show transistor operating point, offset, noise, kickback, or latch resolution.",
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
            "| reset mode | input diff mV | sense diff uV | output diff mV | transfer ratio | sign preserved | margin pass |",
            "|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report["rows"]:
        lines.append(
            f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{float(row.get('sense_diff_v', 0.0)) * 1_000_000.0:.6f}` | `{float(row.get('output_diff_v', 0.0)) * 1000.0:.6f}` | `{float(row.get('sample_to_sense_transfer_ratio', 0.0)):.6f}` | `{row['sign_preserved']}` | `{row['active_output_margin_pass']}` |"
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
    print("sky130_frontend_input_stage_handoff_candidate")
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
    return 0 if report["status"] == "active_macro_handoff_passed_not_sky130_transistor_or_strict_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
