import json
from pathlib import Path

from scripts.verify_handoff_upload_contract import verify


def _write(tmp_path: Path, artifacts: dict[str, object], paths: str):
    manifest = tmp_path / "manifest.json"
    workflow = tmp_path / "workflow.yml"
    manifest.write_text(json.dumps({"artifacts": artifacts}), encoding="utf-8")
    workflow.write_text("jobs:\n  release:\n    steps:\n      - uses: actions/upload-artifact@v4\n        with:\n          path: |\n" + "".join(f"            {line}\n" for line in paths.splitlines()), encoding="utf-8")
    return manifest, workflow


def test_upload_contract_accepts_generated_artifacts(tmp_path):
    manifest, workflow = _write(tmp_path, {".artifacts/a.json": {}}, ".artifacts/a.json")
    assert verify(manifest, workflow) == []


def test_upload_contract_rejects_omitted_generated_artifact(tmp_path):
    manifest, workflow = _write(tmp_path, {".artifacts/a.json": {}, ".artifacts/b.json": {}}, ".artifacts/a.json")
    assert verify(manifest, workflow) == ["generated artifact is not uploaded: .artifacts/b.json"]


def test_upload_contract_allows_local_customer_runtime_rehearsal(tmp_path):
    manifest, workflow = _write(tmp_path, {".artifacts/customer-production-runtime-preflight.json": {}}, "")
    assert verify(manifest, workflow) == []
