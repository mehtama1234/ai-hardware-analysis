#!/usr/bin/env python3
"""Verify hash-chain integrity and referenced artifacts in measurement history."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def digest(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("history",type=Path); args=parser.parse_args(); lines=[line for line in args.history.read_text(encoding="utf-8").splitlines() if line.strip()]; errors=[]; previous="0"*64
    superseded_by_path={}
    for line in lines:
        item=json.loads(line); ref=item.get("release_manifest") or item.get("manifest") or {}; path=Path(ref.get("path", ""))
        if path.is_file():
            try:
                superseded_by_path[str(path.resolve())]=set(json.loads(path.read_text(encoding="utf-8")).get("supersedes_sha256", []))
            except json.JSONDecodeError:
                pass
    for index,line in enumerate(lines):
        item=json.loads(line); expected=item.get("record_hash"); payload=dict(item); payload.pop("record_hash",None); actual=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if expected!=actual: errors.append(f"record {index}: hash mismatch")
        if item.get("previous_record_hash")!=previous: errors.append(f"record {index}: chain link mismatch")
        manifest_ref=item.get("release_manifest") or item.get("manifest") or {}
        manifest=Path(manifest_ref.get("path",""));
        stale_hash=manifest_ref.get("sha256") in superseded_by_path.get(str(manifest.resolve()), set())
        if not manifest.is_file() or (digest(manifest)!=manifest_ref.get("sha256") and not stale_hash): errors.append(f"record {index}: manifest mismatch")
        previous=expected
    if not lines: errors.append("history is empty")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status":"passed","record_count":len(lines),"tip_hash":previous},sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
