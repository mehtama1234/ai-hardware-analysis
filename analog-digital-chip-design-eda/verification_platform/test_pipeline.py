from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.pipeline import run_pipeline


def test_pipeline_persists_plan_and_execution(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text("REQ-A: output resets to zero\n", encoding="utf-8")
    result = run_pipeline(spec, [sys.executable, "-c", "print('ok')"], tool="python", run_root=tmp_path / "run", source_revision="r1")
    assert result["tool_run"].status == "passed"
    assert len(result["plans"]) == 1
    assert (tmp_path / "run/verification-plan.json").is_file()
    assert (tmp_path / "run/generated_checks.sv").is_file()
    assert {item.path for item in result["tool_run"].artifacts} >= {"specification-ir.json", "verification-plan.json", "generated_checks.sv"}
