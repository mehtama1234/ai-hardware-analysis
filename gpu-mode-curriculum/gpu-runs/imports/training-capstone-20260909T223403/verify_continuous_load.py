#!/usr/bin/env python3
"""Recompute acceptance and load summaries from client/server evidence."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def p95(values):
    return sorted(values)[math.ceil(.95 * len(values)) - 1] if values else None


def validate(report, directory):
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)
    def near(a, b):
        return a is None and b is None or (isinstance(a, (int,float)) and isinstance(b, (int,float)) and math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-6))
    check(report['schema_version'] == 'continuous-arrival-load-v0.1' and report['status'] == 'passed' and report['evidence_kind'] == 'measured_gpu', 'measured pass missing')
    check(report['model_revision'] == report['tokenizer_revision'] == '607a30d783dfa663caf39e06633721c8d4cfcd7e', 'model identity')
    expected_sources = {'graph_decode.py','slot_decode.py','continuous_service.py','continuous_http.py','real_model_service.py','run_continuous_load.py'}
    check(set(report['source_hashes']) == expected_sources, 'source closure')
    for name, digest in report['source_hashes'].items():
        path = directory / 'load-sources' / name
        check(Path(name).name == name and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest, f'source hash: {name}')
    protocol = report['protocol']
    check(protocol['rates'] == [4,16,48] and protocol['rounds'] == 2 and protocol['budgets'] == [1,8,16,32], 'workload protocol')
    check(protocol['ttft_target_ms'] == 1000 and protocol['completion_target_ms'] == 3000 and protocol['max_intertoken_gap_ms'] == 500, 'latency targets changed')
    expected_order = ['r0-rate4','r0-rate16','r0-rate48','r1-rate48','r1-rate16','r1-rate4']
    check([run['round'] for run in report['runs']] == expected_order, 'run coverage/order')
    total_rejected = 0
    for run in report['runs']:
        label = run['round']
        rows, summary, state = run['requests'], run['summary'], run['scheduler']
        check(len(rows) == run['offered_rate'] * protocol['seconds_per_window'], f'{label}: request count')
        completed, rejected = [], []
        target_hits = 0
        for i, row in enumerate(rows):
            request_id = f'{label}-{i}'
            budget = protocol['budgets'][(i // 4 + i) % 4]
            check(row['request_id'] == request_id and row['max_new_tokens'] == budget and row['prompt_index'] == i % 4, f'{request_id}: workload mismatch')
            check(row['error'] is None, f'{request_id}: transport error')
            check(near(row['completion_ms'], (row['actual_end_s'] - row['actual_start_s']) * 1000) and near(row['arrival_lateness_ms'], (row['actual_start_s'] - row['planned_start_s']) * 1000), f'{request_id}: client timing')
            if i:
                check(near(row['planned_start_s'] - rows[0]['planned_start_s'], i / run['offered_rate']), f'{request_id}: arrival plan')
            hits = False
            if row['http_status'] == 429:
                rejected.append(row)
                check(not row['token_ids'] and row['terminal'] is None, f'{request_id}: rejected output')
            elif row['http_status'] == 200:
                completed.append(row)
                expected = report['references'][i % 4][:budget]
                check(row['token_ids'] == expected and row['output_parity'] is True, f'{request_id}: output parity')
                terminal = row['terminal']
                check(terminal['status'] == 'completed' and terminal['finish_reason'] == 'length' and terminal['max_new_tokens'] == budget, f'{request_id}: terminal state')
                record = {key: value for key, value in terminal.items() if key != 'type'}
                check(terminal.get('type') == 'done' and record == state['records'][request_id] and terminal['token_ids'] == expected, f'{request_id}: client/server accounting')
                arrivals = row['token_arrival_ms']
                check(len(arrivals) == budget and arrivals == sorted(arrivals) and 0 <= arrivals[0] <= arrivals[-1] <= row['completion_ms'], f'{request_id}: token arrivals')
                hits = arrivals[0] <= 1000 and row['completion_ms'] <= 3000 and all(b-a <= 500 for a,b in zip(arrivals,arrivals[1:]))
            else:
                errors.append(f'{request_id}: unexpected status')
            check(row['meets_latency_targets'] is hits, f'{request_id}: target classification')
            target_hits += hits
        check(bool(completed), f'{label}: no completed work')
        duration = max(r['actual_end_s'] for r in rows) - min(r['actual_start_s'] for r in rows)
        check(duration > 0 and near(summary['measured_window_s'], duration), f'{label}: duration')
        check(summary['completed'] == len(completed) and summary['rejected'] == len(rejected) and summary['failed'] == 0, f'{label}: summary counts')
        check(near(summary['goodput_requests_per_s'], target_hits / duration) and near(summary['output_tokens_per_s'], sum(len(r['token_ids']) for r in completed) / duration), f'{label}: throughput')
        check(near(summary['completion_p95_ms'], p95([r['completion_ms'] for r in completed])) and near(summary['ttft_p95_ms'], p95([r['token_arrival_ms'][0] for r in completed])), f'{label}: latency percentiles')
        check(near(summary['arrival_lateness_p95_ms'], p95([r['arrival_lateness_ms'] for r in rows])), f'{label}: load-generator lateness')
        check(state['rejected'] == len(rejected) and state['active_or_queued'] == 0 and set(state['records']) == {r['request_id'] for r in completed}, f'{label}: queue accounting')
        check(set(run['checks']) == {'no_failed_requests','all_accounted','queue_rejections_match','accepted_records_match','drained','cache_cleared'} and all(v is True for v in run['checks'].values()), f'{label}: execution checks')
        total_rejected += len(rejected)
    probe = report['eos_probe']
    expected_length = report['references'][0].index(probe['eos_token_id']) + 1
    check(probe['passed'] is True and probe['expected_length'] == expected_length < 32 and probe['request']['token_ids'] == report['references'][0][:expected_length] and probe['request']['terminal']['finish_reason'] == 'eos', 'controlled EOS probe')
    check(total_rejected > 0, 'GPU overload not observed')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.report.read_text()), args.report.parent)
    except (KeyError, ValueError, TypeError, IndexError, ZeroDivisionError) as exc:
        errors = [f'malformed report: {exc}']
    result = {'status': 'failed' if errors else 'passed', 'errors': errors,
        'scope': 'Bounded repeated HTTP arrival windows; no matched-baseline advantage or independent replay acceptance'}
    args.report.with_suffix('.verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
