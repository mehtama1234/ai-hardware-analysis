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
SOURCE_FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
SOURCE_TRANSISTOR = EVIDENCE / "sky130-comparator-input-stage-ngspice.json"
SOURCE_PROBE = EVIDENCE / "sky130-transistor-handoff-probe-ladder.json"
DECK_OUT = SPICE_DIR / "sky130_frontend_sense_to_transistor_op_handoff.sp"
CSV_OUT = MEASUREMENTS / "sky130-frontend-sense-to-transistor-op-handoff.csv"
OUT_JSON = EVIDENCE / "sky130-frontend-sense-to-transistor-op-handoff.json"
OUT_MD = EVIDENCE / "sky130-frontend-sense-to-transistor-op-handoff.md"
NGSPICE_TIMEOUT_S = 60


@dataclass(frozen=True)
class Case:
    reset_mode: str
    input_diff_mv: float
    sense_diff_v: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_op_node(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.match(rf"\s*{re.escape(name)}\s+([-+0-9.eE]+)\s*$", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice OP node {name!r}, found none")
    return values[-1]


def build_deck(case: Case) -> str:
    sense_p = 0.9 + case.sense_diff_v / 2.0
    sense_n = 0.9 - case.sense_diff_v / 2.0
    return f"""* Frontend-sense to Sky130 transistor OP handoff.
* This uses the measured extracted-frontend sense voltage as DC input to the real Sky130 input pair.
* It does not include the extracted frontend transient, latch, SAR loop, or accepted converter payload.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param rd=100k
.param itail=20u
.options reltol=1e-4 abstol=1e-14 vntol=1e-8 gmin=1e-12

VDD vdd 0 {{vdd}}
VINP inp 0 {sense_p:.12f}
VINN inn 0 {sense_n:.12f}
RDP vdd outp {{rd}}
RDN vdd outn {{rd}}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
ITAIL tail 0 {{itail}}
COUTP outp 0 2f
COUTN outn 0 2f

.op
.control
op
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.input_diff_mv > 0 else -1
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
        return {
            "reset_mode": case.reset_mode,
            "input_diff_mv": case.input_diff_mv,
            "sense_diff_v": case.sense_diff_v,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "sign_preserved": False,
            "output_margin_pass": False,
        }
    if result.returncode != 0:
        return {
            "reset_mode": case.reset_mode,
            "input_diff_mv": case.input_diff_mv,
            "sense_diff_v": case.sense_diff_v,
            "ngspice_returncode": result.returncode,
            "ngspice_timed_out": False,
            "error_excerpt": (result.stdout + result.stderr)[-1200:],
            "sign_preserved": False,
            "output_margin_pass": False,
        }
    outp_v = read_op_node(result.stdout, "outp")
    outn_v = read_op_node(result.stdout, "outn")
    tail_v = read_op_node(result.stdout, "tail")
    output_diff_v = outn_v - outp_v
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    gain = output_diff_v / case.sense_diff_v if case.sense_diff_v else 0.0
    return {
        "reset_mode": case.reset_mode,
        "input_diff_mv": case.input_diff_mv,
        "sense_diff_v": case.sense_diff_v,
        "outp_v": outp_v,
        "outn_v": outn_v,
        "tail_v": tail_v,
        "output_diff_v": output_diff_v,
        "sense_to_output_gain_v_per_v": gain,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "sign_preserved": measured_sign == expected_sign,
        "output_margin_pass": abs(output_diff_v) >= 0.0005,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    frontend = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    transistor = json.loads(SOURCE_TRANSISTOR.read_text(encoding="utf-8"))
    probe = json.loads(SOURCE_PROBE.read_text(encoding="utf-8"))
    rows = [
        run_case(Case(row["reset_mode"], row["input_diff_mv"], row["sense_diff_after_v"]))
        for row in frontend["rows"]
    ]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    sign_pass_count = sum(1 for row in rows if row["sign_preserved"])
    margin_pass_count = sum(1 for row in rows if row["output_margin_pass"])
    passed = len(measured) == len(rows) and sign_pass_count == len(rows) and margin_pass_count == len(rows)
    return {
        "result_type": "sky130_frontend_sense_to_transistor_op_handoff",
        "status": "frontend_sense_to_transistor_op_handoff_passed_not_transient_or_strict_evidence" if passed else "frontend_sense_to_transistor_op_handoff_failed",
        "source_frontend": rel(SOURCE_FRONTEND),
        "source_standalone_transistor": rel(SOURCE_TRANSISTOR),
        "source_probe_ladder": rel(SOURCE_PROBE),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_measured_frontend_sense_voltage": True,
        "uses_sky130_transistor_input_stage": True,
        "uses_extracted_frontend_transient": False,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "sign_pass_count": sign_pass_count,
        "output_margin_pass_count": margin_pass_count,
        "minimum_abs_output_diff_v": min((abs(row["output_diff_v"]) for row in measured), default=0.0),
        "minimum_gain_v_per_v": min((abs(row["sense_to_output_gain_v_per_v"]) for row in measured), default=0.0),
        "standalone_input_stage_gain_v_per_v": transistor["rows"][1]["gain_v_per_v"],
        "probe_ladder_measured_probe_count": probe["measured_probe_count"],
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "uses measured extracted-frontend sense voltages as DC inputs to a real Sky130 transistor input pair and checks sign, output margin, and operating point",
            "not_allowed": "does not prove the full extracted-frontend transient handoff, latch behavior, SAR conversion, post-layout energy, or accepted converter evidence",
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
        "# Sky130 Frontend Sense To Transistor OP Handoff",
        "",
        f"- status: `{report['status']}`",
        f"- uses measured frontend sense voltage: `{report['uses_measured_frontend_sense_voltage']}`",
        f"- uses Sky130 transistor input stage: `{report['uses_sky130_transistor_input_stage']}`",
        f"- uses extracted frontend transient: `{report['uses_extracted_frontend_transient']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- output margin pass count: `{report['output_margin_pass_count']}`",
        f"- minimum abs output diff V: `{report['minimum_abs_output_diff_v']:.9e}`",
        f"- minimum gain V/V: `{report['minimum_gain_v_per_v']:.6f}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The full transient handoff joins two hard things: an extracted floating-capacitance frontend and real transistor device equations. This OP handoff removes the frontend transient and asks one narrower question: when the transistor pair sees the measured frontend sense voltage as a steady input, does it produce the right output sign and enough output difference?",
        "",
        "If this passes while the full transient times out, the immediate blocker is not transistor gain at the measured sense voltage. The blocker is the dynamic handoff: how the frontend nodes, transistor gates, bias path, and solver move together in time.",
        "",
        "## Results",
        "",
        "| reset mode | input diff mV | sense diff uV | output diff mV | gain V/V | sign preserved | margin pass |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if row.get("ngspice_returncode") != 0 or row.get("ngspice_timed_out"):
            lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | failed | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row['sense_diff_v'] * 1_000_000.0:.6f}` | `{row['output_diff_v'] * 1000.0:.6f}` | `{row['sense_to_output_gain_v_per_v']:.6f}` | `{row['sign_preserved']}` | `{row['output_margin_pass']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_frontend_sense_to_transistor_op_handoff")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"output_margin_pass_count,{report['output_margin_pass_count']}")
    print(f"minimum_abs_output_diff_v,{report['minimum_abs_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
