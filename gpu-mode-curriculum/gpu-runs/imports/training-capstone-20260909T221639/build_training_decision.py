#!/usr/bin/env python3
"""Build a conservative training decision from a verified raw report."""
import argparse
import json
import statistics
from pathlib import Path

from verify_real_training import validate


def build(report, errors):
    def validation_value(run):
        value = run.get('validation_after')
        return value.get('mean_nll') if isinstance(value, dict) else value
    runs = report.get('runs', [])
    rows = []
    for seed in sorted({r.get('seed') for r in runs}):
        arms = {r['mode']: r for r in runs if r.get('seed') == seed}
        if set(arms) != {'standard', 'recomputed'}:
            continue
        rows.append({'seed': seed, 'validation_delta': validation_value(arms['recomputed']) - validation_value(arms['standard']),
            'standard_seconds': statistics.median(s['seconds'] for s in arms['standard'].get('steps', [])),
            'recomputed_seconds': statistics.median(s['seconds'] for s in arms['recomputed'].get('steps', [])),
            'standard_steps': len(arms['standard'].get('steps', [])), 'recomputed_steps': len(arms['recomputed'].get('steps', []))})
    decision = {'schema_version': 'real-training-decision-v0.1', 'input_schema': report.get('schema_version'),
        'input_status': report.get('status'), 'verification': {'status': 'passed' if not errors else 'failed', 'errors': errors},
        'scope': 'measured report only; no claim beyond its protocol', 'paired_seeds': rows,
        'status': 'pending' if errors else 'review',
        'limitations': ['does not select checkpoints', 'does not infer time-to-quality from bounded steps',
            'CPU host timing is not GPU evidence', 'validation scope follows the input report']}
    if rows:
        decision['aggregate'] = {'median_validation_delta_recomputed_minus_standard': statistics.median(r['validation_delta'] for r in rows),
            'median_step_ratio_recomputed_over_standard': statistics.median(r['recomputed_seconds'] / r['standard_seconds'] for r in rows if r['standard_seconds'] > 0)}
    if not errors and report.get('protocol', {}).get('validation_scope') == 'full_split':
        decision['status'] = 'ready_for_review'
    return decision


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    p.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'data')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    report = json.loads(args.report.read_text())
    errors = validate(report, args.report.parent, args.data_dir)
    decision = build(report, errors)
    args.output.write_text(json.dumps(decision, indent=2) + '\n')
    print(json.dumps({'status': decision['status'], 'verification': decision['verification']['status'], 'paired_seeds': len(decision['paired_seeds'])}))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
