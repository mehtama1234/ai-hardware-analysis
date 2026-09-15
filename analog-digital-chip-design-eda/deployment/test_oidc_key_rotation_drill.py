import json

from scripts.run_oidc_key_rotation_drill import run


def test_oidc_key_rotation_drill_records_all_rotation_stages(tmp_path):
    output = tmp_path / "rotation.json"
    result = run(output)
    assert result["verified"] is True
    assert result["stages"] == {
        "old_key_canary": True,
        "overlap_new_key_canary": True,
        "retired_old_key_rejected": True,
    }
    assert result["jwks_refresh_total"] >= 3
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["sha256"] == result["sha256"]
