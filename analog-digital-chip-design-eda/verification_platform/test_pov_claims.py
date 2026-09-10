from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.claims import Claim
from verification_platform.pov import build_pov_report


def test_pov_report_exposes_unsupported_hardware_claim(tmp_path):
    report = build_pov_report(tmp_path, claims=[Claim("measured energy", "measured_hardware", ("instrument-measurement",))])
    assert report["claims"][0]["status"] == "unsupported"


def test_pov_report_carries_mixed_signal_manifest_boundary(tmp_path):
    manifest = {
        "manifest_sha256": "a" * 64,
        "artifacts": [{"path": "sim.json"}],
        "observed_evidence_kinds": ["simulation"],
        "claims": [{"domain": "measured_hardware", "status": "unsupported"}],
    }
    report = build_pov_report(tmp_path, mixed_signal_manifest=manifest)
    assert report["mixed_signal"]["artifact_count"] == 1
    assert report["mixed_signal"]["claims"][0]["status"] == "unsupported"
