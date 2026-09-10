import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_real_model_comparison import validate


def report():
    # Synthetic validator fixture, never published as measurement evidence.
    return {
        "schema_version": "real-model-sdpa-backend-v0.2",
        "evidence_kind": "measured_gpu", "gpu_execution_accepted": True,
        "source_hashes": {"runner.py": "a" * 64}, "command": ["python", "runner.py"],
        "runtime": {"torch": "test"}, "model_profile": {"model_revision": "test"},
        "attention_backends": {"eager": "eager", "sdpa": "sdpa"},
        "protocol": {"repeats": 3},
        "result": {"output_parity": True, "batch_vs_individual_output_parity": True,
                   "generated_token_ids": {"eager": [[4]], "sdpa": [[4]]},
                   "eager_wall_time_ms_samples": [10, 11, 12],
                   "sdpa_wall_time_ms_samples": [8, 9, 10],
                   "eager_wall_time_ms_median": 11, "sdpa_wall_time_ms_median": 9,
                   "sdpa_over_eager_latency_ratio": 9 / 11},
    }


def test_accepts_consistent_report():
    assert validate(report()) == []


def test_rejects_false_success_despite_top_level_acceptance():
    for key in ("output_parity", "batch_vs_individual_output_parity"):
        damaged = report()
        damaged["result"][key] = False
        assert validate(damaged)


def test_rejects_ambiguous_backends_and_fabricated_summary():
    original = report()
    mutations = [
        ("attention_backends", {"eager": "sdpa", "sdpa": "sdpa"}),
        ("schema_version", "real-model-sdpa-backend-v0.1"),
    ]
    for key, value in mutations:
        damaged = copy.deepcopy(original)
        damaged[key] = value
        assert validate(damaged)
    for key, value in (("sdpa_wall_time_ms_median", 1),
                       ("sdpa_over_eager_latency_ratio", 0.01),
                       ("sdpa_wall_time_ms_samples", [float("nan")] * 3),
                       ("generated_token_ids", {"eager": [[4]], "sdpa": [[5]]})):
        damaged = copy.deepcopy(original)
        damaged["result"][key] = value
        assert validate(damaged)
