#!/usr/bin/env python3
"""Check complete reference-DAC characterization against raw logs/waveforms."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import numpy as np


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(root):
    manifest=json.loads((root/'manifest.json').read_text())
    assert {'protocol.json','result.json','model_sources.json','characterize_switched_reference_dac.py',
            'run_active_converter_macro_extracted_transient.py'}<=set(manifest)
    for name,expected in manifest.items():assert digest(root/name)==expected,name
    for name,expected in json.loads((root/'model_sources.json').read_text()).items():assert digest(name)==expected,name
    report=json.loads((root/'result.json').read_text());p=report['protocol']
    assert p==json.loads((root/'protocol.json').read_text())
    assert not p['smoke'] and p['switch_corner']=='SKY130 TT' and p['temperature_c']==27
    assert p['switch_transistors']==32 and p['bits']==8
    assert p['two_R_ohms']==2*p['R_ohms']
    assert len(report['transfers'])==2 and len(report['transients'])==9
    for relative in manifest:
        if relative.endswith('.log'):
            log=(root/relative).read_text()
            assert not re.search(r'(?mi)^\s*(?:error:|error on line|fatal error|doAnalyses:)',log),relative
    for transfer,load in zip(report['transfers'],p['dc_loads_ohm']):
        assert transfer['load_ohm']==load and transfer['simulation']['returncode']==0
        directory=root/f'dc-{load:g}'
        assert digest(directory/'deck.spice')==transfer['simulation']['deck_sha256']
        text=(directory/'stdout.log').read_text()
        blocks=re.findall(r'REF_CODE_(\d+)\s*\n(.*?)(?=REF_CODE_|\Z)',text,re.S)
        assert [int(code) for code,_ in blocks]==list(range(256))
        rows=transfer['rows'];assert [r['code'] for r in rows]==list(range(256))
        for row,(_,block) in zip(rows,blocks):
            for field,name in [('output_v','v(n0)'),('reference_source_current_a','i(vref)'),('vdd_source_current_a','i(vdd)')]:
                value=float(re.search(r'(?mi)^'+re.escape(name)+r'\s*=\s*([-+0-9.eE]+)',block).group(1))
                assert np.isfinite(value) and row[field]==value
            assert row['reference_source_static_power_w']==-p['reference_source_v']*row['reference_source_current_a']
            assert row['normalized_to_code255']==row['output_v']/rows[-1]['output_v']
        assert transfer['code255_output_v']==rows[-1]['output_v']>0
        assert transfer['monotonic']==all(b['output_v']>a['output_v'] for a,b in zip(rows,rows[1:]))
    expected={(a,b,c) for a,b in p['transitions'] for c in p['transient_load_capacitances_f']}
    actual={(t['from_code'],t['to_code'],t['load_capacitance_f']) for t in report['transients']}
    assert expected==actual
    dc={r['code']:r['output_v'] for r in report['transfers'][0]['rows']}
    edge=p['code_transition_s']+p['edge_s']
    for row in report['transients']:
        a,b,c=row['from_code'],row['to_code'],row['load_capacitance_f']
        directory=root/f'tran-{a}-{b}-{c:g}'
        assert digest(directory/'deck.spice')==row['simulation']['deck_sha256']
        assert row['simulation']['returncode']==0
        data=np.loadtxt(directory/'waveform.txt',skiprows=1)
        assert data.shape[1]==2 and len(data)==row['waveform_samples']
        t,v=data[:,0],data[:,1]
        assert np.isfinite(data).all() and np.all(np.diff(t)>0) and t[-1]>=220e-9-1e-15
        assert abs(v[0]-dc[a])<1e-6
        assert row['target_v']==dc[b]
        tolerance=abs(dc[b])*p['settling_fraction_of_target_reference']
        assert abs(row['tolerance_v']-tolerance)<1e-15
        assert row['final_error_v']==v[-1]-dc[b]
        mask=t>=edge
        bad=np.flatnonzero(mask & (np.abs(v-dc[b])>tolerance))
        if row['settled_within_observation']:
            first=bad[-1]+1 if len(bad) else np.flatnonzero(mask)[0]
            assert first<len(t) and abs(row['sampled_settling_after_edge_s']-(t[first]-edge))<1e-15
            assert np.all(np.abs(v[first:]-dc[b])<=tolerance)
        else:
            assert row['sampled_settling_after_edge_s'] is None and len(bad) and bad[-1]==len(t)-1
    assert not report['physical_converter_qualified'] and not report['analog_authorized']
    print(f'Verified {len(manifest)} artifact hashes, 512 DC samples and 9 transient waveforms')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('package',type=Path)
    check(parser.parse_args().package)
