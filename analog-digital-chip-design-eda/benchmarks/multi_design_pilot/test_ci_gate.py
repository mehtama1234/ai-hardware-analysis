import subprocess, sys
import json
from pathlib import Path

def test_ci_gate_runs_reproducibility_checks():
    root = Path(__file__).parent
    result = subprocess.run([sys.executable, str(root / "ci_gate.py")], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads((root / "runs/latest/pilot-release-manifest.json").read_text())
    assert manifest["hardware_required"] is False
    assert manifest["release_sha256"]
