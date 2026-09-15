from pathlib import Path
import sys

from verification_platform.orchestration import run_four_workstream_pipeline


def test_pipeline_records_agent_team_with_collateral_binding(monkeypatch, tmp_path: Path):
    spec = tmp_path / "spec.md"
    spec.write_text("REQ-TEAM: output follows request\n", encoding="utf-8")
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut(input wire clk, output reg q); always @(posedge clk) q <= 1'b0; endmodule\n", encoding="utf-8")
    protocol = tmp_path / "protocol.json"
    protocol.write_text('{"schema_version":"protocol-plan-v1","name":"p","addr_width":8,"data_width":32,"steps":[{"operation":"read","address":0,"expected":0}]}\n', encoding="utf-8")
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    evidence = ["external/evidence.json"]
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="team-pipeline-v1",
        collateral_entries=[{"kind": "specification", "path": spec.name}], collateral_root=tmp_path,
        agent_team_backend="local", agent_team_requests=[
            {"role": "diagnostician", "task": "diagnose_failure", "allowed_source_revision": "team-pipeline-v1", "evidence": evidence, "failure": {"signal": "q", "cycle": 1, "expected": "0", "actual": "1"}},
        ],
    )
    assert result["status"] == "passed"
    assert result["agent_team"]["status"] == "available"
    assert result["agent_team"]["results"][0]["grounded"] is True
    assert Path(result["agent_team"]["path"]).is_file()
