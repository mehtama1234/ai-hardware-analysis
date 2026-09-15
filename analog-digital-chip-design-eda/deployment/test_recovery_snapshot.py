from pathlib import Path
import json

from scripts.verify_recovery_snapshot import verify_snapshot


def test_recovery_snapshot_preserves_artifact_inventory(tmp_path: Path):
    source = tmp_path / "artifacts"
    (source / "jobs" / "job-1").mkdir(parents=True)
    (source / "jobs.sqlite").write_bytes(b"sqlite-pilot")
    (source / "jobs" / "job-1" / "report.json").write_text('{"status":"passed"}\n', encoding="utf-8")
    result = verify_snapshot(source, tmp_path / "snapshot", tmp_path / "restored")
    assert result["match"] is True
    assert result["source_files"] == result["restored_files"] == 2
    assert result["source_sha256"] == result["restored_sha256"]
    output = tmp_path / "recovery.json"
    output.write_text(json.dumps(result), encoding="utf-8")
    assert json.loads(output.read_text())["match"] is True
