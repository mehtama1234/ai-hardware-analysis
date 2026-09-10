from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.ledger import ProvenanceLedger, ToolRun, evidence_for


def test_evidence_hash_and_ledger_round_trip(tmp_path):
    artifact = tmp_path / "compile.log"
    artifact.write_text("PASS\n", encoding="utf-8")
    ref = evidence_for(artifact, root=tmp_path, kind="tool-log", source_revision="rev-1")
    ledger = ProvenanceLedger(runs=[ToolRun("run-1", "iverilog", ["iverilog", "dut.sv"], "passed", 0, "rev-1", [ref])])
    output = tmp_path / "ledger.json"
    digest = ledger.write(output)
    assert len(digest) == 64
    assert ref.path == "compile.log"
    assert ref.sha256 in output.read_text(encoding="utf-8")


def test_evidence_outside_root_is_rejected(tmp_path):
    outside = tmp_path.parent / "outside.log"
    outside.write_text("x", encoding="utf-8")
    try:
        evidence_for(outside, root=tmp_path, kind="tool-log", source_revision="rev-1")
    except ValueError as exc:
        assert "inside" in str(exc)
    else:
        raise AssertionError("outside-root evidence must be rejected")
