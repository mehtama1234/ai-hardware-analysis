from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.claims import Claim, claim_status


def test_mixed_signal_claim_does_not_cross_evidence_domains():
    claim = Claim("measured analog latency", "measured_hardware", ("instrument-measurement",))
    assert claim_status(claim, {"simulation-waveform"}) == "unsupported"
    assert claim_status(claim, {"instrument-measurement"}) == "proven"
