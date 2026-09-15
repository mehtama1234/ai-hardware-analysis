from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.adapter import AdapterSpec, execute_adapter


def test_adapter_contract_uses_common_provenance_runner(tmp_path):
    run = execute_adapter(AdapterSpec("python-check", sys.executable), ["-c", "print('PASS')"], run_root=tmp_path, source_revision="r1")
    assert run.tool == "python-check"
    assert run.status == "passed"
    assert (tmp_path / "provenance-ledger.json").is_file()


def test_adapter_uses_spec_timeout_when_no_override(tmp_path):
    run = execute_adapter(AdapterSpec("python-check", sys.executable, timeout_seconds=5), ["-c", "print('PASS')"], run_root=tmp_path, source_revision="r1")
    assert run.status == "passed"
    assert run.metadata["timeout_seconds"] == 5


def test_adapter_rejects_missing_expected_artifact(tmp_path):
    run = execute_adapter(
        AdapterSpec("missing-output", sys.executable, expected_artifacts=("result.json",)),
        ["-c", "print('PASS')"], run_root=tmp_path, source_revision="r1",
    )
    assert run.status == "blocked"
    assert run.metadata["missing_artifacts"] == ["result.json"]


def test_adapter_records_timeout_as_failure(tmp_path):
    run = execute_adapter(
        AdapterSpec("slow-tool", sys.executable),
        ["-c", "import time; time.sleep(1)"], run_root=tmp_path,
        source_revision="r1", timeout_seconds=0.01,
    )
    assert run.status == "blocked"
    assert run.metadata["timeout_seconds"] == 0.01


def test_adapter_rejects_expected_artifact_path_escape(tmp_path):
    for path in ("../outside.txt", "/tmp/outside.txt"):
        try:
            execute_adapter(AdapterSpec("unsafe", sys.executable, expected_artifacts=(path,)), ["-c", "print('PASS')"], run_root=tmp_path, source_revision="r1")
        except ValueError as error:
            assert "inside the run root" in str(error) or "relative paths" in str(error)
        else:
            raise AssertionError("adapter accepted an escaping artifact path")


def test_adapter_redacts_secret_arguments_in_provenance(tmp_path):
    run = execute_adapter(
        AdapterSpec("secret-check", sys.executable),
        ["-c", "print('PASS')", "--token", "license-secret", "API_KEY=private"],
        run_root=tmp_path, source_revision="r1",
    )
    assert "license-secret" not in run.command
    assert "private" not in run.command
    assert run.command[-2:] == ["[REDACTED]", "API_KEY=[REDACTED]"]
