#!/usr/bin/env python3
"""Verify a pilot artifact snapshot can be restored without file drift."""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import shutil
import json
import sys


def inventory(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[str(path.relative_to(root))] = sha256(path.read_bytes()).hexdigest()
    return result


def verify_snapshot(source: Path, snapshot: Path, restored: Path) -> dict[str, object]:
    source = source.resolve()
    if not source.is_dir():
        raise ValueError("source artifact root must be a directory")
    if snapshot.exists() or restored.exists():
        raise ValueError("snapshot and restored paths must not already exist")
    shutil.copytree(source, snapshot)
    shutil.copytree(snapshot, restored)
    original, recovered = inventory(source), inventory(restored)
    return {"source_files": len(original), "restored_files": len(recovered), "source_sha256": sha256(repr(sorted(original.items())).encode()).hexdigest(), "restored_sha256": sha256(repr(sorted(recovered.items())).encode()).hexdigest(), "match": original == recovered}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("restored", type=Path)
    parser.add_argument("--output", type=Path, help="write the recovery result as JSON")
    args = parser.parse_args()
    try:
        result = verify_snapshot(args.source, args.snapshot, args.restored)
    except (OSError, ValueError) as error:
        print(f"recovery verification failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
