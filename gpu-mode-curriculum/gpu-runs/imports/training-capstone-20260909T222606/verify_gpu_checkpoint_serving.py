#!/usr/bin/env python3
"""Verify the bounded CUDA checkpoint-serving smoke contract."""
import argparse
import json
from pathlib import Path


REQUIRED_CHECKS = ('token_parity', 'terminal_completed', 'accounted', 'cache_empty')


def verify(path: Path):
    errors = []
    try:
        report = json.loads(path.read_text())
    except Exception as exc:
        return {'status': 'failed', 'errors': [f'invalid JSON: {exc}']}
    if report.get('schema_version') != 'gpu-checkpoint-serving-v0.1':
        errors.append('schema_version mismatch')
    if report.get('status') != 'passed':
        errors.append('report status is not passed')
    if report.get('evidence_kind') != 'measured_cuda' or report.get('device') != 'cuda':
        errors.append('CUDA evidence identity missing')
    if report.get('reference_tokens') != report.get('served_tokens'):
        errors.append('served tokens differ from reference')
    checks = report.get('checks')
    if not isinstance(checks, dict):
        errors.append('checks must be an object')
    else:
        for key in REQUIRED_CHECKS:
            if checks.get(key) is not True:
                errors.append(f'check failed: {key}')
    terminal = report.get('terminal')
    if not isinstance(terminal, dict) or terminal.get('status') != 'completed':
        errors.append('terminal completion missing')
    scheduler = report.get('scheduler')
    if not isinstance(scheduler, dict) or scheduler.get('active_or_queued') != 0:
        errors.append('scheduler did not drain')
    return {'status': 'passed' if not errors else 'failed', 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    result = verify(args.report)
    print(json.dumps(result))
    return int(result['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
