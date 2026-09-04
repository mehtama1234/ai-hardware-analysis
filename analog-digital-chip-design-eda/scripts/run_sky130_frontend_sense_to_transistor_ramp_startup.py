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
SOURCE_SHORT = EVIDENCE / "sky130-frontend-sense-to-transistor-short-transient.json"
DECK_OUT = SPICE_DIR / "sky130_frontend_sense_to_transistor_ramp_startup.sp"
CSV_OUT = MEASUREMENTS / "sky130-frontend-sense-to-transistor-ramp-startup.csv"
OUT_JSON = EVIDENCE / "sky130-frontend-sense-to-transistor-ramp-startup.json"
OUT_MD = EVIDENCE / "sky130-frontend-sense-to-transistor-ramp-startup.md"
NGSPICE_TIMEOUT_S = 60


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
    return f"""* Frontend-sense to Sky130 transistor ramp-startup handoff.
* Inputs ramp from common-mode to the measured extracted-frontend sense voltage.
* This does not include the extracted frontend transient, latch, SAR, or accepted converter evidence.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param rd=100k
.param itail=20u
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {{vdd}}
VINP inp 0 PWL(0 0.9 100p 0.9 700p {sense_p:.12f} 2n {sense_p:.12f})
VINN inn 0 PWL(0 0.9 100p 0.9 700p {sense_n:.12f} 2n {sense_n:.12f})
RDP vdd outp {{rd}}
RDN vdd outn {{rd}}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
ITAIL tail 0 {{itail}}
COUTP outp 0 2f
COUTN outn 0 2f

.ic v(outp)=0.8 v(outn)=0.8 v(tail)=0.231
.tran 100p 2n uic
.measure tran outp_end_v FIND v(outp) AT=2n
.measure tran outn_end_v FIND v(outn) AT=2n
.measure tran tail_end_v FIND v(tail) AT=2n
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
            "sense_diff_v": row["sense_diff_v"],
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ramp_startup_measured": False,
            "sign_preserved": False,
            "output_margin_pass": False,
        }
    out: dict[str, Any] = {
        "reset_mode": row["reset_mode"],
        "input_diff_mv": row["input_diff_mv"],
        "sense_diff_v": row["sense_diff_v"],
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": result.returncode == 124,
        "ramp_startup_measured": result.returncode == 0,
    }
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        out["sign_preserved"] = False
        out["output_margin_pass"] = False
        return out
    outp_v = read_measure(result.stdout, "outp_end_v")
    outn_v = read_measure(result.stdout, "outn_end_v")
    tail_v = read_measure(result.stdout, "tail_end_v")
    output_diff_v = outn_v - outp_v
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    out.update(
        {
            "outp_end_v": outp_v,
            "outn_end_v": outn_v,
            "tail_end_v": tail_v,
            "output_diff_v": output_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(output_diff_v) >= 0.0005,
            "sense_to_output_gain_v_per_v": output_diff_v / float(row["sense_diff_v"]),
        }
    )
    return out


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    op = json.loads(SOURCE_OP.read_text(encoding="utf-8"))
    short = json.loads(SOURCE_SHORT.read_text(encoding="utf-8"))
    source_rows = [row for row in op["rows"] if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    rows = [run_case(row) for row in source_rows]
    measured = [row for row in rows if row["ramp_startup_measured"]]
    sign_pass = sum(1 for row in rows if row["sign_preserved"])
    margin_pass = sum(1 for row in rows if row["output_margin_pass"])
    passed = len(rows) > 0 and len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows)
    return {
        "result_type": "sky130_frontend_sense_to_transistor_ramp_startup",
        "status": "frontend_sense_to_transistor_ramp_startup_passed_not_full_handoff_or_strict_evidence" if passed else "frontend_sense_to_transistor_ramp_startup_failed",
        "source_op_handoff": rel(SOURCE_OP),
        "source_short_transient": rel(SOURCE_SHORT),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_measured_frontend_sense_voltage": True,
        "uses_sky130_transistor_input_stage": True,
        "uses_input_ramp_from_common_mode": True,
        "uses_extracted_frontend_transient": False,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "sign_pass_count": sign_pass,
        "output_margin_pass_count": margin_pass,
        "minimum_abs_output_diff_v": min((abs(row["output_diff_v"]) for row in measured), default=0.0),
        "minimum_gain_v_per_v": min((abs(row["sense_to_output_gain_v_per_v"]) for row in measured), default=0.0),
        "source_short_transient_retention_ratio": short["minimum_output_retention_ratio"],
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "ramps real Sky130 transistor input-pair gates from common-mode to measured frontend sense voltages and checks sign, margin, and startup behavior",
            "not_allowed": "does not prove the extracted frontend transient handoff, latch behavior, SAR conversion, post-layout energy, or accepted converter evidence",
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
        "# Sky130 Frontend Sense To Transistor Ramp Startup",
        "",
        f"- status: `{report['status']}`",
        f"- uses measured frontend sense voltage: `{report['uses_measured_frontend_sense_voltage']}`",
        f"- uses Sky130 transistor input stage: `{report['uses_sky130_transistor_input_stage']}`",
        f"- uses input ramp from common mode: `{report['uses_input_ramp_from_common_mode']}`",
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
        "A steady operating point can hide startup problems. This runner starts both transistor inputs at common-mode, then moves them to the measured frontend sense voltages. It asks whether the input pair can acquire the small difference, not merely hold it after being placed there.",
        "",
        "If this passes, the next unsolved object is the extracted frontend coupled into transistor gates during startup. That is closer to the real handoff than the OP and short-hold checks, but it still does not include the extracted frontend transient itself.",
        "",
        "## Results",
        "",
        "| reset mode | input diff mV | output diff mV | gain V/V | sign preserved | margin pass |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if not row["ramp_startup_measured"]:
            lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row['output_diff_v'] * 1000.0:.6f}` | `{row['sense_to_output_gain_v_per_v']:.6f}` | `{row['sign_preserved']}` | `{row['output_margin_pass']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_frontend_sense_to_transistor_ramp_startup")
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
