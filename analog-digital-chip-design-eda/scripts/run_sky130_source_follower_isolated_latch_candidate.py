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
DECK_OUT = SPICE_DIR / "sky130_source_follower_isolated_latch_candidate.sp"
CSV_OUT = MEASUREMENTS / "sky130-source-follower-isolated-latch-candidate.csv"
OUT_JSON = EVIDENCE / "sky130-source-follower-isolated-latch-candidate.json"
OUT_MD = EVIDENCE / "sky130-source-follower-isolated-latch-candidate.md"
NGSPICE_TIMEOUT_S = 25


@dataclass(frozen=True)
class Case:
    name: str
    diff_mv: float
    follower_w_um: float
    follower_bias_ua: float


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
    return f"""* Sky130 source-follower isolated latch candidate.
* The sampled nodes drive source-follower gates. The latch reads follower sources.

.lib "{PDK_LIB}" tt
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
.param wf={case.follower_w_um:.6f}
.param ifollow={case.follower_bias_ua * 1e-6:.12e}
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}

VDD vdd 0 {{vdd}}
VSS vss 0 0
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

XFOLP bufp sp vdd vdd sky130_fd_pr__nfet_01v8 W={{wf}} L={{lmin}}
XFOLN bufn sn vdd vdd sky130_fd_pr__nfet_01v8 W={{wf}} L={{lmin}}
IFOLP bufp 0 {{ifollow}}
IFOLN bufn 0 {{ifollow}}
CBUFP bufp 0 2f
CBUFN bufn 0 2f

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp bufp tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn bufn tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
COUTP outp 0 5f
COUTN outn 0 5f

.tran 2p 3n
.measure tran sampled_diff_before_v PARAM='v(sp)-v(sn)' AT=0.90n
.measure tran sampled_diff_after_v PARAM='v(sp)-v(sn)' AT=2.60n
.measure tran sampled_diff_kickback_v PARAM='abs(sampled_diff_after_v-sampled_diff_before_v)'
.measure tran buffer_diff_before_v PARAM='v(bufp)-v(bufn)' AT=0.90n
.measure tran buffer_diff_after_v PARAM='v(bufp)-v(bufn)' AT=2.60n
.measure tran output_diff_final_v PARAM='v(outn)-v(outp)' AT=2.60n
.control
run
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    print(f"case,{case.name},w={case.follower_w_um},i={case.follower_bias_ua}uA", flush=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"case": case.name, "input_diff_mv": case.diff_mv, "follower_w_um": case.follower_w_um, "follower_bias_ua": case.follower_bias_ua, "ngspice_timed_out": True, "ngspice_returncode": None, "resolved_correct_polarity": False, "kickback_below_half_lsb": False}
    row: dict[str, Any] = {"case": case.name, "input_diff_mv": case.diff_mv, "follower_w_um": case.follower_w_um, "follower_bias_ua": case.follower_bias_ua, "ngspice_timed_out": False, "ngspice_returncode": result.returncode}
    if result.returncode != 0:
        row["ngspice_error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        row["resolved_correct_polarity"] = False
        row["kickback_below_half_lsb"] = False
        return row
    output_diff = read_measure(result.stdout, "output_diff_final_v")
    expected_sign = 1 if case.diff_mv > 0 else -1
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    kickback = read_measure(result.stdout, "sampled_diff_kickback_v")
    row.update(
        {
            "sampled_diff_before_v": read_measure(result.stdout, "sampled_diff_before_v"),
            "sampled_diff_after_v": read_measure(result.stdout, "sampled_diff_after_v"),
            "sampled_diff_kickback_v": kickback,
            "buffer_diff_before_v": read_measure(result.stdout, "buffer_diff_before_v"),
            "buffer_diff_after_v": read_measure(result.stdout, "buffer_diff_after_v"),
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
    settings = [(0.42, 1.0), (1.0, 2.0)]
    cases = [Case(f"w{w:g}_i{i:g}_neg", -target_mv, w, i) for w, i in settings] + [Case(f"w{w:g}_i{i:g}_pos", target_mv, w, i) for w, i in settings]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    pairs: list[dict[str, Any]] = []
    for w, i in settings:
        group = [row for row in rows if row["follower_w_um"] == w and row["follower_bias_ua"] == i]
        pairs.append(
            {
                "follower_w_um": w,
                "follower_bias_ua": i,
                "case_count": len(group),
                "measured_case_count": sum(1 for row in group if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")),
                "resolved_count": sum(1 for row in group if row.get("resolved_correct_polarity")),
                "kickback_pass_count": sum(1 for row in group if row.get("kickback_below_half_lsb")),
                "worst_kickback_v": max((float(row.get("sampled_diff_kickback_v", 0.0)) for row in group if row.get("ngspice_returncode") == 0), default=None),
                "minimum_output_diff_abs_v": min((abs(float(row.get("output_diff_final_v", 0.0))) for row in group if row.get("ngspice_returncode") == 0), default=None),
            }
        )
    passing = [item for item in pairs if item["resolved_count"] == item["case_count"] and item["kickback_pass_count"] == item["case_count"]]
    best = min([item for item in pairs if item["worst_kickback_v"] is not None], key=lambda item: item["worst_kickback_v"], default=None)
    return {
        "result_type": "sky130_source_follower_isolated_latch_candidate",
        "status": "source_follower_isolated_latch_candidate_passed_schematic_not_noise_layout_or_strict" if passing else "source_follower_isolated_latch_candidate_characterized_not_accepted",
        "source_risk_join": rel(RISK_JSON),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row.get("ngspice_timed_out")),
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "prior_best_kickback_v": risk["best_latch_kickback_v"],
        "setting_summaries": pairs,
        "passing_setting_count": len(passing),
        "best_setting": best,
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "tests a source-follower isolation candidate between sampled nodes and the Sky130 clocked latch input pair",
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
        "# Sky130 Source-Follower Isolated Latch Candidate",
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
        "The latch should see the decision voltage without forcing its clock movement back into the sampled nodes. A source follower tries to do that by making the sampled node drive only a gate while a separate source node drives the latch input.",
        "",
        "This is useful only if both facts hold together: both signs still resolve, and sampled-node kickback falls below the half-LSB line.",
        "",
        "## Setting Summary",
        "",
        "| follower W um | bias uA | measured | resolved | kickback pass | worst kickback V | min output diff V |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        worst = "not measured" if item["worst_kickback_v"] is None else f"{item['worst_kickback_v']:.9e}"
        out = "not measured" if item["minimum_output_diff_abs_v"] is None else f"{item['minimum_output_diff_abs_v']:.9e}"
        lines.append(f"| `{item['follower_w_um']}` | `{item['follower_bias_ua']}` | `{item['measured_case_count']}` | `{item['resolved_count']}` | `{item['kickback_pass_count']}` | `{worst}` | `{out}` |")
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_source_follower_isolated_latch_candidate")
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
