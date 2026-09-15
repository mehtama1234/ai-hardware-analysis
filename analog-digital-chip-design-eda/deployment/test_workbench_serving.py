from fastapi.testclient import TestClient
from deployment import verification_service as service
from pathlib import Path


def test_workbench_bootstraps_without_exposing_authenticated_api(monkeypatch, tmp_path):
    monkeypatch.setattr(service, 'JOB_ROOT', tmp_path / 'jobs')
    monkeypatch.setenv('VERIFICATION_SERVICE_API_KEY', 'test-secret')
    client = TestClient(service.app)
    page = client.get('/workbench/')
    assert page.status_code == 200
    assert 'verification-workbench-setup.js' in page.text
    for asset in service.WORKBENCH_ASSETS:
        assert client.get('/workbench/' + asset).status_code == 200
    assert client.get('/v1/projects').status_code == 401
    assert client.get('/v1/projects', headers={'X-API-Key': 'test-secret'}).status_code == 200
    assert client.get('/workbench/verification_service.py', headers={'X-API-Key': 'test-secret'}).status_code == 404


def test_workbench_contains_agentic_closure_review_controls():
    script = (Path(service.ROOT) / 'site' / 'verification-workbench.js').read_text(encoding='utf-8')
    assert '/v1/agentic-closure' in script
    assert '/v1/agentic-closure/signoff' in script
    assert 'Approve closure' in script and 'Reject closure' in script
