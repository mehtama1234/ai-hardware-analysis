from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.capabilities import discover_capabilities, write_capabilities


def test_capability_discovery_labels_missing_backend(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda executable: "/usr/bin/" + executable if executable == "iverilog" else None)
    capabilities = discover_capabilities([("sim", "iverilog"), ("formal", "sby")])
    assert [(item.tool, item.status) for item in capabilities] == [("sim", "available"), ("formal", "blocked")]
    assert write_capabilities(tmp_path / "capabilities.json", capabilities).is_file()
