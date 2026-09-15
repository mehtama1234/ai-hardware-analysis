#!/usr/bin/env python3
"""Recover a terminal interrupted sequence run without discarding its evidence."""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from characterize_switched_reference_dac import digest, simulate
from run_reference_bank_sequences import analyze, bank_events, deck_for


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.source
    if (source / 'result.json').exists() or (source / 'manifest.json').exists():
        raise ValueError('Use the complete package checker instead of resuming a completed run')
    for name in ('run_reference_bank_sequences.py', 'characterize_switched_reference_dac.py', 'run_active_converter_macro_extracted_transient.py'):
        assert digest(source / name) == digest(Path(__file__).with_name(name)), 'Source changed: ' + name
    read = lambda p: json.loads(p.read_text())
    protocol, binding, dac = [read(source / n) for n in ('protocol.json', 'binding.json', 'dac.json')]
    for path, expected in read(source / 'model_sources.json').items():
        assert digest(path) == expected
    source_hashes = {str(p.relative_to(source)): digest(p) for p in source.rglob('*') if p.is_file()}
    curve = {r['code']: r['output_v'] for r in dac['transfers'][0]['rows']}
    # Check completed numerical traces before reusing them.
    for path in source.glob('*/measurements.json'):
        case = read(path); events = bank_events(binding, case['bank'])
        assert digest(path.parent / 'deck.spice') == case['simulation']['deck_sha256']
        assert (path.parent / 'deck.spice').read_text() == deck_for(events, case['capacitance_f'], protocol)
        data = np.loadtxt(path.parent / 'waveform.txt', skiprows=1)
        assert analyze(data, events, curve, protocol) == case['rows']
    shutil.copytree(source, args.output)
    shutil.copyfile(__file__, args.output / Path(__file__).name)
    recovery = dict(source_path=str(source.resolve()), source_hashes=source_hashes,
                    reason='Previous process confirmed terminal after 180-second ngspice timeout',
                    per_case_timeout_seconds=600, circuit_or_measurement_protocol_changed=False,
                    reused_cases=[], resumed_cases=[])
    (args.output / 'recovery.json').write_text(json.dumps(recovery, indent=2) + '\n')
    cases = []
    for cap in protocol['capacitances_f']:
        for bank in range(8):
            name = f'bank-{bank}-cap-{cap:g}'; directory = args.output / name
            if (directory / 'measurements.json').exists():
                case = read(directory / 'measurements.json')
                recovery['reused_cases'].append(name)
            else:
                if directory.exists():
                    failed = args.output / 'failed-attempts'; failed.mkdir(exist_ok=True)
                    directory.rename(failed / name)
                print('Running unfinished case ' + name, flush=True)
                events = bank_events(binding, bank)
                _, meta = simulate(directory, deck_for(events, cap, protocol), timeout=600)
                data = np.loadtxt(directory / 'waveform.txt', skiprows=1)
                rows = analyze(data, events, curve, protocol)
                case = dict(directory=name, bank=bank, capacitance_f=cap, simulation=meta,
                            waveform_samples=len(data), rows=rows)
                (directory / 'measurements.json').write_text(json.dumps(case, indent=2) + '\n')
                recovery['resumed_cases'].append(name)
                print(f"  settled {sum(r['settled_before_next_edge'] for r in rows)}/36", flush=True)
            cases.append(case)
            (args.output / 'recovery.json').write_text(json.dumps(recovery, indent=2) + '\n')
    result = dict(schema_version='reference_bank_sequence.v1', protocol=protocol, cases=cases,
                  binding_source=dict(path=str((source / 'binding.json').resolve()), sha256=digest(source / 'binding.json')),
                  all_sampled_transitions_settled=all(r['settled_before_next_edge'] for c in cases for r in c['rows']),
                  physical_profile_qualified=False, analog_authorized=False,
                  claim_boundary='Nominal TT reference component with ideal resistors/drivers and assumed loads; '
                                 'no array or ADC execution, PVT, mismatch, extracted layout or inference costs')
    (args.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.output / 'manifest.json').write_text(json.dumps({str(p.relative_to(args.output)): digest(p)
        for p in args.output.rglob('*') if p.is_file()}, indent=2) + '\n')
    print(f"Completed with {len(recovery['reused_cases'])} reused and {len(recovery['resumed_cases'])} resumed cases", flush=True)


if __name__ == '__main__':
    main()
