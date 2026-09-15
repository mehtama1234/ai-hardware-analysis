import json
from pathlib import Path


def test_observability_dashboard_matches_exported_metrics():
    root = Path(__file__).resolve().parent
    dashboard = json.loads((root / "observability" / "verification-pilot-dashboard.json").read_text())
    assert dashboard["schema_version"] == "verification-observability-dashboard-v1"
    queries = {panel["id"]: panel["query"] for panel in dashboard["panels"]}
    assert queries["readiness"] == "verification_readiness"
    assert "verification_queue_jobs" in queries["queue"]
    assert "verification_http_responses_total" in queries["errors"]
    assert "verification_http_request_duration_seconds_sum" in queries["latency"]
    assert queries["adapters"] == "verification_eda_adapter_available"
    assert queries["oidc-refresh"] == "verification_oidc_jwks_refresh_total"
    assert queries["oidc-unknown-key"] == "verification_oidc_jwks_unknown_kid_total"
    assert queries["oidc-cache"] == "verification_oidc_cached_keys"
    assert queries["backup-age"] == "verification_backup_age_seconds"
    assert queries["backup-rpo"] == "verification_backup_rpo_seconds"
    assert queries["queue"] == 'verification_queue_jobs{state="queued"}'
    assert dashboard["panels"][1]["alert_above_metric"] == "verification_queue_capacity"
    alerts = {alert["name"]: alert for alert in dashboard["alerts"]}
    assert alerts["VerificationPilotNotReady"]["expr"] == "verification_readiness < 1"
    assert "verification_http_responses_total" in alerts["VerificationPilotHttp5xx"]["expr"]
    assert "verification_http_request_duration_seconds_sum" in alerts["VerificationPilotLatencyHigh"]["expr"]
    assert alerts["VerificationPilotAdapterBlocked"]["severity"] == "warning"
    assert any(alert["name"] == "VerificationPilotOidcUnknownKey" for alert in dashboard["alerts"])
    assert any(alert["name"] == "VerificationPilotQueueBacklog" for alert in dashboard["alerts"])
    assert "do not establish verification completeness" in dashboard["claim_boundary"]


def test_prometheus_rehearsal_scrapes_pilot_contract():
    root = Path(__file__).resolve().parent / "observability"
    config = (root / "prometheus.yml").read_text()
    overlay = (root / "docker-compose.observability.yml").read_text()
    assert "job_name: verification-pilot" in config
    assert "metrics_path: /metrics/prometheus" in config
    assert 'verification-pilot:8080' in config
    assert "prom/prometheus:v2.53.0" in overlay
    assert "prometheus.yml:/etc/prometheus/prometheus.yml:ro" in overlay
    assert "VERIFICATION_PROMETHEUS_RETENTION" in overlay
    assert "verification-pilot-alert-rules.yaml" in config
    assert "verification-pilot-alert-rules.yaml" in overlay


def test_alert_rules_cover_identity_rotation_and_readiness():
    root = Path(__file__).resolve().parent / "observability"
    rules = (root / "verification-pilot-alert-rules.yaml").read_text()
    assert "VerificationPilotNotReady" in rules
    assert "VerificationPilotOidcUnknownKey" in rules
    assert "increase(verification_oidc_jwks_unknown_kid_total[10m]) > 0" in rules
    assert "VerificationPilotOidcRefreshFailure" in rules
    assert "VerificationPilotLatencyHigh" in rules
    assert "VerificationPilotBackupStale" in rules
    assert 'sum(verification_queue_jobs{state="queued"}) > verification_queue_capacity' in rules
