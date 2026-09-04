#!/usr/bin/env python3
"""Complete missing rows in the coupled DAC/comparator all-code artifact."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import OUT_JSON, OUT_MD, TRIALS, run_trial


def main() -> int:
    report = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    rows_by_code = {int(row["code"]): row for row in report.get("rows", [])}
    missing = [code for code, _, _ in TRIALS if not rows_by_code.get(code, {}).get("measured")]
    workers = max(1, int(os.environ.get("AIMC_COUPLED_WORKERS", "1")))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        completed = list(pool.map(lambda code: run_trial(code, 1.2, 1.5), missing))
    for row in completed:
        rows_by_code[int(row["code"])] = row
    rows = [rows_by_code[code] for code, _, _ in TRIALS]
    measured = [row for row in rows if row.get("measured")]
    report.update({
        "status": "coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof" if measured else "coupled_dac_comparator_bit_incomplete",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row.get("timed_out", False) for row in rows),
        "correct_polarity_count": sum(row.get("correct_polarity", False) for row in measured),
        "phase_schedule": {
            "dac_sampling_and_redistribution": "0.1-4.0 ns source sampling, 5.0 ns bottom-plate transition" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "0.1-1.0 ns sampling, 1.0 ns bottom-plate transition",
            "comparator_sampling": "9.1-9.6 ns" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "5.1-5.6 ns",
            "preamp_enable": "9.70 ns" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "5.70 ns",
            "preamp_latch_boundary": "11.55-11.70 ns" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "7.55-7.70 ns",
        },
        "isolation_topology": "direct late sampling of the physical DAC top plate and matched reference by the comparator input switches with preamp disabled during sampling",
        "all_polarities_correct": bool(measured) and all(row.get("correct_polarity", False) for row in measured),
        "failing_codes": [row["code"] for row in measured if not row.get("correct_polarity", False)],
        "rows": rows,
    })
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Coupled DAC And Comparator Bit", "",
        f"- status: `{report['status']}`",
        f"- measured trials: `{report['measured_case_count']}` of `{report['case_count']}`",
        f"- timed-out trials: `{report['timed_out_case_count']}`",
        f"- correct polarity: `{report['correct_polarity_count']}` of `{report['measured_case_count']}`",
        f"- failing codes: `{report['failing_codes']}`", "",
        "## What This Closes", "",
        "The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. The all-code run uses direct late sampling after DAC redistribution; a source-follower control variant was rejected because it introduced a midrange sign offset.", "",
        ("The source switch is enlarged to 32/64 um and source acquisition runs to 4.0 ns before the 5.0 ns bottom-plate transition. The preamp is enabled at 9.7 ns and the latch fires at 11.7 ns. This is a longer-acquisition candidate, but not a retained-bit multi-cycle SAR or PVT/noise proof." if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "The preamp current is disabled while the DAC is sampled and enabled at 5.7 ns, after the comparator storage switch closes. The latch fires at 7.7 ns. This is a complete nominal code-level handoff, but not a retained-bit multi-cycle SAR or PVT/noise proof."), "",
        "## Results", "",
        "| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |", "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if not row.get("measured"):
            lines.append(f"| {row['code']} | timeout/error | timeout/error | timeout/error | False |")
        else:
            lines.append(f"| {row['code']} | {row['dac_top_after_v']:.6f} | {row['dac_to_reference_diff_v']:.6f} | {row['output_diff_v']:.6f} | {row['correct_polarity']} |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"measured,{report['measured_case_count']}/{report['case_count']}")
    print(f"timed_out,{report['timed_out_case_count']}")
    print(f"correct_polarity,{report['correct_polarity_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
