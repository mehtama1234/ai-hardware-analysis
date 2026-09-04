#!/usr/bin/env python3
"""Generate the converter post-layout readiness checklist."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sources" / "evidence" / "converter-circuit-evidence-schema.json"
CONTRACT = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.json"
CIRCUIT_SIM = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json"
HANDOFF = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.json"
ROW_DAC = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.json"
SAR_READOUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sar-readout-spice-evidence.json"
SHARED_LOADING = ROOT / "evidence" / "aimc-simulator-adapters" / "shared-converter-loading-spice-evidence.json"
SUPPLY_ENERGY = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-supply-energy-spice-evidence.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-readiness.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-readiness.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def summary_status(payload: dict) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    return str(summary.get("status", "missing"))


def main() -> None:
    schema = load_json(SCHEMA)
    contract = load_json(CONTRACT)
    circuit_sim = load_json(CIRCUIT_SIM)
    handoff = load_json(HANDOFF)
    row_dac = load_json(ROW_DAC)
    sar_readout = load_json(SAR_READOUT)
    shared_loading = load_json(SHARED_LOADING)
    supply_energy = load_json(SUPPLY_ENERGY)

    completed_local_tests = [
        summary_status(row_dac),
        summary_status(sar_readout),
        summary_status(shared_loading),
        summary_status(supply_energy),
    ]
    local_handoff_complete = all(status != "missing" for status in completed_local_tests)
    allowed_levels = set(schema.get("allowed_measurement_levels", []))
    replacement_levels = {"post_layout_simulation", "measured_silicon"}
    replacement_levels_available = bool(allowed_levels & replacement_levels)
    circuit_validation = circuit_sim.get("validation") if isinstance(circuit_sim.get("validation"), dict) else {}
    handoff_tests = handoff.get("required_testbenches") if isinstance(handoff.get("required_testbenches"), list) else []
    missing_for_replacement = [
        "extracted parasitic netlist for row DAC, SAR readout, shared mux, references, and sample path",
        "post-layout simulation command, process corner, voltage, temperature, and model files",
        "post-layout ADC energy per conversion on a named rail",
        "post-layout DAC energy per row drive on a named rail",
        "post-layout mux and reference energy tied to the same conversion window",
        "post-layout settling time and conversion time for the same 10-bit input and 12-bit output target",
        "post-layout output noise RMS and input-referred noise under the 0.004 output-noise budget",
        "extracted ADC and DAC area in square micrometers",
        "explicit sharing rule for 64 rows, 4 columns, 4 converter instances, and 16 outputs per conversion cost",
        "rerun break-even table using the extracted energy, latency, area, sharing, and noise values",
    ]
    payload = {
        "result_type": "converter_post_layout_readiness",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "schema": str(SCHEMA.relative_to(ROOT)),
            "contract": str(CONTRACT.relative_to(ROOT)),
            "converter_circuit_simulation_estimate": str(CIRCUIT_SIM.relative_to(ROOT)),
            "converter_spice_handoff_spec": str(HANDOFF.relative_to(ROOT)),
            "row_dac_settling_spice": str(ROW_DAC.relative_to(ROOT)),
            "sar_readout_spice": str(SAR_READOUT.relative_to(ROOT)),
            "shared_converter_loading_spice": str(SHARED_LOADING.relative_to(ROOT)),
            "converter_supply_energy_spice": str(SUPPLY_ENERGY.relative_to(ROOT)),
        },
        "current_local_state": {
            "local_handoff_complete": local_handoff_complete,
            "completed_testbenches": [test.get("name") for test in handoff_tests if isinstance(test, dict)],
            "completed_statuses": completed_local_tests,
            "circuit_simulation_schema_complete": circuit_validation.get("schema_complete"),
            "circuit_simulation_meets_output_noise_budget": ((circuit_sim.get("estimate") or {}).get("noise") or {}).get("meets_output_noise_budget") if isinstance(circuit_sim.get("estimate"), dict) else False,
            "circuit_simulation_claim_ready_to_replace_break_even": circuit_validation.get("claim_ready_to_replace_break_even"),
        },
        "replacement_rule": {
            "allowed_measurement_levels": schema.get("allowed_measurement_levels", []),
            "break_even_replacement_levels": sorted(replacement_levels),
            "replacement_levels_available_in_schema": replacement_levels_available,
            "current_measurement_level": (circuit_sim.get("estimate") or {}).get("measurement_level") if isinstance(circuit_sim.get("estimate"), dict) else "missing",
            "claim_ready_now": False,
            "reason": "local SPICE evidence is useful circuit simulation, but the schema only allows post-layout simulation or measured silicon to replace break-even assumptions",
        },
        "missing_for_replacement": missing_for_replacement,
        "claim_boundary": {
            "allowed": "defines the exact post-layout evidence needed after local converter SPICE handoff completion",
            "not_allowed": "does not claim post-layout extraction exists, does not claim DRC/LVS signoff, does not claim measured silicon, and does not upgrade board energy",
        },
        "validation": {
            "status": "local_converter_handoff_complete_post_layout_not_ready",
            "local_handoff_complete": local_handoff_complete,
            "claim_ready_to_replace_break_even": False,
            "missing_replacement_items": len(missing_for_replacement),
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Converter Post-Layout Readiness",
        "",
        "This file turns the completed local converter SPICE handoff into the next stricter gate.",
        "",
        f"- status: `{payload['validation']['status']}`",
        f"- local converter handoff complete: `{payload['validation']['local_handoff_complete']}`",
        f"- claim-ready to replace break-even: `{payload['validation']['claim_ready_to_replace_break_even']}`",
        f"- current measurement level: `{payload['replacement_rule']['current_measurement_level']}`",
        f"- missing replacement items: `{payload['validation']['missing_replacement_items']}`",
        "",
        "## First-Principles Reading",
        "",
        "A clean SPICE load model answers whether the chosen converter target is internally coherent. Post-layout evidence answers a different question: whether the same circuit still works after wires, device sizes, parasitic capacitance, routing resistance, reference paths, and physical area are present.",
        "",
        "The break-even table is about cost. Cost cannot be replaced by a schematic-level or load-model number if layout changes capacitance, routing, area, or timing. The replacement artifact must therefore carry post-layout energy, extracted latency, extracted noise, extracted area, and the same sharing rule into the break-even calculation.",
        "",
        "## Completed Local Handoff Tests",
        "",
    ]
    for status in completed_local_tests:
        lines.append(f"- `{status}`")
    lines.extend(
        [
            "",
            "## Missing Before Break-Even Replacement",
            "",
            *[f"- {item}" for item in missing_for_replacement],
            "",
            "## Refused Claim",
            "",
            payload["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("converter_post_layout_readiness")
    print(f"status,{payload['validation']['status']}")
    print(f"local_handoff_complete,{local_handoff_complete}")
    print(f"claim_ready,{payload['validation']['claim_ready_to_replace_break_even']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
