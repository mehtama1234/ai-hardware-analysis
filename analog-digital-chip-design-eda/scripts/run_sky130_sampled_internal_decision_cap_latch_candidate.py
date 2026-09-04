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
RISK_JSON = EVIDENCE / "sky130-polarity-contract-latch-sar-risk.json"
DECK_OUT = SPICE_DIR / "sky130_sampled_internal_decision_cap_latch_candidate.sp"
CSV_OUT = MEASUREMENTS / "sky130-sampled-internal-decision-cap-latch-candidate.csv"
OUT_JSON = EVIDENCE / "sky130-sampled-internal-decision-cap-latch-candidate.json"
OUT_MD = EVIDENCE / "sky130-sampled-internal-decision-cap-latch-candidate.md"
NGSPICE_TIMEOUT_S = 40


@dataclass(frozen=True)
class Case:
    name: str
    diff_mv: float
    cdec_f: float


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
    return f"""* Sky130 sampled internal decision capacitor latch candidate.
* Original sampled nodes copy charge to smaller internal decision nodes before latch regeneration.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param cstore=0.2p
.param cdec={case.cdec_f:.12e}
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}

VDD vdd 0 {{vdd}}
VSS vss 0 0
VINP inp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.10n 20p 20p 0.75n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.10n 20p 20p 0.75n 20n)
VCOPY copy 0 PULSE(0 {{vdd}} 0.30n 20p 20p 0.55n 20n)
VCOPYB copyb 0 PULSE({{vdd}} 0 0.30n 20p 20p 0.55n 20n)
VCLK clk 0 PULSE(0 {{vdd}} 1.20n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 1.20n 20p 20p 5n 10n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}
CSP sp 0 {{cstore}}
CSN sn 0 {{cstore}}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

* Transmission gates copy the stored voltage to small internal decision capacitors.
XCOPYP_N sp copy dp vss sky130_fd_pr__nfet_01v8 W=0.42 L={{lmin}}
XCOPYP_P sp copyb dp vdd sky130_fd_pr__pfet_01v8 W=0.84 L={{lmin}}
XCOPYN_N sn copy dn vss sky130_fd_pr__nfet_01v8 W=0.42 L={{lmin}}
XCOPYN_P sn copyb dn vdd sky130_fd_pr__pfet_01v8 W=0.84 L={{lmin}}
CDP dp 0 {{cdec}}
CDN dn 0 {{cdec}}
RLEAKDP dp 0 100G
RLEAKDN dn 0 100G

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp dp tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn dn tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
COUTP outp 0 5f
COUTN outn 0 5f

.tran 2p 3n
.measure tran sampled_p_before_v FIND v(sp) AT=0.90n
.measure tran sampled_n_before_v FIND v(sn) AT=0.90n
.measure tran sampled_p_after_v FIND v(sp) AT=2.70n
.measure tran sampled_n_after_v FIND v(sn) AT=2.70n
.measure tran decision_p_before_v FIND v(dp) AT=1.05n
.measure tran decision_n_before_v FIND v(dn) AT=1.05n
.measure tran decision_p_after_v FIND v(dp) AT=2.70n
.measure tran decision_n_after_v FIND v(dn) AT=2.70n
.measure tran output_p_final_v FIND v(outp) AT=2.70n
.measure tran output_n_final_v FIND v(outn) AT=2.70n
.control
run
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    print(f"case,{case.name},cdec={case.cdec_f:.3e}", flush=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"case": case.name, "input_diff_mv": case.diff_mv, "cdec_f": case.cdec_f, "ngspice_timed_out": True, "ngspice_returncode": None, "resolved_correct_polarity": False, "kickback_below_half_lsb": False}
    row: dict[str, Any] = {"case": case.name, "input_diff_mv": case.diff_mv, "cdec_f": case.cdec_f, "ngspice_timed_out": False, "ngspice_returncode": result.returncode}
    if result.returncode != 0:
        row["ngspice_error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        row["resolved_correct_polarity"] = False
        row["kickback_below_half_lsb"] = False
        return row
    sampled_before = read_measure(result.stdout, "sampled_p_before_v") - read_measure(result.stdout, "sampled_n_before_v")
    sampled_after = read_measure(result.stdout, "sampled_p_after_v") - read_measure(result.stdout, "sampled_n_after_v")
    decision_before = read_measure(result.stdout, "decision_p_before_v") - read_measure(result.stdout, "decision_n_before_v")
    decision_after = read_measure(result.stdout, "decision_p_after_v") - read_measure(result.stdout, "decision_n_after_v")
    output_diff = read_measure(result.stdout, "output_n_final_v") - read_measure(result.stdout, "output_p_final_v")
    expected_sign = 1 if case.diff_mv > 0 else -1
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    kickback = abs(sampled_after - sampled_before)
    row.update(
        {
            "sampled_diff_before_v": sampled_before,
            "sampled_diff_after_v": sampled_after,
            "sampled_diff_kickback_v": abs(sampled_after - sampled_before),
            "decision_diff_before_v": decision_before,
            "decision_diff_after_v": decision_after,
            "output_diff_final_v": output_diff,
            "half_lsb_12b_v": half_lsb,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "resolved_correct_polarity": measured_sign == expected_sign and abs(output_diff) >= 0.9,
            "kickback_below_half_lsb": kickback <= half_lsb,
        }
    )
    return row


def build_report() -> dict[str, Any]:
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
    risk = json.loads(RISK_JSON.read_text(encoding="utf-8"))
    target_mv = float(spec["derived_budget"]["target_combined_offset_noise_mv"])
    caps = [20e-15, 50e-15]
    cases = [Case(f"c{cap:.0e}_neg", -target_mv, cap) for cap in caps] + [Case(f"c{cap:.0e}_pos", target_mv, cap) for cap in caps]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    summaries: list[dict[str, Any]] = []
    for cap in caps:
        group = [row for row in rows if row["cdec_f"] == cap]
        summaries.append(
            {
                "cdec_f": cap,
                "case_count": len(group),
                "measured_case_count": sum(1 for row in group if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")),
                "resolved_count": sum(1 for row in group if row.get("resolved_correct_polarity")),
                "kickback_pass_count": sum(1 for row in group if row.get("kickback_below_half_lsb")),
                "worst_kickback_v": max((float(row.get("sampled_diff_kickback_v", 0.0)) for row in group if row.get("ngspice_returncode") == 0), default=None),
                "minimum_output_diff_abs_v": min((abs(float(row.get("output_diff_final_v", 0.0))) for row in group if row.get("ngspice_returncode") == 0), default=None),
            }
        )
    passing = [item for item in summaries if item["resolved_count"] == item["case_count"] and item["kickback_pass_count"] == item["case_count"]]
    best = min([item for item in summaries if item["worst_kickback_v"] is not None], key=lambda item: item["worst_kickback_v"], default=None)
    return {
        "result_type": "sky130_sampled_internal_decision_cap_latch_candidate",
        "status": "sampled_internal_decision_cap_latch_candidate_passed_schematic_not_noise_layout_or_strict" if passing else "sampled_internal_decision_cap_latch_candidate_characterized_not_accepted",
        "source_risk_join": rel(RISK_JSON),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row.get("ngspice_timed_out")),
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "prior_best_kickback_v": risk["best_latch_kickback_v"],
        "setting_summaries": summaries,
        "passing_setting_count": len(passing),
        "best_setting": best,
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "tests whether copying the sampled voltage onto small internal decision capacitors isolates the original sampled nodes from latch kickback",
            "not_allowed": "does not prove noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
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
        "# Sky130 Sampled Internal Decision-Cap Latch Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- prior best kickback V: `{report['prior_best_kickback_v']:.9e}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The sampled value is stored as charge. If the latch input is tied directly to that stored charge, the latch clock can push charge back and change the value being decided.",
        "",
        "This candidate copies the value onto a smaller internal decision capacitor before latch regeneration. The original sampled node should then be less exposed to the latch clock. The candidate is useful only if the copied internal node still gives the latch enough sign while sampled-node kickback falls below half-LSB.",
        "",
        "## Setting Summary",
        "",
        "| decision cap F | measured | resolved | kickback pass | worst kickback V | min output diff V |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        worst = "not measured" if item["worst_kickback_v"] is None else f"{item['worst_kickback_v']:.9e}"
        out = "not measured" if item["minimum_output_diff_abs_v"] is None else f"{item['minimum_output_diff_abs_v']:.9e}"
        lines.append(f"| `{item['cdec_f']:.9e}` | `{item['measured_case_count']}` | `{item['resolved_count']}` | `{item['kickback_pass_count']}` | `{worst}` | `{out}` |")
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_sampled_internal_decision_cap_latch_candidate")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
