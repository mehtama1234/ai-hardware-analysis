#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
import tempfile
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
DECK_OUT = SPICE_DIR / "sky130_two_phase_preamp_latch_candidate.sp"
CSV_OUT = MEASUREMENTS / "sky130-two-phase-preamp-latch-candidate.csv"
OUT_JSON = EVIDENCE / "sky130-two-phase-preamp-latch-candidate.json"
OUT_MD = EVIDENCE / "sky130-two-phase-preamp-latch-candidate.md"
NGSPICE_TIMEOUT_S = 50


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
    return f"""* Sky130 two-phase preamp then latch candidate.
* Phase 1 samples the input. Phase 2 lets a resistor-load preamp form an internal difference.
* Phase 3 enables the latch after the preamp has settled.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param cstore=0.2p
.param pre_w=8.0
.param pre_tail=20u
.param pre_rd=100k
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12

VDD vdd 0 {{vdd}}
VSS vss 0 0
VINP inp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.10n 20p 20p 0.75n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.10n 20p 20p 0.75n 20n)
VCLK clk 0 PULSE(0 {{vdd}} 1.60n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 1.60n 20p 20p 5n 10n)

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

RPREP vdd pre_p {{pre_rd}}
RPREN vdd pre_n {{pre_rd}}
XPREP pre_p sp pre_tail_node 0 sky130_fd_pr__nfet_01v8 W={{pre_w}} L={{lmin}}
XPREN pre_n sn pre_tail_node 0 sky130_fd_pr__nfet_01v8 W={{pre_w}} L={{lmin}}
IPRE pre_tail_node 0 {{pre_tail}}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

XLPRE1 vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLPRE2 vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp pre_p tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn pre_n tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
COUTP outp 0 5f
COUTN outn 0 5f

.ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25 v(outp)=1.8 v(outn)=1.8
.tran 5p 3n
.measure tran sampled_p_before_v FIND v(sp) AT=0.90n
.measure tran sampled_n_before_v FIND v(sn) AT=0.90n
.measure tran sampled_p_after_v FIND v(sp) AT=2.70n
.measure tran sampled_n_after_v FIND v(sn) AT=2.70n
.measure tran preamp_p_before_latch_v FIND v(pre_p) AT=1.45n
.measure tran preamp_n_before_latch_v FIND v(pre_n) AT=1.45n
.measure tran preamp_p_after_latch_v FIND v(pre_p) AT=2.70n
.measure tran preamp_n_after_latch_v FIND v(pre_n) AT=2.70n
.measure tran output_p_final_v FIND v(outp) AT=2.70n
.measure tran output_n_final_v FIND v(outn) AT=2.70n
.control
run
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    print(f"case,{case.name}", flush=True)
    deck = build_deck(case)
    DECK_OUT.write_text(deck, encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
    with tempfile.TemporaryDirectory(prefix="aimc-two-phase-latch-") as tmp:
        case_deck = Path(tmp) / "candidate.sp"
        case_deck.write_text(deck, encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(case_deck)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"case": case.name, "input_diff_mv": case.diff_mv, "ngspice_timed_out": True, "ngspice_returncode": None, "resolved_correct_polarity": False, "kickback_below_half_lsb": False}
    row: dict[str, Any] = {"case": case.name, "input_diff_mv": case.diff_mv, "ngspice_timed_out": False, "ngspice_returncode": result.returncode}
    if result.returncode != 0:
        row["ngspice_error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        row["resolved_correct_polarity"] = False
        row["kickback_below_half_lsb"] = False
        return row
    sampled_before = read_measure(result.stdout, "sampled_p_before_v") - read_measure(result.stdout, "sampled_n_before_v")
    sampled_after = read_measure(result.stdout, "sampled_p_after_v") - read_measure(result.stdout, "sampled_n_after_v")
    preamp_before = read_measure(result.stdout, "preamp_n_before_latch_v") - read_measure(result.stdout, "preamp_p_before_latch_v")
    preamp_after = read_measure(result.stdout, "preamp_n_after_latch_v") - read_measure(result.stdout, "preamp_p_after_latch_v")
    output_diff = read_measure(result.stdout, "output_n_final_v") - read_measure(result.stdout, "output_p_final_v")
    # The converter contract names raw outn-outp as inverted: a positive
    # input is expected to produce a negative raw output difference.
    expected_sign = -1 if case.diff_mv > 0 else 1
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    kickback = abs(sampled_after - sampled_before)
    row.update(
        {
            "sampled_diff_before_v": sampled_before,
            "sampled_diff_after_v": sampled_after,
            "sampled_diff_kickback_v": kickback,
            "preamp_diff_before_latch_v": preamp_before,
            "preamp_diff_after_latch_v": preamp_after,
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
    rows = [run_case(Case("negative_target_edge", -target_mv)), run_case(Case("positive_target_edge", target_mv))]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    resolved = sum(1 for row in rows if row.get("resolved_correct_polarity"))
    kickback = sum(1 for row in rows if row.get("kickback_below_half_lsb"))
    all_pass = resolved == len(rows) and kickback == len(rows)
    worst_kickback = max((float(row.get("sampled_diff_kickback_v", 0.0)) for row in measured), default=None)
    min_preamp = min((abs(float(row.get("preamp_diff_before_latch_v", 0.0))) for row in measured), default=None)
    return {
        "result_type": "sky130_two_phase_preamp_latch_candidate",
        "status": "two_phase_preamp_latch_candidate_passed_schematic_not_noise_layout_or_strict" if all_pass else "two_phase_preamp_latch_candidate_characterized_not_accepted",
        "source_risk_join": rel(RISK_JSON),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row.get("ngspice_timed_out")),
        "resolved_correct_polarity_count": resolved,
        "kickback_below_half_lsb_count": kickback,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "prior_best_kickback_v": risk["best_latch_kickback_v"],
        "worst_sampled_diff_kickback_v": worst_kickback,
        "minimum_preamp_diff_before_latch_v": min_preamp,
        "all_cases_pass": all_pass,
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "tests a two-phase Sky130 preamp-then-latch candidate that lets an internal preamp difference form before latch regeneration",
            "not_allowed": "does not prove noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
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
        "# Sky130 Two-Phase Preamp-Then-Latch Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- resolved correct polarity count: `{report['resolved_correct_polarity_count']}`",
        f"- kickback below half LSB count: `{report['kickback_below_half_lsb_count']}`",
        f"- worst sampled differential kickback V: `{fmt(report['worst_sampled_diff_kickback_v'])}`",
        f"- minimum preamp diff before latch V: `{fmt(report['minimum_preamp_diff_before_latch_v'])}`",
        f"- all cases pass: `{report['all_cases_pass']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A regenerative latch is violent because it uses positive feedback. A preamp-then-latch design separates the quiet part from the violent part. The preamp first turns the small sampled difference into a larger internal difference. Only after that does the latch regenerate.",
        "",
        "This candidate is useful only if the latch still resolves both signs and the latch clock no longer moves the original sampled nodes beyond the half-LSB line.",
        "",
        "## Results",
        "",
        "| case | measured | kickback V | preamp diff before latch V | output diff V | resolved | kickback pass |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['case']}` | `{row.get('ngspice_returncode') == 0 and not row.get('ngspice_timed_out')}` | `{fmt(row.get('sampled_diff_kickback_v'))}` | `{fmt(row.get('preamp_diff_before_latch_v'))}` | `{fmt(row.get('output_diff_final_v'))}` | `{row.get('resolved_correct_polarity')}` | `{row.get('kickback_below_half_lsb')}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_two_phase_preamp_latch_candidate")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"resolved_correct_polarity_count,{report['resolved_correct_polarity_count']}")
    print(f"kickback_below_half_lsb_count,{report['kickback_below_half_lsb_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
