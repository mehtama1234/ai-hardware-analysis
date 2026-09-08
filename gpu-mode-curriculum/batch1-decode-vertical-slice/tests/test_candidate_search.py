import importlib.util
from pathlib import Path

import torch


MODULE_PATH = Path(__file__).parents[1] / "run_decode_comparison.py"
SPEC = importlib.util.spec_from_file_location("decode_comparison", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _result(tokens, value, timing):
    logits = [torch.tensor([[value, 1.0]])]
    return {
        "tokens": tokens,
        "logits": logits,
        "wall_ms_median": timing,
        "cuda_event_ms_median": None,
    }


def test_search_selects_fastest_parity_preserving_candidate():
    reference = _result([1], 2.0, 10.0)
    result = MODULE._candidate_search(
        reference,
        {"slow": _result([1], 2.0, 8.0), "fast": _result([1], 2.0, 4.0)},
    )
    assert result["selected"] == "fast"
    assert all(row["accepted"] for row in result["candidates"])


def test_search_rejects_fast_candidate_with_logit_mismatch():
    reference = _result([1], 2.0, 10.0)
    result = MODULE._candidate_search(
        reference,
        {"bad-fast": _result([1], 9.0, 1.0), "safe": _result([1], 2.0, 5.0)},
    )
    assert result["selected"] == "safe"
    assert not result["candidates"][0]["accepted"]
