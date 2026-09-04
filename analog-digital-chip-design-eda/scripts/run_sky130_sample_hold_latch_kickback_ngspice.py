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
DECK_OUT = SPICE_DIR / "sky130_sample_hold_latch_kickback.sp"
CSV_OUT = MEASUREMENTS / "sky130-sample-hold-latch-kickback-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-latch-kickback-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-latch-kickback-ngspice.md"
SPEC_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-acceptance-fixture-spec.json"
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
    return f"""* Sky130 sampled-node plus clocked comparator latch kickback proxy.
* Differential dummy sample-and-hold candidate drives a clocked latch input pair.
* This measures sampled-node movement caused by the attached latch fixture.

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
.param wn_in=10.0
.param wn_tail=20.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}

VDD vdd 0 {{vdd}}
VINP inp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.10n 20p 20p 0.75n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.10n 20p 20p 0.75n 20n)
VCLK clk 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 1.00n 20p 20p 5n 10n)

* Differential dummy-cancellation sample-and-hold candidate.
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
VSS vss 0 0

* Clocked latch from the prior proxy. The sampled nodes drive the input gates.
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
    half_lsb_v = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "half_lsb_12b_v": half_lsb_v,
            "resolved_correct_polarity": False,
            "kickback_below_half_lsb": False,
        }
    if result.returncode != 0:
        return {
            "case": case.name,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": result.returncode,
            "ngspice_timed_out": False,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "ngspice_error_excerpt": (result.stdout + result.stderr)[-1200:],
            "half_lsb_12b_v": half_lsb_v,
            "resolved_correct_polarity": False,
            "kickback_below_half_lsb": False,
        }
    output_diff = read_measure(result.stdout, "output_diff_final_v")
    expected_sign = 1 if case.diff_mv > 0 else -1
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    kickback_v = read_measure(result.stdout, "sampled_diff_kickback_v")
    return {
        "case": case.name,
        "input_diff_mv": case.diff_mv,
        "sampled_p_before_v": read_measure(result.stdout, "sampled_p_before_v"),
        "sampled_n_before_v": read_measure(result.stdout, "sampled_n_before_v"),
        "sampled_p_after_v": read_measure(result.stdout, "sampled_p_after_v"),
        "sampled_n_after_v": read_measure(result.stdout, "sampled_n_after_v"),
        "sampled_diff_before_v": read_measure(result.stdout, "sampled_diff_before_v"),
        "sampled_diff_after_v": read_measure(result.stdout, "sampled_diff_after_v"),
        "sampled_diff_kickback_v": kickback_v,
        "outp_final_v": read_measure(result.stdout, "outp_final_v"),
        "outn_final_v": read_measure(result.stdout, "outn_final_v"),
        "output_diff_final_v": output_diff,
        "half_lsb_12b_v": half_lsb_v,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "resolved_correct_polarity": expected_sign == measured_sign and abs(output_diff) >= 0.9,
        "kickback_below_half_lsb": kickback_v <= half_lsb_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
    budget = spec["derived_budget"]
    target_mv = float(budget["target_combined_offset_noise_mv"])
    hard_budget_mv = float(budget["remaining_comparator_offset_or_noise_budget_mv"])
    cases = [Case("negative_target_edge", -target_mv), Case("positive_target_edge", target_mv)]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    resolved_count = sum(1 for row in rows if row.get("resolved_correct_polarity") is True)
    kickback_pass_count = sum(1 for row in rows if row.get("kickback_below_half_lsb") is True)
    all_pass = resolved_count == len(rows) and kickback_pass_count == len(rows)
    return {
        "result_type": "sky130_sample_hold_latch_kickback_ngspice",
        "status": "sky130_sample_hold_latch_kickback_proxy_passed_not_noise_or_layout_proof" if all_pass else "sky130_sample_hold_latch_kickback_proxy_characterized_not_accepted",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "topology": "differential_dummy_sample_hold_driving_clocked_sky130_latch_input_pair",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row.get("ngspice_timed_out")),
        "target_combined_offset_noise_mv": target_mv,
        "hard_budget_mv": hard_budget_mv,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "resolved_correct_polarity_count": resolved_count,
        "kickback_below_half_lsb_count": kickback_pass_count,
        "all_cases_pass_coupled_gate": all_pass,
        "worst_sampled_diff_kickback_v": max((row.get("sampled_diff_kickback_v", 0.0) for row in measured), default=None),
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "couples the passing differential dummy sample-and-hold candidate to the Sky130 clocked latch proxy and measures sampled-node kickback plus final latch polarity",
            "not_allowed": "does not prove comparator noise, input-referred offset statistics, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Sample-Hold Latch Kickback Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- target combined offset/noise mV: `{report['target_combined_offset_noise_mv']:.4f}`",
        f"- hard budget mV: `{report['hard_budget_mv']:.4f}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- resolved correct polarity count: `{report['resolved_correct_polarity_count']}` of `{report['case_count']}`",
        f"- kickback below half LSB count: `{report['kickback_below_half_lsb_count']}` of `{report['case_count']}`",
        f"- worst sampled differential kickback V: `{fmt(report['worst_sampled_diff_kickback_v'])}`",
        f"- all cases pass coupled gate: `{report['all_cases_pass_coupled_gate']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A latch is not only a reader. It is also a load. When its clock moves, transistor capacitances can push charge back into the sampled nodes. That movement changes the same small voltage difference the latch is supposed to decide.",
        "",
        "This fixture connects the differential dummy sample-and-hold candidate to the clocked Sky130 latch proxy. It measures the sampled differential voltage before latch evaluation, measures it again after the latch has switched, and checks whether the latch both resolves in the correct direction and keeps sampled-node kickback below the 12-bit half-LSB line.",
        "",
        "This is the first coupled sample-hold plus latch check. It is stronger than driving the latch from ideal voltage sources. It is still not a full comparator proof because it does not include noise, offset statistics, SAR bit cycling, extracted layout, or DRC/LVS.",
        "",
        "## Results",
        "",
        "| case | input diff mV | sampled diff before V | sampled diff after V | kickback V | output diff V | resolved | kickback pass |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if row.get("ngspice_returncode") != 0:
            lines.append(f"| `{row['case']}` | `{row['input_diff_mv']:.6f}` | failed | failed | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['case']}` | `{row['input_diff_mv']:.6f}` | `{row['sampled_diff_before_v']:.9e}` | `{row['sampled_diff_after_v']:.9e}` | `{row['sampled_diff_kickback_v']:.9e}` | `{row['output_diff_final_v']:.9e}` | `{row['resolved_correct_polarity']}` | `{row['kickback_below_half_lsb']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_sample_hold_latch_kickback_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"resolved_correct_polarity_count,{report['resolved_correct_polarity_count']}")
    print(f"kickback_below_half_lsb_count,{report['kickback_below_half_lsb_count']}")
    print(f"worst_sampled_diff_kickback_v,{report['worst_sampled_diff_kickback_v']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
