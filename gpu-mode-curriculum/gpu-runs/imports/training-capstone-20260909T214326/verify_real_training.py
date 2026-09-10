#!/usr/bin/env python3
"""Verify real-data training reports without trusting summary fields."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def validate(report, directory, data_dir):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    check(report.get('schema_version') in ('real-training-v0.1', 'real-training-v0.2'), 'schema')
    check(report.get('status') == 'completed', 'training not completed')
    check(report.get('evidence_kind') in ('measured_cpu', 'measured_cuda'), 'evidence kind')
    manifest = report.get('data_manifest', {})
    check(manifest.get('schema_version') == 'training-data-v0.1', 'data manifest')
    check(data_dir.joinpath('manifest.json').is_file(), 'manifest file missing')
    if data_dir.joinpath('manifest.json').is_file():
        check(sha(data_dir / 'manifest.json') == report.get('data_manifest_sha256'), 'manifest checksum')
    for split in ('train', 'validation', 'test'):
        row = manifest.get('splits', {}).get(split, {})
        path = data_dir / row.get('file', '')
        check(path.is_file() and sha(path) == row.get('sha256'), f'{split} checksum')
    protocol = report.get('protocol', {})
    if not isinstance(protocol, dict):
        errors.append('protocol fields missing')
        return errors
    steps, sequence = protocol.get('steps'), protocol.get('sequence')
    check(type(steps) is int and steps > 0 and type(sequence) is int and 1 <= sequence <= 1024, 'protocol sizes')
    expected_modes = {'standard', 'recomputed'}
    runs = report.get('runs', [])
    check(len(runs) == len(protocol.get('seeds', [])) * 2, 'arm count')
    check({r.get('mode') for r in runs} == expected_modes, 'modes')
    by_seed = {}
    for run in runs:
        seed, mode = run.get('seed'), run.get('mode')
        check(mode in expected_modes and run.get('status') == 'completed', f'{seed}/{mode}: status')
        check(type(run.get('training_starts')) is list and len(run['training_starts']) == steps, f'{seed}/{mode}: sample count')
        by_seed.setdefault(seed, []).append(run)
        check(len(run.get('steps', [])) == steps, f'{seed}/{mode}: steps')
        for i, row in enumerate(run.get('steps', [])):
            check(row.get('step') == i and row.get('tokens_processed') == (i + 1) * sequence, f'{seed}/{mode}: step accounting')
            check(math.isfinite(row.get('loss', float('nan'))) and math.isfinite(row.get('seconds', float('nan'))) and row['seconds'] >= 0, f'{seed}/{mode}: finite step')
        before, after = run.get('validation_before'), run.get('validation_after')
        for label, evaluation in (('before', before), ('after', after)):
            if report.get('schema_version') == 'real-training-v0.1':
                check(isinstance(evaluation, (int, float)) and math.isfinite(evaluation), f'{seed}/{mode}: validation {label}')
                continue
            check(isinstance(evaluation, dict), f'{seed}/{mode}: validation {label}')
            if isinstance(evaluation, dict):
                check(evaluation.get('targets') == protocol.get('validation_targets'), f'{seed}/{mode}: validation target count')
                check(math.isfinite(evaluation.get('mean_nll', float('nan'))) and evaluation.get('mean_nll') >= 0, f'{seed}/{mode}: validation loss')
                check(sum(block.get('targets', 0) for block in evaluation.get('blocks', [])) == evaluation.get('targets'), f'{seed}/{mode}: validation blocks')
    for seed, arms in by_seed.items():
        check(len(arms) == 2, f'{seed}: two arms')
        if len(arms) == 2:
            check(arms[0]['training_starts'] == arms[1]['training_starts'], f'{seed}: unmatched training samples')
    for name, digest in report.get('source_hashes', {}).items():
        path = directory / 'sources' / name
        check(path.is_file() and sha(path) == digest, f'source {name}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'data')
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    errors = validate(report, args.report.parent, args.data_dir)
    print(json.dumps({'status': 'passed' if not errors else 'failed', 'errors': errors[:20], 'error_count': len(errors)}))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
