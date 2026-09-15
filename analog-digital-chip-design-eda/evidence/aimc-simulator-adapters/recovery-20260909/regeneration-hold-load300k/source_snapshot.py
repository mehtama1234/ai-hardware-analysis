#!/usr/bin/env python3
"""Hold reset released/evaluation enabled to separate settling from weak regeneration."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from run_active_converter_macro_extracted_transient import deck,measure


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--netlist',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    netlist=args.netlist.resolve()
    times=[7.9,8.3,18,28,48,98]
    nodes=['decision_p','decision_n','latch_sense_p_ext','latch_sense_n_ext','tail_ext','iso_tail_ext','preamp_iso_tail_ext']
    cases=[]
    for i,diff in enumerate([-100.,100.,-0.1529705854,0.1529705854]):
        case=args.output/f'case-{i}';case.mkdir()
        text=deck(netlist,diff,'extracted').replace('30n 60n)','200n 400n)').replace('20n 30n)','200n 400n)').replace('.tran 20p 20n uic','.tran 20p 100n uic')
        probes=[]
        for ti,t in enumerate(times):
            for ni,node in enumerate(nodes): probes.append(f'.measure tran p{ti}_{ni} FIND v({node}) AT={t}n')
        text=text.replace('.control','\n'.join(probes)+'\n.control')
        path=case/'deck.spice';path.write_text(text)
        try:
            proc=subprocess.run(['ngspice','-b',str(path.resolve())],cwd=case,text=True,capture_output=True,timeout=90)
            (case/'stdout.log').write_text(proc.stdout);(case/'stderr.log').write_text(proc.stderr)
            samples=[{'time_ns':t,**{node:measure(proc.stdout,f'p{ti}_{ni}') for ni,node in enumerate(nodes)}} for ti,t in enumerate(times)]
            complete=proc.returncode==0 and all(v is not None for row in samples for v in row.values())
            for row in samples:
                a,b=row['decision_p'],row['decision_n']
                row['decision_diff_v']=b-a if a is not None and b is not None else None
            result={'input_diff_mv':diff,'measured':complete,'returncode':proc.returncode,'samples':samples}
        except subprocess.TimeoutExpired as exc:
            (case/'stdout.log').write_bytes(exc.stdout if isinstance(exc.stdout,bytes) else (exc.stdout or '').encode())
            (case/'stderr.log').write_bytes(exc.stderr if isinstance(exc.stderr,bytes) else (exc.stderr or '').encode())
            result={'input_diff_mv':diff,'measured':False,'timed_out':True}
        cases.append(result)
        print(json.dumps({'case':i,'measured':result['measured'],'last_sample':result.get('samples',[None])[-1]}),flush=True)
    report={'schema_version':'converter_regeneration_hold_diagnostic.v1','netlist':str(netlist),
            'netlist_sha256':hashlib.sha256(netlist.read_bytes()).hexdigest(),
            'protocol':{'hold_until_ns':100,'reset_release_ns':8,'evaluate_enable_ns':8.2,'sample_times_ns':times,
                        'note':'Single extended evaluation; not normal multicycle operation or a throughput result'},
            'cases':cases,'accepted_converter':False,
            'claim_boundary':'Nominal extracted-netlist settling/regeneration diagnostic; no ADC transfer, PVT/noise/mismatch or analog inference acceptance.'}
    (args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copy2(Path(__file__),args.output/'source_snapshot.py')
    shutil.copy2(Path(__file__).with_name('run_active_converter_macro_extracted_transient.py'),args.output/'deck_generator_snapshot.py')


if __name__=='__main__':main()
