#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run" / "converter-post-layout-evidence.placeholder.json"
VALIDATOR = ROOT / "scripts" / "validate_converter_post_layout_payload.py"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-validator.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-validator.md"


def main() -> None:
    if not PLACEHOLDER.exists():
        raise SystemExit(f"missing placeholder payload: {PLACEHOLDER}")
    result = subprocess.run(
        ["python3", str(VALIDATOR), "--expect-reject", str(PLACEHOLDER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    passed = result.returncode == 0 and "PASS converter_post_layout_payload_rejected" in result.stdout
    payload = {
        "result_type": "converter_post_layout_payload_validator_report",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "post_layout_payload_validator_ready_waiting_for_extracted_payload" if passed else "post_layout_payload_validator_failed",
        "validator": str(VALIDATOR.relative_to(ROOT)),
        "schema": "sources/evidence/converter-post-layout-evidence-schema.json",
        "rejected_placeholder": passed,
        "placeholder_payload": str(PLACEHOLDER.relative_to(ROOT)),
        "placeholder_returncode": result.returncode,
        "placeholder_stdout": result.stdout.strip().splitlines(),
        "placeholder_stderr": result.stderr.strip().splitlines(),
        "accepted_payload_boundary": {
            "measurement_level": ["post_layout_simulation", "measured_silicon"],
            "adc_bits": 12,
            "dac_bits": 10,
            "max_output_noise_rms": 0.004,
            "sharing": {
                "rows_served": 64,
                "columns_served": 4,
                "outputs_per_conversion_cost": 16,
                "converter_instances": 4,
            },
            "requires_extracted_energy_latency_noise_area": True,
            "requires_break_even_rerun_with_extracted_values": True,
        },
        "claim_boundary": {
            "allowed": "proves that the placeholder is rejected and that future post-layout payloads have an executable acceptance gate",
            "not_allowed": "does not provide an extracted netlist, post-layout simulation, measured silicon, or a replacement break-even result",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Payload Validator",
        "",
        "This report turns the post-layout converter contract into an executable gate.",
        "",
        f"- status: `{payload['status']}`",
        f"- rejected placeholder: `{payload['rejected_placeholder']}`",
        f"- validator: `{payload['validator']}`",
        f"- placeholder payload: `{payload['placeholder_payload']}`",
        "",
        "## First-Principles Reading",
        "",
        "The hard question is not whether a converter number exists. The question is whether the number came from the same physical object that the system wants to use. A post-layout payload must therefore name the extracted circuit, the simulation conditions, the measured energy, the measured time, the measured noise, the measured area, and the break-even rerun that consumed those values.",
        "",
        "The placeholder intentionally has the right shape and the wrong evidence. The validator rejects it because it has no extracted netlist, no model files, no positive energy, no positive timing, no area, no passing noise result, and no break-even rerun using extracted values.",
        "",
        "## Accepted Payload Boundary",
        "",
        "- measurement level must be `post_layout_simulation` or `measured_silicon`",
        "- target must remain 10-bit input and 12-bit output",
        "- output noise RMS must be at or below `0.004`",
        "- sharing must remain 64 rows, 4 columns, 4 converters, and 16 outputs per conversion cost",
        "- break-even must be rerun with extracted energy, latency, noise, area, and the same sharing rule",
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if not passed:
        raise SystemExit("validator did not reject placeholder")
    print("converter_post_layout_payload_validator")
    print(f"status,{payload['status']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
