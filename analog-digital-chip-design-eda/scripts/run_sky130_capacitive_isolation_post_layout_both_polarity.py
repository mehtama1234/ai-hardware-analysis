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
CANDIDATE = EVIDENCE / "candidate-post-layout"
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_capacitive_isolation_frontend_extracted.spice"
MODEL = CANDIDATE / "models" / "sky130-capacitive-isolation-ngspice.includes"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
OUT_JSON = CANDIDATE / "rerun" / "sky130-capacitive-isolation-post-layout-both-polarity.json"
OUT_MD = EVIDENCE / "sky130-capacitive-isolation-post-layout-both-polarity.md"
OUT_CSV = MEASUREMENTS / "sky130-capacitive-isolation-post-layout-both-polarity.csv"
DECK_OUT = SPICE_DIR / "sky130_capacitive_isolation_post_layout_both_polarity.sp"
NGSPICE_TIMEOUT_S = 160


@dataclass(frozen=True)
class Case:
    name: str
    diff_mv: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Sky130 extracted-RC capacitive isolation frontend both-polarity rerun.
* Uses Magic-extracted parasitic frontend subcircuit, then the same schematic latch.

.include "{MODEL}"
.include "{EXTRACTED}"
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param csample=0.2p
.param cload=0.05p
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}

VDD vdd 0 {{vdd}}
VSS vss 0 0
VBIAS vcm 0 0.9
VINP inp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.10n 20p 20p 0.75n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.10n 20p 20p 0.75n 20n)
VCLK clk 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 1.00n 20p 20p 5n 10n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}
CSP sp 0 {{csample}}
CSN sn 0 {{csample}}
CLP sp 0 {{cload}}
CLN sn 0 {{cload}}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

XFRONT vss vdd sp gp clk gn sn sky130_capacitive_isolation_frontend
RBIASP gp vcm 100G
RBIASN gn vcm 100G

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp gp tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn gn tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
COUTP outp 0 5f
COUTN outn 0 5f

.tran 2p 3n
.measure tran sampled_p_before_v FIND v(sp) AT=0.90n
.measure tran sampled_n_before_v FIND v(sn) AT=0.90n
.measure tran sampled_p_after_v FIND v(sp) AT=2.60n
.measure tran sampled_n_after_v FIND v(sn) AT=2.60n
.measure tran gate_p_before_v FIND v(gp) AT=0.90n
.measure tran gate_n_before_v FIND v(gn) AT=0.90n
.measure tran gate_p_after_v FIND v(gp) AT=2.60n
.measure tran gate_n_after_v FIND v(gn) AT=2.60n
.measure tran outp_final_v FIND v(outp) AT=2.60n
.measure tran outn_final_v FIND v(outn) AT=2.60n
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
    expected_sign = 1 if case.diff_mv > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"case": case.name, "input_diff_mv": case.diff_mv, "expected_sign": expected_sign, "ngspice_returncode": None, "ngspice_timed_out": True, "resolved_correct_polarity": False, "kickback_below_half_lsb": False}
    if result.returncode != 0:
        return {"case": case.name, "input_diff_mv": case.diff_mv, "expected_sign": expected_sign, "ngspice_returncode": result.returncode, "ngspice_timed_out": False, "ngspice_error_excerpt": (result.stdout + result.stderr)[-1200:], "resolved_correct_polarity": False, "kickback_below_half_lsb": False}
    sampled_p_before = read_measure(result.stdout, "sampled_p_before_v")
    sampled_n_before = read_measure(result.stdout, "sampled_n_before_v")
    sampled_p_after = read_measure(result.stdout, "sampled_p_after_v")
    sampled_n_after = read_measure(result.stdout, "sampled_n_after_v")
    gate_p_before = read_measure(result.stdout, "gate_p_before_v")
    gate_n_before = read_measure(result.stdout, "gate_n_before_v")
    gate_p_after = read_measure(result.stdout, "gate_p_after_v")
    gate_n_after = read_measure(result.stdout, "gate_n_after_v")
    output_diff = read_measure(result.stdout, "output_diff_final_v")
    sampled_diff_before = sampled_p_before - sampled_n_before
    sampled_diff_after = sampled_p_after - sampled_n_after
    gate_diff_before = gate_p_before - gate_n_before
    gate_diff_after = gate_p_after - gate_n_after
    kickback = abs(sampled_diff_after - sampled_diff_before)
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    return {
        "case": case.name,
        "input_diff_mv": case.diff_mv,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "sampled_diff_before_v": sampled_diff_before,
        "sampled_diff_after_v": sampled_diff_after,
        "sampled_diff_kickback_v": kickback,
        "gate_diff_before_v": gate_diff_before,
        "gate_diff_after_v": gate_diff_after,
        "outp_final_v": read_measure(result.stdout, "outp_final_v"),
        "outn_final_v": read_measure(result.stdout, "outn_final_v"),
        "output_diff_final_v": output_diff,
        "half_lsb_12b_v": half_lsb,
        "resolved_correct_polarity": measured_sign == expected_sign and abs(output_diff) >= 0.9,
        "kickback_below_half_lsb": kickback <= half_lsb,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Capacitive Isolation Post-Layout Both-Polarity Rerun",
        "",
        f"- status: `{report['status']}`",
        f"- extracted frontend: `{report['extracted_frontend_netlist']}`",
        f"- model include: `{report['model_include']}`",
        f"- case count: `{report['case_count']}`",
        f"- passing case count: `{report['passing_case_count']}`",
        f"- worst kickback V: `{report['worst_kickback_v']}`",
        f"- hard kickback limit V: `{report['hard_kickback_limit_v']}`",
        f"- accepted ready now: `{report['accepted_ready_now']}`",
        "",
        "## First Principle",
        "",
        "The earlier pass used an ideal capacitor value in a generated schematic deck. This rerun uses the Magic-extracted RC frontend cell. That changes the question from whether a chosen capacitor value can work to whether this starter physical object still lets the latch read both signs without moving the sampled decision voltage too much.",
        "",
        "This is still not accepted comparator evidence. The extracted cell is a starter physical object. It has parasitic capacitance and named ports, but it does not yet prove offset, noise, DRC/LVS, device matching, or a full SAR conversion loop.",
        "",
        "The current result is useful because it separates two effects. The sampled-node kickback stays below the hard line, but the extracted frontend presents the same latch-gate sign for both input directions. The next diagnostic should test port mapping and physical symmetry before treating this as a comparator candidate.",
        "",
        "## Results",
        "",
        "| case | input diff mV | kickback V | hard limit V | output diff V | expected sign | measured sign | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        passed = bool(row.get("resolved_correct_polarity")) and bool(row.get("kickback_below_half_lsb"))
        if row.get("ngspice_returncode") != 0:
            lines.append(f"| `{row['case']}` | `{row['input_diff_mv']}` | failed | failed | failed | `{row['expected_sign']}` | failed | `False` |")
        else:
            lines.append(f"| `{row['case']}` | `{row['input_diff_mv']:.6f}` | `{row['sampled_diff_kickback_v']:.9e}` | `{row['half_lsb_12b_v']:.9e}` | `{row['output_diff_final_v']:.9e}` | `{row['expected_sign']}` | `{row['measured_sign']}` | `{passed}` |")
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    confirm = json.loads(CONFIRM.read_text(encoding="utf-8"))
    target_mv = float(confirm["target_combined_offset_noise_mv"])
    cases = [Case("extracted_rc_negative_target", -target_mv), Case("extracted_rc_positive_target", target_mv)]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    passing = [row for row in measured if row.get("resolved_correct_polarity") and row.get("kickback_below_half_lsb")]
    worst_kickback = max((float(row["sampled_diff_kickback_v"]) for row in measured), default=None)
    all_pass = len(passing) == len(rows) and bool(rows)
    report = {
        "result_type": "sky130_capacitive_isolation_post_layout_both_polarity_rerun",
        "status": "extracted_rc_both_polarity_passed_not_noise_or_drc_lvs_proof" if all_pass else "extracted_rc_both_polarity_characterized_not_confirmed",
        "source_schematic_confirmation": rel(CONFIRM),
        "extracted_frontend_netlist": rel(EXTRACTED),
        "model_include": rel(MODEL),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(OUT_CSV),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "passing_case_count": len(passing),
        "target_combined_offset_noise_mv": target_mv,
        "hard_kickback_limit_v": confirm["hard_kickback_limit_v"],
        "worst_kickback_v": worst_kickback,
        "all_cases_pass": all_pass,
        "rows": rows,
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "runs a both-polarity ngspice rerun through the Magic-extracted RC frontend starter cell",
            "not_allowed": "does not prove comparator offset, comparator noise, DRC/LVS, mismatch, SAR bit cycling, full converter behavior, or accepted replacement economics",
        },
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_markdown(report)
    print("sky130_capacitive_isolation_post_layout_both_polarity")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"passing_case_count,{report['passing_case_count']}")
    print(f"worst_kickback_v,{report['worst_kickback_v']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
