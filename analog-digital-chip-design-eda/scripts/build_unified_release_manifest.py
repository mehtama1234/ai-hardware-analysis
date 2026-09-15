#!/usr/bin/env python3
"""Bind the digital pilot and AIMC evidence manifests into one release record."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


def _digest(payload: object) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _file_digest(path: Path, root: Path) -> str:
    resolved = path.resolve()
    if resolved.is_absolute() and root.resolve() not in resolved.parents:
        raise ValueError(f"evidence path is outside release root: {path}")
    if not resolved.is_file():
        raise ValueError(f"evidence file is missing: {path}")
    return sha256(resolved.read_bytes()).hexdigest()


def _read_manifest(path: Path, schema: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"{path} has unsupported schema_version")
    digest = payload.get("manifest_sha256") or payload.get("release_sha256")
    body_key = "manifest_sha256" if "manifest_sha256" in payload else "release_sha256"
    body = {key: value for key, value in payload.items() if key != body_key}
    if not isinstance(digest, str) or digest != _digest(body):
        raise ValueError(f"{path} self-digest does not match")
    return payload


def build(*, root: Path, digital_path: Path, mixed_signal_path: Path) -> dict[str, object]:
    root = root.resolve()
    digital = _read_manifest(digital_path, "verification-pilot-release-v1")
    mixed = _read_manifest(mixed_signal_path, "mixed-signal-manifest-v1")
    evidence: list[dict[str, object]] = []
    for item in mixed.get("artifacts", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValueError("mixed-signal artifact entry has no relative path")
        path = root / item["path"]
        actual = _file_digest(path, root)
        expected = item.get("evidence", {}).get("sha256") if isinstance(item.get("evidence"), dict) else None
        if actual != expected:
            raise ValueError(f"mixed-signal evidence digest mismatch: {item['path']}")
        evidence.append({"path": item["path"], "kind": item.get("kind"), "sha256": actual})
    claims = mixed.get("claims") if isinstance(mixed.get("claims"), list) else []
    unsupported = [claim.get("domain") for claim in claims if isinstance(claim, dict) and claim.get("status") != "proven"]
    result: dict[str, object] = {
        "schema_version": "unified-hardware-verification-release-v1",
        "digital": {"manifest": str(digital_path), "manifest_sha256": digital.get("release_sha256"), "backend_policy": digital.get("backend_policy"), "design_count": len(digital.get("designs", [])) if isinstance(digital.get("designs"), list) else 0, "reference_release_verified": True},
        "mixed_signal": {"manifest": str(mixed_signal_path), "manifest_sha256": mixed.get("manifest_sha256"), "source_revision": mixed.get("source_revision"), "evidence": evidence, "claims": claims},
        "qualification": {"simulation": "proven" if any(item.get("kind") == "simulation" for item in evidence) else "unsupported", "physical_layout": "unsupported" if "physical_layout" in unsupported else "proven", "measured_hardware": "unsupported" if "measured_hardware" in unsupported else "proven"},
        "release_decision": "blocked_pending_qualification" if unsupported else "review_required",
        "claim_boundary": "Digital reference verification and selected AIMC evidence are bound together; unsupported physical or measured-hardware claims remain open and this record is not customer production signoff.",
    }
    result["manifest_sha256"] = _digest(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--digital", type=Path, default=Path("benchmarks/multi_design_pilot/runs/latest/pilot-release-manifest.json"))
    parser.add_argument("--mixed-signal", type=Path, default=Path("evidence/aimc-hardware-lab/verification-platform-mixed-signal-manifest.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(root=args.root, digital_path=args.digital, mixed_signal_path=args.mixed_signal)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"cannot build unified release manifest: {error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "release_decision": result["release_decision"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
