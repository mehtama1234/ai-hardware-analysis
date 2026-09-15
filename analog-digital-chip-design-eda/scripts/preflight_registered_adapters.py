#!/usr/bin/env python3
"""Emit deployment evidence for registered EDA adapter availability."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deployment.adapter_registry import adapter_payload


def run(raw_registry: str | None, output: Path) -> dict[str, object]:
    errors: list[str] = []
    try:
        adapters = adapter_payload(raw_registry)
    except ValueError as error:
        adapters = []
        errors.append(str(error))
    if not adapters:
        errors.append("at least one registered adapter is required")
    result: dict[str, object] = {
        "schema_version": "verification-registered-adapters-preflight-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "adapters": adapters,
        "adapter_count": len(adapters),
        "available_count": sum(1 for item in adapters if item["available"]),
        "blocked_count": sum(1 for item in adapters if item["status"] == "blocked"),
        "verified": not errors and all(item["available"] for item in adapters),
        "errors": errors,
        "claim_boundary": "Executable availability preflight only; this does not prove adapter correctness, simulator/formal/regression semantics, licensing, or customer production readiness.",
    }
    result["sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", help="JSON adapter registry; defaults to VERIFICATION_EDA_ADAPTERS")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.registry, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
