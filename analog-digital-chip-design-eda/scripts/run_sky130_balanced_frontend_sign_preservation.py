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
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_balanced_capacitive_isolation_frontend_extracted.spice"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
STARTER = EVIDENCE / "sky130-balanced-frontend-starter-extraction.json"
OUT_JSON = EVIDENCE / "sky130-balanced-frontend-sign-preservation.json"
OUT_MD = EVIDENCE / "sky130-balanced-frontend-sign-preservation.md"
OUT_CSV = MEASUREMENTS / "sky130-balanced-frontend-sign-preservation.csv"
DECK_OUT = SPICE_DIR / "sky130_balanced_frontend_sign_preservation.sp"
NGSPICE_TIMEOUT_S = 40


@dataclass(frozen=True)
class Case:
    diff_mv: float
    reset_mode: str


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
        raise ValueError(f"missing measurement {name}")
    return values[-1]


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    reset = "0.9" if case.reset_mode == "quiet_vcm" else "PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)"
    return f"""* Balanced extracted frontend sign-preservation diagnostic.

.include "{EXTRACTED}"
.param vdd=1.8
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}
VDD vdd 0 {{vdd}}
VSS vss 0 0
VSP sp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {{vdd}} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 {reset}
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_balanced_capacitive_isolation_frontend
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G
.tran 2p 3n
.measure tran sp_after_v FIND v(sp) AT=2.60n
.measure tran sn_after_v FIND v(sn) AT=2.60n
.measure tran sense_p_before_v FIND v(sense_p) AT=0.90n
.measure tran sense_n_before_v FIND v(sense_n) AT=0.90n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.control
run
.endc
.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.diff_mv > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"input_diff_mv": case.diff_mv, "reset_mode": case.reset_mode, "expected_sign": expected_sign, "ngspice_timed_out": True, "sign_preserved": False}
    if result.returncode != 0:
        return {"input_diff_mv": case.diff_mv, "reset_mode": case.reset_mode, "expected_sign": expected_sign, "ngspice_returncode": result.returncode, "error_excerpt": (result.stdout + result.stderr)[-1200:], "sign_preserved": False}
    sample_diff = read_measure(result.stdout, "sp_after_v") - read_measure(result.stdout, "sn_after_v")
    sense_before = read_measure(result.stdout, "sense_p_before_v") - read_measure(result.stdout, "sense_n_before_v")
    sense_after = read_measure(result.stdout, "sense_p_after_v") - read_measure(result.stdout, "sense_n_after_v")
    measured_sign = 1 if sense_after > 0 else -1 if sense_after < 0 else 0
    return {
        "input_diff_mv": case.diff_mv,
        "reset_mode": case.reset_mode,
        "expected_sign": expected_sign,
        "sample_diff_after_v": sample_diff,
        "sense_diff_before_v": sense_before,
        "sense_diff_after_v": sense_after,
        "measured_sense_sign": measured_sign,
        "sign_preserved": measured_sign == expected_sign,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Balanced Frontend Sign Preservation",
        "",
        f"- status: `{report['status']}`",
        f"- passing case count: `{report['passing_case_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- extracted frontend: `{report['extracted_frontend_netlist']}`",
        "",
        "## First Principle",
        "",
        "The balanced starter cell is still not a comparator. This test asks one smaller question: after extraction, does the physical frontend carry the sign of the sampled difference onto `sense_p - sense_n`?",
        "",
        "A zero or wrong sign here means the layout is balanced but not useful yet. A correct sign only means the sense-node handoff is plausible; active reset devices, latch resolution, offset/noise, DRC, and LVS are still separate gates.",
        "",
        "## Results",
        "",
        "| reset mode | input diff mV | sample diff after V | sense diff before V | sense diff after V | expected sign | measured sign | sign preserved |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row.get('sample_diff_after_v', 0):.9e}` | `{row.get('sense_diff_before_v', 0):.9e}` | `{row.get('sense_diff_after_v', 0):.9e}` | `{row['expected_sign']}` | `{row.get('measured_sense_sign')}` | `{row['sign_preserved']}` |")
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    confirm = json.loads(CONFIRM.read_text(encoding="utf-8"))
    starter = json.loads(STARTER.read_text(encoding="utf-8"))
    target_mv = float(confirm["target_combined_offset_noise_mv"])
    cases = [Case(diff, mode) for mode in ["quiet_vcm", "reset_pulse"] for diff in (-target_mv, target_mv)]
    rows = [run_case(case) for case in cases]
    passing = sum(1 for row in rows if row.get("sign_preserved") is True)
    all_preserved = passing == len(rows)
    report = {
        "result_type": "sky130_balanced_frontend_sign_preservation",
        "status": "balanced_extracted_frontend_preserves_sign_not_comparator_proof" if all_preserved else "balanced_extracted_frontend_sign_preservation_incomplete",
        "source_starter_extraction": "evidence/aimc-simulator-adapters/sky130-balanced-frontend-starter-extraction.json",
        "extracted_frontend_netlist": rel(EXTRACTED),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(OUT_CSV),
        "starter_sense_capacitance_delta_ff": starter["sense_capacitance_delta_ff"],
        "target_differential_signal_mv": target_mv,
        "case_count": len(rows),
        "passing_case_count": passing,
        "rows": rows,
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "tests whether the extracted balanced starter frontend preserves sampled sign at the sense nodes",
            "not_allowed": "does not prove active reset devices, latch resolution, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(report)
    print("sky130_balanced_frontend_sign_preservation")
    print(f"status,{report['status']}")
    print(f"passing_case_count,{passing}")
    print(f"case_count,{len(rows)}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
