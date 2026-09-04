#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_ID_FIELDS = {
    "simulation.run_id": ("simulation", "run_id"),
    "energy.run_id": ("energy", "run_id"),
    "latency.run_id": ("latency", "run_id"),
    "noise.run_id": ("noise", "run_id"),
    "area.run_id": ("area", "run_id"),
    "break_even_rerun.run_id": ("break_even_rerun", "run_id"),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def placeholder_string(value: Any) -> bool:
    return isinstance(value, str) and ("replace-with" in value.lower() or "replace_with" in value.lower())


def validate_same_run(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    provenance_run_id = provenance.get("run_id")
    if not nonempty_string(provenance_run_id):
        issues.append("provenance.run_id must name the post-layout or measured run")
    elif placeholder_string(provenance_run_id):
        issues.append("provenance.run_id must not be a placeholder")

    observed: dict[str, Any] = {}
    for field_name, (section_name, key) in RUN_ID_FIELDS.items():
        section = payload.get(section_name) if isinstance(payload.get(section_name), dict) else {}
        value = section.get(key)
        observed[field_name] = value
        if not nonempty_string(value):
            issues.append(f"{field_name} must match provenance.run_id")
        elif placeholder_string(value):
            issues.append(f"{field_name} must not be a placeholder")

    if nonempty_string(provenance_run_id):
        for field_name, value in observed.items():
            if nonempty_string(value) and value != provenance_run_id:
                issues.append(f"{field_name} must equal provenance.run_id")

    if payload.get("template_only") is True:
        issues.append("template payloads cannot pass same-run consistency")
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check that post-layout converter payload values come from one named run.")
    parser.add_argument("payload", type=Path)
    parser.add_argument("--expect-reject", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    if not payload_path.exists():
        raise SystemExit(f"payload not found: {payload_path}")
    issues = validate_same_run(load_json(payload_path))
    if args.expect_reject:
        if not issues:
            print("FAIL converter_post_layout_same_run: payload accepted under --expect-reject", file=sys.stderr)
            return 1
        print("PASS converter_post_layout_same_run_rejected")
        print(f"payload,{payload_path}")
        print(f"issues,{len(issues)}")
        print(f"first_issue,{issues[0]}")
        return 0
    if issues:
        print("FAIL converter_post_layout_same_run", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("PASS converter_post_layout_same_run")
    print(f"payload,{payload_path}")
    print("same_run_consistent,True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
