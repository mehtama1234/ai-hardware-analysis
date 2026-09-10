from deployment.collateral_ingest import ingest_artifact
from deployment.collateral_store import CollateralStore
from deployment.planning_service import plan_persisted_ir


def test_plan_persisted_ir_reports_safe_and_unplanned_requirements(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "spec.md", "specification", "v1", "REQ-RST: rst drives reg0 to zero\nREQ-FOO: custom behavior needs review\n")
    ingested = ingest_artifact(record, artifact_root=tmp_path / "collateral", output_root=tmp_path / "ir")
    planned = plan_persisted_ir(ingested["ir_path"], output_root=tmp_path / "ir", project_id="p1", artifact_id=record["id"])
    assert planned["summary"]["planned"] == ["REQ-RST"]
    assert planned["summary"]["unplanned"][0]["requirement_id"] == "REQ-FOO"
