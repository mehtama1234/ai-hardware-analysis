from scripts.verify_customer_production_runtime import validate_http_statuses, validate_payloads
from scripts.verify_execution_sandbox_runtime import probe


def _ready():
    return {"status": "ready", "deployment": "customer-production", "deployment_config": {"ready": True}}


def _contract():
    return {"schema_version": "verification-platform-contract-v1", "execution_safety": {"shell": "disabled", "symlink_outputs": "blocked"}}


def test_runtime_smoke_accepts_complete_payloads():
    assert validate_payloads(_ready(), _contract(), "verification_queue_capacity 32\nverification_backup_age_seconds 1\nverification_backup_rpo_seconds 900\n") == []


def test_runtime_smoke_rejects_unready_or_incomplete_payloads():
    errors = validate_payloads({"status": "not-ready"}, {}, "")
    assert "/readyz did not report ready" in errors
    assert "unexpected platform contract schema" in errors
    assert "Prometheus metric verification_queue_capacity is missing" in errors


def test_execution_sandbox_probe_reports_missing_backend():
    result = probe(unshare_binary=None)
    assert result["schema_version"] == "verification-execution-sandbox-runtime-v1"
    assert result["required_namespaces"] == ["user", "pid", "mount", "network"]


def test_runtime_payload_validation_can_require_sandbox_probe():
    from scripts.verify_customer_production_runtime import validate_payloads

    errors = validate_payloads(_ready(), _contract(), "verification_queue_capacity 32\nverification_backup_age_seconds 1\nverification_backup_rpo_seconds 900\n", {"verified": False})
    assert errors == ["execution sandbox runtime probe did not pass"]


def test_runtime_preflight_rejects_non_success_http_statuses():
    assert validate_http_statuses({"/readyz": "503", "/v1/contract": "200", "/metrics/prometheus": "202"}) == [
        "/readyz returned HTTP 503", "/metrics/prometheus returned HTTP 202"
    ]


def test_runtime_preflight_reports_contract_failure_stage(monkeypatch, capsys):
    import scripts.verify_customer_production_runtime as runtime

    def fail_contract(_base, path, _headers):
        if path == "/readyz":
            return _ready(), "200"
        raise OSError("connection reset")

    monkeypatch.setattr(runtime, "_get", fail_contract)
    monkeypatch.setattr(runtime, "__name__", "__main__")
    # Exercise the public entry point without requiring a live service.
    import sys
    monkeypatch.setattr(sys, "argv", ["preflight", "http://example.test"])
    assert runtime.main() == 2
    output = capsys.readouterr().out
    assert '"schema_version": "verification-customer-production-runtime-v1"' in output
    assert '"schema_path": "deployment/observability/verification-customer-production-runtime.schema.json"' in output
    assert '"stage": "contract"' in output


def test_runtime_preflight_schema_declares_versioned_pass_and_blocked_shapes():
    import json
    from pathlib import Path

    schema = json.loads((Path(__file__).parent / "observability" / "verification-customer-production-runtime.schema.json").read_text(encoding="utf-8"))
    assert schema["$id"] == "verification-customer-production-runtime-v1"
    assert schema["properties"]["status"]["enum"] == ["passed", "blocked"]
    assert any("deployment" in branch.get("then", {}).get("required", []) for branch in schema["allOf"])
    assert any("errors" in branch.get("then", {}).get("anyOf", [{}])[0].get("required", []) for branch in schema["allOf"])


def test_runtime_preflight_examples_validate_against_json_schema():
    import json
    from pathlib import Path
    from jsonschema import validate

    schema = json.loads((Path(__file__).parent / "observability" / "verification-customer-production-runtime.schema.json").read_text(encoding="utf-8"))
    base = {"schema_version": "verification-customer-production-runtime-v1", "schema_path": "deployment/observability/verification-customer-production-runtime.schema.json"}
    validate({**base, "status": "passed", "deployment": "customer-production", "contract": "verification-platform-contract-v1", "checks": ["readyz"]}, schema)
    validate({**base, "status": "blocked", "errors": ["deployment configuration is not ready"]}, schema)
