import json

from deployment.generation_service import generate_persisted_plan


def test_generate_persisted_plan_emits_hashed_review_and_execution_artifacts(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps([{
        "id": "CHECK-REQ-RST",
        "requirement_id": "REQ-RST",
        "kind": "sva",
        "assertion": "assert property (@(posedge clk) rst |-> reg0 == '0);",
        "rationale": "reset requirement",
    }]), encoding="utf-8")
    result = generate_persisted_plan(plan, output_root=tmp_path / "out", project_id="p1", artifact_id="a1")
    assert result["execution_candidate"] == "procedural"
    assert result["files"]["procedural"]["status"] == "execution_candidate"
    assert result["files"]["sva"]["status"] == "review_only"
    assert result["files"]["uvm"]["sha256"]
    manifest = json.loads((tmp_path / "out/p1/generated/a1/generation-manifest.json").read_text())
    assert manifest["plan_sha256"] == result["plan_sha256"]
