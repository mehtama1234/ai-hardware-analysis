import json
from pathlib import Path
import subprocess
import sys


def test_coverage_gap_agent_emits_reviewable_next_test(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / "scripts/run_coverage_gap_agent.py"), "--output", str(tmp_path)], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    report = json.loads((tmp_path / "coverage-gap-agent.json").read_text(encoding="utf-8"))
    assert report["status"] == "review_required"
    assert report["next_test"]["proposal"]["status"] == "review_required"
    assert report["next_test"]["proposal"]["source_revision"] == "seeded-counter-v1"
