#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
SWEEP = SIM_EVIDENCE / "aihwkit-forward-setting-sweep.json"
TILE_CSV = LAB / "tile-operating-point.csv"
OUT_JSON = SIM_EVIDENCE / "aihwkit-physical-setting-review.json"
OUT_MD = SIM_EVIDENCE / "aihwkit-physical-setting-review.md"


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_tile() -> dict[str, str]:
    if not TILE_CSV.exists():
        raise SystemExit(f"missing tile operating point: {TILE_CSV}")
    with TILE_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"empty tile operating point: {TILE_CSV}")
    return rows[0]


def setting_by_id(sweep: dict[str, object], setting_id: str) -> dict[str, object]:
    settings = sweep.get("settings") if isinstance(sweep.get("settings"), list) else []
    for item in settings:
        if isinstance(item, dict) and item.get("id") == setting_id:
            return item
    raise SystemExit(f"missing setting {setting_id}")


def main() -> int:
    sweep = load_json(SWEEP)
    tile = load_tile()
    fine = setting_by_id(sweep, "fine_resolution_no_output_noise")
    ideal = setting_by_id(sweep, "ideal_resolution_no_output_noise")
    fine_summary = fine["summary"] if isinstance(fine.get("summary"), dict) else {}
    ideal_summary = ideal["summary"] if isinstance(ideal.get("summary"), dict) else {}
    tile_adc_bits = int(float(tile["adc_bits"]))
    tile_dac_bits = int(float(tile["dac_bits"]))
    tile_converter_error = float(tile["converter_relative_error"])
    tile_energy = float(tile["converter_energy_relative"])
    fine_effective_input_steps = 1024
    fine_effective_output_steps = 4096
    fine_input_bits = 10
    fine_output_bits = 12
    fine_max_residual = float(fine_summary["max_residual_relative"])
    review_status = "needs_physical_justification"
    if fine_input_bits <= tile_dac_bits and fine_output_bits <= tile_adc_bits and fine_max_residual <= tile_converter_error:
        review_status = "aligned_with_current_tile_boundary"
    payload = {
        "result_type": "aihwkit_physical_setting_review",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "forward_setting_sweep": str(SWEEP.relative_to(ROOT)),
            "tile_operating_point": str(TILE_CSV.relative_to(ROOT)),
        },
        "candidate_setting": {
            "id": "fine_resolution_no_output_noise",
            "effective_input_steps": fine_effective_input_steps,
            "effective_output_steps": fine_effective_output_steps,
            "effective_input_bits": fine_input_bits,
            "effective_output_bits": fine_output_bits,
            "output_noise": 0.0,
            "passing_rows": fine_summary.get("passing_rows"),
            "rows": fine_summary.get("rows"),
            "max_residual_relative": fine_max_residual,
        },
        "ideal_setting": {
            "id": "ideal_resolution_no_output_noise",
            "max_residual_relative": ideal_summary.get("max_residual_relative"),
            "physical_reading": "numerically useful as an upper bound, not a converter claim",
        },
        "current_tile_boundary": {
            "adc_bits": tile_adc_bits,
            "dac_bits": tile_dac_bits,
            "converter_error": tile_converter_error,
            "converter_energy_x": tile_energy,
            "row_case_ohm": float(tile["row_drop_case_ohm"]),
            "row_loss_percent": float(tile["spice_row_drop_loss_pct"]),
        },
        "review": {
            "status": review_status,
            "reason": (
                "The passing AIHWKIT fine-resolution setting assumes about 10 effective input bits, 12 effective output bits, and zero output noise. "
                "The current tile operating point is 4-bit DAC, 6-bit ADC, and nonzero converter error. "
                "So the setting is a target for a stronger analog boundary, not evidence that the current tile has that boundary."
            ),
            "next_proof": "either derive a 10-bit input and 12-bit output converter boundary with an energy/latency cost, or rerun AIHWKIT with the existing 4-bit DAC and 6-bit ADC tile boundary and accept the residual result",
        },
        "claim_boundary": {
            "allowed": "connects the passing AIHWKIT sweep setting to the current tile converter boundary",
            "not_allowed": "does not claim the current tile already has 10-bit input, 12-bit output, zero-noise behavior",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        "# AIHWKIT Physical Setting Review",
        "",
        "This review connects the passing AIHWKIT forward setting to the physical tile boundary.",
        "",
        f"- review status: `{review_status}`",
        f"- candidate setting: `fine_resolution_no_output_noise`",
        f"- candidate residual: `{fine_max_residual:.6f}`",
        f"- candidate effective input bits: `{fine_input_bits}`",
        f"- candidate effective output bits: `{fine_output_bits}`",
        f"- current tile DAC bits: `{tile_dac_bits}`",
        f"- current tile ADC bits: `{tile_adc_bits}`",
        f"- current tile converter error: `{tile_converter_error:.6f}`",
        "",
        "## First-Principles Reading",
        "",
        "A passing simulator setting is not automatically a hardware setting. The simulator setting says how finely the input and output are represented and how much output noise is allowed. The tile operating point says what the local circuit evidence currently pays for.",
        "",
        "The passing AIHWKIT setting uses about 10 effective input bits and 12 effective output bits with zero output noise. The current tile boundary is 4-bit DAC and 6-bit ADC with a measured converter-error budget. Those are not the same claim.",
        "",
        "So the setting is useful, but only as a target. It tells us what kind of converter and noise boundary would make AIHWKIT pass on these rows. It does not prove that the current tile already has that boundary.",
        "",
        "## Concrete Next Proof",
        "",
        "Either derive a 10-bit input and 12-bit output converter boundary with its energy, latency, area, and calibration cost, or rerun AIHWKIT using the existing 4-bit DAC and 6-bit ADC boundary and accept the residual result.",
        "",
        "## Refused Claim",
        "",
        "This review does not prove measured silicon, measured board runtime, measured power, macro layout, PCM device accuracy, or production readiness. It does not weaken the guarded importer threshold.",
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print("aihwkit_physical_setting_review")
    print(f"status,{review_status}")
    print(f"candidate_residual,{fine_max_residual}")
    print(f"candidate_effective_bits,{fine_input_bits},{fine_output_bits}")
    print(f"tile_bits,{tile_dac_bits},{tile_adc_bits}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
