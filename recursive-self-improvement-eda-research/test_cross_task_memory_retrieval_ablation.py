from __future__ import annotations

import json

from run_cross_task_memory_retrieval_ablation import (
    SOURCE_MEMORY,
    SOURCE_POPULATION,
    TARGET_SWEEP,
    OUT,
    choose_local_bits,
    choose_source_action,
    map_bits,
    run,
)


def test_nearest_bit_mapping_ties_choose_lower_precision():
    assert map_bits(11, [6, 8, 10, 12]) == 10


def test_failure_aware_retrieval_uses_observed_failure_rate():
    memory = [
        {"action": {"bits": 10, "gain_factor": 1.0, "placement": ["k"]},
         "attempts": 10, "safe": 8, "failures": 2, "safe_rate": 0.8, "mean_reward": 100.0},
        {"action": {"bits": 12, "gain_factor": 1.0, "placement": ["k"]},
         "attempts": 2, "safe": 2, "failures": 0, "safe_rate": 1.0, "mean_reward": 50.0},
    ]
    assert choose_source_action(memory, "failure_aware")["action"]["bits"] == 12
    assert choose_source_action(memory, "mean_return_only")["action"]["bits"] == 10


def test_local_policy_only_uses_training_noise_rows():
    rows = [
        {"adc_bits": bits, "dac_bits": bits, "noise_stddev": noise,
         "passes_declared_numeric_budget": passes}
        for bits, passes_by_noise in ((8, {0.0: False, 0.01: False}),
                                      (10, {0.0: True, 0.01: False}))
        for noise, passes in passes_by_noise.items()
    ]
    assert choose_local_bits(rows, [0.0]) == 10
    assert choose_local_bits(rows, [0.01]) is None


def test_real_cross_task_ablation_is_fail_closed_and_retrieval_changes_coverage():
    source = json.loads(SOURCE_MEMORY.read_text())
    target = json.loads(TARGET_SWEEP.read_text())
    population = json.loads(SOURCE_POPULATION.read_text())
    result = run(source, target, population)
    assert result == json.loads(OUT.read_text())
    assert run(source, target, population) == result
    assert result["summary"]["all_gated_methods_safe"]
    assert result["summary"]["failure_aware_analog_cases"] == 2
    assert result["summary"]["local_baseline_analog_cases"] == 0
    assert result["summary"]["shuffled_memory_analog_cases"] == 0
    assert result["summary"]["cross_task_coverage_gain"] == 2
    assert result["summary"]["ungated_unsafe_analog_cases"] == 2
    assert result["promotion"]["status"] == "not_eligible"


def test_leave_seed_out_memory_ablation_reports_failure_feature_effect_without_leakage():
    source = json.loads(SOURCE_MEMORY.read_text())
    population = json.loads(SOURCE_POPULATION.read_text())
    result = run(source, json.loads(TARGET_SWEEP.read_text()), population)
    ablation = result["source_seed_holdout_ablation"]
    failure = ablation["methods"]["failure_aware"]
    quality = ablation["methods"]["conditional_quality_only"]

    assert ablation["split"].startswith("leave-one-seed-out")
    assert failure["heldout_cases"] == quality["heldout_cases"] == 36
    assert failure["folds"] == quality["folds"] == 6
    assert all(fold["training_case_count"] == 30 and fold["heldout_case_count"] == 6
               for method in (failure, quality) for fold in method["fold_details"])
    assert ablation["failure_aware_vs_conditional_quality_heldout_reliable_case_delta"] == 1
