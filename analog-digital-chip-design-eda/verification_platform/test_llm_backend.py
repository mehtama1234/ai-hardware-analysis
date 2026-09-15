"""Contract tests for local LLM backend responses."""
import json
from pathlib import Path
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import verification_platform.llm_backend as llm_backend
from verification_platform.llm_backend import invoke_local_backend, invoke_local_backend_batch, invoke_openai_compatible_backend


ROOT = Path(__file__).resolve().parents[1]


class _Handler(BaseHTTPRequestHandler):
    response = {}

    def do_POST(self):
        body = json.dumps({"choices": [{"message": {"content": json.dumps(self.response)}}]}).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def _run(monkeypatch, response):
    _Handler.response = response
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("VERIFICATION_LLM_BASE_URL", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setenv("VERIFICATION_LLM_MODEL", "mock-local")
    result = invoke_openai_compatible_backend({"probe": True})
    server.shutdown()
    return result


def test_openai_compatible_backend_accepts_typed_proposal(monkeypatch):
    result = _run(monkeypatch, {"proposal_id": "mock", "kind": "diagnosis", "source_revision": "r", "action": "inspect", "rationale": "grounded", "evidence": ["e://1"], "status": "review_required"})
    assert result.status == "available" and result.proposal.proposal_id == "mock"


def test_openai_compatible_backend_rejects_unsafe_claim(monkeypatch):
    result = _run(monkeypatch, {"proposal_id": "unsafe", "kind": "diagnosis", "source_revision": "r", "action": "close", "rationale": "unsupported", "evidence": ["e://1"], "claims": ["passed"]})
    assert result.status == "blocked" and "closure claims" in (result.error or "")


def test_openai_compatible_backend_rejects_malformed_output(monkeypatch):
    result = _run(monkeypatch, {"proposal_id": "missing-evidence", "kind": "repair", "source_revision": "r", "action": "edit", "rationale": "unsupported", "evidence": []})
    assert result.status == "blocked"


def test_local_batch_backend_reuses_resident_worker(monkeypatch):
    monkeypatch.setenv("VERIFICATION_LLM_BATCH_COMMAND", f"{sys.executable} {ROOT / 'scripts/mock_llm_backend.py'}")
    diagnosis = {"failure": {"signal": "counter_q", "cycle": 6, "expected": "4", "actual": "5"}, "allowed_source_revision": "r", "evidence": ["e://1"]}
    repair = {"task": "propose_repair", "failure": diagnosis["failure"], "allowed_source_revision": "r", "evidence": ["e://1"], "repair_before": "before", "repair_after": "after"}
    first = invoke_local_backend_batch([diagnosis])
    worker = llm_backend._LOCAL_BATCH_WORKER
    second = invoke_local_backend_batch([repair])
    same_worker = worker is llm_backend._LOCAL_BATCH_WORKER
    llm_backend._stop_local_batch_worker()
    assert first[0].status == "available"
    assert second[0].status == "available" and second[0].raw["kind"] == "repair"
    assert same_worker


def test_single_request_backend_falls_back_to_resident_worker(monkeypatch):
    monkeypatch.delenv("VERIFICATION_LLM_COMMAND", raising=False)
    monkeypatch.setenv("VERIFICATION_LLM_BATCH_COMMAND", f"{sys.executable} {ROOT / 'scripts/mock_llm_backend.py'}")
    request = {"failure": {"signal": "counter_q", "cycle": 2, "expected": "0", "actual": "1"}, "allowed_source_revision": "r", "evidence": ["e://1"]}
    result = invoke_local_backend(request)
    llm_backend._stop_local_batch_worker()
    assert result.status == "available"
    assert result.proposal is not None and result.proposal.kind == "diagnosis"
