import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient

from deployment.verification_service import app, _HTTP_COUNTERS


def test_http_request_log_is_correlated_and_does_not_include_credentials(caplog):
    caplog.set_level(logging.INFO, logger="verification.request")
    response = TestClient(app).get("/healthz?token=should-not-log", headers={"X-Request-ID": "trace-log-1"})
    assert response.status_code == 200
    records = [record for record in caplog.records if record.name == "verification.request"]
    assert records
    event = json.loads(records[-1].getMessage())
    schema = json.loads((Path(__file__).parent / "observability" / "verification-http-log.schema.json").read_text(encoding="utf-8"))
    assert event["schema_version"] == schema["properties"]["schema_version"]["const"]
    assert event == {"event": "http_request", "schema_version": "verification-http-log-v1", "request_id": "trace-log-1", "method": "GET", "path": "/healthz", "status_code": 200, "duration_ms": event["duration_ms"]}
    assert "should-not-log" not in records[-1].getMessage()


def test_http_request_exception_is_logged_with_correlation(caplog):
    def explode():
        raise ValueError("intentional test failure")

    app.add_api_route("/test-request-log-error", explode, methods=["GET"])
    caplog.set_level(logging.INFO, logger="verification.request")
    before = _HTTP_COUNTERS["5xx"]
    response = TestClient(app, raise_server_exceptions=False).get("/test-request-log-error", headers={"X-Request-ID": "trace-error-1"})
    assert response.status_code == 500
    events = [json.loads(record.getMessage()) for record in caplog.records if record.name == "verification.request"]
    assert any(event["request_id"] == "trace-error-1" and event["status_code"] == 500 and event["schema_version"] == "verification-http-log-v1" for event in events)
    assert _HTTP_COUNTERS["5xx"] == before + 1
