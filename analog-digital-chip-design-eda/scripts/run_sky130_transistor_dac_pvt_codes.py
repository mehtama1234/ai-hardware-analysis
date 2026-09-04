#!/usr/bin/env python3
"""Check representative DAC codes across the three measured PVT corners."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_transistor_switched_capacitor_dac import PDK_LIB, ROOT, VDD, VIN, deck, measure

EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-dac-pvt-codes.json"
OUT_MD = EVIDENCE / "sky130-transistor-dac-pvt-codes.md"
TIMEOUT_S = 60
CODES = (0, 8, 15)
CORNERS = (
    {"name": "tt_25c_1p80v", "section": "tt", "temperature_c": 25.0, "supply_v": 1.8},
    {"name": "ss_minus20c_1p62v", "section": "ss", "temperature_c": -20.0, "supply_v": 1.62},
    {"name": "ff_85c_1p98v", "section": "ff", "temperature_c": 85.0, "supply_v": 1.98},
)


def run(corner: dict[str, Any], code: int) -> dict[str, Any]:
    source = deck(code).replace(f'.lib "{PDK_LIB}" tt', f'.lib "{PDK_LIB}" {corner["section"]}')
    source = source.replace(f".param vdd={VDD}", f".param vdd={corner['supply_v']}")
    source = source.replace(f".tran 10p 80n uic", f".temp {corner['temperature_c']}\n.tran 10p 80n uic")
    with tempfile.TemporaryDirectory(prefix="aimc-dac-pvt-") as tmp:
        path = Path(tmp) / "dac.sp"
        path.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"corner": corner["name"], "code": code, "measured": False, "timed_out": True}
    row: dict[str, Any] = {"corner": corner["name"], "code": code, "supply_v": corner["supply_v"], "temperature_c": corner["temperature_c"], "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1000:]
        return row
    settled = measure(result.stdout, "top_settled_v")
    expected = VIN + corner["supply_v"] * code / 16.0
    half_lsb = corner["supply_v"] / 16.0 / 2.0
    row.update({"top_settled_v": settled, "expected_top_v": expected, "error_v": settled - expected, "error_lsb": (settled - expected) / (corner["supply_v"] / 16.0), "half_lsb_v": half_lsb, "half_lsb_pass": abs(settled - expected) <= half_lsb})
    return row


def main() -> int:
    rows = [run(corner, code) for corner in CORNERS for code in CODES]
    measured = [row for row in rows if row["measured"]]
    report = {
        "result_type": "sky130_transistor_dac_pvt_codes",
        "status": "representative_dac_pvt_measured_not_full_calibration_proof",
        "corner_count": len(CORNERS),
        "code_count_per_corner": len(CODES),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row.get("timed_out", False) for row in rows),
        "half_lsb_pass_count": sum(row.get("half_lsb_pass", False) for row in measured),
        "rows": rows,
        "claim_boundary": {"allowed": "measures representative low, mid, and high DAC codes at three process, temperature, and supply corners", "not_allowed": "does not prove all-code calibration stability, mismatch/noise yield, SAR accuracy, extracted layout, board behavior, or silicon"},
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor DAC Representative PVT Codes", "",
        f"- status: `{report['status']}`",
        f"- corners: `{report['corner_count']}`",
        f"- codes per corner: `{report['code_count_per_corner']}`",
        f"- measured cases: `{report['measured_case_count']}` of `{report['case_count']}`",
        f"- timed-out cases: `{report['timed_out_case_count']}`",
        f"- half-LSB passes: `{report['half_lsb_pass_count']}` of `{report['measured_case_count']}`", "",
        "## First-Principles Reading", "",
        "A calibration table is only useful if the code-to-voltage curve is repeatable as operating conditions move. This targeted run checks the endpoints and midscale at the nominal, slow/cold/low-supply, and fast/hot/high-supply corners. It is intentionally smaller than a full all-code PVT matrix, but it tests whether the calibration assumption is already visibly unstable.", "",
        "## Refused Claim", "",
        report["claim_boundary"]["not_allowed"], "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"half_lsb_pass_count,{report['half_lsb_pass_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
