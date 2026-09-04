#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EXTRACTED = LAB / "layout-workbench" / "extracted"
MEASUREMENTS = LAB / "measurements"
SOURCE_NETLIST = EXTRACTED / "aimc_converter_macro_layout_smoke.spice"
DECK_OUT = EXTRACTED / "aimc_converter_macro_extracted_rc_step.sp"
CSV_OUT = MEASUREMENTS / "converter-starter-extracted-rc-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-extracted-rc-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-extracted-rc-ngspice.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def build_deck() -> str:
    return f"""* Extracted RC transient fixture for the AIMC converter starter macro.
* This uses Magic-extracted capacitances, explicit driver/load resistors, and no transistor converter behavior.

.global VSUBS
.include "{SOURCE_NETLIST}"

VDD vdd 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VSTEP src 0 PULSE(0 1.8 0.1n 20p 20p 5n 10n)
RDRV src row_drive 1000
RCOLUMN column_sense 0 2250
RDIG digital_code_out 0 1000
RCLK sample_clock 0 1000
XMAC vss vdd row_drive column_sense digital_code_out sample_clock aimc_converter_macro

.tran 1p 2n
.measure tran row_final FIND v(row_drive) AT=1.5n
.measure tran column_peak MAX v(column_sense) FROM=0.1n TO=2n
.measure tran digital_peak MAX v(digital_code_out) FROM=0.1n TO=2n
.measure tran row_90_when WHEN v(row_drive)=1.62 RISE=1
.measure tran row_99_when WHEN v(row_drive)=1.782 RISE=1
.control
run
.endc

.end
"""


def run_ngspice() -> dict[str, Any]:
    if not SOURCE_NETLIST.exists():
        raise FileNotFoundError(SOURCE_NETLIST)
    DECK_OUT.write_text(build_deck(), encoding="utf-8")
    result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False)
    measurements = {
        "row_final_v": read_measure(result.stdout, "row_final"),
        "column_peak_v": read_measure(result.stdout, "column_peak"),
        "digital_peak_v": read_measure(result.stdout, "digital_peak"),
        "row_90_when_s": read_measure(result.stdout, "row_90_when"),
        "row_99_when_s": read_measure(result.stdout, "row_99_when"),
    }
    measurements["row_90_to_99_s"] = measurements["row_99_when_s"] - measurements["row_90_when_s"]
    return {
        "ngspice_returncode": result.returncode,
        "ngspice_stdout_tail": "\n".join(result.stdout.splitlines()[-40:]),
        "ngspice_stderr_tail": "\n".join(result.stderr.splitlines()[-20:]),
        **measurements,
    }


def build_report() -> dict[str, Any]:
    run = run_ngspice()
    passed = (
        run["ngspice_returncode"] == 0
        and run["row_final_v"] > 1.7
        and run["row_90_when_s"] > 0.0
        and run["row_99_when_s"] > run["row_90_when_s"]
    )
    return {
        "result_type": "converter_starter_extracted_rc_ngspice",
        "status": "starter_extracted_rc_ngspice_passed_not_converter_proof" if passed else "starter_extracted_rc_ngspice_failed",
        "source_netlist": rel(SOURCE_NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "supply_v": 1.8,
        "row_driver_r_ohm": 1000.0,
        "column_load_r_ohm": 2250.0,
        "digital_load_r_ohm": 1000.0,
        "clock_load_r_ohm": 1000.0,
        **run,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "runs ngspice on the Magic-extracted starter macro capacitance network with explicit resistive drivers and loads",
            "not_allowed": "does not simulate transistor converter behavior, comparator offset, DAC linearity, ADC decision error, supply current integration, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["measurement", "value"],
        )
        writer.writeheader()
        for key in ["row_final_v", "column_peak_v", "digital_peak_v", "row_90_when_s", "row_99_when_s", "row_90_to_99_s"]:
            writer.writerow({"measurement": key, "value": report[key]})


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Starter Extracted RC Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- source netlist: `{report['source_netlist']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- ngspice returncode: `{report['ngspice_returncode']}`",
        f"- row final V: `{report['row_final_v']:.9f}`",
        f"- column peak V: `{report['column_peak_v']:.9f}`",
        f"- digital peak V: `{report['digital_peak_v']:.9f}`",
        f"- row 90 when s: `{report['row_90_when_s']:.6e}`",
        f"- row 99 when s: `{report['row_99_when_s']:.6e}`",
        f"- row 90 to 99 s: `{report['row_90_to_99_s']:.6e}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A node changes voltage only when charge moves onto or off of capacitance. The extracted Magic netlist gives the capacitances. The added resistors say how hard the outside circuit can push or pull those nodes. SPICE is now solving time-domain charge movement through that network instead of only using a one-line RC estimate.",
        "",
        "This proves a narrow thing: the starter macro boundary can be driven as an extracted RC load in ngspice, and the row-drive node reaches the requested voltage in this fixture. It does not prove a row DAC, a SAR ADC, a mux switch stack, or a replacement decision.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_starter_extracted_rc_ngspice")
    print(f"status,{report['status']}")
    print(f"ngspice_returncode,{report['ngspice_returncode']}")
    print(f"row_final_v,{report['row_final_v']:.9f}")
    print(f"row_90_when_s,{report['row_90_when_s']:.6e}")
    print(f"row_99_when_s,{report['row_99_when_s']:.6e}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0 if report["status"] == "starter_extracted_rc_ngspice_passed_not_converter_proof" else 1


if __name__ == "__main__":
    raise SystemExit(main())
