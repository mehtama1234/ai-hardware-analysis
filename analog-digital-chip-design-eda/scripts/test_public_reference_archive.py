import json
import tarfile
from pathlib import Path
import subprocess
import sys


def test_public_reference_archive_excludes_generated_runs(tmp_path):
    root = Path(__file__).parents[1]
    output = tmp_path / "release.tar.gz"
    result = subprocess.run([sys.executable, str(root / "scripts/build_public_reference_archive.py"), "--output", str(output)], check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    assert payload["file_count"] > 100
    with tarfile.open(output, "r:gz") as archive:
        names = archive.getnames()
    assert "public-reference/PUBLIC_REFERENCE_RELEASE.md" in names
    assert not any("/runs/" in name or "/.artifacts/" in name for name in names)
    assert (tmp_path / "release.tar.gz.json").is_file()
