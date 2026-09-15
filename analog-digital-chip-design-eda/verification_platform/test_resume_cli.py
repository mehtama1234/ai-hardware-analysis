from pathlib import Path
import subprocess
import sys

from verification_platform.workflow import advance_checkpoint, create_checkpoint, write_checkpoint


def test_resume_cli_reports_next_stage(tmp_path: Path):
    artifact = tmp_path / "plan.json"
    artifact.write_text("{}\n", encoding="utf-8")
    checkpoint = advance_checkpoint(create_checkpoint("run-1", "v1"), "planning", artifact_root=tmp_path, artifact_paths=[artifact])
    path = write_checkpoint(checkpoint, tmp_path / "checkpoint.json")
    result = subprocess.run([sys.executable, "scripts/resume_four_workstream_pipeline.py", "--checkpoint", str(path), "--artifact-root", str(tmp_path)], capture_output=True, text=True, check=True)
    assert '"next_stage": "scheduling"' in result.stdout
