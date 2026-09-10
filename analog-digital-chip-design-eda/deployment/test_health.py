from deployment.verification_service import healthz, readyz, metrics, prometheus_metrics, capabilities

def test_health_and_readiness_endpoints():
    assert healthz() == {"status": "ok", "service": "verification-pilot"}
    result = readyz()
    assert result["status"] == "ready"
    assert result["queue"] == "ready"
    assert metrics()["single_flight"] is True
    text = prometheus_metrics()
    assert 'verification_jobs_total{state="submitted"}' in text
    assert "verification_single_flight 1" in text

def test_capabilities_reports_measured_backend_states():
    result = capabilities()
    assert result["schema_version"] == "verification-capabilities-v1"
    assert {item["tool"] for item in result["capabilities"]} >= {"iverilog", "verilator", "yosys", "sby"}
    assert result["available"] + result["blocked"] == len(result["capabilities"])
