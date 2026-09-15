#!/usr/bin/env python3
"""Verify generated handoff artifacts are present in the CI upload contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml


LOCAL_ONLY = {".artifacts/customer-production-runtime-preflight.json"}


def upload_paths(workflow: Path) -> set[str]:
    document = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    paths: set[str] = set()
    for job in (document.get("jobs") or {}).values():
        for step in job.get("steps", []):
            if step.get("uses") != "actions/upload-artifact@v4":
                continue
            raw = (step.get("with") or {}).get("path", "")
            paths.update(line.strip() for line in str(raw).splitlines() if line.strip())
    return paths


def verify(manifest: Path, workflow: Path) -> list[str]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    artifacts = payload.get("artifacts", {})
    paths = upload_paths(workflow)
    errors = []
    for name in artifacts:
        if not name.startswith(".artifacts/") or name in LOCAL_ONLY:
            continue
        if not any(name == path or name.startswith(path.rstrip("/") + "/") for path in paths):
            errors.append(f"generated artifact is not uploaded: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    try:
        errors = verify(args.manifest, args.workflow)
    except (OSError, ValueError, TypeError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"cannot verify upload contract: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("verified handoff upload contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
