from deployment.verification_service import healthz, readyz, metrics, prometheus_metrics

def test_health_and_readiness_endpoints():
    assert healthz() == {"status": "ok", "service": "verification-pilot"}
    result = readyz()
    assert result["status"] == "ready"
    assert result["queue"] == "ready"
    assert metrics()["single_flight"] is True
    text = prometheus_metrics()
    assert 'verification_jobs_total{state="submitted"}' in text
    assert "verification_single_flight 1" in text
