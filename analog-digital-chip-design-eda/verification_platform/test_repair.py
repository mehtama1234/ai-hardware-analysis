from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.repair import apply_to_copy, propose_enable_guard
from verification_platform.triage import Failure


def test_repair_is_review_required_until_approved():
    proposal = propose_enable_guard(Failure(1, "counter_q", "0", "1"), requirement_id="REQ-COUNTER-HOLD", file="counter.sv", line=7)
    assert proposal.decision() == "review_required"
    assert proposal.decision(human_approved=True) == "allowed"


def test_approved_repair_writes_only_a_copy(tmp_path):
    source = tmp_path / "counter.sv"
    source.write_text("counter_q <= counter_q + 4'd1;\n", encoding="utf-8")
    proposal = propose_enable_guard(Failure(1, "counter_q", "0", "1"), requirement_id="REQ-COUNTER-HOLD", file="counter.sv", line=1)
    destination = apply_to_copy(source, tmp_path / "patched.sv", proposal, human_approved=True)
    assert "if (enable)" in destination.read_text(encoding="utf-8")
    assert "if (enable)" not in source.read_text(encoding="utf-8")
