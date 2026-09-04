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
DECK_OUT = SPICE_DIR / "sky130_capacitive_latch_input_isolation_sweep.sp"
CSV_OUT = MEASUREMENTS / "sky130-capacitive-latch-input-isolation-sweep.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-latch-input-isolation-sweep.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-latch-input-isolation-sweep.md"
TARGET_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-isolation-target.json"
NGSPICE_TIMEOUT_S = 160


@dataclass(frozen=True)
class Case:
    name: str
    coupling_cap_f: float
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


def cap_label(value: float) -> str:
    return f"{value * 1e15:g}f"


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Sky130 capacitive latch-input isolation sweep.
* The sample nodes drive latch input gates through small capacitors and weak common-mode bias.

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
.param ciso={case.coupling_cap_f:.12e}
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

* Isolated comparator input nodes.
CISO_P sp gp {{ciso}}
CISO_N sn gn {{ciso}}
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
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "coupling_cap_f": case.coupling_cap_f,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "resolved_correct_polarity": False,
            "kickback_below_half_lsb": False,
        }
    if result.returncode != 0:
        return {
            "case": case.name,
            "coupling_cap_f": case.coupling_cap_f,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": result.returncode,
            "ngspice_timed_out": False,
            "ngspice_error_excerpt": (result.stdout + result.stderr)[-1200:],
            "resolved_correct_polarity": False,
            "kickback_below_half_lsb": False,
        }
    output_diff = read_measure(result.stdout, "output_diff_final_v")
    sampled_p_before = read_measure(result.stdout, "sampled_p_before_v")
    sampled_n_before = read_measure(result.stdout, "sampled_n_before_v")
    sampled_p_after = read_measure(result.stdout, "sampled_p_after_v")
    sampled_n_after = read_measure(result.stdout, "sampled_n_after_v")
    gate_p_before = read_measure(result.stdout, "gate_p_before_v")
    gate_n_before = read_measure(result.stdout, "gate_n_before_v")
    gate_p_after = read_measure(result.stdout, "gate_p_after_v")
    gate_n_after = read_measure(result.stdout, "gate_n_after_v")
    sampled_diff_before = sampled_p_before - sampled_n_before
    sampled_diff_after = sampled_p_after - sampled_n_after
    gate_diff_before = gate_p_before - gate_n_before
    gate_diff_after = gate_p_after - gate_n_after
    kickback = abs(sampled_diff_after - sampled_diff_before)
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    return {
        "case": case.name,
        "coupling_cap_f": case.coupling_cap_f,
        "coupling_cap_ff": case.coupling_cap_f * 1e15,
        "input_diff_mv": case.diff_mv,
        "sampled_p_before_v": sampled_p_before,
        "sampled_n_before_v": sampled_n_before,
        "sampled_p_after_v": sampled_p_after,
        "sampled_n_after_v": sampled_n_after,
        "sampled_diff_before_v": sampled_diff_before,
        "sampled_diff_after_v": sampled_diff_after,
        "gate_p_before_v": gate_p_before,
        "gate_n_before_v": gate_n_before,
        "gate_p_after_v": gate_p_after,
        "gate_n_after_v": gate_n_after,
        "gate_diff_before_v": gate_diff_before,
        "gate_diff_after_v": gate_diff_after,
        "sampled_diff_kickback_v": kickback,
        "outp_final_v": read_measure(result.stdout, "outp_final_v"),
        "outn_final_v": read_measure(result.stdout, "outn_final_v"),
        "output_diff_final_v": output_diff,
        "half_lsb_12b_v": half_lsb,
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
    target = json.loads(TARGET_JSON.read_text(encoding="utf-8"))
    target_mv = float(target["target"]["target_combined_offset_noise_mv"])
    hard_limit_v = float(target["target"]["hard_kickback_limit_v"])
    recommended_target_v = float(target["target"]["recommended_kickback_target_v"])
    cases = [
        Case(f"ciso_{cap_label(cap)}_positive_target", cap, target_mv)
        for cap in [0.1e-15, 0.2e-15, 0.5e-15, 1.0e-15, 2.0e-15]
    ]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    passing = [row for row in measured if row["resolved_correct_polarity"] and row["kickback_below_half_lsb"]]
    best = min(measured, key=lambda row: float(row["sampled_diff_kickback_v"])) if measured else None
    all_pass = bool(passing)
    return {
        "result_type": "sky130_capacitive_latch_input_isolation_sweep",
        "status": "sky130_capacitive_latch_input_isolation_found_candidate_not_noise_or_layout_proof" if all_pass else "sky130_capacitive_latch_input_isolation_characterized_no_candidate",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "topology": "coupled_sample_hold_with_capacitive_latch_input_isolation",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row.get("ngspice_timed_out")),
        "target_combined_offset_noise_mv": target_mv,
        "hard_kickback_limit_v": hard_limit_v,
        "recommended_kickback_target_v": recommended_target_v,
        "best_coupling_cap_ff": best.get("coupling_cap_ff") if best else None,
        "best_kickback_v": best.get("sampled_diff_kickback_v") if best else None,
        "best_resolved_correct_polarity": best.get("resolved_correct_polarity") if best else None,
        "passing_candidate_count": len(passing),
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "sweeps small capacitive isolation between the sampled nodes and the Sky130 latch input gates to test whether sampled-node kickback can be reduced while preserving latch polarity",
            "not_allowed": "does not prove comparator noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Capacitive Latch Input Isolation Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- target combined offset/noise mV: `{report['target_combined_offset_noise_mv']:.4f}`",
        f"- hard kickback limit V: `{fmt(report['hard_kickback_limit_v'])}`",
        f"- recommended kickback target V: `{fmt(report['recommended_kickback_target_v'])}`",
        f"- best coupling capacitor fF: `{report['best_coupling_cap_ff']}`",
        f"- best kickback V: `{fmt(report['best_kickback_v'])}`",
        f"- best resolved correct polarity: `{report['best_resolved_correct_polarity']}`",
        f"- passing candidate count: `{report['passing_candidate_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "Direct latch input gates moved the sampled nodes because the sampled capacitors were tied to a fast regenerative circuit. A coupling capacitor tries to separate those two jobs. The sample-and-hold keeps the original charge. A smaller internal input node receives only enough of the voltage difference to steer the latch.",
        "",
        "This is a trade. A smaller coupling capacitor should reduce kickback, but it may also starve the latch of signal. The useful question is whether any tested capacitor keeps sampled-node movement below the half-LSB line while the latch still resolves with the correct polarity.",
        "",
        "## Results",
        "",
        "| coupling cap fF | kickback V | hard limit V | gate diff after V | output diff V | resolved | kickback pass |",
        "|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if row.get("ngspice_returncode") != 0:
            lines.append(f"| `{row.get('coupling_cap_f', 0) * 1e15:.3f}` | failed | failed | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['coupling_cap_ff']:.3f}` | `{row['sampled_diff_kickback_v']:.9e}` | `{row['half_lsb_12b_v']:.9e}` | `{row['gate_diff_after_v']:.9e}` | `{row['output_diff_final_v']:.9e}` | `{row['resolved_correct_polarity']}` | `{row['kickback_below_half_lsb']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_capacitive_latch_input_isolation_sweep")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"best_coupling_cap_ff,{report['best_coupling_cap_ff']}")
    print(f"best_kickback_v,{report['best_kickback_v']}")
    print(f"passing_candidate_count,{report['passing_candidate_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
