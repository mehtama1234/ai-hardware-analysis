from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def test_sequential_rsi_result_is_safe_and_budgeted() -> None:
    result = json.loads((ROOT / "sequential-rsi-rl-benchmark.json").read_text())

    assert result["status"] == "passed"
    assert result["split"]["heldout_cases"] == 36
    for method in result["methods"].values():
        assert method["safe_cases"] == method["cases"]
    assert result["methods"]["sequential_rsi"]["analog_cases"] == 6
    assert result["methods"]["sequential_rsi_early_stop"]["candidate_evaluations"] < result["methods"]["sequential_rsi"]["candidate_evaluations"]
    assert result["recursive_adaptation"]["second_pass"]["safe_cases"] == 36
    assert "not deep RL" in result["claim_boundary"]
