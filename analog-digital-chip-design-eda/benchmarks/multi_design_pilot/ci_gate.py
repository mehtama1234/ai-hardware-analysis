"""CI entry point for the reproducible multi-design verification pilot."""
from __future__ import annotations
import subprocess
import sys
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main() -> int:
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("run_pilot.py"))], cwd=ROOT, check=False)
    if result.returncode != 0:
        return result.returncode
    manifest = {
        "schema_version": "verification-pilot-release-v1",
        "pilot": "multi-design-open-source-verification",
        "designs": ["seeded_counter", "seeded_fifo", "seeded_regblock", "register_peripheral", "seeded_handshake"],
        "backend_policy": "open-source-only",
        "commands": ["python3 benchmarks/multi_design_pilot/run_pilot.py", "python3 benchmarks/multi_design_pilot/validate_pilot.py"],
        "evidence_contract": ["typed_planning", "generated_checks", "simulation", "triage", "human_approved_retest", "artifact_manifest", "session_ledger"],
        "hardware_required": False,
    }
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    manifest["release_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    output = ROOT / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "pilot-release-manifest.json"
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Validate only after the fresh pilot and release manifest exist. This
    # keeps a clean checkout/container independent of stale artifacts.
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("validate_pilot.py"))], cwd=ROOT, check=False)
    if result.returncode != 0:
        return result.returncode
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
