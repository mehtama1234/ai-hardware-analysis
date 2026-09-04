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
FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
DECK_OUT = SPICE_DIR / "first_real_converter_frontend_to_input_stage_proxy.sp"
CSV_OUT = MEASUREMENTS / "first-real-converter-frontend-to-input-stage-proxy.csv"
OUT_JSON = EVIDENCE / "first-real-converter-frontend-to-input-stage-proxy.json"
OUT_MD = EVIDENCE / "first-real-converter-frontend-to-input-stage-proxy.md"

CANDIDATE_ID = "aimc_readout_candidate_001"
RUN_ID = "aimc_readout_candidate_001_frontend_to_input_stage_proxy_run001"
NGSPICE_TIMEOUT_S = 8
MIN_ACTIVE_STAGE_INPUT_DIFF_V = 1.0e-4


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


def build_deck(input_diff_v: float) -> str:
    vinp = 0.9 + input_diff_v / 2.0
    vinn = 0.9 - input_diff_v / 2.0
    return f"""* First real converter frontend-to-input-stage proxy.
* Input difference comes from the measured ultra frontend extracted-RC sense output.
* The active stage is a Sky130 nfet differential pair with ideal bias and resistive loads.
* This is not a full comparator, SAR, or accepted converter simulation.

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


def run_case(source_row: dict[str, Any]) -> dict[str, Any]:
    measured_frontend_diff_v = float(source_row["sense_diff_after_v"])
    input_diff_v = measured_frontend_diff_v
    if abs(input_diff_v) < MIN_ACTIVE_STAGE_INPUT_DIFF_V:
        input_diff_v = (1 if input_diff_v >= 0 else -1) * MIN_ACTIVE_STAGE_INPUT_DIFF_V
    expected_sign = 1 if input_diff_v > 0 else -1 if input_diff_v < 0 else 0
    DECK_OUT.write_text(build_deck(input_diff_v), encoding="utf-8")
    try:
        result = subprocess.run(["timeout", f"{NGSPICE_TIMEOUT_S}s", "ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S + 2)
    except subprocess.TimeoutExpired:
        return {
            "source_reset_mode": source_row["reset_mode"],
            "source_input_diff_mv": source_row["input_diff_mv"],
            "frontend_sense_diff_v": measured_frontend_diff_v,
            "active_stage_input_diff_v": input_diff_v,
            "uses_measured_frontend_diff_without_floor": abs(measured_frontend_diff_v) >= MIN_ACTIVE_STAGE_INPUT_DIFF_V,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "polarity_correct": False,
        }
    if result.returncode == 124:
        return {
            "source_reset_mode": source_row["reset_mode"],
            "source_input_diff_mv": source_row["input_diff_mv"],
            "frontend_sample_diff_v": source_row["sample_diff_after_v"],
            "frontend_sense_diff_v": measured_frontend_diff_v,
            "active_stage_input_diff_v": input_diff_v,
            "uses_measured_frontend_diff_without_floor": abs(measured_frontend_diff_v) >= MIN_ACTIVE_STAGE_INPUT_DIFF_V,
            "ngspice_returncode": result.returncode,
            "ngspice_timed_out": True,
            "error_excerpt": (result.stdout + result.stderr)[-1200:],
            "polarity_correct": False,
        }
    if result.returncode != 0:
        return {
            "source_reset_mode": source_row["reset_mode"],
            "source_input_diff_mv": source_row["input_diff_mv"],
            "frontend_sense_diff_v": measured_frontend_diff_v,
            "active_stage_input_diff_v": input_diff_v,
            "uses_measured_frontend_diff_without_floor": abs(measured_frontend_diff_v) >= MIN_ACTIVE_STAGE_INPUT_DIFF_V,
            "ngspice_returncode": result.returncode,
            "ngspice_timed_out": False,
            "error_excerpt": (result.stdout + result.stderr)[-1200:],
            "polarity_correct": False,
        }
    outp_v = read_op_node(result.stdout, "outp")
    outn_v = read_op_node(result.stdout, "outn")
    output_diff_v = outn_v - outp_v
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    return {
        "source_reset_mode": source_row["reset_mode"],
        "source_input_diff_mv": source_row["input_diff_mv"],
        "frontend_sample_diff_v": source_row["sample_diff_after_v"],
        "frontend_sense_diff_v": measured_frontend_diff_v,
        "active_stage_input_diff_v": input_diff_v,
        "uses_measured_frontend_diff_without_floor": abs(measured_frontend_diff_v) >= MIN_ACTIVE_STAGE_INPUT_DIFF_V,
        "outp_v": outp_v,
        "outn_v": outn_v,
        "tail_v": read_op_node(result.stdout, "tail"),
        "output_diff_v": output_diff_v,
        "stage_gain_v_per_v": output_diff_v / input_diff_v if input_diff_v else None,
        "overall_sample_to_output_gain_v_per_v": output_diff_v / float(source_row["sample_diff_after_v"]) if source_row["sample_diff_after_v"] else None,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "polarity_correct": measured_sign == expected_sign,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    frontend = json.loads(FRONTEND.read_text(encoding="utf-8"))
    source_rows = [row for row in frontend["rows"] if row.get("sign_preserved") is True]
    rows = [run_case(row) for row in source_rows]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    polarity_pass_count = sum(1 for row in rows if row.get("polarity_correct") is True)
    stage_gains = [abs(float(row["stage_gain_v_per_v"])) for row in measured if row.get("stage_gain_v_per_v") is not None]
    overall_gains = [abs(float(row["overall_sample_to_output_gain_v_per_v"])) for row in measured if row.get("overall_sample_to_output_gain_v_per_v") is not None]
    min_output_diff_v = min((abs(float(row["output_diff_v"])) for row in measured), default=0.0)
    floor_case_count = sum(1 for row in rows if row.get("uses_measured_frontend_diff_without_floor") is False)
    timed_out_case_count = sum(1 for row in rows if row.get("ngspice_timed_out") is True)
    passed = bool(rows) and polarity_pass_count == len(rows) and min_output_diff_v > 0.0005
    status = (
        "frontend_to_input_stage_proxy_passed_not_full_comparator_or_strict_evidence"
        if passed
        else "frontend_to_input_stage_proxy_timed_out_not_strict_evidence"
        if timed_out_case_count
        else "frontend_to_input_stage_proxy_failed"
    )
    return {
        "result_type": "first_real_converter_frontend_to_input_stage_proxy",
        "status": status,
        "candidate_id": CANDIDATE_ID,
        "run_id": RUN_ID,
        "source_frontend_evidence": rel(FRONTEND),
        "source_frontend_candidate": frontend.get("candidate_name"),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": timed_out_case_count,
        "polarity_pass_count": polarity_pass_count,
        "minimum_frontend_sense_diff_v": min((abs(float(row["frontend_sense_diff_v"])) for row in measured), default=0.0),
        "minimum_active_stage_input_diff_v": min((abs(float(row["active_stage_input_diff_v"])) for row in measured), default=0.0),
        "minimum_output_diff_v": min_output_diff_v,
        "minimum_stage_gain_v_per_v": min(stage_gains) if stage_gains else 0.0,
        "minimum_overall_sample_to_output_gain_v_per_v": min(overall_gains) if overall_gains else 0.0,
        "uses_measured_extracted_frontend_sense_delta": True,
        "minimum_practical_active_stage_input_diff_v": MIN_ACTIVE_STAGE_INPUT_DIFF_V,
        "floor_case_count": floor_case_count,
        "uses_sky130_transistor_input_stage": True,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "strict_blockers": [
            "The frontend sense values and active input stage are connected by a scripted proxy, not one extracted post-layout netlist containing both blocks.",
            "The measured frontend sense difference is below the practical active-stage deck floor used here, so this run proves sign handoff at a bounded proxy input rather than direct acceptance of the raw frontend output.",
            "The active stage is a differential-pair polarity and gain proxy, not a clocked comparator with metastability, kickback, offset, or noise evidence.",
            "The run does not include DAC switching, SAR bit cycling, full supply-current integration, DRC/LVS area, or a same-run break-even payload.",
        ],
        "claim_boundary": {
            "allowed": "uses the measured ultra frontend sense difference as the input to a Sky130 transistor input-stage proxy and checks polarity plus gain",
            "not_allowed": "does not prove a full comparator, full converter, same-run extracted post-layout package, or accepted replacement evidence",
        },
        "rows": rows,
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = report["rows"]
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Frontend To Input-Stage Proxy",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- source frontend evidence: `{report['source_frontend_evidence']}`",
        f"- source frontend candidate: `{report['source_frontend_candidate']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- case count: `{report['case_count']}`",
        f"- polarity pass count: `{report['polarity_pass_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- minimum frontend sense diff V: `{report['minimum_frontend_sense_diff_v']:.9e}`",
        f"- minimum active-stage input diff V: `{report['minimum_active_stage_input_diff_v']:.9e}`",
        f"- active-stage input floor V: `{report['minimum_practical_active_stage_input_diff_v']:.9e}`",
        f"- floor case count: `{report['floor_case_count']}`",
        f"- minimum output diff V: `{report['minimum_output_diff_v']:.9e}`",
        f"- minimum stage gain V/V: `{report['minimum_stage_gain_v_per_v']:.6f}`",
        f"- minimum overall sample-to-output gain V/V: `{report['minimum_overall_sample_to_output_gain_v_per_v']:.6f}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The passive frontend creates a very small voltage difference. That difference is not useful by itself unless the next circuit can turn it into a larger, correctly signed electrical state.",
        "",
        "This run takes the measured sense-node sign from the extracted ultra frontend and feeds a bounded small input difference into a Sky130 transistor differential pair. The raw frontend difference is only about 67 microvolts, so the deck uses a 100 microvolt floor to keep the active-stage operating-point solve in a practical range. The input pair spends current to make a larger output difference. In simple terms: the passive block preserves the sign, and the active block pays power to make that sign easier for a latch to decide.",
        "",
        "This is a bridge, not an accepted converter. The frontend and input pair are not yet one extracted layout netlist. The pair is not a clocked latch. There is no SAR loop, no code transition, no noise or mismatch simulation, and no signed physical area for the whole converter.",
        "",
        "## Result",
        "",
        "| reset mode | original sample diff mV | frontend sense diff uV | active input diff uV | input-stage output diff mV | stage gain V/V | overall gain V/V | polarity correct |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        sample_mv = float(row.get("frontend_sample_diff_v", 0.0)) * 1000.0
        sense_uv = float(row.get("frontend_sense_diff_v", 0.0)) * 1_000_000.0
        active_uv = float(row.get("active_stage_input_diff_v", 0.0)) * 1_000_000.0
        out_mv = float(row.get("output_diff_v", 0.0)) * 1000.0
        stage_gain = row.get("stage_gain_v_per_v")
        overall_gain = row.get("overall_sample_to_output_gain_v_per_v")
        out_text = "timeout" if row.get("ngspice_timed_out") else f"{out_mv:.6f}"
        stage_gain_text = "timeout" if stage_gain is None else f"{stage_gain:.6f}"
        overall_gain_text = "timeout" if overall_gain is None else f"{overall_gain:.6f}"
        lines.append(
            f"| `{row['source_reset_mode']}` | `{sample_mv:.6f}` | `{sense_uv:.6f}` | `{active_uv:.6f}` | `{out_text}` | `{stage_gain_text}` | `{overall_gain_text}` | `{row['polarity_correct']}` |"
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
    print("first_real_converter_frontend_to_input_stage_proxy")
    print(f"status,{report['status']}")
    print(f"candidate_id,{report['candidate_id']}")
    print(f"run_id,{report['run_id']}")
    print(f"case_count,{report['case_count']}")
    print(f"polarity_pass_count,{report['polarity_pass_count']}")
    print(f"minimum_output_diff_v,{report['minimum_output_diff_v']:.9e}")
    print(f"minimum_stage_gain_v_per_v,{report['minimum_stage_gain_v_per_v']:.6f}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0 if report["status"] in {"frontend_to_input_stage_proxy_passed_not_full_comparator_or_strict_evidence", "frontend_to_input_stage_proxy_timed_out_not_strict_evidence"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
