import json,subprocess,sys
from pathlib import Path
def test_register_peripheral_failure_and_repair():
    root=Path(__file__).parent
    assert subprocess.run([sys.executable,str(root/"run_benchmark.py")],capture_output=True).returncode==0
    baseline=json.loads((root/"runs/latest/triage-report.json").read_text())
    assert baseline["status"]=="failed" and baseline["failure"]["signal"]=="control"
    assert baseline["formal_preflight"] in {"passed", "blocked"}
    assert baseline["verilator_lint"] == "passed"
    assert "registerperipheralagent_env" in (root / "runs/latest/uvm-register-peripheral-agent.sv").read_text()
    inventory = json.loads((root / "runs/latest/rtl-collateral.json").read_text())
    assert {module["name"] for module in inventory["modules"]} == {"peripheral", "csr_regs"}
    assert subprocess.run([sys.executable,str(root/"retest_benchmark.py")],capture_output=True).returncode==0
    retest=json.loads((root/"runs/retest/retest-report.json").read_text())
    assert retest["status"]=="passed" and retest["repair"]["original_unchanged"] is True
    assert retest["formal_preflight"] in {"passed", "blocked"}
    assert retest["verilator_lint"] == "passed"
