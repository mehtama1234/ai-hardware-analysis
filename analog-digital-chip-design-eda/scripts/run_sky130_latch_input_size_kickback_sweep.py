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
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
DECK_OUT = SPICE_DIR / "sky130_latch_input_size_kickback_sweep.sp"
CSV_OUT = MEASUREMENTS / "sky130-latch-input-size-kickback-sweep.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-input-size-kickback-sweep.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-input-size-kickback-sweep.md"
SPEC_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-acceptance-fixture-spec.json"
BASELINE_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-latch-kickback-ngspice.json"
NGSPICE_TIMEOUT_S = 160


@dataclass(frozen=True)
class Case:
    name: str
    input_width_um: float
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
    return f"""* Sky130 latch input-size kickback sweep.
* Same coupled sample-hold/latch fixture, with only the comparator input width changed.

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
.param wn_in={case.input_width_um:.6f}
.param wn_tail=20.0
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

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp sp tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn sn tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
COUTP outp 0 5f
COUTN outn 0 5f

.tran 2p 3n
.measure tran sampled_p_before_v FIND v(sp) AT=0.90n
.measure tran sampled_n_before_v FIND v(sn) AT=0.90n
.measure tran sampled_p_after_v FIND v(sp) AT=2.60n
.measure tran sampled_n_after_v FIND v(sn) AT=2.60n
.measure tran outp_final_v FIND v(outp) AT=2.60n
.measure tran outn_final_v FIND v(outn) AT=2.60n
.measure tran sampled_diff_before_v PARAM='sampled_p_before_v-sampled_n_before_v'
.measure tran sampled_diff_after_v PARAM='sampled_p_after_v-sampled_n_after_v'
.measure tran sampled_diff_kickback_v PARAM='abs(sampled_diff_after_v-sampled_diff_before_v)'
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "input_width_um": case.input_width_um,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "resolved_correct_polarity": False,
            "kickback_below_half_lsb": False,
        }
    if result.returncode != 0:
        return {
            "case": case.name,
            "input_width_um": case.input_width_um,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": result.returncode,
            "ngspice_timed_out": False,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "ngspice_error_excerpt": (result.stdout + result.stderr)[-1200:],
            "resolved_correct_polarity": False,
            "kickback_below_half_lsb": False,
        }
    output_diff = read_measure(result.stdout, "output_diff_final_v")
    kickback = read_measure(result.stdout, "sampled_diff_kickback_v")
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    return {
        "case": case.name,
        "input_width_um": case.input_width_um,
        "input_diff_mv": case.diff_mv,
        "sampled_diff_before_v": read_measure(result.stdout, "sampled_diff_before_v"),
        "sampled_diff_after_v": read_measure(result.stdout, "sampled_diff_after_v"),
        "sampled_diff_kickback_v": kickback,
        "outp_final_v": read_measure(result.stdout, "outp_final_v"),
        "outn_final_v": read_measure(result.stdout, "outn_final_v"),
        "output_diff_final_v": output_diff,
        "half_lsb_12b_v": half_lsb,
        "expected_sign": 1,
        "measured_sign": measured_sign,
        "resolved_correct_polarity": measured_sign == 1 and abs(output_diff) >= 0.9,
        "kickback_below_half_lsb": kickback <= half_lsb,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    target_mv = float(spec["derived_budget"]["target_combined_offset_noise_mv"])
    widths = [10.0, 5.0, 2.0, 1.0, 0.5]
    rows = [run_case(Case(f"wn_in_{width:g}um_positive_target", width, target_mv)) for width in widths]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    passing = [row for row in measured if row.get("resolved_correct_polarity") and row.get("kickback_below_half_lsb")]
    best = min(measured, key=lambda row: float(row["sampled_diff_kickback_v"])) if measured else None
    baseline_kickback = float(baseline["worst_sampled_diff_kickback_v"])
    best_kickback = float(best["sampled_diff_kickback_v"]) if best else None
    return {
        "result_type": "sky130_latch_input_size_kickback_sweep",
        "status": "sky130_latch_input_size_sweep_found_passing_width_not_noise_or_layout_proof" if passing else "sky130_latch_input_size_sweep_characterized_no_passing_width",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "topology": "coupled_differential_sample_hold_latch_with_swept_input_pair_width",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row.get("ngspice_timed_out")),
        "target_combined_offset_noise_mv": target_mv,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "baseline_input_width_um": 10.0,
        "baseline_kickback_v": baseline_kickback,
        "best_width_um": best.get("input_width_um") if best else None,
        "best_kickback_v": best_kickback,
        "best_improvement_x": baseline_kickback / best_kickback if best_kickback and best_kickback > 0 else None,
        "passing_width_count": len(passing),
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "tests whether reducing the Sky130 latch input-pair width reduces sampled-node kickback in the coupled sample-hold/latch fixture",
            "not_allowed": "does not prove comparator noise, mismatch, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Latch Input-Size Kickback Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- target combined offset/noise mV: `{report['target_combined_offset_noise_mv']:.4f}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- baseline input width um: `{report['baseline_input_width_um']}`",
        f"- baseline kickback V: `{report['baseline_kickback_v']:.9e}`",
        f"- best width um: `{report['best_width_um']}`",
        f"- best kickback V: `{fmt(report['best_kickback_v'])}`",
        f"- best improvement x: `{fmt(report['best_improvement_x'])}`",
        f"- passing width count: `{report['passing_width_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The latch failed the coupled gate because it moved the sampled nodes. One direct cause is input capacitance. A wider input transistor has more gate capacitance and stronger coupling paths. Shrinking it should reduce kickback, but it can also weaken the latch input signal.",
        "",
        "This sweep changes only the latch input-pair width. The question is whether a smaller input pair can still resolve the target-edge input while pushing less charge back into the sample-and-hold nodes.",
        "",
        "## Results",
        "",
        "| input width um | kickback V | half LSB V | output diff V | resolved | kickback pass |",
        "|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if row.get("ngspice_returncode") != 0:
            lines.append(f"| `{row['input_width_um']}` | failed | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['input_width_um']}` | `{row['sampled_diff_kickback_v']:.9e}` | `{row['half_lsb_12b_v']:.9e}` | `{row['output_diff_final_v']:.9e}` | `{row['resolved_correct_polarity']}` | `{row['kickback_below_half_lsb']}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If smaller input width lowers kickback but still misses the half-LSB line, the next circuit needs isolation, preamplification, or a sampled comparator input network. If a smaller width passes both resolution and kickback, it becomes the next candidate to test in both polarities and across input range.",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_latch_input_size_kickback_sweep")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"best_width_um,{report['best_width_um']}")
    print(f"best_kickback_v,{report['best_kickback_v']}")
    print(f"passing_width_count,{report['passing_width_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
