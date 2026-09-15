import hashlib
import json
from pathlib import Path

import pytest

from verification_platform.workflow import advance_checkpoint, create_checkpoint, load_checkpoint, promote_checkpoint_to_release, resume_checkpoint, verify_four_workstream_release_inputs, write_checkpoint
from verification_platform.artifacts import build_artifact_manifest, write_artifact_manifest


def test_workflow_checkpoint_resumes_and_hashes_artifacts(tmp_path: Path):
    artifact = tmp_path / "plan.json"
    artifact.write_text("{}\n", encoding="utf-8")
    checkpoint = advance_checkpoint(create_checkpoint("run-1", "v1"), "planning", artifact_root=tmp_path, artifact_paths=[artifact])
    path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    restored = load_checkpoint(path)
    assert restored.completed == ("planning",)
    assert restored.artifacts["plan.json"]
    assert restored.status == "running"


def test_workflow_rejects_skips_missing_artifacts_and_unapproved_release(tmp_path: Path):
    checkpoint = create_checkpoint("run-1", "v1")
    with pytest.raises(ValueError, match="missing"):
        advance_checkpoint(checkpoint, "planning", artifact_root=tmp_path, artifact_paths=["missing.json"])
    checkpoint = advance_checkpoint(checkpoint, "planning", artifact_root=tmp_path)
    with pytest.raises(ValueError, match="cannot advance"):
        advance_checkpoint(checkpoint, "protocol", artifact_root=tmp_path)
    for stage in ("scheduling", "structural", "protocol", "debug", "optimization"):
        checkpoint = advance_checkpoint(checkpoint, stage, artifact_root=tmp_path)
    with pytest.raises(PermissionError, match="human approval"):
        advance_checkpoint(checkpoint, "release", artifact_root=tmp_path)


def test_workflow_checkpoint_tampering_is_detected(tmp_path: Path):
    path = write_checkpoint(create_checkpoint("run-1", "v1"), tmp_path / "checkpoint.json")
    path.write_text(path.read_text(encoding="utf-8").replace("run-1", "run-2"), encoding="utf-8")
    with pytest.raises(ValueError, match="self-digest"):
        load_checkpoint(path)


def test_workflow_resume_verifies_artifacts_and_reports_next_stage(tmp_path: Path):
    artifact = tmp_path / "plan.json"
    artifact.write_text("{}\n", encoding="utf-8")
    checkpoint = advance_checkpoint(create_checkpoint("run-1", "v1"), "planning", artifact_root=tmp_path, artifact_paths=[artifact])
    path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    result = resume_checkpoint(path, artifact_root=tmp_path)
    assert result["status"] == "ready"
    assert result["next_stage"] == "scheduling"
    artifact.write_text("changed\n", encoding="utf-8")
    blocked = resume_checkpoint(path, artifact_root=tmp_path)
    assert blocked["status"] == "blocked"
    assert "digest mismatch" in blocked["artifact_errors"][0]


def test_workflow_resume_verifies_inner_evidence_manifest_hashes(tmp_path: Path):
    tracked = tmp_path / "tracked.json"
    extra = tmp_path / "extra.json"
    tracked.write_text("{}\n", encoding="utf-8")
    extra.write_text("original\n", encoding="utf-8")
    manifest = write_artifact_manifest(
        tmp_path / "four-workstream-evidence-manifest.json",
        build_artifact_manifest(tmp_path, exclude={"four-workstream-evidence-manifest.json", "checkpoint.json"}),
    )
    checkpoint = advance_checkpoint(
        create_checkpoint("run-1", "v1"), "planning", artifact_root=tmp_path,
        artifact_paths=[manifest.name],
    )
    checkpoint_path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    assert resume_checkpoint(checkpoint_path, artifact_root=tmp_path)["status"] == "ready"
    extra.write_text("tampered\n", encoding="utf-8")
    blocked = resume_checkpoint(checkpoint_path, artifact_root=tmp_path)
    assert blocked["status"] == "blocked"
    assert "evidence manifest contents are invalid" in blocked["artifact_errors"][0]


def test_release_promotion_requires_approval_and_records_manifest(tmp_path: Path):
    checkpoint = create_checkpoint("release-run", "v1")
    for stage in ("planning", "scheduling", "structural", "protocol", "debug", "optimization"):
        artifact = tmp_path / f"{stage}.json"
        artifact.write_text("{}\n", encoding="utf-8")
        checkpoint = advance_checkpoint(checkpoint, stage, artifact_root=tmp_path, artifact_paths=[artifact.name])
    checkpoint_path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    with pytest.raises(PermissionError, match="approval"):
        promote_checkpoint_to_release(checkpoint_path, artifact_root=tmp_path, reviewer="alice", approval_note="reviewed", human_approved=False)
    result = promote_checkpoint_to_release(checkpoint_path, artifact_root=tmp_path, reviewer="alice", approval_note="reviewed all evidence", human_approved=True)
    assert result["status"] == "released"
    assert load_checkpoint(checkpoint_path).status == "complete"
    assert (tmp_path / "release-manifest.json").is_file()


def test_four_workstream_release_requires_valid_tier_inventory(tmp_path: Path):
    checkpoint = create_checkpoint("four-workstream-run", "v1")
    for stage in ("planning", "scheduling", "structural", "protocol", "debug", "optimization"):
        artifact = tmp_path / f"{stage}.json"
        artifact.write_text("{}\n", encoding="utf-8")
        checkpoint = advance_checkpoint(checkpoint, stage, artifact_root=tmp_path, artifact_paths=[artifact.name])
    checkpoint_path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    audit = verify_four_workstream_release_inputs(checkpoint, artifact_root=tmp_path)
    assert not audit["valid"]
    assert "tier evidence is missing" in audit["errors"][0]
    with pytest.raises(ValueError, match="release evidence is invalid"):
        promote_checkpoint_to_release(checkpoint_path, artifact_root=tmp_path, reviewer="alice", approval_note="reviewed", human_approved=True)


def test_four_workstream_release_requires_checkpoint_bound_evidence(tmp_path: Path):
    checkpoint = create_checkpoint("four-workstream-run", "v1")
    tier = {
        "schema_version": "four-workstream-tier-evidence-v1",
        "source_revision": "v1",
        "tiers": [{"id": f"tier-{index}", "status": "passed"} for index in range(1, 7)],
    }
    tier["tier_evidence_sha256"] = hashlib.sha256(json.dumps(tier, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (tmp_path / "four-workstream-tier-evidence.json").write_text(json.dumps(tier), encoding="utf-8")
    (tmp_path / "four-workstream-evidence-manifest.json").write_text("{}", encoding="utf-8")
    audit = verify_four_workstream_release_inputs(checkpoint, artifact_root=tmp_path)
    assert not audit["valid"]
    assert "checkpoint-bound" in " ".join(audit["errors"])


def test_four_workstream_release_rejects_claim_status_tier_mismatch(tmp_path: Path):
    tier = {
        "schema_version": "four-workstream-tier-evidence-v1",
        "source_revision": "v1",
        "tiers": [{"id": f"tier-{index}", "status": "passed"} for index in range(1, 7)],
    }
    tier["tier_evidence_sha256"] = hashlib.sha256(json.dumps(tier, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (tmp_path / "four-workstream-tier-evidence.json").write_text(json.dumps(tier), encoding="utf-8")
    result = {"schema_version": "four-workstream-pipeline-v1", "source_revision": "v1", "status": "passed", "claim_status": "review_required"}
    (tmp_path / "four-workstream-result.json").write_text(json.dumps(result), encoding="utf-8")
    manifest = write_artifact_manifest(
        tmp_path / "four-workstream-evidence-manifest.json",
        build_artifact_manifest(tmp_path, exclude={"four-workstream-evidence-manifest.json", "checkpoint.json"}),
    )
    checkpoint = create_checkpoint("four-workstream-run", "v1")
    checkpoint = advance_checkpoint(
        checkpoint, "planning", artifact_root=tmp_path,
        artifact_paths=["four-workstream-tier-evidence.json", "four-workstream-result.json", manifest.name],
    )
    for stage in ("scheduling", "structural", "protocol", "debug", "optimization"):
        checkpoint = advance_checkpoint(checkpoint, stage, artifact_root=tmp_path)
    audit = verify_four_workstream_release_inputs(checkpoint, artifact_root=tmp_path)
    assert not audit["valid"]
    assert "claim status is inconsistent" in " ".join(audit["errors"])


def test_four_workstream_release_promotes_valid_checkpoint_with_explicit_approval(tmp_path: Path):
    tier = {
        "schema_version": "four-workstream-tier-evidence-v1",
        "source_revision": "v1",
        "tiers": [{"id": f"tier-{index}", "status": "passed"} for index in range(1, 7)],
    }
    tier["tier_evidence_sha256"] = hashlib.sha256(json.dumps(tier, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (tmp_path / "four-workstream-tier-evidence.json").write_text(json.dumps(tier), encoding="utf-8")
    result = {"schema_version": "four-workstream-pipeline-v1", "source_revision": "v1", "status": "passed", "claim_status": "evidence_only"}
    (tmp_path / "four-workstream-result.json").write_text(json.dumps(result), encoding="utf-8")
    manifest = write_artifact_manifest(
        tmp_path / "four-workstream-evidence-manifest.json",
        build_artifact_manifest(tmp_path, exclude={"four-workstream-evidence-manifest.json", "checkpoint.json"}),
    )
    checkpoint = create_checkpoint("four-workstream-valid-run", "v1")
    checkpoint = advance_checkpoint(
        checkpoint, "planning", artifact_root=tmp_path,
        artifact_paths=["four-workstream-tier-evidence.json", "four-workstream-result.json", manifest.name],
    )
    for stage in ("scheduling", "structural", "protocol", "debug", "optimization"):
        checkpoint = advance_checkpoint(checkpoint, stage, artifact_root=tmp_path)
    checkpoint_path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    released = promote_checkpoint_to_release(
        checkpoint_path, artifact_root=tmp_path, reviewer="alice",
        approval_note="validated all six evidence tiers", human_approved=True,
    )
    assert released["status"] == "released"
    assert load_checkpoint(checkpoint_path).status == "complete"
    assert (tmp_path / "release-manifest.json").is_file()


def test_four_workstream_release_audit_requires_approval_but_does_not_promote(tmp_path: Path):
    checkpoint = create_checkpoint("four-workstream-run", "v1")
    for stage in ("planning", "scheduling", "structural", "protocol", "debug", "optimization"):
        artifact = tmp_path / f"{stage}.json"
        artifact.write_text("{}\n", encoding="utf-8")
        checkpoint = advance_checkpoint(checkpoint, stage, artifact_root=tmp_path, artifact_paths=[artifact.name])
    checkpoint_path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    from scripts.audit_four_workstream_release import audit

    result = audit(checkpoint_path, tmp_path)
    assert result["status"] == "blocked"
    assert result["pipeline_status"] is None
    assert not (tmp_path / "release-manifest.json").exists()
