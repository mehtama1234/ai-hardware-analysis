#!/usr/bin/env python3
"""Verify that a pilot scorecard still matches its referenced evidence files."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys


def verify(scorecard_path: Path, root: Path) -> list[str]:
    payload = json.loads(scorecard_path.read_text(encoding="utf-8"))
    digests = payload.get("evidence_sha256")
    if not isinstance(digests, dict) or not digests:
        return ["scorecard has no evidence_sha256 map"]
    errors: list[str] = []
    for raw_path, expected in digests.items():
        path = str(raw_path)
        candidate = (root / path).resolve()
        if Path(path).is_absolute() or "\\" in path or any(part in {"", ".", ".."} for part in path.split("/")) or root.resolve() not in candidate.parents:
            errors.append(f"unsafe evidence path: {path}")
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", str(expected)):
            errors.append(f"invalid digest for {path}")
            continue
        if not candidate.is_file():
            errors.append(f"missing evidence file: {path}")
            continue
        actual = sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"evidence digest mismatch: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scorecard", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        errors = verify(args.scorecard, args.root)
    except (OSError, json.JSONDecodeError, TypeError) as error:
        print(f"cannot verify scorecard evidence: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"verified scorecard evidence: {args.scorecard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
