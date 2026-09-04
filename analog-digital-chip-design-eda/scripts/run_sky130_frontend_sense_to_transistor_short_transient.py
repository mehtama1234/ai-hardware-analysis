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
SOURCE_OP = EVIDENCE / "sky130-frontend-sense-to-transistor-op-handoff.json"
DECK_OUT = SPICE_DIR / "sky130_frontend_sense_to_transistor_short_transient.sp"
CSV_OUT = MEASUREMENTS / "sky130-frontend-sense-to-transistor-short-transient.csv"
OUT_JSON = EVIDENCE / "sky130-frontend-sense-to-transistor-short-transient.json"
OUT_MD = EVIDENCE / "sky130-frontend-sense-to-transistor-short-transient.md"
NGSPICE_TIMEOUT_S = 45


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


def build_deck(row: dict[str, Any]) -> str:
    sense_diff_v = float(row["sense_diff_v"])
    sense_p = 0.9 + sense_diff_v / 2.0
    sense_n = 0.9 - sense_diff_v / 2.0
    outp_ic = float(row["outp_v"])
    outn_ic = float(row["outn_v"])
    tail_ic = float(row["tail_v"])
    return f"""* Frontend-sense to Sky130 transistor short transient.
* Starts from the measured OP point and runs only a short local transient.
* This is not the full extracted frontend transient, latch, SAR, or accepted converter evidence.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param rd=100k
.param itail=20u
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

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

.ic v(outp)={outp_ic:.12f} v(outn)={outn_ic:.12f} v(tail)={tail_ic:.12f}
.tran 100p 500p uic
.measure tran outp_end_v FIND v(outp) AT=500p
.measure tran outn_end_v FIND v(outn) AT=500p
.measure tran tail_end_v FIND v(tail) AT=500p
.control
set noaskquit
run
.endc
.end
"""


def run_case(row: dict[str, Any]) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row), encoding="utf-8")
    expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
    try:
        result = subprocess.run(
            ["timeout", f"{NGSPICE_TIMEOUT_S}s", "ngspice", "-b", str(DECK_OUT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=NGSPICE_TIMEOUT_S + 3,
        )
    except subprocess.TimeoutExpired:
        return {
            "reset_mode": row["reset_mode"],
            "input_diff_mv": row["input_diff_mv"],
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "short_transient_measured": False,
            "sign_preserved": False,
            "output_margin_pass": False,
        }
    result_row: dict[str, Any] = {
        "reset_mode": row["reset_mode"],
        "input_diff_mv": row["input_diff_mv"],
        "sense_diff_v": row["sense_diff_v"],
        "source_op_output_diff_v": row["output_diff_v"],
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": result.returncode == 124,
        "short_transient_measured": result.returncode == 0,
    }
    if result.returncode != 0:
        result_row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        result_row["sign_preserved"] = False
        result_row["output_margin_pass"] = False
        return result_row
    outp_v = read_measure(result.stdout, "outp_end_v")
    outn_v = read_measure(result.stdout, "outn_end_v")
    tail_v = read_measure(result.stdout, "tail_end_v")
    output_diff_v = outn_v - outp_v
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    result_row.update(
        {
            "outp_end_v": outp_v,
            "outn_end_v": outn_v,
            "tail_end_v": tail_v,
            "output_diff_v": output_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(output_diff_v) >= 0.0005,
            "output_retention_ratio": abs(output_diff_v) / abs(float(row["output_diff_v"])) if row["output_diff_v"] else 0.0,
        }
    )
    return result_row


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    source = json.loads(SOURCE_OP.read_text(encoding="utf-8"))
    source_rows = [row for row in source["rows"] if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    rows = [run_case(row) for row in source_rows]
    measured = [row for row in rows if row["short_transient_measured"]]
    sign_pass = sum(1 for row in rows if row["sign_preserved"])
    margin_pass = sum(1 for row in rows if row["output_margin_pass"])
    passed = len(rows) > 0 and len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows)
    return {
        "result_type": "sky130_frontend_sense_to_transistor_short_transient",
        "status": "frontend_sense_to_transistor_short_transient_passed_not_full_handoff_or_strict_evidence" if passed else "frontend_sense_to_transistor_short_transient_failed",
        "source_op_handoff": rel(SOURCE_OP),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_measured_frontend_sense_voltage": True,
        "uses_sky130_transistor_input_stage": True,
        "uses_op_initial_conditions": True,
        "uses_extracted_frontend_transient": False,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "sign_pass_count": sign_pass,
        "output_margin_pass_count": margin_pass,
        "minimum_abs_output_diff_v": min((abs(row["output_diff_v"]) for row in measured), default=0.0),
        "minimum_output_retention_ratio": min((row["output_retention_ratio"] for row in measured), default=0.0),
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "runs a short local transient from the measured OP state for the Sky130 input pair at measured frontend sense voltage",
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
        "# Sky130 Frontend Sense To Transistor Short Transient",
        "",
        f"- status: `{report['status']}`",
        f"- uses measured frontend sense voltage: `{report['uses_measured_frontend_sense_voltage']}`",
        f"- uses Sky130 transistor input stage: `{report['uses_sky130_transistor_input_stage']}`",
        f"- uses OP initial conditions: `{report['uses_op_initial_conditions']}`",
        f"- uses extracted frontend transient: `{report['uses_extracted_frontend_transient']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- output margin pass count: `{report['output_margin_pass_count']}`",
        f"- minimum abs output diff V: `{report['minimum_abs_output_diff_v']:.9e}`",
        f"- minimum output retention ratio: `{report['minimum_output_retention_ratio']:.6f}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The OP handoff proves a static point. The full handoff asks for a moving extracted frontend and transistor stage together. This short transient sits between them: it starts the transistor pair at the measured OP state and asks whether the output sign and margin survive a small time step.",
        "",
        "If this passes, the transistor pair can hold the measured frontend sense voltage dynamically once it is already at the right operating point. The remaining hard problem is then startup and coupling from the extracted frontend into that operating point.",
        "",
        "## Results",
        "",
        "| reset mode | input diff mV | output diff mV | retention | sign preserved | margin pass |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if not row["short_transient_measured"]:
            lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row['output_diff_v'] * 1000.0:.6f}` | `{row['output_retention_ratio']:.6f}` | `{row['sign_preserved']}` | `{row['output_margin_pass']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_frontend_sense_to_transistor_short_transient")
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
