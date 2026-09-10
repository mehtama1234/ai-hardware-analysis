from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.claims import Claim
from verification_platform.mixed_signal import build_mixed_signal_manifest


def test_mixed_signal_manifest_preserves_claim_boundary(tmp_path):
    (tmp_path / "sim.json").write_text("{}", encoding="utf-8")
    (tmp_path / "layout.json").write_text("{}", encoding="utf-8")
    manifest = build_mixed_signal_manifest(
        tmp_path,
        [("sim.json", "simulation"), ("layout.json", "physical_layout")],
        source_revision="aimc-case-v1",
        claims=[
            Claim("converter simulation is reproducible", "simulation", ("simulation",)),
            Claim("silicon latency is measured", "measured_hardware", ("measured_hardware",)),
        ],
    )
    assert manifest["claims"][0]["status"] == "proven"
    assert manifest["claims"][1]["status"] == "unsupported"
    assert manifest["artifacts"][0]["evidence"]["sha256"]
