from pathlib import Path

from scripts.preflight_customer_production_overlay import validate


def test_customer_preflight_rejects_missing_production_wiring(tmp_path: Path):
    rendered = tmp_path / "rendered.yaml"
    rendered.write_text("kind: Deployment\nmetadata:\n  name: verification-pilot\nspec: {}\n")
    errors = validate(rendered)
    assert any("API container is missing" in error for error in errors)
    assert any("CronJob is missing" in error for error in errors)


def test_customer_preflight_rejects_credential_material(tmp_path: Path):
    rendered = tmp_path / "rendered.yaml"
    rendered.write_text("kind: Secret\nstringData:\n  database-url: replace-out-of-band\n")
    assert any("credential placeholder" in error for error in validate(rendered))
