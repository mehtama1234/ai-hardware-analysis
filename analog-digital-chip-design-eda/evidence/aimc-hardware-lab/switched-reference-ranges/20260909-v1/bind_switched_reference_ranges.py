#!/usr/bin/env python3
"""Freeze nominal reference-DAC codes for a subsequent numerical quality study."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from check_switched_reference_dac import check as check_dac
from check_calibrated_array_scaling import check as check_scaling
from calibrated_adc_controller_contract import unpack_ranges


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verified_manifest(root):
    for name, expected in json.loads((root / 'manifest.json').read_text()).items():
        assert digest(root / name) == expected, name


def derive(scaling, dac, descriptors, program):
    """Use nearest simulated reference; no model data is refitted here."""
    transfer = dac['transfers'][0]
    assert transfer['load_ohm'] == 1e12 and transfer['monotonic']
    assert not dac['analog_authorized'] and not scaling['analog_authorized']
    candidates = transfer['rows'][1:]  # Zero reference cannot define an ADC scale.
    assert len(candidates) == 255
    assert len(scaling['tiles']) == len(descriptors) == 144
    tiles = []
    for tile, descriptor in zip(scaling['tiles'], descriptors):
        assert all(tile[k] == descriptor[k] for k in ('tile_id', 'row', 'column'))
        bound = tile['adc_bound_model_units']
        assert bound == descriptor['bound_model_units'] and descriptor['adc_bits'] == 12
        target = tile['adc_reference_fraction_of_max_at_fixed_gain']
        selected = min(candidates, key=lambda row: (abs(row['normalized_to_code255'] - target), row['code']))
        actual = selected['normalized_to_code255']
        ratio = actual / target
        tiles.append(dict(tile_id=tile['tile_id'], row=tile['row'], column=tile['column'],
                          reference_code=selected['code'], target_reference_fraction=target,
                          simulated_reference_fraction=actual, simulated_reference_v=selected['output_v'],
                          frozen_bound_model_units=bound, effective_bound_model_units=bound * ratio,
                          relative_bound_error=ratio - 1,
                          reference_source_static_power_w=selected['reference_source_static_power_w']))
    configured = [e for e in program if e['operation'] == 'configure_range']
    assert sorted(e['tile'] for e in configured) == list(range(144))
    assert set(e['bank'] for e in configured) == set(range(8))
    probes = {tuple(pair) for pair in dac['protocol']['transitions']}
    transitions = []
    for bank in range(8):
        events = [e for e in configured if e['bank'] == bank]
        assert len(events) == 18
        # Include the previous vector's last wave; startup remains unspecified.
        for previous, current in zip(events[-1:] + events[:-1], events):
            a, b = (tiles[e['tile']]['reference_code'] for e in (previous, current))
            transitions.append(dict(bank=bank, from_tile=previous['tile'], to_tile=current['tile'],
                                    from_code=a, to_code=b, binding_epoch=current['binding_epoch'],
                                    between_vectors=current is events[0],
                                    included_in_three_transition_probe=(a, b) in probes))
    pairs = sorted({(e['from_code'], e['to_code']) for e in transitions})
    return dict(schema_version='nominal_reference_range_binding.v1', tiles=tiles,
                steady_state_bank_transitions=transitions,
                unique_code_transitions=[list(p) for p in pairs],
                uncharacterized_code_transitions=[list(p) for p in pairs if p not in probes],
                maximum_absolute_relative_bound_error=max(abs(t['relative_bound_error']) for t in tiles),
                digital_dequantization='Must use effective_bound_model_units, including changed clipping thresholds',
                code_encoding='One unsigned byte per canonical tile; review data, not a firmware register protocol',
                reference_basis='Nominal 1e12-ohm DC curve normalized to its own code 255 output',
                startup_reference_state=None, actual_adc_load=None, total_energy_per_vector_j=None,
                model_quality_revalidated=False, physical_profile_qualified=False, analog_authorized=False,
                claim_boundary='SKY130 TT schematic reference component only; excludes array, ADC errors, '
                               'real loading, PVT, mismatch, layout and model quality revalidation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('scaling', 'dac', 'controller', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    check_dac(args.dac)
    check_scaling(args.scaling)
    verified_manifest(args.controller)
    sources = {'scaling.json': args.scaling / 'normalized_array_scaling.json',
               'dac.json': args.dac / 'result.json',
               'range_descriptors.bin': args.controller / 'range_descriptors.bin',
               'controller_program.json': args.controller / 'controller_review_program.json'}
    read = lambda path: json.loads(path.read_text())
    result = derive(read(sources['scaling.json']), read(sources['dac.json']),
                    unpack_ranges(sources['range_descriptors.bin'].read_bytes()), read(sources['controller_program.json']))
    args.output.mkdir(parents=True, exist_ok=False)
    for name, path in sources.items():
        shutil.copyfile(path, args.output / name)
    result['sources'] = {name: {'path': str(path.resolve()), 'sha256': digest(path)} for name, path in sources.items()}
    (args.output / 'binding.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.output / 'reference_codes.bin').write_bytes(bytes(t['reference_code'] for t in result['tiles']))
    shutil.copyfile(__file__, args.output / Path(__file__).name)
    manifest = {p.name: digest(p) for p in sorted(args.output.iterdir())}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('maximum_absolute_relative_bound_error', 'model_quality_revalidated')}))
    print(f"Frozen 144 codes and {len(result['unique_code_transitions'])} distinct bank transitions")


if __name__ == '__main__':
    main()
