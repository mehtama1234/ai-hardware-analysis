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
