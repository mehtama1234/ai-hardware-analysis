#!/usr/bin/env python3
"""Simulate frozen bank reference sequences; nominal component evidence only."""
import argparse
import json
from pathlib import Path
import re
import shutil

import numpy as np
from characterize_switched_reference_dac import circuit, simulate, digest
from check_switched_reference_ranges import check as check_binding


def bank_events(binding, bank, cycles=2):
    one = [e for e in binding['steady_state_bank_transitions'] if e['bank'] == bank]
    assert len(one) == 18
    return [dict(e, cycle=cycle, sequence_index=cycle * 18 + i)
            for cycle in range(cycles) for i, e in enumerate(one)]


def deck_for(events, cap, protocol):
    initial = events[0]['from_code']
    base = circuit(initial, capacitance=cap, resistor=10000, switch_scale=8)
    lines = []
    for line in base.splitlines():
        match = re.match(r'^VB([0-7])(bar)? ', line)
        if not match:
            lines.append(line)
            continue
        bit, invert = int(match[1]), bool(match[2])
        def voltage(code):
            value = (code >> (7 - bit)) & 1
            return 1.8 * (1 - value if invert else value)
        points = [(0, voltage(initial))]
        previous = initial
        for event in events:
            start = protocol['first_edge_s'] + event['sequence_index'] * protocol['dwell_s']
            points.extend([(start, voltage(previous)), (start + protocol['edge_s'], voltage(event['to_code']))])
            previous = event['to_code']
        points.append((protocol['stop_s'], voltage(previous)))
        prefix = ' '.join(line.split()[:3])
        lines.append(prefix + ' PWL(' + ' '.join(f'{t:.15g} {v:.15g}' for t, v in points) + ')')
    lines.extend([f".tran {protocol['maximum_step_s']:.15g} {protocol['stop_s']:.15g} 0 {protocol['maximum_step_s']:.15g}",
                  '.control', 'set numdgt=15', 'set wr_singlescale', 'set wr_vecnames',
                  'run', 'wrdata waveform.txt v(n0)', 'quit', '.endc', '.end'])
    return '\n'.join(lines) + '\n'


def analyze(data, events, curve, protocol):
    times, volts = data[:, 0], data[:, 1]
    assert np.isfinite(data).all() and np.all(np.diff(times) > 0)
    assert abs(volts[0] - curve[events[0]['from_code']]) < 1e-6
    assert times[-1] >= protocol['stop_s'] - 1e-15
    rows = []
    for event in events:
        start = protocol['first_edge_s'] + event['sequence_index'] * protocol['dwell_s']
        end = start + protocol['dwell_s']
        edge = start + protocol['edge_s']
        indices = np.flatnonzero((times >= edge) & (times < end))
        assert len(indices) > 2 and end - times[indices[-1]] <= protocol['maximum_step_s'] * 1.01
        target = curve[event['to_code']]
        tolerance = abs(target) * protocol['tolerance_fraction']
        errors = np.abs(volts[indices] - target)
        bad = np.flatnonzero(errors > tolerance)
        first = int(bad[-1] + 1) if len(bad) else 0
        settled = first < len(indices)
        rows.append(dict(event, target_v=target, tolerance_v=tolerance,
                         settled_before_next_edge=settled,
                         sampled_settling_after_edge_s=float(times[indices[first]] - edge) if settled else None,
                         last_sample_before_next_edge_s=float(times[indices[-1]]),
                         final_error_v=float(volts[indices[-1]] - target), samples=len(indices)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check_binding(args.binding)
    binding = json.loads((args.binding / 'binding.json').read_text())
    dac = json.loads((args.binding / 'dac.json').read_text())
    p = dac['protocol']
    assert p['R_ohms'] == 10000 and p['switch_nfet_w_l_um'] == [32, .15] and p['switch_pfet_w_l_um'] == [64, .15]
    dac_root = Path(binding['sources']['dac.json']['path']).parent
    model_sources = json.loads((dac_root / 'model_sources.json').read_text())
    for path, expected in model_sources.items():
        assert digest(path) == expected
    protocol = dict(cycles=2, banks=8, waves_per_cycle=18, first_edge_s=20e-9,
                    edge_s=100e-12, dwell_s=150e-9, maximum_step_s=50e-12,
                    stop_s=20e-9 + 36 * 150e-9, capacitances_f=[10e-15, 100e-15, 1e-12],
                    resistive_load_ohm=1e12, tolerance_fraction=1/4094,
                    initial_condition='DC operating point at previous vector final code; excludes power-up',
                    timing_scope='Assumed 150 ns between reference commands; excludes array/ADC/readout timing',
                    physical_profile_qualified=False, analog_authorized=False)
    args.output.mkdir(parents=True, exist_ok=False)
    for name in ('binding.json', 'dac.json'):
        shutil.copyfile(args.binding / name, args.output / name)
    shutil.copyfile(dac_root / 'model_sources.json', args.output / 'model_sources.json')
    for name in (Path(__file__).name, 'characterize_switched_reference_dac.py', 'run_active_converter_macro_extracted_transient.py'):
        shutil.copyfile(Path(__file__).with_name(name), args.output / name)
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    curve = {r['code']: r['output_v'] for r in dac['transfers'][0]['rows']}
    cases = []
    for cap in protocol['capacitances_f']:
        for bank in range(8):
            name = f'bank-{bank}-cap-{cap:g}'
            print(name, flush=True)
            events = bank_events(binding, bank)
            directory = args.output / name
            _, meta = simulate(directory, deck_for(events, cap, protocol), timeout=180)
            data = np.loadtxt(directory / 'waveform.txt', skiprows=1)
            rows = analyze(data, events, curve, protocol)
            case = dict(directory=name, bank=bank, capacitance_f=cap, simulation=meta,
                        waveform_samples=len(data), rows=rows)
            (directory / 'measurements.json').write_text(json.dumps(case, indent=2) + '\n')
            cases.append(case)
            print(f"  settled {sum(r['settled_before_next_edge'] for r in rows)}/36", flush=True)
    result = dict(schema_version='reference_bank_sequence.v1', protocol=protocol, cases=cases,
                  binding_source=dict(path=str((args.binding / 'binding.json').resolve()), sha256=digest(args.binding / 'binding.json')),
                  all_sampled_transitions_settled=all(r['settled_before_next_edge'] for c in cases for r in c['rows']),
                  physical_profile_qualified=False, analog_authorized=False,
                  claim_boundary='Nominal TT reference component with ideal resistors/drivers and assumed loads; '
                                 'no array or ADC execution, PVT, mismatch, extracted layout or inference costs')
    (args.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.output / 'manifest.json').write_text(json.dumps({str(p.relative_to(args.output)): digest(p)
        for p in args.output.rglob('*') if p.is_file()}, indent=2) + '\n')
    print('Completed 24 bank/load sequences and 864 transition observations', flush=True)


if __name__ == '__main__':
    main()
