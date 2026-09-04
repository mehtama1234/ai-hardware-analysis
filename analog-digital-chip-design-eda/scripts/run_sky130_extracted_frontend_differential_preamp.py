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
SOURCE_FOLLOWER = EVIDENCE / "sky130-extracted-frontend-source-follower-handoff.json"
DECK_OUT = SPICE_DIR / "sky130_extracted_frontend_differential_preamp.sp"
CSV_OUT = MEASUREMENTS / "sky130-extracted-frontend-differential-preamp.csv"
OUT_JSON = EVIDENCE / "sky130-extracted-frontend-differential-preamp.json"
OUT_MD = EVIDENCE / "sky130-extracted-frontend-differential-preamp.md"
NGSPICE_TIMEOUT_S = 120


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
    diff_v = float(row["input_diff_mv"]) / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Extracted frontend into a biased Sky130 differential preamp.
* The preamp gates read the extracted sense nodes directly.
* This is a first active-preamp probe, not a latch or SAR converter.

.global VSUBS
.lib "{PDK_LIB}" tt
.include "{FRONTEND_NETLIST}"
.param vdd=1.8
.param rd=100k
.param itail=20u
.param win=8.0
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

RDP vdd pre_p {{rd}}
RDN vdd pre_n {{rd}}
XPREP pre_p sense_p tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
XPREN pre_n sense_n tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
ITAIL tail 0 {{itail}}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(sense_p)=0.9 v(sense_n)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(tail)=0.25
.tran 20p 3n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.measure tran tail_after_v FIND v(tail) AT=2.60n
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
            ["ngspice", "-b", str(DECK_OUT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=NGSPICE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return {
            "reset_mode": row["reset_mode"],
            "input_diff_mv": row["input_diff_mv"],
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
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "measured": result.returncode == 0,
    }
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1600:]
        out["sign_preserved"] = False
        out["output_margin_pass"] = False
        return out
    sample_diff_v = read_measure(result.stdout, "sample_p_after_v") - read_measure(result.stdout, "sample_n_after_v")
    sense_diff_v = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    preamp_diff_v = read_measure(result.stdout, "pre_n_after_v") - read_measure(result.stdout, "pre_p_after_v")
    measured_sign = 1 if preamp_diff_v > 0 else -1 if preamp_diff_v < 0 else 0
    out.update(
        {
            "sample_diff_v": sample_diff_v,
            "sense_diff_v": sense_diff_v,
            "preamp_output_diff_v": preamp_diff_v,
            "tail_v": read_measure(result.stdout, "tail_after_v"),
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(preamp_diff_v) >= 0.0005,
            "sample_to_sense_transfer_ratio": abs(sense_diff_v) / abs(sample_diff_v) if sample_diff_v else 0.0,
            "sense_to_preamp_gain_v_per_v": abs(preamp_diff_v) / abs(sense_diff_v) if sense_diff_v else 0.0,
        }
    )
    return out


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    if not FRONTEND_NETLIST.exists():
        raise FileNotFoundError(FRONTEND_NETLIST)
    frontend = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    follower = json.loads(SOURCE_FOLLOWER.read_text(encoding="utf-8"))
    source_rows = [row for row in frontend["rows"] if row["reset_mode"] == "reset_pulse"]
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [run_case(row) for row in source_rows]
    measured = [row for row in rows if row["measured"]]
    sign_pass = sum(1 for row in rows if row["sign_preserved"])
    margin_pass = sum(1 for row in rows if row["output_margin_pass"])
    timed_out = sum(1 for row in rows if row["ngspice_timed_out"])
    passed = len(rows) > 0 and len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows)
    return {
        "result_type": "sky130_extracted_frontend_differential_preamp",
        "status": "differential_preamp_handoff_passed_not_latch_sar_or_strict_evidence" if passed else "differential_preamp_handoff_failed",
        "source_frontend_evidence": rel(SOURCE_FRONTEND),
        "source_source_follower_handoff": rel(SOURCE_FOLLOWER),
        "source_frontend_netlist": rel(FRONTEND_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_extracted_frontend_netlist": True,
        "uses_sky130_differential_preamp": True,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": timed_out,
        "sign_pass_count": sign_pass,
        "output_margin_pass_count": margin_pass,
        "minimum_abs_preamp_output_diff_v": min((abs(row["preamp_output_diff_v"]) for row in measured), default=0.0),
        "minimum_sample_to_sense_transfer_ratio": min((row["sample_to_sense_transfer_ratio"] for row in measured), default=0.0),
        "minimum_sense_to_preamp_gain_v_per_v": min((row["sense_to_preamp_gain_v_per_v"] for row in measured), default=0.0),
        "prior_source_follower_sign_pass_count": follower["sign_pass_count"],
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "tests whether a resistively loaded Sky130 differential preamp can read the extracted frontend sense nodes for two reset-pulse polarities",
            "not_allowed": "does not prove latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence",
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
        "# Sky130 Extracted Frontend Differential Preamp",
        "",
        f"- status: `{report['status']}`",
        f"- uses extracted frontend netlist: `{report['uses_extracted_frontend_netlist']}`",
        f"- uses Sky130 differential preamp: `{report['uses_sky130_differential_preamp']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- output margin pass count: `{report['output_margin_pass_count']}`",
        f"- minimum abs preamp output diff V: `{report['minimum_abs_preamp_output_diff_v']:.9e}`",
        f"- minimum sample-to-sense transfer ratio: `{report['minimum_sample_to_sense_transfer_ratio']:.6f}`",
        f"- minimum sense-to-preamp gain V/V: `{report['minimum_sense_to_preamp_gain_v_per_v']:.6f}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A differential preamp spends current to make the small difference visible before a hard decision. The frontend should only have to move transistor gates. The preamp then converts the small gate-voltage difference into a larger drain-voltage difference.",
        "",
        "This is the first active version after passive gate coupling and a source follower both failed. It asks whether a simple biased pair is enough to make both signs survive at the preamp output.",
        "",
        "## Results",
        "",
        "| reset mode | input diff mV | sense diff uV | preamp output diff mV | sign preserved | margin pass |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if not row["measured"]:
            lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row['sense_diff_v'] * 1e6:.6f}` | `{row['preamp_output_diff_v'] * 1000.0:.6f}` | `{row['sign_preserved']}` | `{row['output_margin_pass']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_extracted_frontend_differential_preamp")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"output_margin_pass_count,{report['output_margin_pass_count']}")
    print(f"minimum_abs_preamp_output_diff_v,{report['minimum_abs_preamp_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
