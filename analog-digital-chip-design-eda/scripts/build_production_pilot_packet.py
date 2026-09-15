#!/usr/bin/env python3
"""Bind deployed-flight and pilot evidence into one content-addressed packet."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    paths = {
        "flight": ROOT / ".artifacts/production-pilot-flight.json",
        "scorecard": ROOT / ".artifacts/customer-pilot-scorecard.json",
        "adversarial": ROOT / ".artifacts/workbench-adversarial/judge-packet.json",
        "replay": ROOT / ".artifacts/public-reference-replay.json",
        "handoff": ROOT / ".artifacts/commercial-handoff-manifest.json",
    }
    for name, path in paths.items():
        if not path.is_file():
            raise SystemExit(f"missing required {name} evidence: {path}")
    flight = json.loads(paths["flight"].read_text())
    scorecard = json.loads(paths["scorecard"].read_text())
    adversarial = json.loads(paths["adversarial"].read_text())
    replay = json.loads(paths["replay"].read_text())
    handoff = json.loads(paths["handoff"].read_text())
    packet = {"schema_version": "production-pilot-packet-v1", "flight": {"path": str(paths["flight"].relative_to(ROOT)), "sha256": hashlib.sha256(paths["flight"].read_bytes()).hexdigest(), "project_id": flight["project"]["id"], "job_status_after_restart": flight["job_status_after_restart"]}, "scorecard": {"path": str(paths["scorecard"].relative_to(ROOT)), "sha256": hashlib.sha256(paths["scorecard"].read_bytes()).hexdigest(), "sample_size": scorecard["pilot"]["sample_size"]}, "adversarial": {"path": str(paths["adversarial"].relative_to(ROOT)), "sha256": hashlib.sha256(paths["adversarial"].read_bytes()).hexdigest(), "gate_passed": adversarial["deterministic_gate"]["passed"]}, "archive_replay": {"path": str(paths["replay"].relative_to(ROOT)), "sha256": hashlib.sha256(paths["replay"].read_bytes()).hexdigest(), "replay": replay["replay"], "passed_retests": replay["passed_retests"], "design_count": replay["design_count"]}, "commercial_manifest": {"path": str(paths["handoff"].relative_to(ROOT)), "sha256": hashlib.sha256(paths["handoff"].read_bytes()).hexdigest()}, "claim_boundary": "Reference pilot handoff evidence only; no enterprise production, exhaustive coverage, formal completeness, silicon correctness, or measured customer ROI claim."
    }
    packet["packet_sha256"] = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = ROOT / ".artifacts/production-pilot-packet.json"
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"packet": str(output), "packet_sha256": packet["packet_sha256"], "gate": "passed"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
