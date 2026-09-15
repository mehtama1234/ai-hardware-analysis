import json
from fastapi.testclient import TestClient
import deployment.verification_service as service
from deployment.verification_service import app, healthz, readyz, metrics, prometheus_metrics, capabilities, platform_contract, release_readiness, pilot_scorecard_summary

def test_health_and_readiness_endpoints():
    assert healthz() == {"status": "ok", "service": "verification-pilot"}
    result = readyz()
    assert result["status"] == "ready"
    assert result["queue"] == "ready"
    assert result["storage"] == "ready"
    assert result["storage_provider"] == "filesystem-pilot"
    assert result["storage_contract"] == "evidence-store-v1"
    assert result["identity_mode"] == "api-key-pilot"
    assert result["identity_subject_required"] is False
    assert result["deployment"] == "pilot"
    assert result["deployment_config"]["ready"] is True
    assert result["storage_controls"]["managed_controls_required"] is False
    assert metrics()["single_flight"] is True
    text = prometheus_metrics()
    assert 'verification_jobs_total{state="submitted"}' in text
    assert "verification_single_flight 1" in text
    assert 'verification_http_responses_total{class="2xx"}' in text
    assert 'verification_http_request_duration_seconds_sum{class="2xx"}' in text
    assert 'verification_http_request_duration_seconds_count{class="2xx"}' in text
    assert "verification_queue_capacity" in text

def test_capabilities_reports_measured_backend_states():
    result = capabilities()
    assert result["schema_version"] == "verification-capabilities-v1"
    assert {item["tool"] for item in result["capabilities"]} >= {"iverilog", "verilator", "yosys", "sby"}
    assert result["available"] + result["blocked"] == len(result["capabilities"])
    assert result["eda_adapters"] == []


def test_capabilities_publishes_registered_adapter_execution_contract(monkeypatch):
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", '[{"name":"customer-sim","kind":"simulation","executable":"sim","expected_artifacts":["simulation/waveform.vcd"],"timeout_seconds":120}]')
    monkeypatch.setattr("deployment.adapter_registry.shutil.which", lambda command: "/usr/bin/sim")
    result = capabilities()
    adapter = result["eda_adapters"][0]
    assert adapter["available"] is True
    assert adapter["expected_artifacts"] == ["simulation/waveform.vcd"]
    assert adapter["timeout_seconds"] == 120


def test_prometheus_reports_adapter_and_readiness_gauges(monkeypatch):
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", '[{"name":"pilot-sim","kind":"simulation","executable":"missing-pilot-sim"}]')
    text = prometheus_metrics()
    assert 'verification_eda_adapter_available{name="pilot-sim",kind="simulation"} 0' in text
    assert "verification_readiness 1" in text


def test_prometheus_reports_backup_freshness_contract(tmp_path, monkeypatch):
    manifest = tmp_path / "backup.dump.manifest.json"
    manifest.write_text('{"created_at":"2026-09-10T12:00:00Z"}')
    monkeypatch.setenv("VERIFICATION_BACKUP_MANIFEST_PATH", str(manifest))
    monkeypatch.setenv("VERIFICATION_DR_RPO_MINUTES", "15")
    text = prometheus_metrics()
    assert "verification_backup_last_success_timestamp " in text
    assert "verification_backup_age_seconds " in text
    assert "verification_backup_rpo_seconds 900" in text


def test_platform_contract_exposes_versioned_workflow_and_claim_boundaries():
    result = platform_contract()
    assert result["schema_version"] == "verification-platform-contract-v1"
    assert result["workflow"][0:3] == ["ingest", "plan", "generate"]
    assert result["agent_proposals"]["execution_authority"] == "deterministic-only"
    assert "evidence" in result["agent_proposals"]["required_fields"]
    assert "hash_bound_signoff" in result["evidence_guarantees"]
    assert "simulation_is_not_exhaustive_coverage" in result["claim_boundaries"]
    assert result["storage_contract"] == "evidence-store-v1"
    assert result["observability_contract"].endswith("verification-pilot-dashboard.json")
    assert result["request_log_schema"].endswith("verification-http-log.schema.json")
    assert result["readiness_report_tool"] == "scripts/report_production_readiness.py"
    assert result["handoff_manifest_tool"].endswith("build_commercial_handoff_manifest.py")
    assert result["handoff_manifest_verifier"].endswith("verify_commercial_handoff_manifest.py")
    assert result["execution_safety"]["shell"] == "disabled"
    assert result["execution_safety"]["symlink_outputs"] == "blocked"
    assert "per-job namespace and read-only source mounts" in result["execution_safety"]["customer_production_requirements"]
    assert "non-empty customer EDA adapter registry" in result["execution_safety"]["customer_production_requirements"]
    assert "managed logs and alert routing" in result["execution_safety"]["customer_production_requirements"]
    requirements = result["customer_production_requirements"]
    assert "VERIFICATION_EDA_ADAPTERS" in requirements["required_environment"]
    assert "VERIFICATION_SLO_OWNER" in requirements["required_environment"]
    assert "object-store control probe" in requirements["runtime_evidence"]
    assert "signed customer pilot" in requirements["claim_boundary"]
    assert requirements["runtime_preflight_schema"] == "verification-customer-production-runtime-v1"
    assert requirements["runtime_preflight_schema_path"].endswith("verification-customer-production-runtime.schema.json")
    assert result["managed_state_contract"].endswith("managed_state_contract.py")
    assert result["capabilities_endpoint"] == "/v1/capabilities"
    assert result["readiness_endpoint"] == "/v1/readiness"
    assert result["pilot_scorecard_endpoint"] == "/v1/pilot/scorecard"
    assert result["storage_controls_endpoint"] == "/v1/storage/controls"
    assert result["customer_adapter_job"]["required_fields"] == ["project_id", "adapter_name", "adapter_args"]
    assert "adapter-result.json" in result["customer_adapter_job"]["evidence"]
    assert result["customer_adapter_job"]["argument_limits"] == {"max_count": 64, "max_argument_bytes": 4096, "max_total_bytes": 65536}


def test_release_readiness_returns_bounded_summary(tmp_path, monkeypatch):
    report = tmp_path / "readiness.json"
    report.write_text('{"schema_version":"verification-production-readiness-v1","control_count":2,"verified_count":1,"open_count":1,"open_controls":["pilot"],"customer_production_ready":false,"claim_boundary":"summary only"}', encoding="utf-8")
    monkeypatch.setenv("VERIFICATION_READINESS_REPORT_PATH", str(report))
    result = release_readiness()
    assert result["control_count"] == 2
    assert result["open_controls"] == ["pilot"]
    assert "path" not in result


def test_pilot_scorecard_summary_omits_raw_observations(tmp_path, monkeypatch):
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps({
        "schema_version": "verification-pilot-scorecard-v1",
        "pilot": {"customer": "fixture", "project": "p", "sample_size": 5, "baseline_window": "b", "workbench_window": "w"},
        "metrics": [{"name": name, "unit": "seconds", "baseline_median": None, "workbench_median": None, "evidence": []} for name in ("triage_latency", "root_cause_usefulness", "reproduction_time", "evidence_completeness", "manual_effort", "closure_integrity")],
        "review": {}, "claim_boundary": "fixture only"
    }), encoding="utf-8")
    monkeypatch.setenv("VERIFICATION_SCORECARD_PATH", str(scorecard))
    result = pilot_scorecard_summary()
    assert result["finalized"] is False
    assert result["pilot"]["sample_size"] == 5
    assert "observations" not in result
    assert all("evidence_count" in metric for metric in result["metrics"])


def test_pilot_scorecard_summary_normalizes_malformed_sample_metadata(tmp_path, monkeypatch):
    source = json.loads((service.ROOT / ".artifacts" / "open-source-pilot-scorecard.json").read_text(encoding="utf-8"))
    source["pilot"]["sample_size"] = "not-a-number"
    source["review"] = "invalid"
    source.pop("scorecard_sha256", None)
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps(source), encoding="utf-8")
    monkeypatch.setenv("VERIFICATION_SCORECARD_PATH", str(scorecard))
    result = pilot_scorecard_summary()
    assert result["pilot"]["sample_size"] == 0
    assert result["finalized"] is False


def test_pilot_scorecard_http_route_returns_bounded_payload(tmp_path, monkeypatch):
    source = (service.ROOT / ".artifacts" / "open-source-pilot-scorecard.json").read_text(encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(source, encoding="utf-8")
    monkeypatch.setenv("VERIFICATION_SCORECARD_PATH", str(scorecard))
    response = TestClient(app).get("/v1/pilot/scorecard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "verification-pilot-scorecard-v1"
    assert "observations" not in payload
    assert all("evidence_count" in metric for metric in payload["metrics"])


def test_storage_controls_endpoint_reports_pilot_boundary():
    result = service.storage_controls()
    assert result["provider"] == "filesystem-pilot"
    assert result["ready"] is True
    assert result["managed_controls_required"] is True


def test_platform_contract_route_requires_api_auth(monkeypatch):
    monkeypatch.setenv("VERIFICATION_SERVICE_API_KEY", "contract-secret")
    client = TestClient(app)
    denied = client.get("/v1/contract")
    assert denied.status_code == 401
    allowed = client.get("/v1/contract", headers={"X-API-Key": "contract-secret"})
    assert allowed.status_code == 200
    assert allowed.json()["schema_version"] == "verification-platform-contract-v1"
    assert allowed.headers["cache-control"] == "no-store"


def test_api_responses_expose_request_correlation_id(monkeypatch):
    monkeypatch.setenv("VERIFICATION_SERVICE_API_KEY", "secret")
    client = TestClient(app)
    supplied = client.get("/healthz", headers={"X-Request-ID": "pilot-trace-42"})
    generated = client.get("/healthz")
    invalid = client.get("/healthz", headers={"X-Request-ID": "pilot trace with spaces"})
    assert supplied.headers["x-request-id"] == "pilot-trace-42"
    assert generated.headers["x-request-id"]
    assert len(generated.headers["x-request-id"]) == 32
    assert invalid.headers["x-request-id"] != "pilot trace with spaces"
    assert len(invalid.headers["x-request-id"]) == 32
    rejected = client.get("/v1/projects", headers={"X-Request-ID": "auth-denied-9"})
    assert rejected.status_code == 401
    assert rejected.headers["x-request-id"] == "auth-denied-9"
    assert rejected.headers["x-frame-options"] == "DENY"
    monkeypatch.setenv("VERIFICATION_PROJECT_KEYS", '{"p1":"project-secret"}')
    project_rejected = client.get("/v1/projects/p1", headers={"X-API-Key": "secret", "X-Request-ID": "project-denied-3"})
    assert project_rejected.status_code == 403
    assert project_rejected.headers["x-request-id"] == "project-denied-3"
    assert project_rejected.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in project_rejected.headers["content-security-policy"]


def test_api_responses_include_conservative_browser_security_headers():
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers["permissions-policy"]
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_workbench_html_carries_browser_policy():
    client = TestClient(app)
    response = client.get("/workbench/verification-workbench.html")
    assert response.status_code == 200
    assert "script-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["x-frame-options"] == "DENY"


def test_readiness_rejects_unwritable_artifact_root(tmp_path, monkeypatch):
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("occupied")
    monkeypatch.setattr(service, "JOB_ROOT", blocked_parent / "jobs")
    result = readyz()
    assert result["status"] == "not-ready"
    assert result["storage"] == "unavailable"


def test_readiness_rejects_unimplemented_storage_provider(monkeypatch):
    monkeypatch.setattr(service, "EVIDENCE_STORE_PROVIDER", "managed-object-store")
    result = readyz()
    assert result["status"] == "not-ready"
    assert result["storage_provider"] == "managed-object-store"
    assert "not implemented" in result["storage_provider_error"]


def test_readiness_rejects_malformed_adapter_configuration(monkeypatch):
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", "not-json")
    result = readyz()
    assert result["status"] == "not-ready"
    assert result["adapter_config"] == "invalid"
    assert "JSON array" in result["adapter_config_error"]


def test_readiness_reports_identity_subject_enforcement(monkeypatch):
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "true")
    result = readyz()
    assert result["status"] == "ready"
    assert result["identity_mode"] == "oidc-subject-required"
    assert result["identity_subject_required"] is True


def test_customer_production_readiness_fails_closed_without_managed_contract(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    result = readyz()
    assert result["status"] == "not-ready"
    assert result["deployment"] == "customer-production"
    assert result["deployment_config"]["ready"] is False
    assert "VERIFICATION_DATABASE_URL" in result["deployment_config_error"]


def test_customer_production_requires_bounded_dr_targets(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    result = readyz()
    assert "VERIFICATION_DR_RPO_MINUTES" in result["deployment_config_error"]
    assert "VERIFICATION_DR_RTO_MINUTES" in result["deployment_config_error"]


def test_customer_production_requires_workspace_quotas(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    result = readyz()
    assert "VERIFICATION_JOB_MAX_WORKSPACE_BYTES" in result["deployment_config_error"]
    assert "VERIFICATION_JOB_MAX_FILE_BYTES" in result["deployment_config_error"]


def test_customer_production_rejects_file_quota_larger_than_workspace(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    monkeypatch.setenv("VERIFICATION_JOB_MAX_WORKSPACE_BYTES", "100")
    monkeypatch.setenv("VERIFICATION_JOB_MAX_FILE_BYTES", "101")
    result = readyz()
    assert "must not exceed" in result["deployment_config_error"]


def test_customer_production_rejects_non_https_jwks(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    monkeypatch.setenv("VERIFICATION_IDENTITY_JWKS_URL", "http://issuer.internal/jwks")
    result = readyz()
    assert result["status"] == "not-ready"
    assert "https://" in result["deployment_config_error"]


def test_customer_production_rejects_non_https_issuer(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    monkeypatch.setenv("VERIFICATION_IDENTITY_ISSUER", "http://issuer.internal")
    result = readyz()
    assert result["status"] == "not-ready"
    assert "VERIFICATION_IDENTITY_ISSUER" in result["deployment_config_error"]


def test_customer_production_readiness_accepts_declared_managed_contract(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    monkeypatch.setenv("VERIFICATION_DATABASE_URL", "postgresql://db.internal/verification")
    monkeypatch.setenv("VERIFICATION_EVIDENCE_STORE_PROVIDER", "object-store")
    monkeypatch.setenv("VERIFICATION_EVIDENCE_STORE_BUCKET", "verification-evidence")
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "true")
    monkeypatch.setenv("VERIFICATION_REVIEWER_ROLE", "verification-reviewer")
    monkeypatch.setenv("VERIFICATION_OPERATOR_ROLE", "verification-operator")
    monkeypatch.setenv("VERIFICATION_PROJECT_SUBJECTS", '{"customer-project":["subject-1"]}')
    monkeypatch.setenv("VERIFICATION_IDENTITY_ISSUER", "https://issuer.internal")
    monkeypatch.setenv("VERIFICATION_IDENTITY_AUDIENCE", "verification-platform")
    monkeypatch.setenv("VERIFICATION_IDENTITY_JWKS_URL", "https://issuer.internal/.well-known/jwks.json")
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_TOKEN", "true")
    monkeypatch.setenv("VERIFICATION_EXECUTION_SANDBOX", "isolated")
    monkeypatch.setenv("VERIFICATION_EXECUTION_WORKSPACE", "disposable")
    monkeypatch.setenv("VERIFICATION_EXECUTION_NETWORK_POLICY", "deny-by-default")
    monkeypatch.setenv("VERIFICATION_JOB_MAX_WORKSPACE_BYTES", "2147483648")
    monkeypatch.setenv("VERIFICATION_JOB_MAX_FILE_BYTES", "536870912")
    monkeypatch.setenv("VERIFICATION_OBSERVABILITY_ENDPOINT", "https://otel.internal")
    monkeypatch.setenv("VERIFICATION_LOGS_ENDPOINT", "https://logs.internal")
    monkeypatch.setenv("VERIFICATION_ALERTMANAGER_ENDPOINT", "https://alerts.internal")
    monkeypatch.setenv("VERIFICATION_SLO_OWNER", "verification-oncall@example.com")
    monkeypatch.setenv("VERIFICATION_EDA_ADAPTERS", '[{"name":"customer-sim","kind":"simulation","executable":"customer-sim"}]')
    monkeypatch.setenv("VERIFICATION_BACKUP_POLICY", "daily-35d")
    monkeypatch.setenv("VERIFICATION_DR_RPO_MINUTES", "15")
    monkeypatch.setenv("VERIFICATION_DR_RTO_MINUTES", "60")
    monkeypatch.setattr(service, "EVIDENCE_STORE_PROVIDER", "object-store")
    result = readyz()
    assert result["deployment_config"]["ready"] is True
    # The pilot image still refuses to advertise an unimplemented object-store
    # provider; declarations are necessary but are not an implementation claim.
    assert result["status"] == "not-ready"


def test_customer_production_requires_project_subject_mapping(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    monkeypatch.setenv("VERIFICATION_DATABASE_URL", "postgresql://db.internal/verification")
    monkeypatch.setenv("VERIFICATION_EVIDENCE_STORE_PROVIDER", "object-store")
    monkeypatch.setenv("VERIFICATION_EVIDENCE_STORE_BUCKET", "verification-evidence")
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_SUBJECT", "true")
    monkeypatch.setenv("VERIFICATION_REVIEWER_ROLE", "verification-reviewer")
    monkeypatch.setenv("VERIFICATION_IDENTITY_ISSUER", "https://issuer.internal")
    monkeypatch.setenv("VERIFICATION_IDENTITY_AUDIENCE", "verification-platform")
    monkeypatch.setenv("VERIFICATION_IDENTITY_JWKS_URL", "https://issuer.internal/.well-known/jwks.json")
    monkeypatch.setenv("VERIFICATION_REQUIRE_IDENTITY_TOKEN", "true")
    monkeypatch.setenv("VERIFICATION_EXECUTION_SANDBOX", "isolated")
    monkeypatch.setenv("VERIFICATION_EXECUTION_WORKSPACE", "disposable")
    monkeypatch.setenv("VERIFICATION_EXECUTION_NETWORK_POLICY", "deny-by-default")
    monkeypatch.setenv("VERIFICATION_OBSERVABILITY_ENDPOINT", "https://otel.internal")
    monkeypatch.setenv("VERIFICATION_BACKUP_POLICY", "daily-35d")
    monkeypatch.setenv("VERIFICATION_DR_RPO_MINUTES", "15")
    monkeypatch.setenv("VERIFICATION_DR_RTO_MINUTES", "60")
    result = readyz()
    assert result["deployment_config"]["ready"] is False
    assert "VERIFICATION_PROJECT_SUBJECTS" in result["deployment_config_error"]


def test_customer_production_requires_customer_adapter_registry(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DEPLOYMENT_TIER", "customer-production")
    result = readyz()
    assert result["deployment_config"]["ready"] is False
    assert "VERIFICATION_EDA_ADAPTERS" in result["deployment_config_error"]
