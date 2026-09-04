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
KNOWN = EVIDENCE / "sky130-comparator-input-stage-ngspice.json"
RAMP = EVIDENCE / "sky130-frontend-sense-to-transistor-ramp-startup.json"
DECK_OUT = SPICE_DIR / "sky130_preamp_known_good_reproduction.sp"
CSV_OUT = MEASUREMENTS / "sky130-preamp-known-good-reproduction.csv"
OUT_JSON = EVIDENCE / "sky130-preamp-known-good-reproduction.json"
OUT_MD = EVIDENCE / "sky130-preamp-known-good-reproduction.md"
NGSPICE_TIMEOUT_S = 120


@dataclass(frozen=True)
class Case:
    name: str
    diff_v: float
    source: str


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
    vinp = 0.9 + case.diff_v / 2.0
    vinn = 0.9 - case.diff_v / 2.0
    return f"""* Sky130 preamp known-good reproduction.
* This reproduces the passing comparator input-stage deck shape.
* It is not extracted layout, not a latch, and not accepted converter evidence.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}
.param rd=100k
.param itail=20u

VDD vdd 0 {{vdd}}
VINP inp 0 {{vinp}}
VINN inn 0 {{vinn}}
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
    expected_sign = 1 if case.diff_v > 0 else -1 if case.diff_v < 0 else 0
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
            "case": case.name,
            "source": case.source,
            "input_diff_v": case.diff_v,
            "input_diff_mv": case.diff_v * 1000.0,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "op_measured": False,
            "polarity_correct": False,
        }
    out: dict[str, Any] = {
        "case": case.name,
        "source": case.source,
        "input_diff_v": case.diff_v,
        "input_diff_mv": case.diff_v * 1000.0,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "op_measured": result.returncode == 0,
    }
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        out["polarity_correct"] = False
        return out
    outp_v = read_op_node(result.stdout, "outp")
    outn_v = read_op_node(result.stdout, "outn")
    output_diff_v = outn_v - outp_v
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    out.update(
        {
            "outp_v": outp_v,
            "outn_v": outn_v,
            "tail_v": read_op_node(result.stdout, "tail"),
            "output_diff_v": output_diff_v,
            "gain_v_per_v": output_diff_v / case.diff_v if case.diff_v else None,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "polarity_correct": measured_sign == expected_sign,
        }
    )
    return out


def build_cases() -> list[Case]:
    known = json.loads(KNOWN.read_text(encoding="utf-8"))
    known_target = next(row for row in known["rows"] if row["case"] == "positive_target_edge")
    ramp = json.loads(RAMP.read_text(encoding="utf-8"))
    measured_positive = next(row for row in ramp["rows"] if row.get("ramp_startup_measured") and float(row["input_diff_mv"]) > 0)
    return [
        Case("known_good_positive_target_edge", float(known_target["input_diff_mv"]) / 1000.0, rel(KNOWN)),
        Case("measured_frontend_positive_sense_edge", float(measured_positive["sense_diff_v"]), rel(RAMP)),
    ]


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    cases = build_cases()
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row["op_measured"]]
    polarity_pass_count = sum(1 for row in rows if row["polarity_correct"])
    all_pass = len(measured) == len(rows) and polarity_pass_count == len(rows)
    return {
        "result_type": "sky130_preamp_known_good_reproduction",
        "status": "known_good_reproduction_passed_for_known_and_measured_sense_inputs" if all_pass else "known_good_reproduction_failed_or_timed_out",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "source_known_good": rel(KNOWN),
        "source_measured_frontend": rel(RAMP),
        "topology": "same_resistively_loaded_sky130_nfet_differential_pair_with_ideal_tail_bias_as_known_good_input_stage",
        "case_count": len(rows),
        "op_measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "polarity_pass_count": polarity_pass_count,
        "rows": rows,
        "strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "reproduces the known-good Sky130 input-stage deck shape at the prior target input and at the smaller measured frontend sense input",
            "not_allowed": "does not prove extracted frontend loading, a preamp topology change, clocked latch behavior, SAR conversion, layout extraction, DRC/LVS, or accepted converter evidence",
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
        "# Sky130 Preamp Known-Good Reproduction",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- case count: `{report['case_count']}`",
        f"- OP measured case count: `{report['op_measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- polarity pass count: `{report['polarity_pass_count']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A failed larger circuit should be reduced to the smallest circuit that already had evidence. If that smallest circuit no longer runs, the problem is the run setup or the toolchain. If it still runs at the old input and at the smaller measured input, the next problem is loading or topology, not the basic differential pair.",
        "",
        "This test uses the same node names, ideal tail, resistive loads, output capacitors, device size, common-mode voltage, and OP flow as the passing input-stage deck. It changes only the input difference.",
        "",
        "## Cases",
        "",
        "| case | source | input mV | OP measured | output mV | gain V/V | polarity pass |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        output_mv = row.get("output_diff_v")
        gain = row.get("gain_v_per_v")
        lines.append(
            f"| `{row['case']}` | `{row['source']}` | `{row['input_diff_mv']:.9f}` | `{row['op_measured']}` | `{output_mv * 1000.0:.9f}` | `{gain:.6f}` | `{row['polarity_correct']}` |"
            if output_mv is not None and gain is not None
            else f"| `{row['case']}` | `{row['source']}` | `{row['input_diff_mv']:.9f}` | `{row['op_measured']}` | `not measured` | `not measured` | `{row['polarity_correct']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_preamp_known_good_reproduction")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"op_measured_case_count,{report['op_measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"polarity_pass_count,{report['polarity_pass_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
