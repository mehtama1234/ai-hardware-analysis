#!/usr/bin/env python3
"""Schematic-only experiment: switch input acquisition off before regeneration."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from run_active_converter_macro_extracted_transient import deck,measure


def schematic(source):
    lines=source.splitlines()
    changed=[]
    for i,line in enumerate(lines):
        if line.startswith('+ iso_tail_ext tail_ext vdd_ext preamp_iso_tail_ext'):
            lines[i]=line+' sample_clock regen_bar'
        fields=line.split()
        if not fields:continue
        if fields[0] in ('X4','X6'):
            assert 'tail_ext' in fields[1:4]
            fields[1:4]=['sample_tail' if n=='tail_ext' else n for n in fields[1:4]]
            lines[i]=' '.join(fields);changed.append(fields[0])
        if fields[0] in ('X1','X7'):
            assert 'vdd_ext' in (fields[1],fields[3])
            fields[1]='regen_vdd' if fields[1]=='vdd_ext' else fields[1]
            fields[3]='regen_vdd' if fields[3]=='vdd_ext' else fields[3]
            lines[i]=' '.join(fields);changed.append(fields[0])
    assert sorted(changed)==['X1','X4','X6','X7']
    extra='''Xsample_tail sample_tail sample_clock vss_escape vss_escape sky130_fd_pr__nfet_01v8 w=6 l=0.6
Xregen_header regen_vdd regen_bar vdd_ext vdd_ext sky130_fd_pr__pfet_01v8 w=6 l=0.6
'''
    text='\n'.join(lines)+'\n'
    return '* SCHEMATIC EXPERIMENT: modified topology, inherited parasitics are provisional\n'+text.replace('.ends',extra+'.ends',1)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--netlist',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    original=args.netlist.resolve();new=out/'separated_sample_regeneration.spice';new.write_text(schematic(original.read_text()))
    shutil.copy2(Path(__file__),out/'source_snapshot.py')
    shutil.copy2(Path(__file__).with_name('run_active_converter_macro_extracted_transient.py'),out/'deck_generator_snapshot.py')
    cases=[]
    for duration in [0.1,0.3,1.0]:
        for diff in [-100.,100.,-0.1529705854,0.1529705854]:
            case=out/f'case-{len(cases)}';case.mkdir()
            regen=8.2+duration+0.1
            text=deck(new,diff,'extracted')
            text=text.replace('preamp_iso_tail_ext aimc_converter_macro_active_candidate_flat',
                              'preamp_iso_tail_ext sample_clock regen_bar aimc_converter_macro_active_candidate_flat')
            text=text.replace('VEVAL eval 0 PULSE(0 {vdd} 8.20n',f'VEVAL eval 0 PULSE(0 {{vdd}} {regen}n')
            text=text.replace('RTAIL tail_ext 0 100G',f'''RTAIL tail_ext 0 100G
VSAMPLE sample_clock 0 PULSE(0 {{vdd}} 8.2n 20p 20p {duration}n 60n)
VREGEN regen_bar 0 PULSE({{vdd}} 0 {regen}n 20p 20p 20n 60n)''')
            probes=f'''.measure tran acquired_p FIND v(decision_p) AT={8.2+duration}n
.measure tran acquired_n FIND v(decision_n) AT={8.2+duration}n
'''
            text=text.replace('.control',probes+'.control')
            path=case/'deck.spice';path.write_text(text)
            try:
                proc=subprocess.run(['ngspice','-b',str(path)],cwd=case,capture_output=True,text=True,timeout=60)
                (case/'stdout.log').write_text(proc.stdout);(case/'stderr.log').write_text(proc.stderr)
                d=measure(proc.stdout,'decision_diff_v')
                row={'sample_duration_ns':duration,'input_diff_mv':diff,'returncode':proc.returncode,
                     'measured':proc.returncode==0 and d is not None,'decision_diff_v':d,
                     'acquired_p':measure(proc.stdout,'acquired_p'),'acquired_n':measure(proc.stdout,'acquired_n'),
                     'polarity_pass':d is not None and d!=0 and (d>0)==(diff<0),
                     'logic_margin_pass':d is not None and abs(d)>=.9}
            except subprocess.TimeoutExpired as exc:
                (case/'stdout.log').write_bytes(exc.stdout if isinstance(exc.stdout,bytes) else (exc.stdout or '').encode())
                row={'sample_duration_ns':duration,'input_diff_mv':diff,'measured':False,'timed_out':True}
            cases.append(row);print(json.dumps(row),flush=True)
    report={'schema_version':'separated_sample_regeneration_experiment.v1','evidence_kind':'schematic_topology_experiment',
            'source_netlist':str(original),'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
            'schematic_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'cases':cases,
            'scope':'Input pair gets a separate switched tail; cross-coupled PFET supply and feedback tail enable after acquisition. Added devices are not laid out; inherited capacitors are provisional.',
            'accepted_converter':False,'claim_boundary':'Not extracted evidence for this new topology, complete SAR qualification, or a physically authorized analog profile.'}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
