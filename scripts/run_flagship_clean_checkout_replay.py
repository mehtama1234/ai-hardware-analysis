#!/usr/bin/env python3
"""Replay the committed flagship evidence package from a clean archive."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path) -> dict[str, object]:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "status": "passed" if completed.returncode == 0 else "blocked",
        "stdout_tail": completed.stdout[-3000:],
        "stderr_tail": completed.stderr[-3000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    archive = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD"], cwd=ROOT, capture_output=True, check=True,
    ).stdout
    archive_sha256 = hashlib.sha256(archive).hexdigest()
    commands = [
        ["python3", "scripts/check_flagship_end_to_end_release.py", ".artifacts/flagship-end-to-end-release.json"],
        ["python3", "scripts/check_local_unified_release_acceptance.py", ".artifacts/local-unified-release-acceptance.json"],
        ["python3", "scripts/check_next_stage_milestone.py", ".artifacts/flagship-next-stage-20260915-report.json"],
        ["python3", "scripts/check_flagship_closure_evidence.py", ".artifacts/flagship-closure-evidence-20260915/manifest.json"],
        ["python3", "scripts/check_real_four_causal_agent_colab_package.py", ".artifacts/flagship-four-causal-agent-20260915-package.tgz"],
        ["python3", "analog-digital-chip-design-eda/scripts/check_verified_rtl2gds_bridge.py"],
        [
            "python3",
            "analog-digital-chip-design-eda/scripts/check_register_peripheral_rtl2gds_handoff.py",
            "analog-digital-chip-design-eda/evidence/register-peripheral/model-repair-rtl2gds-handoff-20260913.json",
        ],
        ["python3", "scripts/validate_end_to_end_handoff.py"],
    ]
    with tempfile.TemporaryDirectory(prefix="flagship-clean-checkout-") as temporary:
        # The cross-repository handoff records workspace-relative paths with
        # the canonical checkout directory name.  Recreate that topology so
        # validation exercises the same path contract as a real clean clone.
        checkout = Path(temporary) / "ai-hardware-analysis"
        checkout.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            bundle.extractall(checkout, filter="data")
        checks = [run(command, cwd=checkout) for command in commands]

    result = {
        "schema_version": "flagship-clean-checkout-replay-v1",
        "source_revision": revision,
        "archive_sha256": archive_sha256,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "status": "passed" if all(item["status"] == "passed" for item in checks) else "blocked",
        "claim_boundary": "clean archived-checkout replay of committed evidence checkers; not physical, silicon, or production signoff",
    }
    result["replay_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "source_revision": revision, "output": str(output)}, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
