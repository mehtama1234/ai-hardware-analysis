from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.adapter import AdapterSpec, execute_adapter


def test_adapter_contract_uses_common_provenance_runner(tmp_path):
    run = execute_adapter(AdapterSpec("python-check", sys.executable), ["-c", "print('PASS')"], run_root=tmp_path, source_revision="r1")
    assert run.tool == "python-check"
    assert run.status == "passed"
    assert (tmp_path / "provenance-ledger.json").is_file()
