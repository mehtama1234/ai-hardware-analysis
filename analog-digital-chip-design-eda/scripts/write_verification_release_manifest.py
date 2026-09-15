"""Write a content-addressed release manifest for a verification-pilot image."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _run(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def build(image: str) -> dict:
    inspect = json.loads(_run(["docker", "image", "inspect", image]))[0]
    config = inspect.get("Config", {})
    dockerfile = Path("deployment/Dockerfile").read_text(encoding="utf-8")
    from_lines = [line.strip() for line in dockerfile.splitlines() if line.strip().upper().startswith("FROM ")]
    changed = _run(["git", "status", "--porcelain", "--untracked-files=all"]).splitlines()
    changed_paths = [line[3:] for line in changed]
    return {
        "schema_version": "verification-release-v1",
        "image": image,
        "image_id": inspect.get("Id"),
        "repo_digests": sorted(inspect.get("RepoDigests") or []),
        "base_image": from_lines[0] if from_lines else None,
        "base_image_digest_pinned": bool(from_lines and "@sha256:" in from_lines[0]),
        "container_user": config.get("User"),
        "expected_runtime_uid": "10001",
        "source_revision": _run(["git", "rev-parse", "HEAD"]),
        "source_tree_dirty": bool(changed),
        "changed_paths": changed_paths[:2000],
        "changed_paths_truncated": len(changed_paths) > 2000,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_gates": {
            "backend_tests": "python3 -m pytest verification_platform deployment",
            "browser_smoke": "python3 scripts/verify_workbench_browser.py",
            "adversarial_judge": "python3 scripts/run_workbench_adversarial_judge.py",
            "deployment_preflight": "python3 scripts/preflight_verification_deployment.py",
            "runtime_smoke": "python3 scripts/verify_verification_image_runtime.py <image> --sandbox-probe",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        payload = build(args.image)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, IndexError) as error:
        print(f"FAIL: unable to inspect release image: {error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: wrote release manifest {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
