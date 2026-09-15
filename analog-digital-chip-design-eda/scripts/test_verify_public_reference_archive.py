import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))
from verify_public_reference_archive import verify


def test_public_reference_archive_verifies_and_rejects_digest_tamper(tmp_path):
    root = Path(__file__).parents[1]
    archive = tmp_path / "release.tar.gz"
    subprocess.run([sys.executable, str(root / "scripts/build_public_reference_archive.py"), "--output", str(archive)], check=True, capture_output=True, text=True)
    sidecar = archive.with_suffix(archive.suffix + ".json")
    assert verify(archive, sidecar) == []
    payload = json.loads(sidecar.read_text())
    payload["archive_sha256"] = "0" * 64
    sidecar.write_text(json.dumps(payload))
    assert "archive digest does not match sidecar" in verify(archive, sidecar)
