"""Validate the bounded fixed-shape StaticCache graph bucket report."""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(); p.add_argument('report', type=Path)
    p.add_argument('--model-id', default='EleutherAI/pythia-70m'); p.add_argument('--model-revision', required=True)
    a = p.parse_args(); d = json.loads(a.report.read_text()); errors = []
    def check(ok, msg):
        if not ok: errors.append(msg)
    check(d.get('status') == 'passed' and d.get('evidence_kind') == 'measured_gpu', 'GPU pass')
    check(d.get('model_id') == a.model_id and d.get('model_revision') == a.model_revision, 'model identity')
    check(d.get('protocol', {}).get('policy') == 'recapture-per-bucket', 'lifecycle policy')
    check(len(d.get('buckets', [])) == 2, 'two buckets')
    checks = d.get('checks', {})
    for key in ('first_bucket_parity', 'second_bucket_parity', 'fixed_shape', 'recaptured'):
        check(checks.get(key) is True, key)
    check(all(b.get('recapture_ms', 0) > 0 for b in d['buckets']), 'recapture timing')
    result = {'status': 'failed' if errors else 'passed', 'errors': errors}
    a.report.with_suffix('.verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2)); return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
