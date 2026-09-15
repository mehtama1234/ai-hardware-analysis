#!/usr/bin/env python3
"""Build a hash-bound typed collateral intake package."""

from __future__ import annotations

import argparse
from pathlib import Path

from verification_platform.collateral import build_collateral_package, write_collateral_package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--entry", action="append", nargs=2, metavar=("KIND", "PATH"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = build_collateral_package(
        [{"kind": kind, "path": path} for kind, path in args.entry],
        root=args.root, source_revision=args.source_revision,
    )
    write_collateral_package(package, args.output)
    print(package["status"])
    return 0 if package["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
