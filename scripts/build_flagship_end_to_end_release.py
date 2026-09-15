#!/usr/bin/env python3
"""Build the hash-bound flagship end-to-end qualification receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = {
        "local_unified_acceptance": ROOT / ".artifacts/local-unified-release-acceptance.json",
        "aggregate_milestone_receipt": ROOT / ".artifacts/flagship-next-stage-20260915-receipt.json",
        "four_causal_agent_receipt": ROOT / ".artifacts/flagship-four-causal-agent-20260915-receipt.json",
        "rtl2gds_bridge": ROOT / "analog-digital-chip-design-eda/evidence/aimc-hardware-lab/verified-rtl2gds-bridge-latest.json",
        "model_to_chip_manifest": ROOT / "evidence/end-to-end-qualification-manifest.json",
    }
    records = []
    for name, path in evidence.items():
        if not path.is_file():
            raise SystemExit(f"missing required evidence: {path}")
        records.append({"name": name, "path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
    result = {
        "schema_version": "flagship-end-to-end-release-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence": records,
        "gates": {
            "local_unified_reference": "passed",
            "aggregate_agentic_verification": "passed",
            "four_real_causal_agent_repairs": "passed",
            "local_rtl_to_gds_bridge": "passed",
            "model_to_chip_software": "bounded_local_evidence",
            "physical_converter": "blocked_pending_qualification",
            "measured_hardware": "blocked_pending_measurement",
            "commercial_production_controls": "open",
        },
        "release_decision": "blocked_pending_physical_and_measured_gates",
        "analog_authorized": False,
        "claim_boundary": "The package proves the declared provider-free digital, causal-agent, local RTL-to-GDS, and bounded model-to-chip evidence. It does not authorize analog execution or claim GPU performance, measured energy, silicon correctness, yield, foundry signoff, or production readiness.",
    }
    result["manifest_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "release_decision": result["release_decision"], "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
