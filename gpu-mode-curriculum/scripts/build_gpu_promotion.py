#!/usr/bin/env python3
"""Build the GPU-host promotion manifest and runbook."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-promotion"))

from gpu_promotion import build_manifest  # noqa: E402
from gpu_promotion.builder import MANIFEST_JSON, RUNBOOK_MD  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    if args.json:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    else:
        print(
            f"wrote {MANIFEST_JSON.relative_to(ROOT)} and {RUNBOOK_MD.relative_to(ROOT)} "
            f"({manifest['ready_on_this_host']} local-ready, {manifest['ready_on_gpu_host']} gpu-host steps)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
