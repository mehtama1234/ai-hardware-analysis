"""Durable, resumable checkpoints for long-running verification workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
from typing import Any

from .ledger import sha256_file
from .artifacts import verify_artifact_manifest


STAGES = ("planning", "scheduling", "structural", "protocol", "debug", "optimization", "release")


@dataclass(frozen=True)
class WorkflowCheckpoint:
    workflow_id: str
    source_revision: str
    completed: tuple[str, ...] = ()
    artifacts: dict[str, str] | None = None
    skipped: tuple[str, ...] = ()
    status: str = "running"
    schema_version: str = "verification-workflow-checkpoint-v1"

    def to_dict(self) -> dict[str, Any]:
        if not self.workflow_id or not self.source_revision:
            raise ValueError("workflow identity and source revision are required")
        if self.schema_version != "verification-workflow-checkpoint-v1":
            raise ValueError("unsupported workflow checkpoint schema")
        if self.status not in {"running", "paused", "complete", "blocked"}:
            raise ValueError("unsupported workflow checkpoint status")
        if tuple(dict.fromkeys(self.completed)) != self.completed or any(stage not in STAGES for stage in self.completed):
            raise ValueError("workflow stages must be known and ordered uniquely")
        if tuple(STAGES[:len(self.completed)]) != self.completed:
            raise ValueError("workflow stages cannot be skipped")
        if tuple(dict.fromkeys(self.skipped)) != self.skipped or any(stage not in self.completed for stage in self.skipped):
            raise ValueError("skipped workflow stages must be completed stages")
        payload = asdict(self)
        payload["completed"] = list(self.completed)
        payload["artifacts"] = dict(sorted((self.artifacts or {}).items()))
        payload["skipped"] = list(self.skipped)
        return payload

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def create_checkpoint(workflow_id: str, source_revision: str) -> WorkflowCheckpoint:
    checkpoint = WorkflowCheckpoint(workflow_id, source_revision, artifacts={})
    checkpoint.to_dict()
    return checkpoint


def advance_checkpoint(
    checkpoint: WorkflowCheckpoint,
    stage: str,
    *,
    artifact_root: str | Path,
    artifact_paths: list[str | Path] = (),
    human_approved: bool = False,
) -> WorkflowCheckpoint:
    """Advance exactly one stage after verifying its artifacts exist and hash."""
    checkpoint.to_dict()
    if stage not in STAGES:
        raise ValueError(f"unknown workflow stage: {stage}")
    expected_index = len(checkpoint.completed)
    skipped = checkpoint.skipped
    completed_prefix = list(checkpoint.completed)
    if expected_index < len(STAGES) and STAGES[expected_index] == "debug" and stage == "optimization":
        completed_prefix.append("debug")
        skipped = (*skipped, "debug")
        expected_index += 1
    if expected_index >= len(STAGES) or STAGES[expected_index] != stage:
        raise ValueError(f"workflow cannot advance to {stage}")
    if stage == "release" and not human_approved:
        raise PermissionError("human approval is required before release stage")
    root = Path(artifact_root).resolve()
    hashes = dict(checkpoint.artifacts or {})
    for raw_path in artifact_paths:
        path = Path(raw_path)
        if path.is_absolute():
            resolved = path.resolve()
            label = str(resolved.relative_to(root))
        else:
            resolved = (root / path).resolve()
            label = path.as_posix()
        if not resolved.is_file():
            raise ValueError(f"workflow artifact is missing: {label}")
        hashes[label] = sha256_file(resolved)
    completed = (*completed_prefix, stage)
    return replace(checkpoint, completed=completed, skipped=skipped, artifacts=hashes, status="complete" if stage == "release" else "running")


def write_checkpoint(checkpoint: WorkflowCheckpoint, path: str | Path) -> Path:
    payload = checkpoint.to_dict()
    payload["checkpoint_sha256"] = checkpoint.digest()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def load_checkpoint(path: str | Path) -> WorkflowCheckpoint:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    supplied = payload.pop("checkpoint_sha256", None)
    checkpoint = WorkflowCheckpoint(
        workflow_id=str(payload.get("workflow_id", "")), source_revision=str(payload.get("source_revision", "")),
        completed=tuple(payload.get("completed", [])), artifacts=dict(payload.get("artifacts", {})),
        skipped=tuple(payload.get("skipped", [])),
        status=str(payload.get("status", "running")), schema_version=str(payload.get("schema_version", "")),
    )
    if supplied != checkpoint.digest():
        raise ValueError("workflow checkpoint self-digest does not match")
    checkpoint.to_dict()
    return checkpoint


def resume_checkpoint(checkpoint_path: str | Path, *, artifact_root: str | Path) -> dict[str, Any]:
    """Verify persisted evidence and report the next stage to execute."""
    checkpoint = load_checkpoint(checkpoint_path)
    root = Path(artifact_root).resolve()
    mismatches: list[str] = []
    for label, expected in (checkpoint.artifacts or {}).items():
        path = (root / label).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            mismatches.append(f"artifact escapes workflow root: {label}")
            continue
        if not path.is_file():
            mismatches.append(f"artifact is missing: {label}")
        elif sha256_file(path) != expected:
            mismatches.append(f"artifact digest mismatch: {label}")
        elif label == "four-workstream-evidence-manifest.json":
            try:
                manifest = json.loads(path.read_text(encoding="utf-8"))
                audit = verify_artifact_manifest(root, manifest, manifest_name=label)
                if not audit["valid"]:
                    mismatches.append(f"evidence manifest contents are invalid: {audit}")
            except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
                mismatches.append(f"evidence manifest cannot be read: {error}")
    if mismatches:
        return {"schema_version": "verification-workflow-resume-v1", "status": "blocked", "workflow_id": checkpoint.workflow_id, "completed": list(checkpoint.completed), "artifact_errors": mismatches}
    next_stage = STAGES[len(checkpoint.completed)] if len(checkpoint.completed) < len(STAGES) else None
    return {"schema_version": "verification-workflow-resume-v1", "status": "ready" if next_stage else "complete", "workflow_id": checkpoint.workflow_id, "completed": list(checkpoint.completed), "next_stage": next_stage, "artifact_errors": [], "checkpoint_sha256": checkpoint.digest()}


def verify_four_workstream_release_inputs(checkpoint: WorkflowCheckpoint, *, artifact_root: str | Path) -> dict[str, Any]:
    """Validate semantic evidence required by a four-workstream release."""
    root = Path(artifact_root).resolve()
    errors: list[str] = []
    tier_path = root / "four-workstream-tier-evidence.json"
    manifest_path = root / "four-workstream-evidence-manifest.json"
    tier: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    if not tier_path.is_file():
        errors.append("four-workstream tier evidence is missing")
    else:
        try:
            tier = json.loads(tier_path.read_text(encoding="utf-8"))
            if tier.get("schema_version") != "four-workstream-tier-evidence-v1":
                errors.append("four-workstream tier evidence schema is unsupported")
            if tier.get("source_revision") != checkpoint.source_revision:
                errors.append("four-workstream tier evidence source revision does not match checkpoint")
            if "four-workstream-tier-evidence.json" not in (checkpoint.artifacts or {}):
                errors.append("four-workstream tier evidence is not checkpoint-bound")
            expected_digest = hashlib.sha256(json.dumps({key: value for key, value in tier.items() if key != "tier_evidence_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if tier.get("tier_evidence_sha256") != expected_digest:
                errors.append("four-workstream tier evidence self-digest does not match")
            tiers = tier.get("tiers")
            expected_ids = [f"tier-{index}" for index in range(1, 7)]
            actual_ids = [item.get("id") for item in tiers if isinstance(item, dict)] if isinstance(tiers, list) else []
            if actual_ids != expected_ids:
                errors.append("four-workstream tier evidence must contain tier-1 through tier-6 in order")
            elif any(item.get("status") in {"blocked", "not_run"} for item in tiers):
                errors.append("four-workstream release cannot contain blocked or not-run tiers")
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            errors.append(f"four-workstream tier evidence cannot be read: {error}")
    if not manifest_path.is_file():
        errors.append("four-workstream evidence manifest is missing")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if "four-workstream-evidence-manifest.json" not in (checkpoint.artifacts or {}):
                errors.append("four-workstream evidence manifest is not checkpoint-bound")
            audit = verify_artifact_manifest(root, manifest, manifest_name=manifest_path.name)
            if not audit["valid"]:
                errors.append(f"four-workstream evidence manifest is invalid: {audit}")
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            errors.append(f"four-workstream evidence manifest cannot be read: {error}")
    result_path = root / "four-workstream-result.json"
    if not result_path.is_file():
        errors.append("four-workstream result is missing")
    elif "four-workstream-result.json" not in (checkpoint.artifacts or {}):
        errors.append("four-workstream result is not checkpoint-bound")
    else:
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("source_revision") != checkpoint.source_revision:
                errors.append("four-workstream result source revision does not match checkpoint")
            if result.get("status") not in {"passed", "blocked"}:
                errors.append("four-workstream result status is unsupported")
            if result.get("claim_status") not in {"blocked", "review_required", "evidence_only"}:
                errors.append("four-workstream result claim status is missing or unsupported")
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            errors.append(f"four-workstream result cannot be read: {error}")
    if tier is not None and result is not None and isinstance(tier.get("tiers"), list):
        tier_statuses = [item.get("status") for item in tier["tiers"] if isinstance(item, dict)]
        expected_claim_status = "blocked" if any(status == "blocked" for status in tier_statuses) else "review_required" if any(status == "review_required" for status in tier_statuses) else "evidence_only"
        if result.get("claim_status") != expected_claim_status:
            errors.append("four-workstream result claim status is inconsistent with tier evidence")
    return {"valid": not errors, "errors": errors, "workflow_id": checkpoint.workflow_id}


def promote_checkpoint_to_release(
    checkpoint_path: str | Path,
    *,
    artifact_root: str | Path,
    reviewer: str,
    approval_note: str,
    human_approved: bool = False,
) -> dict[str, Any]:
    """Create a release manifest and advance a verified workflow to release."""
    if not reviewer.strip() or not approval_note.strip():
        raise ValueError("reviewer and approval_note are required")
    checkpoint = load_checkpoint(checkpoint_path)
    audit = resume_checkpoint(checkpoint_path, artifact_root=artifact_root)
    if audit["status"] != "ready" or audit.get("next_stage") != "release":
        raise ValueError("workflow is not verified and ready for release")
    if checkpoint.workflow_id.startswith("four-workstream-"):
        release_inputs = verify_four_workstream_release_inputs(checkpoint, artifact_root=artifact_root)
        if not release_inputs["valid"]:
            raise ValueError(f"four-workstream release evidence is invalid: {release_inputs['errors']}")
    if not human_approved:
        raise PermissionError("human approval is required before release")
    root = Path(artifact_root).resolve()
    manifest: dict[str, Any] = {
        "schema_version": "four-workstream-release-manifest-v1",
        "workflow_id": checkpoint.workflow_id,
        "source_revision": checkpoint.source_revision,
        "pre_release_checkpoint_sha256": checkpoint.digest(),
        "reviewer": reviewer,
        "approval_note": approval_note,
        "approved": True,
        "artifact_hashes": dict(sorted(checkpoint.artifacts.items())),
        "claim_boundary": "human-approved local workflow release manifest; not silicon signoff or production EDA certification",
    }
    manifest["manifest_sha256"] = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    manifest_path = root / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    released = advance_checkpoint(checkpoint, "release", artifact_root=root, artifact_paths=["release-manifest.json"], human_approved=True)
    released_path = write_checkpoint(released, checkpoint_path)
    return {"status": "released", "manifest": str(manifest_path), "checkpoint": str(released_path), "checkpoint_sha256": released.digest(), "manifest_sha256": manifest["manifest_sha256"]}
