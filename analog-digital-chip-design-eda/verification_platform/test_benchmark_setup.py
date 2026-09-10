from pathlib import Path
from verification_platform.benchmark_setup import write_planning_artifacts

def test_shared_benchmark_setup_emits_traceable_plans(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text("REQ-ID: count never exceeds the FIFO depth\n")
    result = write_planning_artifacts(spec, tmp_path / "run", source_revision="test-v1")
    assert result == {"requirements": 1, "planned": 1, "unplanned": 0}
    assert (tmp_path / "run" / "specification-ir.json").is_file()
    assert (tmp_path / "run" / "generated_checks.sv").is_file()
