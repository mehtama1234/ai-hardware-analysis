from deployment.collateral_store import CollateralStore
from deployment.repair_service import propose_repair


def test_repair_requires_approval_and_exactly_one_match(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r1", "module counter; assign q = bad; endmodule\n")
    review, content = propose_repair(record, collateral_root=tmp_path / "collateral", before="bad", after="good", rationale="correct the selected driver")
    assert review["status"] == "review_required"
    assert content is None
    allowed, repaired = propose_repair(record, collateral_root=tmp_path / "collateral", before="bad", after="good", rationale="correct the selected driver", approved=True)
    assert allowed["status"] == "allowed"
    assert "assign q = good" in repaired


def test_repair_rejects_ambiguous_match_even_when_approved(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r1", "assign q = bad; assign r = bad;\n")
    review, content = propose_repair(record, collateral_root=tmp_path / "collateral", before="bad", after="good", rationale="ambiguous", approved=True)
    assert review["status"] == "review_required"
    assert review["occurrences"] == 2
    assert content is None
