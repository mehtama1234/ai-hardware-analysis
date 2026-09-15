from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.artifacts import build_artifact_manifest, verify_artifact_manifest


def test_artifact_manifest_hashes_run_files(tmp_path):
    (tmp_path / "a.log").write_text("a", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.vcd").write_text("b", encoding="utf-8")
    manifest = build_artifact_manifest(tmp_path)
    assert [item["path"] for item in manifest["artifacts"]] == ["a.log", "nested/b.vcd"]
    assert len(manifest["manifest_sha256"]) == 64
    assert verify_artifact_manifest(tmp_path, manifest)["valid"]
    (tmp_path / "a.log").write_text("tampered", encoding="utf-8")
    assert not verify_artifact_manifest(tmp_path, manifest)["valid"]


def test_artifact_manifest_rejects_path_escape_and_size_tampering(tmp_path):
    (tmp_path / "safe.txt").write_text("safe", encoding="utf-8")
    manifest = build_artifact_manifest(tmp_path)
    escaped = dict(manifest)
    escaped["artifacts"] = [{"path": "../outside", "sha256": "x", "size_bytes": 1}]
    assert not verify_artifact_manifest(tmp_path, escaped)["valid"]
    resized = build_artifact_manifest(tmp_path)
    resized["artifacts"][0]["size_bytes"] += 1
    assert not verify_artifact_manifest(tmp_path, resized)["valid"]


def test_artifact_manifest_rejects_unlisted_files(tmp_path):
    (tmp_path / "a.log").write_text("a", encoding="utf-8")
    manifest = build_artifact_manifest(tmp_path)
    (tmp_path / "new.log").write_text("new", encoding="utf-8")
    audit = verify_artifact_manifest(tmp_path, manifest)
    assert not audit["valid"]
    assert audit["unlisted"] == ["new.log"]
