#!/usr/bin/env python3
"""Record a named, non-destructive checkpoint for the local evidence state."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="20260912-local-unified-reference")
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts" / "local-checkpoints" / "20260912-local-unified-reference.json")
    args = parser.parse_args()
    repos = {}
    for name, path in {"product": ROOT, "eda": ROOT / "analog-digital-chip-design-eda", "deepseek": ROOT.parent / "DeepSeek-From-Scratch"}.items():
        status = git(path, "status", "--short", "--untracked-files=all")
        repo_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path("..") / path.name
        repos[name] = {"path": str(repo_path), "head": git(path, "rev-parse", "HEAD"), "dirty": bool(status), "dirty_path_count": len(status.splitlines()) if status else 0, "status_sha256": hashlib.sha256(status.encode()).hexdigest()}
    artifact_paths = {
        "unified_acceptance": ROOT / ".artifacts/local-unified-release-acceptance.json",
        "public_acceptance": ROOT / "analog-digital-chip-design-eda/.artifacts/public-reference-acceptance.json",
        "unified_hardware_release": ROOT / "analog-digital-chip-design-eda/.artifacts/unified-hardware-verification-release.json",
        "commercial_handoff": ROOT / "analog-digital-chip-design-eda/.artifacts/commercial-handoff-manifest.json",
    }
    manifest = {
        "schema_version": "local-checkpoint-manifest-v1",
        "checkpoint_name": args.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "non_destructive": True,
        "claim_boundary": "This names and hashes a local worktree state; it is not a git commit, signed release, hardware qualification, or customer production signoff.",
        "repositories": repos,
        "artifacts": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for name, path in artifact_paths.items()},
    }
    body = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    manifest["manifest_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checkpoint": args.name, "output": str(args.output), "dirty_repositories": [name for name, repo in repos.items() if repo["dirty"]]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
