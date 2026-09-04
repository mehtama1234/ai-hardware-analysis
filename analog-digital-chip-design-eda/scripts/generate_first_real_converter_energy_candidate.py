#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CANDIDATE = EVIDENCE / "candidate-post-layout"
OBJECT_AUDIT = EVIDENCE / "first-real-converter-physical-object-audit.json"
ENERGY_SOURCE = EVIDENCE / "converter-supply-energy-spice-evidence.json"
OUT_JSON = EVIDENCE / "first-real-converter-energy-candidate.json"
OUT_MD = EVIDENCE / "first-real-converter-energy-candidate.md"
MEASUREMENT_JSON = CANDIDATE / "measurements" / "readout-energy.json"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    object_audit = load_json(OBJECT_AUDIT)
    energy = load_json(ENERGY_SOURCE)
    if object_audit.get("ready_for_b1") is not True:
        raise SystemExit("B1 physical object must be ready before generating B2 candidate energy")
    summary = energy["summary"]
    target = energy["target"]
    measurement = {
        "result_type": "first_real_converter_readout_energy_candidate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "aimc_readout_candidate_001",
        "run_id": "aimc_readout_candidate_001_simple_load_energy_run001",
        "energy_level": "simple_load_spice_tied_to_named_candidate_not_extracted_power",
        "source_energy_artifact": rel(ENERGY_SOURCE),
        "source_netlist": object_audit["expected_extracted_netlist"],
        "adc_energy_per_conversion": summary["worst_adc_energy_j"],
        "dac_energy_per_row_drive": summary["worst_dac_energy_j"],
        "mux_energy_per_conversion": summary["worst_mux_energy_j"],
        "total_energy_per_conversion": summary["worst_total_energy_j"],
        "energy_unit": "joule",
        "rail_v": target["rail_v"],
        "settling_time_ns": target["settling_time_ns"],
        "conversion_time_ns": target["conversion_time_ns"],
        "method": "reuse local converter supply-energy SPICE simple-load run and bind the worst case to the named candidate object",
        "strict_payload_ready": False,
        "why_not_strict": [
            "the source energy deck is a simple switched-capacitance load model",
            "the energy was not integrated through the assembled extracted candidate netlist",
            "bias current, leakage, clock power, and comparator short-circuit current are still absent",
        ],
    }
    MEASUREMENT_JSON.parent.mkdir(parents=True, exist_ok=True)
    MEASUREMENT_JSON.write_text(json.dumps(measurement, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "result_type": "first_real_converter_energy_candidate",
        "created_at": measurement["created_at"],
        "status": "b2_energy_candidate_written_not_strict_extracted_energy",
        "candidate_id": measurement["candidate_id"],
        "run_id": measurement["run_id"],
        "measurement_artifact": rel(MEASUREMENT_JSON),
        "source_energy_artifact": rel(ENERGY_SOURCE),
        "source_netlist": measurement["source_netlist"],
        "adc_energy_per_conversion": measurement["adc_energy_per_conversion"],
        "dac_energy_per_row_drive": measurement["dac_energy_per_row_drive"],
        "mux_energy_per_conversion": measurement["mux_energy_per_conversion"],
        "total_energy_per_conversion": measurement["total_energy_per_conversion"],
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "creates a named-candidate energy candidate from existing simple-load SPICE energy evidence",
            "not_allowed": "does not replace extracted converter energy, does not fill the strict payload, and does not write accepted post-layout evidence",
        },
        "why_not_strict": measurement["why_not_strict"],
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Energy Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- measurement artifact: `{report['measurement_artifact']}`",
        f"- source netlist: `{report['source_netlist']}`",
        f"- ADC energy per conversion: `{report['adc_energy_per_conversion']}` J",
        f"- DAC energy per row drive: `{report['dac_energy_per_row_drive']}` J",
        f"- mux energy per conversion: `{report['mux_energy_per_conversion']}` J",
        f"- total energy per conversion: `{report['total_energy_per_conversion']}` J",
        f"- strict payload ready: `{report['strict_payload_ready']}`",
        "",
        "## First Principle",
        "",
        "Energy is charge moved through a voltage. For this converter path, the useful question is not only whether a voltage settles. The useful question is how much supply work is spent to create the row voltage, charge the readout reference, and move the muxed sample.",
        "",
        "This file binds the existing simple-load SPICE energy run to the named candidate object. That makes the energy discussion point at the same converter candidate as B1. It still does not become accepted energy, because accepted energy must be integrated through the extracted candidate path itself.",
        "",
        "## Why This Is Not Strict Yet",
        "",
    ]
    lines.extend(f"- {item}" for item in report["why_not_strict"])
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_energy_candidate")
    print(f"status,{report['status']}")
    print(f"measurement_artifact,{report['measurement_artifact']}")
    print(f"total_energy_per_conversion,{report['total_energy_per_conversion']}")
    print(f"strict_payload_ready,{report['strict_payload_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
