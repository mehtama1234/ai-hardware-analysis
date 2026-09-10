#!/usr/bin/env python3
"""Validate matched workload, controls, and recomputed serving metrics."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from verify_continuous_load import p95


def validate(report, directory, expected_model_id='openai-community/gpt2',
             expected_revision='607a30d783dfa663caf39e06633721c8d4cfcd7e'):
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)
    def near(a,b):
        return a is None and b is None or isinstance(a,(int,float)) and isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-6)
    modes = ['native_microbatch','graph_microbatch','graph_continuous']
    check(report['schema_version'] in ('matched-serving-v0.1','matched-serving-v0.2') and report['status']=='passed' and report['evidence_kind']=='measured_gpu','GPU pass missing')
    check(report.get('model_id', 'openai-community/gpt2') == expected_model_id and
          report['model_revision']==report['tokenizer_revision']==expected_revision,'model identity')
    expected_sources = {'graph_decode.py','slot_decode.py','continuous_service.py','continuous_http.py','real_model_service.py','run_continuous_load.py','microbatch_control.py','run_serving_comparison.py'}
    if report.get('engine') == 'hf':
        expected_sources.add('hf_slot_decode.py')
    check(set(report['source_hashes'])==expected_sources,'source closure')
    for name,digest in report['source_hashes'].items():
        path=directory/'comparison-sources'/name
        check(Path(name).name==name and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,f'source: {name}')
    if report['schema_version']=='matched-serving-v0.2':
        bundle=report['reproduction_bundle']
        path=directory/bundle['path']
        check(Path(bundle['path']).name==bundle['path'] and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==bundle['sha256'],'source bundle')
    protocol=report['protocol']
    check(protocol['modes']==modes and protocol['rates']==[16,48] and protocol['rounds']==3 and protocol['budgets']==[1,8,16,32],'protocol')
    check(protocol['slots']==2 and protocol['queue']==8 and protocol['microbatch_window_ms']==5,'scheduling limits')
    if report.get('engine') == 'hf':
        check('no performance advantage' in protocol.get('replay_criterion', ''), 'cross-architecture criterion')
    check((protocol['ttft_ms'],protocol['completion_ms'],protocol['intertoken_ms'])==(1000,3000,500),'latency targets')
    check(len(report['runs'])==18 and {(r['round_index'],r['offered_rate'],r['mode']) for r in report['runs']}=={(i,rate,m) for i in range(3) for rate in (16,48) for m in modes},'run coverage')
    for run in report['runs']:
        label=run['round']
        check(run['order_position']==(modes.index(run['mode'])-run['round_index'])%3,f'{label}: order')
        rows,state,summary=run['requests'],run['scheduler'],run['summary']
        check(len(rows)==run['offered_rate']*protocol['seconds'],f'{label}: count')
        completed,rejected=[],[]
        hits=0
        for i,row in enumerate(rows):
            request_id=f'{label}-{i}'
            budget=protocol['budgets'][(i//4+i)%4]
            check(row['request_id']==request_id and row['max_new_tokens']==budget and row['prompt_index']==i%4,f'{request_id}: workload')
            check(near(row['planned_start_s']-rows[0]['planned_start_s'],i/run['offered_rate']),f'{request_id}: arrival plan')
            check(near(row['completion_ms'],(row['actual_end_s']-row['actual_start_s'])*1000) and near(row['arrival_lateness_ms'],(row['actual_start_s']-row['planned_start_s'])*1000),f'{request_id}: timing')
            check(row['error'] is None,f'{request_id}: transport')
            hit=False
            if row['http_status']==429:
                rejected.append(row)
                check(not row['token_ids'] and row['terminal'] is None,f'{request_id}: rejected output')
            elif row['http_status']==200:
                completed.append(row)
                expected=report['references'][i%4][:budget]
                terminal=row['terminal']
                check(row['token_ids']==expected and row['output_parity'] is True,f'{request_id}: parity')
                check(terminal['type']=='done' and terminal['status']=='completed' and terminal['finish_reason']=='length' and terminal['max_new_tokens']==budget,f'{request_id}: terminal')
                check({k:v for k,v in terminal.items() if k!='type'}==state['records'][request_id] and terminal['token_ids']==expected,f'{request_id}: accounting')
                arrivals=row['token_arrival_ms']
                check(len(arrivals)==budget and arrivals==sorted(arrivals) and 0<=arrivals[0]<=arrivals[-1]<=row['completion_ms'],f'{request_id}: token timing')
                hit=arrivals[0]<=1000 and row['completion_ms']<=3000 and all(b-a<=500 for a,b in zip(arrivals,arrivals[1:]))
            else:
                errors.append(f'{request_id}: status')
            check(row['meets_latency_targets'] is hit,f'{request_id}: goodput classification')
            hits+=hit
        duration=max(r['actual_end_s'] for r in rows)-min(r['actual_start_s'] for r in rows)
        check(bool(completed) and summary['completed']==len(completed) and summary['rejected']==len(rejected) and summary['failed']==0,f'{label}: summary counts')
        check(near(summary['measured_window_s'],duration) and near(summary['goodput_requests_per_s'],hits/duration) and near(summary['output_tokens_per_s'],sum(len(r['token_ids']) for r in completed)/duration),f'{label}: throughput')
        check(near(summary['completion_p95_ms'],p95([r['completion_ms'] for r in completed])) and near(summary['ttft_p95_ms'],p95([r['token_arrival_ms'][0] for r in completed])),f'{label}: percentiles')
        check(summary['accepted_by_budget']=={str(b):sum(r['max_new_tokens']==b for r in completed) for b in protocol['budgets']},f'{label}: workload mix')
        check(state['rejected']==len(rejected) and state['active_or_queued']==0 and set(state['records'])=={r['request_id'] for r in completed},f'{label}: server accounting')
        check(all(value is True for value in run['checks'].values()),f'{label}: execution checks')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report',type=Path)
    parser.add_argument('--model-id', default='openai-community/gpt2')
    parser.add_argument('--model-revision', default='607a30d783dfa663caf39e06633721c8d4cfcd7e')
    args=parser.parse_args()
    try:
        errors=validate(json.loads(args.report.read_text()),args.report.parent,
                        args.model_id, args.model_revision)
    except (KeyError,ValueError,TypeError,IndexError,ZeroDivisionError) as exc:
        errors=[f'malformed report: {exc}']
    result={'status':'failed' if errors else 'passed','errors':errors,
            'scope':'Matched bounded HTTP windows; no independent replay or production capacity acceptance'}
    args.report.with_suffix('.verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'error_count':len(errors),'errors':errors[:10]},indent=2))
    return int(bool(errors))


if __name__=='__main__':
    raise SystemExit(main())
