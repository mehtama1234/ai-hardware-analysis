#!/usr/bin/env python3
"""Verify generic CUDA cache-characterization report integrity."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('--model-id', required=True)
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    d = json.loads(args.report.read_text())
    errors = []
    if d.get('schema_version') != 'real-model-serving-characterization-v0.1': errors.append('schema')
    profile = d.get('model_profile', {})
    if profile.get('model_id') != args.model_id or profile.get('requested_revision') != args.revision: errors.append('model identity')
    if d.get('evidence_kind') != 'measured_gpu' or d.get('device') != 'cuda': errors.append('CUDA identity')
    rows = d.get('rows', [])
    if [r.get('batch_size') for r in rows] != [1, 2, 4]: errors.append('batch coverage')
    for row in rows:
        if row.get('output_parity') is not True: errors.append(f"parity batch {row.get('batch_size')}")
        for side in ('cached', 'uncached'):
            if not row.get(side, {}).get('wall_time_ms_samples'): errors.append(f"timing batch {row.get('batch_size')} {side}")
    result = {'status': 'passed' if not errors else 'failed', 'errors': errors}
    print(json.dumps(result))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
