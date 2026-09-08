import importlib.util
from pathlib import Path

import torch


MODULE_PATH = Path(__file__).parents[1] / "run_decode_comparison.py"
SPEC = importlib.util.spec_from_file_location("decode_comparison", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

SERVING_SPEC = importlib.util.spec_from_file_location(
    "serving_bridge", Path(__file__).parents[1] / "run_serving_bridge.py"
)
SERVING_MODULE = importlib.util.module_from_spec(SERVING_SPEC)
assert SERVING_SPEC.loader is not None
SERVING_SPEC.loader.exec_module(SERVING_MODULE)


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


def test_serving_search_selects_fastest_output_parity_backend():
    reference = {"output_texts": ["ok"], "accepted": 1}
    result = SERVING_MODULE._serving_candidate_search(
        reference,
        {
            "slow": {"output_texts": ["ok"], "accepted": 1, "latency_ms_median": 8.0},
            "fast": {"output_texts": ["ok"], "accepted": 1, "latency_ms_median": 3.0},
        },
    )
    assert result["selected"] == "fast"


def test_serving_search_rejects_output_divergence():
    reference = {"output_texts": ["ok"], "accepted": 1}
    result = SERVING_MODULE._serving_candidate_search(
        reference,
        {"bad": {"output_texts": ["wrong"], "accepted": 1, "latency_ms_median": 1.0}},
    )
    assert result["selected"] is None
    assert result["candidates"][0]["accepted"] is False
