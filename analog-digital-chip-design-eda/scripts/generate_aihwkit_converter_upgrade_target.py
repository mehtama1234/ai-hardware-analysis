#!/usr/bin/env python3
"""Generate the concrete AIHWKIT converter/noise upgrade target."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHYSICAL_REVIEW = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-physical-setting-review.json"
TILE_REPLAY = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-current-tile-boundary-replay.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-upgrade-target.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-upgrade-target.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def steps(bits: int) -> int:
    return (2**bits) - 1


def main() -> None:
    physical = load_json(PHYSICAL_REVIEW)
    replay = load_json(TILE_REPLAY)
    candidate = physical.get("candidate_setting") if isinstance(physical.get("candidate_setting"), dict) else {}
    tile = physical.get("current_tile_boundary") if isinstance(physical.get("current_tile_boundary"), dict) else {}
    replay_summary = replay.get("summary") if isinstance(replay.get("summary"), dict) else {}

    current_dac_bits = int(tile.get("dac_bits", 0))
    current_adc_bits = int(tile.get("adc_bits", 0))
    target_input_bits = int(candidate.get("effective_input_bits", 0))
    target_output_bits = int(candidate.get("effective_output_bits", 0))
    current_input_steps = steps(current_dac_bits)
    current_output_steps = steps(current_adc_bits)
    target_input_steps = int(candidate.get("effective_input_steps") or steps(target_input_bits))
    target_output_steps = int(candidate.get("effective_output_steps") or steps(target_output_bits))

    target = {
        "result_type": "aihwkit_converter_upgrade_target",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "physical_setting_review": str(PHYSICAL_REVIEW.relative_to(ROOT)),
            "current_tile_replay": str(TILE_REPLAY.relative_to(ROOT)),
        },
        "status": "target_defined_not_justified",
        "current_boundary": {
            "dac_bits": current_dac_bits,
            "adc_bits": current_adc_bits,
            "input_steps": current_input_steps,
            "output_steps": current_output_steps,
            "current_tile_passing_rows": replay_summary.get("passing_rows"),
            "current_tile_failing_rows": replay_summary.get("failing_rows"),
            "current_tile_max_residual_relative": replay_summary.get("max_residual_relative"),
        },
        "minimum_passing_aihwkit_target": {
            "setting": candidate.get("id"),
            "effective_input_bits": target_input_bits,
            "effective_output_bits": target_output_bits,
            "input_steps": target_input_steps,
            "output_steps": target_output_steps,
            "output_noise": candidate.get("output_noise"),
            "passing_rows": candidate.get("passing_rows"),
            "rows": candidate.get("rows"),
            "max_residual_relative": candidate.get("max_residual_relative"),
        },
        "gap": {
            "input_bit_gap": target_input_bits - current_dac_bits,
            "output_bit_gap": target_output_bits - current_adc_bits,
            "input_step_ratio": target_input_steps / current_input_steps if current_input_steps else None,
            "output_step_ratio": target_output_steps / current_output_steps if current_output_steps else None,
        },
        "required_next_evidence": [
            "converter architecture for the target input and output precision",
            "noise budget showing why zero-output-noise simulation is a valid approximation or what nonzero noise remains",
            "energy per conversion or per MatMul row under the stronger converter boundary",
            "latency per conversion or per MatMul row under the stronger converter boundary",
            "area or macro-level placement cost for the stronger converter boundary",
            "calibration method that maps device conductance and converter range to the held-out MatMul rows",
            "AIHWKIT replay that passes held-out rows without weakening the guarded importer threshold",
        ],
        "claim_boundary": {
            "allowed": "defines the concrete converter and noise target implied by the passing AIHWKIT sweep setting",
            "not_allowed": "does not prove the current 4-bit DAC and 6-bit ADC tile has this target precision, noise, energy, latency, area, or calibration behavior",
        },
    }

    OUT_JSON.write_text(json.dumps(target, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    gap = target["gap"]
    md = [
        "# AIHWKIT Converter Upgrade Target",
        "",
        "This artifact turns the AIHWKIT sweep result into a concrete design target.",
        "",
        f"- status: `{target['status']}`",
        f"- source physical review: `{target['source_artifacts']['physical_setting_review']}`",
        f"- source current-tile replay: `{target['source_artifacts']['current_tile_replay']}`",
        "",
        "## Current Boundary",
        "",
        f"- DAC bits: `{current_dac_bits}`",
        f"- ADC bits: `{current_adc_bits}`",
        f"- input steps: `{current_input_steps}`",
        f"- output steps: `{current_output_steps}`",
        f"- current-tile passing rows: `{replay_summary.get('passing_rows')}`",
        f"- current-tile failing rows: `{replay_summary.get('failing_rows')}`",
        f"- current-tile max residual: `{replay_summary.get('max_residual_relative')}`",
        "",
        "## Minimum Passing Target",
        "",
        f"- AIHWKIT setting: `{candidate.get('id')}`",
        f"- effective input bits: `{target_input_bits}`",
        f"- effective output bits: `{target_output_bits}`",
        f"- input steps: `{target_input_steps}`",
        f"- output steps: `{target_output_steps}`",
        f"- output noise: `{candidate.get('output_noise')}`",
        f"- passing rows: `{candidate.get('passing_rows')}` of `{candidate.get('rows')}`",
        f"- max residual: `{candidate.get('max_residual_relative')}`",
        "",
        "## Precision Gap",
        "",
        f"- input bit gap: `{gap['input_bit_gap']}`",
        f"- output bit gap: `{gap['output_bit_gap']}`",
        f"- input step ratio: `{gap['input_step_ratio']:.3f}`",
        f"- output step ratio: `{gap['output_step_ratio']:.3f}`",
        "",
        "## First-Principles Reading",
        "",
        "The current tile does not fail because the MatMul shape is wrong. The ideal-forward proof already showed that the row, column, sign, and weight orientation are correct. It fails when the signal has to pass through the coarse input and output bins of the current tile.",
        "",
        "The passing setting gives a target, not a victory. It says the same rows pass when the input side is represented with about 10 effective bits, the output side with about 12 effective bits, and output noise is removed from this local test. Compared with the current tile, that is six more input bits and six more output bits. In step terms, the input must be about 68 times finer and the output about 65 times finer.",
        "",
        "That extra precision is not free. The next design has to pay for it with converter architecture, range selection, calibration, energy, latency, area, and a noise budget. If that cost is too high, the correct architecture is not to force analog placement. The correct architecture is to keep those rows on the digital path.",
        "",
        "## Required Next Evidence",
        "",
        *[f"- {item}" for item in target["required_next_evidence"]],
        "",
        "## Refused Claim",
        "",
        target["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print("aihwkit_converter_upgrade_target")
    print(f"status,{target['status']}")
    print(f"current_bits,{current_dac_bits},{current_adc_bits}")
    print(f"target_bits,{target_input_bits},{target_output_bits}")
    print(f"input_step_ratio,{gap['input_step_ratio']:.3f}")
    print(f"output_step_ratio,{gap['output_step_ratio']:.3f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
