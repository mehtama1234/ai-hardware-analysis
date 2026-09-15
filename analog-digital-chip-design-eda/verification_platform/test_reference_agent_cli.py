import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reference_agent_cli_emits_proposal(tmp_path: Path):
    failure = tmp_path / "failure.json"
    failure.write_text(json.dumps({"cycle": 1, "signal": "counter_q", "expected": "0", "actual": "1"}), encoding="utf-8")
    output = tmp_path / "proposal.json"
    result = subprocess.run([
        sys.executable, "scripts/run_reference_agent.py", str(failure),
        "--source-revision", "rtl-cli", "--evidence", "triage.json", "waveform.vcd",
        "--output", str(output),
    ], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    proposal = json.loads(output.read_text(encoding="utf-8"))
    assert proposal["status"] == "review_required"
    assert proposal["source_revision"] == "rtl-cli"
    assert proposal["proposal_sha256"]
