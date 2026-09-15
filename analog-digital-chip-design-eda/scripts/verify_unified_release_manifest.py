#!/usr/bin/env python3
"""Verify a unified digital-verification and AIMC release manifest."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


def _digest(payload: object) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _resolve(root: Path, raw: object, label: str) -> Path:
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or "\\" in raw or any(part in {"", ".", ".."} for part in raw.split("/")):
        raise ValueError(f"{label} path is unsafe")
    path = (root / raw).resolve()
    if root not in path.parents or not path.is_file():
        raise ValueError(f"{label} manifest is missing")
    return path


def _verify_parent(path: Path, schema: str, digest_key: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"{path} has unsupported schema")
    stored = payload.get(digest_key)
    body = {key: value for key, value in payload.items() if key != digest_key}
    if not isinstance(stored, str) or stored != _digest(body):
        raise ValueError(f"{path} self-digest does not match")
    return payload


def verify(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read unified release: {error}"]
    if payload.get("schema_version") != "unified-hardware-verification-release-v1":
        errors.append("unsupported unified release schema")
    stored = payload.get("manifest_sha256")
    body = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    if not isinstance(stored, str) or stored != _digest(body):
        errors.append("unified release self-digest does not match")
    if payload.get("release_decision") not in {"blocked_pending_qualification", "review_required"}:
        errors.append("unified release decision is invalid")
    digital = payload.get("digital") if isinstance(payload.get("digital"), dict) else {}
    mixed = payload.get("mixed_signal") if isinstance(payload.get("mixed_signal"), dict) else {}
    root = root.resolve()
    try:
        digital_parent = _resolve(root, digital.get("manifest"), "digital")
        digital_payload = _verify_parent(digital_parent, "verification-pilot-release-v1", "release_sha256")
        if digital.get("manifest_sha256") != digital_payload.get("release_sha256"):
            errors.append("digital parent manifest digest does not match")
        mixed_parent = _resolve(root, mixed.get("manifest"), "mixed-signal")
        mixed_payload = _verify_parent(mixed_parent, "mixed-signal-manifest-v1", "manifest_sha256")
        if mixed.get("manifest_sha256") != mixed_payload.get("manifest_sha256"):
            errors.append("mixed-signal parent manifest digest does not match")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(str(error))
    if digital.get("reference_release_verified") is not True:
        errors.append("digital reference release is not verified")
    if not isinstance(digital.get("design_count"), int) or digital.get("design_count", 0) < 1:
        errors.append("digital release has no designs")
    claim_statuses = {item.get("domain"): item.get("status") for item in mixed.get("claims", []) if isinstance(item, dict)}
    qualification = payload.get("qualification") if isinstance(payload.get("qualification"), dict) else {}
    for domain in ("simulation", "physical_layout", "measured_hardware"):
        if qualification.get(domain) not in {"proven", "unsupported"}:
            errors.append(f"qualification status missing for {domain}")
    if claim_statuses.get("physical_layout") == "unsupported" and qualification.get("physical_layout") != "unsupported":
        errors.append("physical-layout claim boundary was upgraded")
    if claim_statuses.get("measured_hardware") == "unsupported" and qualification.get("measured_hardware") != "unsupported":
        errors.append("measured-hardware claim boundary was upgraded")
    for item in mixed.get("evidence", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append("mixed-signal evidence entry is malformed")
            continue
        candidate = (root / item["path"]).resolve()
        if root not in candidate.parents or not candidate.is_file():
            errors.append(f"missing mixed-signal evidence: {item['path']}")
        elif sha256(candidate.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"mixed-signal evidence digest mismatch: {item['path']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = verify(args.manifest, args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"verified unified release: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
