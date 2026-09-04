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
OP_JSON = EVIDENCE / "sky130-known-good-shape-preamp-op-latch-debug.json"
DECK_OUT = SPICE_DIR / "sky130_known_good_shape_preamp_transient_latch_debug.sp"
CSV_OUT = MEASUREMENTS / "sky130-known-good-shape-preamp-transient-latch-debug.csv"
OUT_JSON = EVIDENCE / "sky130-known-good-shape-preamp-transient-latch-debug.json"
OUT_MD = EVIDENCE / "sky130-known-good-shape-preamp-transient-latch-debug.md"
NGSPICE_TIMEOUT_S = 120
OUTPUT_MARGIN_TARGET_V = 0.0005


@dataclass(frozen=True)
class Case:
    name: str
    diff_mv: float
    outp_ic: float
    outn_ic: float
    tail_ic: float


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
    return f"""* Sky130 known-good-shape preamp transient latch debug.
* Same simple OP-passing preamp shape, no latch attached.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}
.param rd=100k
.param itail=20u
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {{vdd}}
VINP inp 0 PWL(0 0.9 100p 0.9 500p {{vinp}} 2n {{vinp}})
VINN inn 0 PWL(0 0.9 100p 0.9 500p {{vinn}} 2n {{vinn}})
RDP vdd outp {{rd}}
RDN vdd outn {{rd}}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
ITAIL tail 0 {{itail}}
COUTP outp 0 2f
COUTN outn 0 2f

.ic v(outp)={case.outp_ic:.12f} v(outn)={case.outn_ic:.12f} v(tail)={case.tail_ic:.12f}
.tran 20p 2n uic
.measure tran outp_1p2n_v FIND v(outp) AT=1.20n
.measure tran outn_1p2n_v FIND v(outn) AT=1.20n
.measure tran outp_1p6n_v FIND v(outp) AT=1.60n
.measure tran outn_1p6n_v FIND v(outn) AT=1.60n
.measure tran outp_2n_v FIND v(outp) AT=2.00n
.measure tran outn_2n_v FIND v(outn) AT=2.00n
.measure tran tail_2n_v FIND v(tail) AT=2.00n
.control
set noaskquit
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    print(f"case,{case.name}", flush=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.diff_mv > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"case": case.name, "input_diff_mv": case.diff_mv, "measured": False, "ngspice_timed_out": True, "ngspice_returncode": None, "sign_preserved": False, "output_margin_pass": False}
    row: dict[str, Any] = {"case": case.name, "input_diff_mv": case.diff_mv, "measured": result.returncode == 0, "ngspice_timed_out": False, "ngspice_returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        row["sign_preserved"] = False
        row["output_margin_pass"] = False
        return row
    outp_12 = read_measure(result.stdout, "outp_1p2n_v")
    outn_12 = read_measure(result.stdout, "outn_1p2n_v")
    outp_16 = read_measure(result.stdout, "outp_1p6n_v")
    outn_16 = read_measure(result.stdout, "outn_1p6n_v")
    outp_20 = read_measure(result.stdout, "outp_2n_v")
    outn_20 = read_measure(result.stdout, "outn_2n_v")
    diff_12 = outn_12 - outp_12
    diff_16 = outn_16 - outp_16
    diff_20 = outn_20 - outp_20
    measured_sign = 1 if diff_20 > 0 else -1 if diff_20 < 0 else 0
    settling_delta = abs(diff_20 - diff_16)
    row.update(
        {
            "outp_1p2n_v": outp_12,
            "outn_1p2n_v": outn_12,
            "outp_1p6n_v": outp_16,
            "outn_1p6n_v": outn_16,
            "outp_2n_v": outp_20,
            "outn_2n_v": outn_20,
            "tail_2n_v": read_measure(result.stdout, "tail_2n_v"),
            "preamp_diff_1p2n_v": diff_12,
            "preamp_diff_1p6n_v": diff_16,
            "preamp_diff_2n_v": diff_20,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(diff_20) >= OUTPUT_MARGIN_TARGET_V,
            "settling_delta_1p6n_to_2n_v": settling_delta,
            "settled_enough_for_latch_debug": settling_delta <= max(abs(diff_20) * 0.05, 1e-6),
            "gain_v_per_v": diff_20 / (case.diff_mv / 1000.0),
        }
    )
    return row


def build_cases(op: dict[str, Any]) -> list[Case]:
    cases: list[Case] = []
    for row in op["rows"]:
        cases.append(Case(row["case"], float(row["input_diff_mv"]), float(row["outp_v"]), float(row["outn_v"]), float(row["tail_v"])))
    return cases


def build_report() -> dict[str, Any]:
    op = json.loads(OP_JSON.read_text(encoding="utf-8"))
    rows = [run_case(case) for case in build_cases(op)]
    measured = [row for row in rows if row["measured"]]
    sign_pass = sum(1 for row in rows if row.get("sign_preserved"))
    margin_pass = sum(1 for row in rows if row.get("output_margin_pass"))
    settled_pass = sum(1 for row in rows if row.get("settled_enough_for_latch_debug"))
    passed = len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows) and settled_pass == len(rows)
    return {
        "result_type": "sky130_known_good_shape_preamp_transient_latch_debug",
        "status": "known_good_shape_preamp_transient_passed_ready_for_latch_alone" if passed else "known_good_shape_preamp_transient_failed",
        "source_op_debug": rel(OP_JSON),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "sign_pass_count": sign_pass,
        "output_margin_pass_count": margin_pass,
        "settled_case_count": settled_pass,
        "minimum_abs_preamp_output_diff_v": min((abs(row["preamp_diff_2n_v"]) for row in measured), default=0.0),
        "maximum_settling_delta_1p6n_to_2n_v": max((row["settling_delta_1p6n_to_2n_v"] for row in measured), default=None),
        "output_margin_target_v": OUTPUT_MARGIN_TARGET_V,
        "uses_known_good_op_initial_point": True,
        "uses_regenerative_latch": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "checks whether the OP-passing preamp shape also settles in transient from its measured OP initial point before latch reconnection",
            "not_allowed": "does not prove latch resolution, kickback, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
        },
    }


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def write_outputs(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Known-Good-Shape Preamp Transient Latch Debug",
        "",
        f"- status: `{report['status']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- output margin pass count: `{report['output_margin_pass_count']}`",
        f"- settled case count: `{report['settled_case_count']}`",
        f"- minimum abs preamp output diff V: `{report['minimum_abs_preamp_output_diff_v']:.9e}`",
        f"- maximum settling delta 1.6ns to 2.0ns V: `{fmt(report['maximum_settling_delta_1p6n_to_2n_v'])}`",
        f"- uses known-good OP initial point: `{report['uses_known_good_op_initial_point']}`",
        f"- uses regenerative latch: `{report['uses_regenerative_latch']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A DC operating point says a circuit has a place to rest. A transient run asks whether the circuit can get there from a stated starting state within the time available before the latch is enabled.",
        "",
        "This run uses the OP-passing preamp shape and starts from the measured OP values. It keeps the latch disconnected. If it passes, the preamp is ready for a latch-alone driven-voltage check. If it fails, transient startup is still the blocker.",
        "",
        "## Results",
        "",
        "| case | measured | diff 1.2ns V | diff 1.6ns V | diff 2.0ns V | sign pass | margin pass | settled |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['case']}` | `{row['measured']}` | `{fmt(row.get('preamp_diff_1p2n_v'))}` | `{fmt(row.get('preamp_diff_1p6n_v'))}` | `{fmt(row.get('preamp_diff_2n_v'))}` | `{row.get('sign_preserved')}` | `{row.get('output_margin_pass')}` | `{row.get('settled_enough_for_latch_debug')}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_known_good_shape_preamp_transient_latch_debug")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"output_margin_pass_count,{report['output_margin_pass_count']}")
    print(f"settled_case_count,{report['settled_case_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
