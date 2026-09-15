#!/usr/bin/env python3
"""Independently verify a flagship clean-checkout replay receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        receipt = {}
        errors.append(str(error))
    body = {key: value for key, value in receipt.items() if key != "replay_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if receipt.get("schema_version") != "flagship-clean-checkout-replay-v1":
        errors.append("unsupported replay schema")
    if receipt.get("replay_sha256") != expected:
        errors.append("replay receipt digest mismatch")
    checks = receipt.get("checks")
    if not isinstance(checks, list) or len(checks) != 19:
        errors.append("replay check set is incomplete")
    elif any(item.get("status") != "passed" or item.get("returncode") != 0 for item in checks if isinstance(item, dict)):
        errors.append("one or more clean-checkout checks did not pass")
    if receipt.get("status") != "passed":
        errors.append("replay status is not passed")
    result = {
        "schema_version": "flagship-clean-checkout-replay-check-v1",
        "status": "passed" if not errors else "blocked",
        "receipt": str(args.receipt.resolve()),
        "errors": sorted(set(errors)),
    }
    result["check_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
