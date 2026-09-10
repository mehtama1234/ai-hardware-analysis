import json
from pathlib import Path
import subprocess
import sys


def test_seeded_failure_is_localized():
    root = Path(__file__).parent
    result = subprocess.run([sys.executable, str(root / "run_benchmark.py")], capture_output=True, text=True, check=False)
    assert result.returncode == 0  # expected benchmark failure is a successful triage
    report = json.loads((root / "runs/latest/triage-report.json").read_text(encoding="utf-8"))
    assert report["status"] == "failed"
    assert (root / "runs/latest/procedural_checks.sv").is_file()
    assert "counteragent_env" in (root / "runs/latest/uvm-counter-agent.sv").read_text(encoding="utf-8")
    rtl_inventory = json.loads((root / "runs/latest/rtl-collateral.json").read_text(encoding="utf-8"))
    assert rtl_inventory["modules"][0]["ports"][2]["name"] == "enable"
    retrieval = json.loads((root / "runs/latest/retrieval-index.json").read_text(encoding="utf-8"))
    assert retrieval["schema_version"] == "retrieval-index-v1"
    verification_ir = json.loads((root / "runs/latest/verification-ir.json").read_text(encoding="utf-8"))
    assert {run["tool"] for run in verification_ir["tool_runs"]} >= {"iverilog-baseline", "vvp-baseline"}
    specification_ir = json.loads((root / "runs/latest/specification-ir.json").read_text(encoding="utf-8"))
    assert {check["requirement_id"] for check in specification_ir["checks"]} == {"REQ-COUNTER-ENABLE", "REQ-COUNTER-HOLD"}
    assert (root / "runs/latest/compile.stderr.log").read_text(encoding="utf-8") == ""
    assert report["first_divergence"] == {"actual": "1", "cycle": 1, "expected": "0", "signal": "counter_q"}
    assert report["root_cause"]["marker"] == "SEEDED_BUG"
    assert "dependency_cone" in report["root_cause"]
    assert "enable" not in report["root_cause"]["dependency_cone"]
    assert report["waveform_confirmation"] is True
    assert report["vacuity"]["status"] == "vacuous"
    pov = json.loads((root / "runs/latest/proof-of-value-report.json").read_text(encoding="utf-8"))
    assert pov["mixed_signal"]["claims"][1]["status"] == "unsupported"
    assert pov["requirements"]["unplanned"] == 1
    planning = json.loads((root / "runs/latest/planning-summary.json").read_text(encoding="utf-8"))
    assert planning["unplanned"][0]["requirement_id"] == "REQ-COUNTER-RESET"
    assert pov["requirements"]["planning_queue"][0]["requirement_id"] == "REQ-COUNTER-RESET"
    capabilities = json.loads((root / "runs/latest/tool-capabilities.json").read_text(encoding="utf-8"))
    assert {item["tool"] for item in capabilities} >= {"iverilog", "verilator", "yosys", "sby"}
    ir = json.loads((root / "runs/latest/verification-ir.json").read_text(encoding="utf-8"))
    assert {ref["path"] for ref in ir["requirements"][0]["evidence"]} >= {"spec.md", "counter.sv", "tb.sv", "runs/latest/generated_checks.sv", "runs/latest/procedural_checks.sv"}
    assert Path(root / "runs/latest/waveform.vcd").is_file()
