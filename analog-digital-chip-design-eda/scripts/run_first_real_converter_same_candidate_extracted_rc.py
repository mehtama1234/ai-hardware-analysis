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
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
CANDIDATE_DIR = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
NETLIST = CANDIDATE_DIR / "netlist" / "aimc_readout_candidate_001_extracted.spice"
DECK_OUT = SPICE_DIR / "aimc_readout_candidate_001_extracted_rc_measurement.sp"
CSV_OUT = MEASUREMENTS / "first-real-converter-same-candidate-extracted-rc.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-same-candidate-extracted-rc.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-same-candidate-extracted-rc.md"

CANDIDATE_ID = "aimc_readout_candidate_001"
RUN_ID = "aimc_readout_candidate_001_extracted_rc_run001"


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
    return f"""* Same-candidate extracted-RC fixture for aimc_readout_candidate_001.
* This includes the assembled candidate netlist and measures charge movement on its extracted capacitances.
* It is not a transistor converter proof.

.global VSUBS
.include "{NETLIST}"

VDD vdd 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VREFP vrefp 0 1.2
VREFN vrefn 0 0.6
VROW row_src 0 PULSE(0 1.8 0.1n 20p 20p 5n 10n)
VSENSE sense_src 0 PULSE(0.9 0.92 0.25n 20p 20p 5n 10n)
VCLK clk_src 0 PULSE(0 1.8 0.2n 20p 20p 1n 2n)
RROW row_src row_drive 1000
RSENSE sense_src column_sense 2000
RCLK clk_src sample_clock 1000
RDIG digital_code_out 0 1000

XCAND vss vdd row_drive column_sense digital_code_out sample_clock vrefp vrefn {CANDIDATE_ID}

.tran 1p 2n
.measure tran row_final FIND v(row_drive) AT=1.5n
.measure tran sense_final FIND v(column_sense) AT=1.5n
.measure tran clock_peak MAX v(sample_clock) FROM=0.2n TO=1.2n
.measure tran digital_peak MAX v(digital_code_out) FROM=0.1n TO=2n
.measure tran row_90_when WHEN v(row_drive)=1.62 RISE=1
.measure tran row_99_when WHEN v(row_drive)=1.782 RISE=1
.measure tran sense_delta PARAM='abs(sense_final - 0.92)'
.control
run
.endc

.end
"""


def run_ngspice() -> dict[str, Any]:
    if not NETLIST.exists():
        raise FileNotFoundError(NETLIST)
    SPICE_DIR.mkdir(parents=True, exist_ok=True)
    DECK_OUT.write_text(build_deck(), encoding="utf-8")
    result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
    measurements = {
        "row_final_v": read_measure(result.stdout, "row_final"),
        "sense_final_v": read_measure(result.stdout, "sense_final"),
        "clock_peak_v": read_measure(result.stdout, "clock_peak"),
        "digital_peak_v": read_measure(result.stdout, "digital_peak"),
        "row_90_when_s": read_measure(result.stdout, "row_90_when"),
        "row_99_when_s": read_measure(result.stdout, "row_99_when"),
        "sense_delta_v": read_measure(result.stdout, "sense_delta"),
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
        and run["sense_delta_v"] < 0.01
        and run["row_99_when_s"] > run["row_90_when_s"] > 0.0
    )
    return {
        "result_type": "first_real_converter_same_candidate_extracted_rc",
        "status": "same_candidate_extracted_rc_passed_not_strict_accepted_evidence" if passed else "same_candidate_extracted_rc_failed",
        "candidate_id": CANDIDATE_ID,
        "run_id": RUN_ID,
        "source_netlist": rel(NETLIST),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "uses_assembled_candidate_netlist": True,
        "uses_transistor_converter_behavior": False,
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "strict_payload_written": False,
        "strict_blockers": [
            "The assembled candidate netlist contains extracted capacitances from starter cells, not transistor-level DAC, mux, sample path, comparator, SAR, and reference circuits.",
            "The run measures driven RC settling on the same candidate object, not supply current integration from active converter devices.",
            "The run has no comparator decision, no ADC code transition, no DAC linearity check, no DRC/LVS signoff area, and no same-run break-even replacement payload.",
        ],
        "claim_boundary": {
            "allowed": "the named assembled candidate can be included and driven as one extracted-RC object in ngspice",
            "not_allowed": "accepted post-layout converter evidence, transistor converter correctness, ADC/DAC accuracy, or replacement of the strict break-even payload",
        },
        **run,
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["measurement", "value"])
        writer.writeheader()
        for key in [
            "row_final_v",
            "sense_final_v",
            "clock_peak_v",
            "digital_peak_v",
            "row_90_when_s",
            "row_99_when_s",
            "row_90_to_99_s",
            "sense_delta_v",
        ]:
            writer.writerow({"measurement": key, "value": report[key]})


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Same-Candidate Extracted RC",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- source netlist: `{report['source_netlist']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- ngspice returncode: `{report['ngspice_returncode']}`",
        f"- row final V: `{report['row_final_v']:.9f}`",
        f"- sense final V: `{report['sense_final_v']:.9f}`",
        f"- clock peak V: `{report['clock_peak_v']:.9f}`",
        f"- digital peak V: `{report['digital_peak_v']:.9f}`",
        f"- row 90 to 99 s: `{report['row_90_to_99_s']:.6e}`",
        f"- sense delta V: `{report['sense_delta_v']:.9f}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The first physical question is smaller than whether the converter is good. It is whether one named extracted object can be put into the circuit equations and driven through its pins. In this run, the candidate is not a set of disconnected estimates. The row pin, sense pin, clock pin, output pin, supplies, and references all belong to the same subcircuit instance.",
        "",
        "What SPICE solves here is charge movement through extracted capacitance. A voltage source does not instantly set every internal node. The driver resistors limit current. The extracted capacitances store charge. The measured settling time is the time needed for those capacitors to move close to the requested voltage in this fixture.",
        "",
        "That is useful because it closes one gap in the previous candidate loop: the physical object can be driven as one assembled netlist. It is still not enough to accept the converter. A real converter decision needs active devices, supply-current integration, comparator behavior, code error, signed area evidence, and a break-even rerun from the same accepted run.",
        "",
        "## Strict Blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in report["strict_blockers"])
    lines.extend(
        [
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
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_same_candidate_extracted_rc")
    print(f"status,{report['status']}")
    print(f"candidate_id,{report['candidate_id']}")
    print(f"run_id,{report['run_id']}")
    print(f"ngspice_returncode,{report['ngspice_returncode']}")
    print(f"row_final_v,{report['row_final_v']:.9f}")
    print(f"sense_delta_v,{report['sense_delta_v']:.9f}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0 if report["status"] == "same_candidate_extracted_rc_passed_not_strict_accepted_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
