from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.runner import _sandbox_command, run_command


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


def test_runner_terminates_process_group_on_timeout(tmp_path):
    run = run_command([sys.executable, "-c", "import time; time.sleep(10)"], tool="python", run_root=tmp_path, timeout_seconds=0.1)
    assert run.status == "blocked"
    assert "TIMEOUT" in (tmp_path / "stderr.log").read_text()


def test_runner_bounds_noisy_tool_logs(tmp_path):
    from verification_platform.runner import MAX_LOG_BYTES
    run = run_command([sys.executable, "-c", "print('x' * 3000000)"], tool="noisy", run_root=tmp_path)
    assert run.status == "passed"
    assert run.metadata["stdout_truncated"] is True
    assert (tmp_path / "stdout.log").stat().st_size <= MAX_LOG_BYTES + 32


def test_runner_hardens_and_rejects_symlinked_run_root(tmp_path):
    run_root = tmp_path / "private"
    run_command([sys.executable, "-c", "print('PASS')"], tool="python", run_root=run_root)
    assert run_root.stat().st_mode & 0o777 == 0o700
    outside = tmp_path / "outside"
    outside.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(outside, target_is_directory=True)
    import pytest
    with pytest.raises(ValueError, match="symlink"):
        run_command([sys.executable, "-c", "print('PASS')"], tool="python", run_root=linked)


def test_runner_records_posix_resource_limits(tmp_path):
    run = run_command([sys.executable, "-c", "print('PASS')"], tool="python", run_root=tmp_path, timeout_seconds=2.2)
    limits = run.metadata["execution_limits"]
    assert limits["cpu_seconds"] == 3
    assert limits["max_file_bytes"] > 0


def test_runner_blocks_symlinked_workspace_outputs(tmp_path):
    run = run_command([sys.executable, "-c", "import pathlib; pathlib.Path('escape').symlink_to('/tmp')"], tool="unsafe", run_root=tmp_path)
    assert run.status == "blocked"
    assert run.metadata["workspace_violations"] == ["escape"]


def test_runner_blocks_workspace_quota_excess(tmp_path, monkeypatch):
    monkeypatch.setenv("VERIFICATION_JOB_MAX_WORKSPACE_BYTES", "8")
    run = run_command([sys.executable, "-c", "from pathlib import Path; Path('large.bin').write_bytes(b'0123456789')"], tool="quota", run_root=tmp_path)
    assert run.status == "blocked"
    assert any(item.startswith("workspace-quota-exceeded:") for item in run.metadata["workspace_violations"])


def test_isolated_sandbox_wraps_tools_in_private_linux_namespaces(monkeypatch):
    monkeypatch.setenv("VERIFICATION_EXECUTION_SANDBOX", "isolated")
    wrapped, metadata = _sandbox_command(["tool", "--batch"])
    assert wrapped[0].endswith("unshare")
    assert set(("--user", "--pid", "--mount", "--net")).issubset(wrapped)
    assert wrapped[-2:] == ["tool", "--batch"]
    assert metadata["enforced"] is True
    assert metadata["backend"] == "linux-unshare"


def test_unknown_sandbox_mode_fails_closed(monkeypatch):
    monkeypatch.setenv("VERIFICATION_EXECUTION_SANDBOX", "mystery")
    with pytest.raises(ValueError, match="pilot or isolated"):
        _sandbox_command(["tool"])
