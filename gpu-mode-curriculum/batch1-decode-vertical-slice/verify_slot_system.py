#!/usr/bin/env python3
"""Validate slot lifecycle/continuous HTTP functional evidence and source identity."""
import argparse
import hashlib
import json
from pathlib import Path


def validate(report, directory):
    errors = []
    def check(value, message):
        if not value:
            errors.append(message)
    check(report.get('status') == 'passed' and report.get('evidence_kind') == 'measured_gpu', 'measured GPU pass missing')
    check(report.get('model_revision') == report.get('tokenizer_revision') == '607a30d783dfa663caf39e06633721c8d4cfcd7e', 'model identity mismatch')
    hashes = report.get('source_hashes', {})
    check(bool(hashes), 'source identity missing')
    for name, digest in hashes.items():
        path = directory / 'sources' / name
        check(Path(name).name == name and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest, f'source mismatch: {name}')
    if report['schema_version'] == 'gpt2-slot-lifecycle-v0.1':
        check(set(report['modes']) == {'eager', 'graph'}, 'mode coverage missing')
        required = {'cancellation_ack','cancelled_cache_cleared','slot_reused','stale_cancel_rejected',
            'peer_cache_preserved','completed_slot_reclaimed','one_token_reclaimed',
            'outputs_match_individual_library','all_owners_released','all_cache_cleared',
            'idle_tick_empty','stale_eos_cancel_rejected'}
        for mode, row in report['modes'].items():
            check(set(row['checks']) == required and all(v is True for v in row['checks'].values()), f'{mode}: lifecycle checks failed/missing')
            expected_lengths = {'peer': 12, 'cancel': 2, 'replacement': 4, 'single': 1,
                'eos': report['reference_tokens']['eos'].index(row['controlled_eos_token_id']) + 1}
            check(row['expected_lengths'] == expected_lengths, f'{mode}: expected lengths changed')
            for name, length in expected_lengths.items():
                events = [event for event in row['events'] if event['handle']['request_id'] == name]
                check([event['index'] for event in events] == list(range(length)), f'{mode}/{name}: token indexing')
                check([event['token_id'] for event in events] == row['outputs'][name] == report['reference_tokens'][name][:length], f'{mode}/{name}: token parity')
            handles = {event['handle']['request_id']: event['handle'] for event in row['events']}
            check(handles['replacement']['slot'] == handles['cancel']['slot'] and handles['replacement']['generation'] > handles['cancel']['generation'], f'{mode}: reuse identity')
    elif report['schema_version'] == 'gpt2-continuous-http-v0.1':
        required = {'peer_output_parity','replacement_output_parity','cancelled_prefix_parity',
            'cancelled_before_completion','replacement_admitted_with_peer_active',
            'cancelled_slot_reused','all_requests_accounted','cache_empty_after_drain'}
        check(set(report['checks']) == required and all(v is True for v in report['checks'].values()), 'HTTP checks failed/missing')
        check(set(report['clients']) == set(report['scheduler']['records']) == {'peer','cancel','replacement'}, 'request accounting mismatch')
        for name, client in report['clients'].items():
            tokens = client['token_ids']
            check(tokens == report['references'][name][:len(tokens)], f'{name}: output mismatch')
            check(tokens == client['terminal']['token_ids'] == report['scheduler']['records'][name]['token_ids'], f'{name}: client/server token mismatch')
            if name == 'cancel':
                check(client['cancel_ack'] is True and client['terminal']['status'] == 'cancelled_inflight' and 2 <= len(tokens) < 32, 'cancellation not demonstrated')
            else:
                check(len(tokens) == 32 and client['terminal']['status'] == 'completed', f'{name}: incomplete output')
            arrivals = client['token_arrival_ms']
            check(len(arrivals) == len(tokens) and arrivals == sorted(arrivals) and arrivals[0] >= 0 and client['completion_ms'] >= arrivals[-1], f'{name}: invalid client timing')
        admissions = {a['request_id']: a for a in report['scheduler']['admissions']}
        replacement, cancelled = admissions['replacement'], admissions['cancel']
        check('peer' in replacement['peers'] and replacement['slot'] == cancelled['slot'] and replacement['generation'] > cancelled['generation'], 'mid-peer admission/reuse missing')
        check(report['scheduler']['active_or_queued'] == 0, 'requests not drained')
    else:
        errors.append('unsupported schema')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.report.read_text()), args.report.parent)
    except (KeyError, ValueError, TypeError, IndexError) as exc:
        errors = [f'malformed report: {exc}']
    result = {'status': 'failed' if errors else 'passed', 'errors': errors,
              'scope': 'Bounded functional lifecycle/HTTP proof; not capacity or independent replay acceptance'}
    args.report.with_suffix('.verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
