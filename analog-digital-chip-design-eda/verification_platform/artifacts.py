"""Run-level content-addressed artifact inventory."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .ledger import sha256_file


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    sha256: str
    size_bytes: int


def build_artifact_manifest(run_root: str | Path, *, exclude: set[str] | None = None) -> dict:
    root = Path(run_root).resolve()
    if not root.is_dir():
        raise ValueError("run_root must be a directory")
    ignored = exclude or set()
    records = [ArtifactRecord(path.relative_to(root).as_posix(), sha256_file(path), path.stat().st_size) for path in sorted(root.rglob("*")) if path.is_file() and path.relative_to(root).as_posix() not in ignored]
    payload = {"schema_version": "artifact-manifest-v1", "artifacts": [asdict(record) for record in records]}
    payload["manifest_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def write_artifact_manifest(path: str | Path, manifest: dict) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def verify_artifact_manifest(run_root: str | Path, manifest: dict, *, manifest_name: str = "artifact-manifest.json") -> dict[str, list[str] | bool]:
    """Check listed files and hashes without trusting the manifest contents."""
    root = Path(run_root).resolve()
    missing, mismatched = [], []
    for item in manifest.get("artifacts", []):
        path = item.get("path", "")
        file_path = root / path
        if not path or Path(path).is_absolute() or not file_path.is_file():
            missing.append(path)
        elif sha256_file(file_path) != item.get("sha256"):
            mismatched.append(path)
    payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    digest_valid = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == manifest.get("manifest_sha256")
    return {"valid": not missing and not mismatched and digest_valid, "missing": missing, "mismatched": mismatched, "manifest_digest_valid": digest_valid}
