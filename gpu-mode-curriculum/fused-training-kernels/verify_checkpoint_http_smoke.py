#!/usr/bin/env python3
"""Verify checkpoint-to-HTTP smoke evidence and reject incomplete reports."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def validate(report, checkpoint):
    errors = []
    def check(value, message):
        if not value: errors.append(message)
    check(report.get('schema_version') == 'checkpoint-http-smoke-v0.1', 'schema')
    check(report.get('status') == 'passed', 'status')
    check(report.get('evidence_kind') == 'measured_cpu', 'evidence kind')
    check(report.get('model_revision') == report.get('tokenizer_revision') == '607a30d783dfa663caf39e06633721c8d4cfcd7e', 'model identity')
    check(all(report.get('checks', {}).get(name) is True for name in ('token_parity','terminal_completed','accounted','cache_empty')), 'checks')
    check(report.get('served_tokens') == report.get('reference_tokens'), 'tokens')
    terminal = report.get('terminal') or {}
    check(terminal.get('status') == 'completed' and terminal.get('finish_reason') == 'length', 'terminal')
    check(terminal.get('max_new_tokens') == len(report.get('served_tokens', [])), 'budget')
    scheduler = report.get('scheduler') or {}
    check(scheduler.get('active_or_queued') == 0, 'drain')
    hashes = report.get('checkpoint_hashes') or {}
    check(checkpoint.is_dir() and bool(hashes), 'checkpoint')
    for name, digest in hashes.items():
        path = checkpoint / name
        check(path.is_file() and sha(path) == digest, f'checkpoint hash {name}')
    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    p.add_argument('--checkpoint', type=Path, required=True)
    args = p.parse_args()
    errors = validate(json.loads(args.report.read_text()), args.checkpoint)
    print(json.dumps({'status': 'passed' if not errors else 'failed', 'errors': errors}))
    return int(bool(errors))


if __name__ == '__main__': raise SystemExit(main())
