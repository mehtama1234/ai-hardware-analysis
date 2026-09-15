#!/usr/bin/env python3
"""Regenerate and print the joined model-to-chip qualification state."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_end_to_end_qualification_manifest.py"
MANIFEST = ROOT / "evidence" / "end-to-end-qualification-manifest.json"


def main() -> int:
    result = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        return result.returncode
    report = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print("gate,status,pass")
    for name, gate in report["gates"].items():
        print(f"{name},{gate['status']},{gate['pass']}")
        evidence = gate.get("evidence", {})
        if isinstance(evidence, dict):
            for label, item in evidence.items():
                if isinstance(item, dict) and "path" in item:
                    print(f"evidence.{name}.{label},{item['path']},{item.get('present', 'false')}")
    print(f"decision,{report['decision']}")
    print(f"analog_authorized,{report['analog_authorized']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
