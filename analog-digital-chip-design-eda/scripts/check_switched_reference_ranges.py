#!/usr/bin/env python3
"""Verify reference-code binding, effective ADC scale and bank transitions."""
import argparse
import json
import math
from pathlib import Path

from bind_switched_reference_ranges import digest, verified_manifest
from calibrated_adc_controller_contract import unpack_ranges, replay


def check(root):
    verified_manifest(root)
    read = lambda name: json.loads((root / name).read_text())
    result = read('binding.json')
    for name, source in result['sources'].items():
        assert digest(root / name) == digest(source['path']) == source['sha256']
    scaling, dac, program = read('scaling.json'), read('dac.json'), read('controller_program.json')
    descriptors = unpack_ranges((root / 'range_descriptors.bin').read_bytes())
    replay(program, descriptors)
    curve = dac['transfers'][0]['rows']
    assert len(curve) == 256 and all(b['output_v'] > a['output_v'] for a, b in zip(curve, curve[1:]))
    assert len(result['tiles']) == 144
    for row, tile, descriptor in zip(result['tiles'], scaling['tiles'], descriptors):
        for k in ('tile_id', 'row', 'column'):
            assert row[k] == tile[k] == descriptor[k]
        target = tile['adc_reference_fraction_of_max_at_fixed_gain']
        code = row['reference_code']
        assert code == min(range(1, 256), key=lambda c: (abs(curve[c]['output_v'] / curve[255]['output_v'] - target), c))
        actual = curve[code]['output_v'] / curve[255]['output_v']
        bound = descriptor['bound_model_units']
        assert row['frozen_bound_model_units'] == bound == tile['adc_bound_model_units']
        assert row['target_reference_fraction'] == target
        assert row['simulated_reference_fraction'] == actual
        assert row['simulated_reference_v'] == curve[code]['output_v']
        # At the same physical gain, bound / reference must be invariant.
        assert math.isclose(row['effective_bound_model_units'] / actual, bound / target, rel_tol=1e-14)
        assert row['relative_bound_error'] == actual / target - 1
        assert row['reference_source_static_power_w'] == curve[code]['reference_source_static_power_w']
    assert (root / 'reference_codes.bin').read_bytes() == bytes(t['reference_code'] for t in result['tiles'])
    probes = {tuple(p) for p in dac['protocol']['transitions']}
    expected = []
    for bank in range(8):
        events = [e for e in program if e['operation'] == 'configure_range' and e['bank'] == bank]
        assert len(events) == 18
        for i, event in enumerate(events):
            before = events[i - 1]
            a, b = [result['tiles'][e['tile']]['reference_code'] for e in (before, event)]
            expected.append(dict(bank=bank, from_tile=before['tile'], to_tile=event['tile'],
                                 from_code=a, to_code=b, binding_epoch=event['binding_epoch'],
                                 between_vectors=i == 0, included_in_three_transition_probe=(a, b) in probes))
    assert result['steady_state_bank_transitions'] == expected
    pairs = sorted({(e['from_code'], e['to_code']) for e in expected})
    assert result['unique_code_transitions'] == [list(p) for p in pairs]
    assert result['uncharacterized_code_transitions'] == [list(p) for p in pairs if p not in probes]
    assert result['maximum_absolute_relative_bound_error'] == max(abs(t['relative_bound_error']) for t in result['tiles'])
    for k in ('model_quality_revalidated', 'physical_profile_qualified', 'analog_authorized'):
        assert result[k] is False
    for k in ('startup_reference_state', 'actual_adc_load', 'total_energy_per_vector_j'):
        assert result[k] is None
    print('Verified 144 reference codes, effective scales, and cyclic bank transitions; no physical authorization')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    check(parser.parse_args().package)
