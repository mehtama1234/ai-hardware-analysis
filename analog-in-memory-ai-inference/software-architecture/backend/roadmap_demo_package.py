from copy import deepcopy
from pathlib import Path
import json


MANIFEST_SCHEMA_VERSION = "review_package_manifest.v1"
ARTIFACT_SCHEMA_VERSION = "roadmap_step_artifact.v1"
REQUIRED_ARTIFACT_FIELDS = {
    "schema_version",
    "artifact_id",
    "step",
    "title",
    "proof_level",
    "status",
    "plain_reading",
    "what_this_supports",
    "what_this_does_not_prove",
    "missing_evidence",
    "next_actions",
}


def _package_dir():
    return Path(__file__).resolve().parent.parent / "review-package-demo"


def _load_json(path):
    return json.loads(path.read_text())


def _load_manifest():
    path = _package_dir() / "manifest.json"
    if not path.exists():
        raise ValueError("Demo review package manifest is missing.")
    manifest = _load_json(path)
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValueError("Unexpected demo review package manifest schema version.")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 14:
        raise ValueError("Demo review package must list exactly 14 artifacts.")
    if manifest.get("artifact_count") != len(artifacts):
        raise ValueError("Demo review package artifact_count does not match artifact list length.")
    return manifest


def _artifact_path(relative_path):
    package_dir = _package_dir()
    path = (package_dir / relative_path).resolve()
    if package_dir.resolve() not in path.parents:
        raise ValueError("Artifact path leaves the demo review package.")
    return path


def _validate_artifact(relative_path, expected_step):
    path = _artifact_path(relative_path)
    if not path.exists():
        raise ValueError(f"Demo review package artifact is missing: {relative_path}")
    artifact = _load_json(path)
    missing = sorted(REQUIRED_ARTIFACT_FIELDS - set(artifact))
    if missing:
        raise ValueError(f"Demo review package artifact {relative_path} is missing fields: {', '.join(missing)}")
    if artifact.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
        raise ValueError(f"Unexpected schema version in demo artifact: {relative_path}")
    if artifact.get("step") != expected_step:
        raise ValueError(f"Unexpected step number in demo artifact: {relative_path}")
    return artifact


def load_demo_review_package():
    manifest = _load_manifest()
    artifacts = {}
    ordered_artifacts = []
    for index, relative_path in enumerate(manifest["artifacts"], start=1):
        artifact = _validate_artifact(relative_path, index)
        artifact_id = artifact["artifact_id"]
        if artifact_id in artifacts:
            raise ValueError(f"Duplicate demo artifact id: {artifact_id}")
        artifacts[artifact_id] = artifact
        ordered_artifacts.append(
            {
                "artifact_id": artifact_id,
                "step": artifact["step"],
                "title": artifact["title"],
                "proof_level": artifact["proof_level"],
                "status": artifact["status"],
                "path": relative_path,
            }
        )

    result = deepcopy(manifest)
    result.update(
        {
            "result_type": "roadmap_demo_review_package",
            "source": "static_demo_review_package",
            "plain_reading": (
                "This endpoint returns the demo review package used by the roadmap page. "
                "It validates the manifest and all fourteen step artifacts, but it is not measured silicon proof."
            ),
            "ordered_artifacts": ordered_artifacts,
            "artifact_records": artifacts,
        }
    )
    return result


def load_demo_review_artifact(artifact_id):
    package = load_demo_review_package()
    artifact = package["artifact_records"].get(artifact_id)
    if not artifact:
        raise KeyError(artifact_id)
    return {
        "result_type": "roadmap_demo_review_artifact",
        "package_id": package["package_id"],
        "source": "static_demo_review_package",
        "artifact": artifact,
    }
