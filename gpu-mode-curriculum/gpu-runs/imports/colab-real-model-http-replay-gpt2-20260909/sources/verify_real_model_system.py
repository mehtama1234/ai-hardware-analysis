#!/usr/bin/env python3
"""Verify direct profiler and live HTTP evidence from raw samples and outputs."""
import argparse
import gzip
import hashlib
import json
import math
import statistics
import tarfile
from pathlib import Path


def validate(report, directory=None):
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)
    def near(value, expected):
        return isinstance(value, (int, float)) and math.isfinite(value) and math.isclose(value, expected, rel_tol=1e-7)
    check(report.get('evidence_kind') == 'measured_gpu', 'GPU evidence required')
    check(report.get('gpu_execution_accepted') is True, 'execution not accepted')
    for field in ('model_revision', 'tokenizer_revision', 'runtime', 'source_hashes', 'command'):
        check(bool(report.get(field)), f'missing {field}')
    if directory is not None:
        for name, expected in report.get('source_hashes', {}).items():
            source = directory / 'sources' / name
            if not source.is_file():
                source = Path(__file__).resolve().parent / name
            check(source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == expected, f'source mismatch: {name}')
    if report.get('schema_version') == 'real-model-http-repeated-v0.1':
        names = ('eager_serial', 'eager_microbatch', 'sdpa_microbatch', 'paged_microbatch')
        rounds = report.get('rounds', [])
        count = report.get('protocol', {}).get('round_count', 0)
        check(count >= 4 and count % 4 == 0 and len(rounds) == count, 'invalid counterbalanced round count')
        for index, round_report in enumerate(rounds):
            check(round_report.get('index') == index, 'round index mismatch')
            check(round_report.get('order') == list(names[index % 4:] + names[:index % 4]), 'mode order is not counterbalanced')
            child = {**report, 'schema_version': 'real-model-http-v0.2', 'modes': round_report.get('modes', {})}
            errors.extend(f'round {index}: {error}' for error in validate(child))
        for name in names:
            for key in ('completion_ms_p95', 'ttft_ms_median', 'output_tokens_per_second'):
                actual = report.get('summary_samples', {}).get(name, {}).get(key)
                expected = [r.get('modes', {}).get(name, {}).get(key) for r in rounds]
                check(actual == expected, f'{name}: repeated summary mismatch for {key}')
        if directory is not None:
            bundle = directory / report['reproduction_bundle']['path']
            check(bundle.is_file(), 'missing reproduction bundle')
            if bundle.is_file():
                check(hashlib.sha256(bundle.read_bytes()).hexdigest() == report['reproduction_bundle']['sha256'], 'reproduction bundle checksum mismatch')
                with tarfile.open(bundle) as archive:
                    for name, expected in report['source_hashes'].items():
                        member = archive.extractfile(name)
                        check(member is not None and hashlib.sha256(member.read()).hexdigest() == expected, f'bundled source mismatch: {name}')
    elif report.get('schema_version') == 'real-model-profile-v0.1':
        check(report.get('batch_vs_individual_output_parity') is True, 'batching parity failed')
        variants = report.get('variants', {})
        check(set(variants) == {'eager', 'sdpa', 'paged', 'persistent'}, 'missing comparison variant')
        for name, row in variants.items():
            check(row.get('output_parity') is True and row.get('generated_token_ids') == report.get('reference_token_ids'), f'{name}: reference output mismatch')
            samples = row.get('samples', [])
            check(len(samples) == report['protocol']['repeats'] and len(samples) >= 3, f'{name}: insufficient repeats')
            for clock in ('wall_ms', 'cuda_event_ms'):
                values = [sample.get(clock) for sample in samples]
                valid = bool(values) and all(isinstance(x, (int, float)) and math.isfinite(x) and x > 0 for x in values)
                check(valid, f'{name}: invalid {clock} samples')
                if valid:
                    check(near(row.get(clock + '_median'), statistics.median(values)), f'{name}: inconsistent {clock} median')
            check(any(op.get('self_device_us', 0) > 0 for op in row['profile']['operators']), f'{name}: missing CUDA activity')
            if directory is not None:
                path = directory / row['profile']['trace']
                check(path.is_file(), f'{name}: missing raw trace')
                if path.is_file():
                    check(hashlib.sha256(path.read_bytes()).hexdigest() == row['profile']['trace_sha256'], f'{name}: trace checksum mismatch')
        if 'eager' in variants:
            for name, row in variants.items():
                check(near(row.get('latency_over_eager_ratio'), row['wall_ms_median'] / variants['eager']['wall_ms_median']), f'{name}: invalid baseline ratio')
    elif report.get('schema_version') in ('real-model-http-v0.1', 'real-model-http-v0.2'):
        modes = report.get('modes', {})
        expected_modes = {'eager_serial', 'eager_microbatch', 'sdpa_microbatch'}
        if report['schema_version'] == 'real-model-http-v0.2':
            expected_modes.add('paged_microbatch')
        check(set(modes) == expected_modes, 'missing HTTP mode')
        references = report['reference_token_ids']
        for name, row in {**modes, 'controls': report['controls']}.items():
            requests = row['requests']
            expected = report['protocol']['requests_per_mode']
            check(len(requests) == expected, f'{name}: request count mismatch')
            ids = [r['request_id'] for r in requests]
            check(len(set(ids)) == len(ids), f'{name}: duplicate requests')
            completed = []
            rejected = 0
            for index, request in enumerate(requests):
                if request['http_status'] == 429:
                    rejected += 1
                    continue
                check(request['http_status'] == 200, f'{name}: unexpected HTTP status')
                terminal = request.get('terminal') or {}
                check(terminal.get('status') == 'completed', f'{name}: request failed to complete')
                check(request['token_ids'] == references[index % len(references)] == terminal.get('token_ids'), f'{name}: HTTP/reference/terminal output mismatch')
                check(request['ttft_ms'] is not None and 0 < request['ttft_ms'] <= request['completion_ms'], f'{name}: invalid TTFT')
                completed.append(request)
            check(row['rejected_count'] == rejected and row['completed_count'] == len(completed), f'{name}: summary accounting mismatch')
            check(row['scheduler']['active_or_queued'] == 0, f'{name}: leaked requests')
            check(row['scheduler']['rejected'] == rejected, f'{name}: scheduler/client rejection mismatch')
            if name != 'controls':
                if report['schema_version'] == 'real-model-http-v0.2':
                    batches = row['scheduler']['batches']
                    check(all(b.get('peak_kv_cache_bytes', 0) > 0 for b in batches), f'{name}: missing measured KV bytes')
                    expected_calls = 12 * (report['protocol']['max_new_tokens'] - 1) * len(batches) if name == 'paged_microbatch' else 0
                    check(row.get('custom_attention_calls') == expected_calls, f'{name}: custom kernel execution count mismatch')
                    check(row.get('attention_backend') == ('sdpa' if name == 'sdpa_microbatch' else 'eager'), f'{name}: backend mismatch')
                check(len(completed) == expected, f'{name}: incomplete load')
                if 'microbatch' in name:
                    check(any(batch['size'] > 1 for batch in row['scheduler']['batches']), f'{name}: no actual batching')
            if completed:
                latencies = sorted(r['completion_ms'] for r in completed)
                check(near(row['completion_ms_median'], statistics.median(latencies)), f'{name}: median mismatch')
                check(near(row['completion_ms_p95'], latencies[math.ceil(.95 * len(latencies)) - 1]), f'{name}: p95 mismatch')
                duration = max(r['actual_end_s'] for r in requests) - min(r['actual_start_s'] for r in requests)
                check(near(row['output_tokens_per_second'], sum(len(r['token_ids']) for r in completed) / duration), f'{name}: throughput mismatch')
        probe = report['controls']['cancellation_probe']
        check(report['controls']['rejected_count'] > 0, 'no measured overload rejection')
        check(probe['cancel_ack'] is True and (probe.get('terminal') or {}).get('status') == 'cancelled_inflight', 'inflight cancellation not proven')
        check(len(probe['token_ids']) < report['protocol']['max_new_tokens'], 'cancellation did not stop token delivery')
    else:
        errors.append('unsupported schema')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    errors = validate(json.loads(args.report.read_text()), args.report.parent)
    print(json.dumps({'status': 'failed' if errors else 'passed', 'errors': errors}, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
