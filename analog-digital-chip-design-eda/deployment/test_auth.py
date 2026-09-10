import asyncio
from deployment.verification_service import api_key_guard

class Request:
    url = type("URL", (), {"path": "/v1/jobs"})()
    headers = {}

async def _next(request):
    return "ok"

def test_api_key_guard_is_transparent_when_unconfigured(monkeypatch):
    monkeypatch.delenv("VERIFICATION_SERVICE_API_KEY", raising=False)
    assert asyncio.run(api_key_guard(Request(), _next)) == "ok"

def test_api_key_guard_rejects_missing_and_accepts_valid_key(monkeypatch):
    monkeypatch.setenv("VERIFICATION_SERVICE_API_KEY", "secret")
    missing = asyncio.run(api_key_guard(Request(), _next))
    assert missing.status_code == 401
    valid = Request()
    valid.headers = {"x-api-key": "secret"}
    assert asyncio.run(api_key_guard(valid, _next)) == "ok"

def test_api_key_guard_accepts_secret_file(monkeypatch, tmp_path):
    key_file = tmp_path / "api-key"
    key_file.write_text("file-secret\n", encoding="utf-8")
    monkeypatch.delenv("VERIFICATION_SERVICE_API_KEY", raising=False)
    monkeypatch.setenv("VERIFICATION_SERVICE_API_KEY_FILE", str(key_file))
    valid = Request()
    valid.headers = {"x-api-key": "file-secret"}
    assert asyncio.run(api_key_guard(valid, _next)) == "ok"
