from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_mock_backend_supports_diagnosis_and_bounded_repair() -> None:
    requests = [
        {
            "failure": {"signal": "counter_q", "cycle": 6, "expected": "4", "actual": "5"},
            "allowed_source_revision": "counter-reference-v1",
            "evidence": ["pilot://seeded_counter/baseline"],
        },
        {
            "task": "propose_repair",
            "design_id": "seeded_counter",
            "failure": {"signal": "counter_q", "cycle": 6, "expected": "4", "actual": "5"},
            "allowed_source_revision": "counter-reference-v1",
            "evidence": ["pilot://seeded_counter/baseline"],
            "repair_before": "counter_q <= counter_q + 4'd1;",
            "repair_after": "if (enable) counter_q <= counter_q + 4'd1;",
        },
    ]
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/mock_llm_backend.py")],
        input="\n".join(json.dumps(item) for item in requests) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    outputs = [json.loads(line) for line in completed.stdout.splitlines()]
    assert outputs[0]["kind"] == "diagnosis"
    assert outputs[0]["status"] == "review_required"
    assert outputs[1]["kind"] == "repair"
    assert outputs[1]["status"] == "review_required"
    assert outputs[1]["before"] == requests[1]["repair_before"]
    assert outputs[1]["after"] == requests[1]["repair_after"]
