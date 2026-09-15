#!/usr/bin/env python3
"""Verify exact model codes, normalized scales and analytic rounding bounds."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from safetensors import safe_open


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def check(root):
    manifest=json.loads((root/'manifest.json').read_text())
    assert {'normalized_array_scaling.json','signed_weight_codes.npz','derive_calibrated_array_scaling.py',
            'tiled_projection_model.py','check_gpt2_adc_holdout.py'}<=set(manifest)
    for name,expected in manifest.items():assert digest(root/name)==expected,name
    report=json.loads((root/'normalized_array_scaling.json').read_text())
    for source in report['sources'].values():assert digest(source['path'])==source['sha256']
    plan=json.loads(Path(report['sources']['plan']['path']).read_text())
    contract=plan['selected_contract'];profile=contract['profile']
    with safe_open(report['sources']['weights']['path'],framework='numpy') as f:
        weights=f.get_tensor(report['checkpoint_tensor'])
    with np.load(root/'signed_weight_codes.npz',allow_pickle=False) as archive:codes=archive['codes']
    assert codes.dtype==np.int8 and list(codes.shape)==contract['weight_shape_input_output']
    assert len(report['tiles'])==len(contract['adc_range']['ranges'])==144
    assert report['signed_weight_codes']['specified_signed_levels']==255
    assert report['signed_weight_codes']['specified_levels_per_differential_branch']==128
    dac=report['dac_codes'];m=(1<<(profile['dac_bits']-1))-1
    step_x=np.float32(np.float32(contract['calibrated_activation_abs_max'])/np.float32(m))
    all_codes=np.arange(-m,m+1,dtype=np.int32)
    dx=float(np.abs((all_codes.astype(np.float32)*step_x).astype(np.float64)-all_codes*float(step_x)).max())
    span=m*float(step_x)
    assert dac['model_step']==float(step_x) and dac['equivalent_span_model_units']==span
    assert dac['maximum_float32_code_rounding_error']==dx
    gains=[];bounds=[]
    for index,(row,frozen) in enumerate(zip(report['tiles'],contract['adc_range']['ranges'])):
        r,c=frozen['row'],frozen['column']
        assert (row['tile_id'],row['row'],row['column'])==(index,r,c)
        assert row['adc_bound_model_units']==frozen['selected_bound']
        w=weights[r:r+128,c:c+128];q=codes[r:r+128,c:c+128]
        step=np.float32(np.max(np.abs(w))/np.float32(127))
        expected=np.clip(np.rint(w/step),-127,127).astype(np.int8)
        assert np.array_equal(q,expected)
        assert hashlib.sha256(q.tobytes()).hexdigest()==row['codes_sha256']
        assert row['weight_step_model_units']==float(step)
        gain=span*127*float(step)/frozen['selected_bound'];gains.append(gain)
        assert math.isclose(row['normalized_transimpedance_gain'],gain,rel_tol=1e-12)
        qw=(q.astype(np.float32)*step).astype(np.float64)
        dw=np.abs(qw-q.astype(np.float64)*float(step))
        bound=float((span*dw.sum(axis=0)+dx*np.abs(qw).sum(axis=0)).max());bounds.append(bound)
        measured=report['rounding_check']['rows'][index]
        assert measured['tile_id']==index and measured['tested_vectors']==4
        assert math.isclose(measured['all_input_code_vectors_partial_error_bound'],bound,rel_tol=1e-12)
        assert measured['maximum_partial_abs_error']<=bound+1e-12
    for gain,row in zip(gains,report['tiles']):
        assert math.isclose(row['gain_relative_to_minimum'],gain/min(gains),rel_tol=1e-12)
        assert math.isclose(row['adc_reference_fraction_of_max_at_fixed_gain'],min(gains)/gain,rel_tol=1e-12)
    assert math.isclose(report['normalized_gain']['span_ratio'],max(gains)/min(gains),rel_tol=1e-12)
    assert report['rounding_check']['maximum_all_input_code_vectors_bound']==max(bounds)<1e-5
    assert report['rounding_check']['tile_vector_cases']==576
    assert all(value is None for value in report['unassigned_physical_values'].values())
    assert not report['analog_authorized'] and not report['physical_io_performed']
    print(f"Verified {len(manifest)} artifact hashes, all 2,359,296 weight codes, 144 gain ratios and all-input-code rounding bounds")


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package',type=Path)
    check(parser.parse_args().package)
