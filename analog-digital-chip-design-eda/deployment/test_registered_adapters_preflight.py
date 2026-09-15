import json

from scripts.preflight_registered_adapters import run


def test_registered_adapter_preflight_reports_available_and_blocked(tmp_path):
    raw = json.dumps([
        {"name": "reference", "kind": "simulation", "executable": "python3", "version": "3"},
        {"name": "customer-formal", "kind": "formal", "executable": "missing-formal-binary"},
    ])
    result = run(raw, tmp_path / "adapters.json")
    assert result["verified"] is False
    assert result["available_count"] == 1
    assert result["blocked_count"] == 1
    payload = json.loads((tmp_path / "adapters.json").read_text())
    assert payload["sha256"] == result["sha256"]


def test_registered_adapter_preflight_rejects_empty_registry(tmp_path):
    result = run("[]", tmp_path / "adapters.json")
    assert result["verified"] is False
    assert "at least one registered adapter is required" in result["errors"]
