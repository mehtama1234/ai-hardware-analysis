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
SPEC_JSON = EVIDENCE / "sky130-comparator-acceptance-fixture-spec.json"
FAILED_OP = EVIDENCE / "sky130-preamp-op-latch-debug.json"
KNOWN_GOOD = EVIDENCE / "sky130-preamp-known-good-reproduction.json"
DECK_OUT = SPICE_DIR / "sky130_known_good_shape_preamp_op_latch_debug.sp"
CSV_OUT = MEASUREMENTS / "sky130-known-good-shape-preamp-op-latch-debug.csv"
OUT_JSON = EVIDENCE / "sky130-known-good-shape-preamp-op-latch-debug.json"
OUT_MD = EVIDENCE / "sky130-known-good-shape-preamp-op-latch-debug.md"
NGSPICE_TIMEOUT_S = 120
OUTPUT_MARGIN_TARGET_V = 0.0005


@dataclass(frozen=True)
class Case:
    name: str
    diff_mv: float


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
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Sky130 known-good-shape preamp OP latch debug.
* This keeps the known-good reproduction deck shape and tests both target-edge signs.

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
    print(f"case,{case.name}", flush=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.diff_mv > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"case": case.name, "input_diff_mv": case.diff_mv, "op_measured": False, "ngspice_timed_out": True, "ngspice_returncode": None, "sign_preserved": False, "output_margin_pass": False}
    row: dict[str, Any] = {"case": case.name, "input_diff_mv": case.diff_mv, "op_measured": result.returncode == 0, "ngspice_timed_out": False, "ngspice_returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        row["sign_preserved"] = False
        row["output_margin_pass"] = False
        return row
    outp = read_op_node(result.stdout, "outp")
    outn = read_op_node(result.stdout, "outn")
    diff = outn - outp
    measured_sign = 1 if diff > 0 else -1 if diff < 0 else 0
    row.update(
        {
            "outp_v": outp,
            "outn_v": outn,
            "tail_v": read_op_node(result.stdout, "tail"),
            "preamp_output_diff_v": diff,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(diff) >= OUTPUT_MARGIN_TARGET_V,
            "gain_v_per_v": diff / (case.diff_mv / 1000.0),
        }
    )
    return row


def build_report() -> dict[str, Any]:
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
    failed = json.loads(FAILED_OP.read_text(encoding="utf-8"))
    known = json.loads(KNOWN_GOOD.read_text(encoding="utf-8"))
    target_mv = float(spec["derived_budget"]["target_combined_offset_noise_mv"])
    rows = [run_case(Case("negative_target_edge", -target_mv)), run_case(Case("positive_target_edge", target_mv))]
    measured = [row for row in rows if row["op_measured"]]
    sign_pass = sum(1 for row in rows if row.get("sign_preserved"))
    margin_pass = sum(1 for row in rows if row.get("output_margin_pass"))
    passed = len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows)
    return {
        "result_type": "sky130_known_good_shape_preamp_op_latch_debug",
        "status": "known_good_shape_preamp_op_debug_passed_both_signs" if passed else "known_good_shape_preamp_op_debug_failed",
        "source_failed_op_debug": rel(FAILED_OP),
        "source_known_good_reproduction": rel(KNOWN_GOOD),
        "known_good_status": known["status"],
        "failed_op_status": failed["status"],
        "repair_hypothesis": "keep exact known-good OP deck shape; only extend it to both target-edge signs",
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "op_measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "sign_pass_count": sign_pass,
        "output_margin_pass_count": margin_pass,
        "minimum_abs_preamp_output_diff_v": min((abs(row["preamp_output_diff_v"]) for row in measured), default=0.0),
        "output_margin_target_v": OUTPUT_MARGIN_TARGET_V,
        "uses_known_good_deck_shape": True,
        "uses_transient": False,
        "uses_regenerative_latch": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "checks whether the known-good OP preamp deck shape works for both target-edge signs after the failed renamed-node OP debug",
            "not_allowed": "does not prove transient settling, latch resolution, kickback, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
        },
    }


def write_outputs(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Known-Good-Shape Preamp OP Latch Debug",
        "",
        f"- status: `{report['status']}`",
        f"- known-good status: `{report['known_good_status']}`",
        f"- failed OP status: `{report['failed_op_status']}`",
        f"- repair hypothesis: `{report['repair_hypothesis']}`",
        f"- case count: `{report['case_count']}`",
        f"- OP measured case count: `{report['op_measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- output margin pass count: `{report['output_margin_pass_count']}`",
        f"- minimum abs preamp output diff V: `{report['minimum_abs_preamp_output_diff_v']:.9e}`",
        f"- uses known-good deck shape: `{report['uses_known_good_deck_shape']}`",
        f"- uses transient: `{report['uses_transient']}`",
        f"- uses regenerative latch: `{report['uses_regenerative_latch']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "When a smaller debug deck fails but an older similar deck passes, the first repair is not a new topology. The first repair is to remove accidental differences and keep the exact shape that already worked.",
        "",
        "This run keeps the known-good OP preamp shape and only changes the sign of the target-edge input. If this passes, the preamp DC point is not the real blocker. The earlier OP failure is a deck-shape problem, and the next step is transient startup using the same known-good shape.",
        "",
        "## Results",
        "",
        "| case | OP measured | output diff V | gain V/V | sign pass | margin pass |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        output = row.get("preamp_output_diff_v")
        gain = row.get("gain_v_per_v")
        lines.append(
            f"| `{row['case']}` | `{row['op_measured']}` | `{output:.9e}` | `{gain:.6f}` | `{row.get('sign_preserved')}` | `{row.get('output_margin_pass')}` |"
            if output is not None and gain is not None
            else f"| `{row['case']}` | `{row['op_measured']}` | `not measured` | `not measured` | `{row.get('sign_preserved')}` | `{row.get('output_margin_pass')}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_known_good_shape_preamp_op_latch_debug")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"op_measured_case_count,{report['op_measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"output_margin_pass_count,{report['output_margin_pass_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
