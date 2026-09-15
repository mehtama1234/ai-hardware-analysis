#!/usr/bin/env python3
"""Check sequence coverage and settling against saved transistor waveforms."""
import argparse
import json
from pathlib import Path
import re

import numpy as np
from characterize_switched_reference_dac import digest
from run_reference_bank_sequences import bank_events, deck_for


def check(root):
    read = lambda path: json.loads(path.read_text())
    manifest = read(root / 'manifest.json')
    for name, expected in manifest.items():
        assert digest(root / name) == expected, name
    for name, expected in read(root / 'model_sources.json').items():
        assert digest(name) == expected, name
    if (root / 'recovery.json').exists():
        recovery = read(root / 'recovery.json')
        assert recovery['circuit_or_measurement_protocol_changed'] is False
        for name, expected in recovery['source_hashes'].items():
            assert digest(Path(recovery['source_path']) / name) == expected
        for name in recovery['reused_cases']:
            for suffix in ('deck.spice', 'waveform.txt', 'measurements.json', 'stdout.log', 'stderr.log'):
                assert digest(root / name / suffix) == recovery['source_hashes'][name + '/' + suffix]
        assert len(set(recovery['reused_cases'] + recovery['resumed_cases'])) == 24
    result = read(root / 'result.json')
    protocol = read(root / 'protocol.json')
    assert result['protocol'] == protocol
    assert protocol['cycles'] == 2 and protocol['banks'] == 8 and protocol['waves_per_cycle'] == 18
    assert protocol['dwell_s'] == 150e-9 and protocol['edge_s'] == 100e-12
    assert protocol['first_edge_s'] == 20e-9 and protocol['maximum_step_s'] == 50e-12
    assert protocol['stop_s'] == 20e-9 + 36 * 150e-9 and protocol['tolerance_fraction'] == 1/4094
    assert protocol['capacitances_f'] == [10e-15, 100e-15, 1e-12]
    source = result['binding_source']
    assert digest(source['path']) == digest(root / 'binding.json') == source['sha256']
    binding = read(root / 'binding.json')
    assert digest(root / 'dac.json') == binding['sources']['dac.json']['sha256']
    curve = {r['code']: r['output_v'] for r in read(root / 'dac.json')['transfers'][0]['rows']}
    cases = result['cases']
    assert len(cases) == 24
    assert {(c['bank'], c['capacitance_f']) for c in cases} == {(b, c) for b in range(8) for c in protocol['capacitances_f']}
    passed = 0
    for case in cases:
        directory = root / case['directory']
        assert case == read(directory / 'measurements.json')
        assert case['simulation']['returncode'] == 0
        assert digest(directory / 'deck.spice') == case['simulation']['deck_sha256']
        for name in ('stdout.log', 'stderr.log'):
            assert not re.search(r'(?mi)^\s*(?:error:|error on line|fatal error|doAnalyses:)', (directory / name).read_text())
        events = bank_events(binding, case['bank'])
        assert (directory / 'deck.spice').read_text() == deck_for(events, case['capacitance_f'], protocol)
        data = np.loadtxt(directory / 'waveform.txt', skiprows=1)
        assert data.shape == (case['waveform_samples'], 2) and np.isfinite(data).all()
        times, volts = data.T
        assert np.all(np.diff(times) > 0) and times[-1] >= protocol['stop_s'] - 1e-15
        assert abs(volts[0] - curve[events[0]['from_code']]) < 1e-6
        assert len(case['rows']) == 36
        for row, event in zip(case['rows'], events):
            for key, value in event.items():
                assert row[key] == value
            start = 20e-9 + event['sequence_index'] * 150e-9
            edge, end = start + 100e-12, start + 150e-9
            indices = np.where((times >= edge) & (times < end))[0]
            assert len(indices) == row['samples'] and len(indices) > 2
            assert end - times[indices[-1]] <= 50e-12 * 1.01
            target = curve[event['to_code']]
            assert row['target_v'] == target and abs(row['tolerance_v'] - abs(target) / 4094) < 1e-18
            errors = np.abs(volts[indices] - target)
            bad = np.where(errors > row['tolerance_v'])[0]
            first = int(bad[-1] + 1) if len(bad) else 0
            settled = first < len(indices)
            assert row['settled_before_next_edge'] == settled
            assert row['last_sample_before_next_edge_s'] == times[indices[-1]]
            assert row['final_error_v'] == volts[indices[-1]] - target
            if settled:
                assert abs(row['sampled_settling_after_edge_s'] - (times[indices[first]] - edge)) < 1e-15
                assert np.all(errors[first:] <= row['tolerance_v'])
            else:
                assert row['sampled_settling_after_edge_s'] is None
            passed += settled
    assert result['all_sampled_transitions_settled'] == (passed == 864)
    for obj in (protocol, result):
        assert obj['analog_authorized'] is False and obj['physical_profile_qualified'] is False
    print(f'Verified 24 waveform sequences, 864 observations, {passed} settled within assumed dwell')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    check(parser.parse_args().package)
