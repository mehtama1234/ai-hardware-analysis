#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RERUN = ROOT / "scripts" / "rerun_converter_break_even_from_post_layout_payload.py"
PLACEHOLDER = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run" / "converter-post-layout-evidence.placeholder.json"
TEMPLATE = ROOT / "sources" / "evidence" / "converter-post-layout-payload.template.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-break-even-rerun-path.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-break-even-rerun-path.md"


def run_rejection(path: Path) -> dict[str, object]:
    result = subprocess.run(
        ["python3", str(RERUN), "--expect-reject", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "payload": str(path.relative_to(ROOT)),
        "returncode": result.returncode,
        "passed": result.returncode == 0 and "PASS converter_post_layout_break_even_rerun_rejected" in result.stdout,
        "stdout": result.stdout.strip().splitlines(),
        "stderr": result.stderr.strip().splitlines(),
    }


def main() -> None:
    checks = [run_rejection(PLACEHOLDER), run_rejection(TEMPLATE)]
    all_rejected = all(check["passed"] for check in checks)
    payload = {
        "result_type": "converter_post_layout_break_even_rerun_path",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "rerun_path_ready_waiting_for_validator_passing_payload" if all_rejected else "rerun_path_guard_failed",
        "rerun_script": str(RERUN.relative_to(ROOT)),
        "base_break_even": "evidence/aimc-simulator-adapters/aihwkit-converter-break-even.json",
        "rejection_checks": checks,
        "required_input": {
            "validator": "scripts/validate_converter_post_layout_payload.py",
            "measurement_level": ["post_layout_simulation", "measured_silicon"],
            "requires_extracted_energy": True,
            "requires_extracted_latency": True,
            "requires_extracted_noise": True,
            "requires_extracted_area": True,
            "requires_same_sharing_rule": True,
        },
        "claim_boundary": {
            "allowed": "defines the executable break-even rerun path after a post-layout or measured-silicon payload passes validation",
            "not_allowed": "does not supply a real post-layout payload and does not replace the current digital fallback decision",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Break-Even Rerun Path",
        "",
        "This report adds the executable step after post-layout payload validation.",
        "",
        f"- status: `{payload['status']}`",
        f"- rerun script: `{payload['rerun_script']}`",
        f"- base break-even: `{payload['base_break_even']}`",
        f"- rejected placeholder/template: `{all_rejected}`",
        "",
        "## First-Principles Reading",
        "",
        "Validation answers whether the payload is real enough to use. Break-even answers whether the real converter is worth using. These are different questions. A validated payload can still tell the system to keep the digital fallback if the converter energy, latency, area, noise, or sharing rule makes the analog path too expensive.",
        "",
        "The rerun script takes the extracted ADC energy, DAC energy, conversion time, settling time, noise, area, and sharing rule from the payload. It then recomputes the analog-output cost against a digital MAC baseline for the same served rows. The default decision comes from the payload sharing rule, not from the earlier local estimate.",
        "",
        "## Guarded Dry Run",
        "",
    ]
    for check in checks:
        lines.append(f"- `{check['payload']}` rejected: `{check['passed']}`")
    lines.extend(
        [
            "",
            "## How To Use With A Real Payload",
            "",
            "1. Fill `sources/evidence/converter-post-layout-payload.template.json` with extracted or measured values.",
            "2. Run `python3 scripts/validate_converter_post_layout_payload.py FILLED_PAYLOAD.json`.",
            "3. Run `python3 scripts/rerun_converter_break_even_from_post_layout_payload.py FILLED_PAYLOAD.json --output evidence/aimc-simulator-adapters/FILLED_BREAK_EVEN_RERUN.json`.",
            "4. Use the rerun decision, not the local planning estimate, as the converter replacement boundary.",
            "",
            "## Refused Claim",
            "",
            payload["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if not all_rejected:
        raise SystemExit("post-layout break-even rerun guard failed")
    print("converter_post_layout_break_even_rerun_path")
    print(f"status,{payload['status']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
