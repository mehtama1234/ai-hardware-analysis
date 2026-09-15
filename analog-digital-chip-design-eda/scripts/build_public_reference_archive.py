#!/usr/bin/env python3
"""Build a curated, source-only public reference archive."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ("verification_platform", "deployment", "scripts", "benchmarks", "site")
FILES = ("README.md", "PUBLIC_REFERENCE_RELEASE.md")


def _files() -> list[Path]:
    found = [ROOT / path for path in FILES]
    for prefix in PREFIXES:
        base = ROOT / prefix
        for path in base.rglob("*"):
            if not path.is_file() or "/runs/" in path.as_posix() or "/__pycache__/" in path.as_posix() or ".artifacts" in path.parts:
                continue
            found.append(path)
    return sorted(set(found), key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts" / "public-reference-release.tar.gz")
    args = parser.parse_args()
    files = _files()
    inventory = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    manifest = {"schema_version": "public-reference-archive-v1", "backend_policy": "open-source-only", "hardware_required": False, "files": inventory, "file_count": len(inventory), "excluded": ["**/runs/**", "**/__pycache__/**", "**/.artifacts/**", "secrets and generated customer evidence"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, "w:gz") as archive:
        for path in files:
            archive.add(path, arcname=Path("public-reference") / path.relative_to(ROOT), recursive=False)
        payload = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
        info = tarfile.TarInfo("public-reference/archive-manifest.json")
        info.size = len(payload)
        info.mode = 0o644
        archive.addfile(info, __import__("io").BytesIO(payload))
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    sidecar = args.output.with_suffix(args.output.suffix + ".json")
    sidecar.write_text(json.dumps({**manifest, "archive": args.output.name, "archive_sha256": digest}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"archive": str(args.output), "archive_sha256": digest, "file_count": len(inventory)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
