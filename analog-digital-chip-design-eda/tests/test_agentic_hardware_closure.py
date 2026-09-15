from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_llm_model_evaluation


def test_real_model_verifier_rejects_fixture_without_runtime_provenance(tmp_path: Path) -> None:
    artifact = tmp_path / "fixture.json"
    artifact.write_text(json.dumps({"schema_version": "llm-verification-agent-benchmark-v1"}), encoding="utf-8")
    assert any("runtime provenance" in error for error in verify_llm_model_evaluation.verify(artifact, require_real_model=True))


def test_real_model_verifier_rejects_tampered_provenance(tmp_path: Path) -> None:
    source = ROOT / ".artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913/llm-agent-benchmark.json"
    artifact = tmp_path / "tampered.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["model_provenance"]["gpu"] = "tampered"
    artifact.write_text(json.dumps(payload), encoding="utf-8")
    assert any("self-digest" in error for error in verify_llm_model_evaluation.verify(artifact, require_real_model=True))


def test_review_only_orchestrator_covers_primary_and_held_out(tmp_path: Path) -> None:
    output = tmp_path / "closure"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_agentic_hardware_closure.py"), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    summary = json.loads((output / "closure-summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "review_required"
    assert summary["approval"]["status"] == "required"
    assert summary["canonical_source_unchanged"] is True
    assert summary["held_out"]["design"] == "seeded_timeout"
    assert summary["held_out"]["status"] == "review_required"
    assert summary["artifacts"]["benchmark_sha256"]
    assert summary["artifacts"]["repair_review_sha256"]
    assert summary["artifacts"]["held_out_repair_review_sha256"]
    assert not Path(summary["benchmark"]).is_absolute()
    assert not Path(summary["repair_review"]).is_absolute()
    assert not Path(summary["held_out_repair_review"]).is_absolute()
    release = json.loads((output / "agentic-hardware-release-manifest.json").read_text(encoding="utf-8"))
    assert release["analog_authorized"] is False
    assert release["release_decision"] == "blocked_pending_human_approval"


def test_checker_rejects_tampered_artifact_digest(tmp_path: Path) -> None:
    output = tmp_path / "closure"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_agentic_hardware_closure.py"), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    summary_path = output / "closure-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["artifacts"]["benchmark_sha256"] = "0" * 64
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    checked = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/check_agentic_hardware_closure.py"),
            str(summary_path),
            "--source",
            str(ROOT / "benchmarks/seeded_counter/counter.sv"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert checked.returncode != 0
    assert "benchmark digest does not match summary" in checked.stdout


def test_release_checker_rejects_analog_authorization(tmp_path: Path) -> None:
    output = tmp_path / "closure"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_agentic_hardware_closure.py"), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    manifest_path = output / "agentic-hardware-release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["analog_authorized"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    checked = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_agentic_hardware_release_manifest.py"), str(manifest_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert checked.returncode != 0
    assert "analog_authorized must remain false" in checked.stdout


def test_release_checker_rejects_self_digested_pass_without_signoff(tmp_path: Path) -> None:
    source = ROOT / ".artifacts/llm-agent-colab/agentic-hardware-closure-realcolab-v4-20260913/agentic-hardware-release-manifest.json"
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(source.read_text(encoding="utf-8"))
    manifest["release_decision"] = "passed"
    manifest["human_signoff"] = None
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    manifest["manifest_sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    checked = subprocess.run([sys.executable, str(ROOT / "scripts/check_agentic_hardware_release_manifest.py"), str(manifest_path)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert checked.returncode != 0
    assert "passed release has no approved human signoff" in checked.stdout


def test_release_builder_consumes_closure_bound_human_receipt(tmp_path: Path) -> None:
    output = tmp_path / "closure"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_agentic_hardware_closure.py"), "--output", str(output), "--approve", "--reviewer", "reviewer-test@example.com", "--approval-note", "Disposable test receipt; not human signoff."],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    summary = output / "closure-summary.json"
    closure_sha256 = hashlib.sha256(summary.read_bytes()).hexdigest()
    closure_payload = json.loads(summary.read_text(encoding="utf-8"))
    manifest = json.loads((output / "agentic-hardware-release-manifest.json").read_text(encoding="utf-8"))
    receipt = {"schema_version": "agentic-human-signoff-v1", "status": "approved", "reviewer": "reviewer-test@example.com", "reviewer_subject": "test-subject", "notes": "Disposable test receipt; not human signoff.", "manifest_sha256": manifest["manifest_sha256"], "closure_sha256": closure_sha256, "created_at": "2026-09-13T00:00:00+00:00", "review_started_at": "2026-09-12T23:59:00+00:00", "review_duration_seconds": 60.0, "review_bindings": {"primary": {key: closure_payload["approval"].get(key) for key in ("proposal_sha256", "source_sha256", "scope_sha256")}, "held_out": {key: closure_payload["held_out"]["approval"].get(key) for key in ("proposal_sha256", "source_sha256", "scope_sha256")}}}
    receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    receipt_path = output / "agentic-human-signoff.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    approved = output / "approved-release.json"
    rebuilt = subprocess.run([sys.executable, str(ROOT / "scripts/build_agentic_hardware_release_manifest.py"), "--closure-summary", str(summary), "--output", str(approved), "--human-signoff", str(receipt_path)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert rebuilt.returncode == 0, rebuilt.stderr
    result = json.loads(approved.read_text(encoding="utf-8"))
    assert result["release_decision"] == "blocked"
    assert result["analog_authorized"] is False
    assert result["metrics"]["human_review_effort"]["status"] == "measured"
    assert result["metrics"]["human_review_effort"]["duration_seconds"] == 60.0
