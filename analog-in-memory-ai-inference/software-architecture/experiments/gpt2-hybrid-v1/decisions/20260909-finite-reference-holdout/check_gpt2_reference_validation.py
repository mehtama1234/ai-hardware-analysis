#!/usr/bin/env python3
"""Check validation-only circuit-reference evaluation and unchanged ADC scales."""
import argparse
import json
import math
from pathlib import Path

from run_gpt2_hybrid_evaluation import digest
from projection_numerical_control import CONTRACT


def check(root):
    read = lambda name: json.loads((root / name).read_text())
    for name, expected in read('manifest.json').items():
        assert digest(root / name) == expected, name
    for source in read('inputs.json').values():
        for name, expected in source['manifest'].items():
            assert digest(Path(source['path']) / name) == expected
    protocol, result, plan, binding = [read(n) for n in ('protocol.json', 'result.json', 'training_plan.json', 'binding.json')]
    validation = read('validation_source.json')
    assert validation['evaluation_split'] == 'validation'
    if protocol['schema_version'] == 'circuit_reference_disjoint_holdout.v1':
        from freeze_reference_holdout import check_plan
        frozen = check_plan(root / 'frozen_test_plan')
        assert protocol['evaluation_split'] == result['evaluation_split'] == 'test'
        assert protocol['test_plan_sha256'] == digest(root / 'frozen_test_plan/plan.json')
        assert protocol['windows'] == frozen['windows']
        assert result['variants']['finite_reference_adc12']['contract'] == frozen['selected_contract']
        assert result['sampled_holdout_screen_pass'] == result['variants']['finite_reference_adc12']['screen_pass']
        expected_contexts = 32
    else:
        assert protocol['schema_version'] == 'circuit_reference_validation.v1'
        assert protocol['evaluation_split'] == result['evaluation_split'] == 'validation'
        assert protocol['windows'] == validation['validation']['windows']
        expected_contexts = 16
    assert result['schema_version'] == protocol['schema_version']
    assert protocol['screen'] == plan['screen'] and protocol['numerical_control'] == CONTRACT
    assert protocol['binding_sha256'] == digest(root / 'binding.json')
    rows = [json.loads(line) for line in (root / 'rows.jsonl').read_text().splitlines()]
    names = ['ideal', 'frozen_adc12', 'finite_reference_adc12']
    n = len(protocol['windows'])
    assert n == expected_contexts and len(rows) == n * 3
    assert [(r['window'], r['variant']) for r in rows] == [(i, name) for i in range(n) for name in names]
    assert result['fallback_controls'] == [dict(window=i, exact=True) for i in range(n)]
    for index, window in enumerate(protocol['windows']):
        group = rows[index*3:index*3+3]
        assert len({r['baseline_nll_sum'] for r in group}) == 1
        for row in group:
            assert row['start'] == window['start'] and row['tokens'] == len(window['ids']) - 1 == 128
            assert 0 <= row['argmax_matches'] <= row['tokens']
            assert all(math.isfinite(row[k]) for k in ('baseline_nll_sum', 'candidate_nll_sum'))
        assert group[0]['numerical_control']['pass'] is True
        control = group[0]['numerical_control']
        assert control['finite'] and control['projection_close'] and control['identical_argmax']
        assert control['maximum_log_probability_error'] < CONTRACT['maximum_log_probability_error']
        assert abs(control['mean_target_nll_change']) < CONTRACT['maximum_absolute_mean_target_nll_change']
    for name in names:
        summary = result['variants'][name]
        subset = [r for r in rows if r['variant'] == name]
        count = sum(r['tokens'] for r in subset)
        delta = sum(r['candidate_nll_sum'] - r['baseline_nll_sum'] for r in subset) / count
        agreement = sum(r['argmax_matches'] for r in subset) / count
        assert summary['tokens'] == count and summary['nll_increase'] == delta and summary['argmax_agreement'] == agreement
        assert summary['screen_pass'] == (delta <= plan['screen']['maximum_nll_increase_nats'] and agreement >= plan['screen']['minimum_argmax_agreement'])
        assert len(summary['trace']) == n and all(t['vectors'] == 129 for t in summary['trace'])
    assert result['variants']['frozen_adc12']['contract'] == plan['selected_contract']
    finite = result['variants']['finite_reference_adc12']['contract']
    assert finite['profile'] == plan['selected_contract']['profile']
    assert finite['adc_range']['original_training_contract'] == plan['selected_contract']
    assert finite['adc_range']['reference_binding'] == binding
    assert len(finite['adc_range']['ranges']) == 144
    for actual, selected in zip(finite['adc_range']['ranges'], binding['tiles']):
        assert (actual['row'], actual['column']) == (selected['row'], selected['column'])
        assert actual['selected_bound'] == selected['effective_bound_model_units']
    assert result['ideal_control_pass'] is True
    for key in ('analog_authorized', 'physical_profile_qualified', 'test_quality_established'):
        assert result[key] is False
    print(f'Verified {len(rows)} rows, {n} {protocol["evaluation_split"]} contexts, digital fallback and all 144 effective ADC scales')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    check(parser.parse_args().package)
