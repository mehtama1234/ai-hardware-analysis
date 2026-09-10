"""Validate bounded HTTP StaticGraphBucket evidence."""
import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('report',type=Path); p.add_argument('--model-id',default='EleutherAI/pythia-70m'); p.add_argument('--model-revision',required=True); a=p.parse_args()
    d=json.loads(a.report.read_text()); e=[]
    def c(ok,m):
        if not ok:e.append(m)
    c(d.get('status')=='passed' and d.get('evidence_kind')=='measured_gpu','GPU pass')
    c(d.get('model_id')==a.model_id and d.get('model_revision')==a.model_revision,'model identity')
    checks = d.get('checks', {})
    if 'four_shape_budget_classes' in checks:
        for k in ('four_shape_budget_classes','all_http_ok','mixed_output_budgets',
                  'token_parity','bounded_backpressure','overload_accounted','drained'):
            c(checks.get(k) is True,k)
        c((checks.get('eight_requests_per_round') is True or checks.get('eight_requests') is True), 'eight_requests_per_round')
        c((checks.get('four_recaptures_per_round') is True or checks.get('four_recaptures') is True), 'four_recaptures_per_round')
        c(len(d.get('bucket_meta',[]))>=4 and all(x.get('recapture_ms',0)>0 for x in d['bucket_meta']),'bucket timing')
        c(d.get('overload',{}).get('rejected_429',0)>0,'backpressure count')
    else:
        # Preserve verification of the earlier two-shape, fixed-budget artifact.
        for k in ('two_shape_classes','four_requests','all_http_ok','all_eight_tokens',
                  'token_parity','drained','two_recaptures'):
            c(checks.get(k) is True,k)
        c(len(d.get('bucket_meta',[]))==2 and all(x.get('recapture_ms',0)>0 for x in d['bucket_meta']),'bucket timing')
    r={'status':'failed' if e else 'passed','errors':e}; a.report.with_suffix('.verification.json').write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2)); return int(bool(e))
if __name__=='__main__': raise SystemExit(main())
