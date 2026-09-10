import json
from deployment.collateral_ingest import ingest_artifact
from deployment.collateral_store import CollateralStore


def test_ingest_extracts_requirements_and_rtl_entities(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "spec.md", "specification", "v1", "REQ-DATA: data must be stable\nmodule dut(input logic clk, output logic q); endmodule\n")
    result = ingest_artifact(record, artifact_root=tmp_path / "collateral", output_root=tmp_path / "ir")
    assert result["requirements"] == 1
    assert result["modules"] == ["dut"]
    payload = json.loads((tmp_path / "ir" / "p1" / "ir" / f"{record['id']}.json").read_text())
    assert payload["schema_version"] == "verification-ir-v1"
