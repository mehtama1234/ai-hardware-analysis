#!/usr/bin/env python3
"""Verify checkpoint files recorded by run_real_training.py."""
import argparse
import hashlib
import json
from pathlib import Path

import torch


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def validate(report, directory):
    errors = []
    for run in report.get('runs', []):
        hashes = run.get('checkpoint_hashes')
        if hashes is None:
            continue
        checkpoint = directory / f"{run['seed']}-{run['mode']}"
        if not checkpoint.is_dir():
            errors.append(f"{run['seed']}/{run['mode']}: checkpoint missing")
            continue
        for name, digest in hashes.items():
            path = checkpoint / name
            if not path.is_file() or sha(path) != digest:
                errors.append(f"{run['seed']}/{run['mode']}: checksum {name}")
        state = checkpoint / 'training-state.pt'
        if state.is_file():
            try:
                value = torch.load(state, map_location='cpu', weights_only=False)
                if not isinstance(value, dict) or not isinstance(value.get('optimizer'), dict):
                    errors.append(f"{run['seed']}/{run['mode']}: optimizer state")
                if value.get('steps') != len(run.get('steps', [])):
                    errors.append(f"{run['seed']}/{run['mode']}: step state")
            except Exception as error:
                errors.append(f"{run['seed']}/{run['mode']}: unreadable state: {error}")
        else:
            errors.append(f"{run['seed']}/{run['mode']}: training state missing")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    errors = validate(report, args.report.parent)
    checked = sum(1 for run in report.get('runs', []) if run.get('checkpoint_hashes') is not None)
    status = 'not_applicable' if checked == 0 and not errors else ('passed' if not errors else 'failed')
    print(json.dumps({'status': status, 'checkpoint_runs': checked, 'errors': errors[:20]}))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
