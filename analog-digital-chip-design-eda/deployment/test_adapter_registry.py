import json

import pytest

from deployment.adapter_registry import discover_registered_adapters


def test_registry_reports_available_and_blocked_without_credentials(monkeypatch):
    monkeypatch.setattr("deployment.adapter_registry.shutil.which", lambda command: "/bin/tool" if command == "sim" else None)
    adapters = discover_registered_adapters(json.dumps([
        {"name": "customer-sim", "kind": "simulation", "executable": "sim", "version": "2026.1"},
        {"name": "customer-formal", "kind": "formal", "executable": "formal"},
    ]))
    assert [(item.name, item.status) for item in adapters] == [("customer-sim", "available"), ("customer-formal", "blocked")]
    assert all("key" not in item.__dict__ for item in adapters)


def test_registry_carries_bounded_execution_contract(monkeypatch):
    monkeypatch.setattr("deployment.adapter_registry.shutil.which", lambda command: "/bin/tool")
    from deployment.adapter_registry import adapter_spec

    spec = adapter_spec("customer-sim", json.dumps([{
        "name": "customer-sim",
        "kind": "simulation",
        "executable": "sim",
        "expected_artifacts": ["simulation/waveform.vcd", "simulation/result.json"],
        "timeout_seconds": 120,
    }]))
    assert spec.expected_artifacts == ("simulation/waveform.vcd", "simulation/result.json")
    assert spec.timeout_seconds == 120


@pytest.mark.parametrize("entry", [
    {"name": "x", "kind": "sim", "executable": "sim", "expected_artifacts": ["../escape"]},
    {"name": "x", "kind": "sim", "executable": "sim", "timeout_seconds": 0},
    {"name": "x", "kind": "sim", "executable": "sim", "timeout_seconds": "nan"},
])
def test_registry_rejects_unsafe_execution_contract(entry):
    with pytest.raises(ValueError):
        discover_registered_adapters(json.dumps([entry]))


@pytest.mark.parametrize("raw", ["{}", "not-json", json.dumps([{"name": "x", "kind": "sim", "executable": "/tmp/tool"}]), json.dumps([{"name": "x", "kind": "sim", "executable": "sim"}, {"name": "x", "kind": "formal", "executable": "formal"}])])
def test_registry_rejects_invalid_configuration(raw):
    with pytest.raises(ValueError):
        discover_registered_adapters(raw)


def test_reference_adapter_acceptance_matrix_is_complete(tmp_path):
    from scripts.run_adapter_acceptance import run_acceptance

    result = run_acceptance(tmp_path)
    assert result["verified"] is True
    assert {case["case"] for case in result["cases"]} == {"pass", "fail", "timeout", "missing-artifact"}
