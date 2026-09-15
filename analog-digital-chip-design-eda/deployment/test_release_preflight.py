from pathlib import Path

from scripts.preflight_verification_deployment import validate


ROOT = Path(__file__).resolve().parents[1]


def test_release_preflight_accepts_current_pilot_manifest():
    assert validate(ROOT / "deployment" / "kubernetes") == []


def test_release_preflight_rejects_incomplete_manifest(tmp_path):
    manifest_dir = tmp_path / "kubernetes"
    manifest_dir.mkdir()
    (manifest_dir / "verification-pilot.yaml").write_text(
        (ROOT / "deployment" / "kubernetes" / "verification-pilot.yaml").read_text(), encoding="utf-8"
    )
    (manifest_dir / "kustomization.yaml").write_text(
        (ROOT / "deployment" / "kubernetes" / "kustomization.yaml").read_text(), encoding="utf-8"
    )
    # An isolated manifest is intentionally incomplete.
    (manifest_dir / "verification-pilot.yaml").write_text("apiVersion: v1\nkind: Service\n", encoding="utf-8")
    errors = validate(manifest_dir)
    assert any("PersistentVolumeClaim" in error for error in errors)
