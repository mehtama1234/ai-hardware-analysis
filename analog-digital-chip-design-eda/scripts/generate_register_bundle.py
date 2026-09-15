#!/usr/bin/env python3
"""Generate deterministic register collateral from the register-spec-v1 IR."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.registers import load_ipxact_spec, load_register_spec, load_systemrdl_spec, verify_register_bundle, write_register_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="register-spec-v1 JSON file")
    parser.add_argument("output", type=Path, help="output directory for generated collateral")
    parser.add_argument("--format", choices=("json", "ipxact", "systemrdl"), default=None, help="input format; defaults to the file suffix")
    args = parser.parse_args()
    try:
        input_format = args.format or ("ipxact" if args.spec.suffix.lower() in {".xml", ".ipxact"} else "systemrdl" if args.spec.suffix.lower() in {".rdl", ".systemrdl"} else "json")
        if input_format == "ipxact":
            spec = load_ipxact_spec(args.spec)
        elif input_format == "systemrdl":
            spec = load_systemrdl_spec(args.spec)
        else:
            spec = load_register_spec(args.spec)
        manifest = write_register_bundle(spec, args.output)
        errors = verify_register_bundle(spec, args.output, manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"register bundle generation blocked: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "passed", "spec_digest": spec.digest(), "bundle_sha256": manifest["bundle_sha256"], "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
