#!/usr/bin/env python3
"""Dependency-checked isolated replay of the captured matched serving experiment."""
import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from replay_graph_decode import dependencies, extract, sha
from verify_serving_comparison import validate


def conclusions(report):
    def median(mode,rate,metric):
        return statistics.median(r['summary'][metric] for r in report['runs'] if r['mode']==mode and r['offered_rate']==rate)
    return {'high_rate_goodput':all(median('graph_continuous',48,'goodput_requests_per_s')>
            median(mode,48,'goodput_requests_per_s') for mode in ('native_microbatch','graph_microbatch')),
        'low_rate_tail_latency':median('graph_continuous',16,'completion_p95_ms')<median('graph_microbatch',16,'completion_p95_ms')}


def prepare_output(output):
    output.mkdir(parents=True, exist_ok=True)
    for name in ('serving-comparison.json', 'serving-reproduction.json', 'serving-replay.log'):
        if (output / name).exists():
            raise ValueError(f'replay output already exists: {name}; use a fresh output directory')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-report',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--checkpoint',type=Path)
    args=parser.parse_args()
    original=json.loads(args.original_report.read_text())
    output=args.output_dir.resolve()
    prepare_output(output)
    result={'original_report_sha256':sha(args.original_report),'errors':[],
        'source_isolation':'checksum-verified archive extracted in a new temporary directory; PYTHONPATH cleared',
        'performance_criterion':original['protocol']['replay_criterion'],
        'wrapper_source_hashes':{name:sha(Path(__file__).with_name(name)) for name in
            ('replay_serving_comparison.py','replay_graph_decode.py','verify_serving_comparison.py','verify_continuous_load.py')}}
    errors=result['errors']
    with tempfile.TemporaryDirectory(prefix='matched-serving-replay-') as temp:
        source=Path(temp)
        extract(args.original_report.parent/original['reproduction_bundle']['path'],original,source)
        checks,mismatches=dependencies((source/'requirements.recorded.txt').read_text())
        result['dependency_checks']=checks
        errors.extend(mismatches)
        if platform.python_version()!=original['runtime']['python']:
            errors.append('Python version mismatch')
        if not errors:
            env=dict(os.environ)
            env.pop('PYTHONPATH',None)
            env['PYTHONNOUSERSITE']='1'
            command=[sys.executable,str(source/'run_serving_comparison.py'),'--output-dir',str(output),'--seconds',str(original['protocol']['seconds'])]
            if args.checkpoint:
                command.extend(['--checkpoint', str(args.checkpoint.resolve())])
            with (output/'serving-replay.log').open('w') as log:
                proc=subprocess.run(command,cwd=source,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1500)
            result['returncode']=proc.returncode
            if proc.returncode:
                errors.append('replayed experiment failed')
            path=output/'serving-comparison.json'
            if not path.exists():
                errors.append('replayed report missing')
            else:
                replay=json.loads(path.read_text())
                result['replayed_report_sha256']=sha(path)
                errors.extend(validate(replay,output))
                for key in ('source_hashes','runtime','model_revision','tokenizer_revision','protocol','prompts','references'):
                    if replay[key]!=original[key]:
                        errors.append(f'replay identity mismatch: {key}')
                result['original_conclusions']=conclusions(original)
                result['replayed_conclusions']=conclusions(replay)
                if not all(result['original_conclusions'].values()) or not all(result['replayed_conclusions'].values()):
                    errors.append('declared performance conclusion did not reproduce')
    result['status']='failed' if errors else 'passed'
    (output/'serving-reproduction.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'dependency_count':len(result.get('dependency_checks',{})),'errors':errors[:10]}),flush=True)
    return int(bool(errors))


if __name__=='__main__':
    raise SystemExit(main())
