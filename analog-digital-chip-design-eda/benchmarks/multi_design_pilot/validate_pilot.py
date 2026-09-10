"""Validate a copied multi-design pilot bundle without rerunning generation."""
from __future__ import annotations
import hashlib, json, shutil, tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from verification_platform.artifacts import verify_artifact_manifest

DESIGNS = ("seeded_counter", "seeded_fifo", "seeded_regblock", "register_peripheral", "seeded_handshake")

def _summary_digest(summary: dict) -> str:
    body = {key: value for key, value in summary.items() if key != "summary_sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def validate(bundle: Path) -> dict:
    summary_path = bundle / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "pilot-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    session_path = bundle / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "session-ledger.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    session_body = {key: value for key, value in session.items() if key != "session_sha256"}
    session_valid = hashlib.sha256(json.dumps(session_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == session.get("session_sha256")
    release_path = bundle / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "pilot-release-manifest.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    release_body = {key: value for key, value in release.items() if key != "release_sha256"}
    release_valid = hashlib.sha256(json.dumps(release_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == release.get("release_sha256")
    checks: dict[str, object] = {"summary_digest_valid": _summary_digest(summary) == summary.get("summary_sha256"), "session_digest_valid": session_valid, "release_digest_valid": release_valid, "session_stages": [event.get("stage") for event in session.get("events", [])], "manifests": {}}
    for name in DESIGNS:
        root = bundle / "benchmarks" / name
        for phase in ("latest", "retest"):
            run = root / "runs" / phase
            manifest_path = run / "artifact-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            checks["manifests"][f"{name}/{phase}"] = verify_artifact_manifest(run, manifest)
    checks["valid"] = bool(checks["summary_digest_valid"]) and bool(checks["session_digest_valid"]) and bool(checks["release_digest_valid"]) and checks["session_stages"] == ["created", "planned", "executed", "triaged", "repair_review", "retested", "closed"] and all(item["valid"] for item in checks["manifests"].values())
    return checks

def main() -> int:
    source = ROOT / "benchmarks"
    with tempfile.TemporaryDirectory(prefix="verification-pilot-") as temp:
        bundle = Path(temp) / "bundle"
        shutil.copytree(source, bundle / "benchmarks")
        result = validate(bundle)
    output = ROOT / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "clean-checkout-validation.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
