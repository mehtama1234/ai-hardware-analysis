"""Validate a copied multi-design pilot bundle without rerunning generation."""
from __future__ import annotations
import hashlib, json, shutil, tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from verification_platform.artifacts import verify_artifact_manifest

DESIGNS = ("seeded_counter", "seeded_fifo", "seeded_regblock", "register_peripheral", "seeded_handshake", "seeded_arbiter", "seeded_decoder", "seeded_parity", "seeded_width", "seeded_timeout", "seeded_signed")
TAXONOMY_PATH = Path(__file__).with_name("fault-taxonomy.json")

def _summary_digest(summary: dict) -> str:
    body = {key: value for key, value in summary.items() if key != "summary_sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _proposal_valid(path: Path) -> bool:
    try:
        proposal = json.loads(path.read_text(encoding="utf-8"))
        stored = proposal.get("proposal_sha256")
        body = {key: value for key, value in proposal.items() if key != "proposal_sha256"}
        return proposal.get("status") == "review_required" and isinstance(stored, str) and hashlib.sha256(json.dumps({key: body[key] for key in ("proposal_id", "kind", "source_revision", "action", "rationale", "evidence", "status")}, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == stored
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        return False

def _next_test_valid(path: Path) -> bool:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
        proposal = plan["proposal"]
        return (
            isinstance(plan.get("plan_sha256"), str)
            and plan.get("target_kind")
            and plan.get("expected_artifact")
            and _proposal_valid_payload(proposal)
        )
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        return False

def _proposal_valid_payload(proposal: dict) -> bool:
    stored = proposal.get("proposal_sha256")
    body = {key: proposal[key] for key in ("proposal_id", "kind", "source_revision", "action", "rationale", "evidence", "status")}
    return proposal.get("status") == "review_required" and isinstance(stored, str) and hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == stored

def validate(bundle: Path) -> dict:
    summary_path = bundle / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "pilot-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    taxonomy = json.loads((bundle / "benchmarks" / "multi_design_pilot" / "fault-taxonomy.json").read_text(encoding="utf-8"))
    session_path = bundle / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "session-ledger.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    session_body = {key: value for key, value in session.items() if key != "session_sha256"}
    session_valid = hashlib.sha256(json.dumps(session_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == session.get("session_sha256")
    release_path = bundle / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "pilot-release-manifest.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    release_body = {key: value for key, value in release.items() if key != "release_sha256"}
    release_valid = hashlib.sha256(json.dumps(release_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == release.get("release_sha256")
    taxonomy_digest_valid = hashlib.sha256((bundle / "benchmarks" / "multi_design_pilot" / "fault-taxonomy.json").read_bytes()).hexdigest() == release.get("fault_taxonomy_sha256")
    expected_counts = {
        "design_count": len(DESIGNS),
        "failed_designs": len(DESIGNS),
        "passed_retests": len(DESIGNS),
    }
    counts_valid = all(summary.get(key) == value for key, value in expected_counts.items())
    release_designs_valid = release.get("designs") == list(DESIGNS)
    classes = taxonomy.get("designs", {}) if isinstance(taxonomy, dict) else {}
    taxonomy_valid = set(classes) == set(DESIGNS) and len(set(classes.values())) == taxonomy.get("required_unique_classes") == len(DESIGNS)
    summary_taxonomy_valid = summary.get("metrics", {}).get("unique_fault_classes") == len(DESIGNS)
    scope_valid = all(item.get("scope_comparable") is True and item.get("scope_id") == item.get("retest_scope_id") for item in summary.get("results", []))
    checks: dict[str, object] = {"summary_digest_valid": _summary_digest(summary) == summary.get("summary_sha256"), "session_digest_valid": session_valid, "release_digest_valid": release_valid, "taxonomy_digest_valid": taxonomy_digest_valid, "taxonomy_valid": taxonomy_valid and summary_taxonomy_valid, "scope_comparable": scope_valid, "expected_counts": expected_counts, "counts_valid": counts_valid, "release_designs_valid": release_designs_valid, "session_stages": [event.get("stage") for event in session.get("events", [])], "agent_proposals": {}, "manifests": {}}
    for name in DESIGNS:
        root = bundle / "benchmarks" / name
        for phase in ("latest", "retest"):
            run = root / "runs" / phase
            manifest_path = run / "artifact-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            checks["manifests"][f"{name}/{phase}"] = verify_artifact_manifest(run, manifest)
        proposal_path = bundle / "benchmarks" / name / "runs" / "latest" / "reference-agent-proposal.json"
        checks["agent_proposals"][name] = _proposal_valid(proposal_path)
        next_test_path = bundle / "benchmarks" / name / "runs" / "latest" / "next-test-proposal.json"
        checks.setdefault("next_test_proposals", {})[name] = _next_test_valid(next_test_path)
    checks["valid"] = bool(checks["summary_digest_valid"]) and bool(checks["session_digest_valid"]) and bool(checks["release_digest_valid"]) and bool(checks["taxonomy_digest_valid"]) and bool(checks["taxonomy_valid"]) and bool(checks["scope_comparable"]) and bool(checks["counts_valid"]) and bool(checks["release_designs_valid"]) and checks["session_stages"] == ["created", "planned", "executed", "triaged", "repair_review", "retested", "closed"] and all(item["valid"] for item in checks["manifests"].values()) and all(checks["agent_proposals"].values()) and all(checks["next_test_proposals"].values())
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
