#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_sky130_capacitive_latch_input_isolation_sweep import Case, run_case  # noqa: E402


EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
MEASUREMENTS = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
SWEEP_JSON = EVIDENCE / "sky130-capacitive-latch-input-isolation-sweep.json"
OUT_JSON = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
OUT_MD = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.md"
CSV_OUT = MEASUREMENTS / "sky130-capacitive-isolation-both-polarity-confirm.csv"


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def signed_case_name(cap_ff: float, sign: str) -> str:
    return f"ciso_{cap_ff:g}f_{sign}_target"


def build_report() -> dict[str, Any]:
    sweep = json.loads(SWEEP_JSON.read_text(encoding="utf-8"))
    target_mv = float(sweep["target_combined_offset_noise_mv"])
    hard_limit = float(sweep["hard_kickback_limit_v"])
    passing_caps = sorted(
        {
            float(row["coupling_cap_f"])
            for row in sweep["rows"]
            if row.get("resolved_correct_polarity") is True and row.get("kickback_below_half_lsb") is True
        }
    )
    cases: list[Case] = []
    for cap in passing_caps:
        cap_ff = cap * 1e15
        cases.append(Case(signed_case_name(cap_ff, "negative"), cap, -target_mv))
        cases.append(Case(signed_case_name(cap_ff, "positive"), cap, target_mv))
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row.get("ngspice_returncode") == 0 and not row.get("ngspice_timed_out")]
    for row in rows:
        expected_sign = 1 if float(row.get("input_diff_mv", 0.0)) > 0 else -1
        row["expected_sign"] = expected_sign
        if row.get("ngspice_returncode") == 0:
            row["resolved_correct_polarity"] = row.get("measured_sign") == expected_sign and abs(float(row.get("output_diff_final_v", 0.0))) >= 0.9
    passing = [row for row in measured if row.get("resolved_correct_polarity") and row.get("kickback_below_half_lsb")]
    worst_kickback = max((float(row["sampled_diff_kickback_v"]) for row in measured), default=None)
    all_pass = len(passing) == len(rows) and bool(rows)
    return {
        "result_type": "sky130_capacitive_isolation_both_polarity_confirm",
        "status": "sky130_capacitive_isolation_both_polarity_confirmed_not_noise_or_layout_proof" if all_pass else "sky130_capacitive_isolation_both_polarity_characterized_not_confirmed",
        "source_sweep": "sky130-capacitive-latch-input-isolation-sweep.json",
        "csv": str(CSV_OUT.relative_to(ROOT)),
        "confirmed_coupling_caps_ff": [cap * 1e15 for cap in passing_caps],
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "passing_case_count": len(passing),
        "target_combined_offset_noise_mv": target_mv,
        "hard_kickback_limit_v": hard_limit,
        "worst_kickback_v": worst_kickback,
        "all_cases_pass": all_pass,
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "confirms the passing capacitive-isolation candidates in both positive and negative target-edge directions",
            "not_allowed": "does not prove comparator noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Capacitive Isolation Both-Polarity Confirm",
        "",
        f"- status: `{report['status']}`",
        f"- confirmed coupling caps fF: `{', '.join(f'{cap:g}' for cap in report['confirmed_coupling_caps_ff'])}`",
        f"- target combined offset/noise mV: `{report['target_combined_offset_noise_mv']:.4f}`",
        f"- hard kickback limit V: `{fmt(report['hard_kickback_limit_v'])}`",
        f"- worst kickback V: `{fmt(report['worst_kickback_v'])}`",
        f"- passing case count: `{report['passing_case_count']}` of `{report['case_count']}`",
        f"- all cases pass: `{report['all_cases_pass']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A useful comparator isolation trick must work for either sign of the input difference. If it only works when the positive side is larger, it is not a comparator front end. It is a one-sided accident.",
        "",
        "This run takes only the capacitor values that passed the first capacitive-isolation sweep, then reruns them with positive and negative target-edge inputs. The check is simple: the latch must resolve in the correct direction and the sampled differential kickback must stay below the half-LSB line.",
        "",
        "## Results",
        "",
        "| cap fF | input diff mV | kickback V | hard limit V | output diff V | expected sign | measured sign | pass |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        if row.get("ngspice_returncode") != 0:
            lines.append(f"| `{row.get('coupling_cap_f', 0) * 1e15:.3f}` | `{row.get('input_diff_mv')}` | failed | failed | failed | `{row.get('expected_sign')}` | failed | `False` |")
            continue
        passed = bool(row.get("resolved_correct_polarity")) and bool(row.get("kickback_below_half_lsb"))
        lines.append(
            f"| `{row['coupling_cap_ff']:.3f}` | `{row['input_diff_mv']:.6f}` | `{row['sampled_diff_kickback_v']:.9e}` | `{row['half_lsb_12b_v']:.9e}` | `{row['output_diff_final_v']:.9e}` | `{row['expected_sign']}` | `{row['measured_sign']}` | `{passed}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_capacitive_isolation_both_polarity_confirm")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"passing_case_count,{report['passing_case_count']}")
    print(f"worst_kickback_v,{report['worst_kickback_v']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
