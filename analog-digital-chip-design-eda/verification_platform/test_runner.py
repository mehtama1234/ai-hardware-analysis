from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.runner import run_command


def test_runner_records_success_and_artifacts(tmp_path):
    run = run_command([sys.executable, "-c", "print('PASS')"], tool="python", run_root=tmp_path, source_revision="r1")
    assert run.status == "passed"
    assert run.exit_code == 0
    assert {ref.path for ref in run.artifacts} == {"stdout.log", "stderr.log"}
    assert (tmp_path / "provenance-ledger.json").is_file()
    second = run_command([sys.executable, "-c", "print('PASS')"], tool="python", run_root=tmp_path / "other", source_revision="r1")
    assert run.id == second.id


def test_runner_records_failure_without_throwing(tmp_path):
    run = run_command([sys.executable, "-c", "raise SystemExit(3)"], tool="python", run_root=tmp_path)
    assert run.status == "failed"
    assert run.exit_code == 3


def test_runner_records_missing_tool_as_blocked(tmp_path):
    run = run_command(["definitely-not-installed"], tool="missing", run_root=tmp_path)
    assert run.status == "blocked"
    assert run.exit_code is None


def test_runner_blocks_when_expected_artifact_is_missing(tmp_path):
    run = run_command([sys.executable, "-c", "print('PASS')"], tool="python", run_root=tmp_path, expected_artifacts=["required.vcd"])
    assert run.status == "blocked"
    assert run.metadata["missing_artifacts"] == ["required.vcd"]
