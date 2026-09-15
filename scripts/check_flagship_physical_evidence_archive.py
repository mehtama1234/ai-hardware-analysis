#!/usr/bin/env python3
"""Independently check the portable local physical evidence archive."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile


def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("receipt", type=Path); args = parser.parse_args()
    receipt_path = args.receipt.resolve(); errors = []
    try: receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: print(json.dumps({"status":"blocked","errors":[str(exc)]})); return 1
    archive_info = receipt.get("archive", {}); archive = receipt_path.parent / archive_info.get("path", "")
    if receipt.get("schema_version") != "flagship-physical-evidence-archive-v1": errors.append("unsupported schema")
    if receipt.get("status") != "passed" or set(receipt.get("designs", [])) != {"aimc", "register"}: errors.append("physical archive scope is incomplete")
    if not archive.is_file() or sha256(archive.read_bytes()) != archive_info.get("sha256"): errors.append("archive missing or digest mismatch")
    else:
        try:
            with ZipFile(archive) as z:
                names = set(z.namelist()); inner = json.loads(z.read("archive-receipt.json"))
                if inner.get("receipt_sha256") != receipt.get("receipt_sha256"): errors.append("embedded receipt mismatch")
                for item in receipt.get("entries", []):
                    name = item.get("archive_path", "")
                    if name not in names or name.startswith("/") or ".." in Path(name).parts: errors.append(f"unsafe or missing entry: {name}"); continue
                    if sha256(z.read(name)) != item.get("sha256"): errors.append(f"entry digest mismatch: {name}")
                required_exact = {"receipts/aimc_bridge.json", "receipts/register_handoff.json", "receipts/aimc_prep_manifest.json"}
                required_prefixes = {f"{d}/{label}/" for d in ("aimc", "register") for label in ("metrics.csv", "lvs.rpt", "xor.rpt", "drc.rpt", "antenna.rpt", "gds", "lef", "lib", "sdc", "spef", "sdf")}
                if not required_exact.issubset(names) or not all(any(name.startswith(prefix) for name in names) for prefix in required_prefixes): errors.append("required physical artifacts are incomplete")
                for receipt_name in ("receipts/aimc_bridge.json", "receipts/register_handoff.json"):
                    payload = json.loads(z.read(receipt_name));
                    if payload.get("status") != "passed": errors.append(f"physical receipt is not passed: {receipt_name}")
        except (BadZipFile, KeyError, json.JSONDecodeError) as exc: errors.append(f"invalid physical archive: {exc}")
    if "not commercial" not in receipt.get("claim_boundary", "").lower() or "silicon" not in receipt.get("claim_boundary", "").lower(): errors.append("physical claim boundary is too broad")
    result = {"schema_version":"flagship-physical-evidence-archive-check-v1","status":"passed" if not errors else "blocked","receipt":str(receipt_path),"entries":len(receipt.get("entries",[])),"errors":sorted(set(errors))}; result["check_sha256"] = hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest(); print(json.dumps(result,sort_keys=True)); return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
