#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rerun_converter_break_even_from_post_layout_payload import build_rerun
from validate_converter_post_layout_same_run import validate_same_run
from validate_converter_post_layout_payload import SCHEMA, load_json, validate_payload, validate_referenced_files


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout"


def slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif cleaned and cleaned[-1] != "-":
            cleaned.append("-")
    return "".join(cleaned).strip("-") or "converter-post-layout"


def write_submission_report(
    payload_path: Path,
    output_dir: Path,
    rerun: dict[str, Any],
    analog_mac_energy_j: float,
    digital_mac_energy_j: float,
) -> tuple[Path, Path]:
    converter_id = slug(str(rerun["source_payload"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    rerun_path = output_dir / f"{converter_id}.break-even-rerun.json"
    report_path = output_dir / f"{converter_id}.submission-report.json"
    rerun_path.write_text(json.dumps(rerun, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = {
        "result_type": "converter_post_layout_submission_report",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "accepted_post_layout_payload_rerun_written",
        "source_payload_path": str(payload_path),
        "rerun_artifact": str(rerun_path),
        "replacement_decision": rerun["summary"]["replacement_decision"],
        "claim_ready_to_replace_break_even": rerun["summary"]["claim_ready_to_replace_break_even"],
        "analog_mac_energy_j": analog_mac_energy_j,
        "digital_mac_energy_j": digital_mac_energy_j,
        "claim_boundary": {
            "allowed": "records that a strict post-layout or measured-silicon payload passed intake and produced a rerun artifact",
            "not_allowed": "does not prove full chip performance, board power, another workload, or production readiness",
        },
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rerun_path, report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strictly validate and submit a real converter post-layout payload.")
    parser.add_argument("payload", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--analog-mac-energy-j", type=float, default=1.0e-15)
    parser.add_argument("--digital-mac-energy-j", type=float, default=1.0e-14)
    parser.add_argument("--expect-reject", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    schema = load_json(SCHEMA)
    payload = load_json(payload_path)
    issues = validate_payload(payload, schema)
    issues.extend(validate_referenced_files(payload, payload_path))
    issues.extend(validate_same_run(payload))
    if payload.get("template_only") is True:
        issues.append("template payloads cannot be submitted")
    if issues:
        if args.expect_reject:
            print("PASS converter_post_layout_submission_rejected")
            print(f"payload,{payload_path}")
            print(f"issues,{len(issues)}")
            print(f"first_issue,{issues[0]}")
            return 0
        print("FAIL converter_post_layout_submission", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    if args.expect_reject:
        print("FAIL converter_post_layout_submission: payload accepted under --expect-reject", file=sys.stderr)
        return 1
    rerun = build_rerun(payload, args.analog_mac_energy_j, args.digital_mac_energy_j)
    rerun_path, report_path = write_submission_report(
        payload_path,
        args.output_dir.resolve(),
        rerun,
        args.analog_mac_energy_j,
        args.digital_mac_energy_j,
    )
    print("PASS converter_post_layout_submission")
    print(f"payload,{payload_path}")
    print(f"replacement_decision,{rerun['summary']['replacement_decision']}")
    print(f"rerun_artifact,{rerun_path}")
    print(f"submission_report,{report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
