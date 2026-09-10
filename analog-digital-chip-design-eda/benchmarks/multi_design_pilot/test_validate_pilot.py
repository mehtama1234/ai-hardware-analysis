import json, subprocess, sys
from pathlib import Path

def test_clean_checkout_validation_passes():
    root = Path(__file__).parent
    subprocess.run([sys.executable, str(root / "run_pilot.py")], check=True, capture_output=True, text=True)
    result = subprocess.run([sys.executable, str(root / "validate_pilot.py")], check=False, capture_output=True, text=True)
    assert result.returncode == 0
    report = json.loads((root / "runs/latest/clean-checkout-validation.json").read_text())
    assert report["valid"] is True
    assert report["session_digest_valid"] is True
    assert report["release_digest_valid"] is True
    assert report["session_stages"][-1] == "closed"
    assert all(check["valid"] for check in report["manifests"].values())
