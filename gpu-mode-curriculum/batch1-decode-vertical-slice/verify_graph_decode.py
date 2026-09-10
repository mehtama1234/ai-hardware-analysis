#!/usr/bin/env python3
"""Validate measured graph experiment artifacts; does not imply serving acceptance."""
import argparse
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path


def validate(report, directory):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    def digest(path, expected):
        return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected
    version = report.get('schema_version')
    check(version in ('real-model-graph-decode-v0.1', 'real-model-graph-decode-v0.2'), 'schema mismatch')
    check(report.get('evidence_kind') == 'measured_gpu', 'GPU measurement missing')
    check(report.get('status') == 'passed', 'experiment not passed')
    check(report.get('model_revision') == report.get('tokenizer_revision') and bool(report.get('model_revision')), 'model/tokenizer identity missing')
    hashes = report.get('source_hashes', {})
    check(set(hashes) == {'graph_decode.py', 'run_real_model_graph_decode.py'}, 'source closure missing')
    for name, expected in hashes.items():
        check(Path(name).name == name and digest(directory / 'sources' / name, expected), f'source mismatch: {name}')
    protocol = report.get('protocol', {})
    count, repeats = protocol.get('max_new_tokens', 0), protocol.get('repeats', 0)
    check(2 <= count <= 32 and repeats >= 3, 'invalid measurement protocol')
    modes = ['dynamic_eager', 'static_eager', 'static_graph']
    rows = report.get('rows', [])
    check({(r['batch'], r['capacity'], r['fixture']) for r in rows} ==
          {(b, c, f) for b, c in ((1, 128), (4, 256)) for f in range(3)} and len(rows) == 6, 'fixture coverage missing')
    for row in rows:
        label = f"batch={row['batch']} fixture={row['fixture']}"
        reference = row['reference_token_ids']
        check(len(reference) == row['batch'] and all(len(tokens) == count for tokens in reference), f'{label}: reference shape')
        check(row['output_parity'] is True, f'{label}: reference parity failed')
        check(set(row['samples']) == set(modes), f'{label}: comparison missing')
        for mode in modes:
            samples = row['samples'].get(mode, [])
            check(len(samples) == repeats, f'{label} {mode}: repeat count')
            for i, sample in enumerate(samples):
                check(sample['round'] == i and sample['order'] == (modes.index(mode) - i) % 3, f'{label} {mode}: order')
                check(math.isfinite(sample['wall_ms']) and sample['wall_ms'] > 0, f'{label} {mode}: timing')
                check(sample['output_parity'] is True and sample['token_ids'] == reference, f'{label} {mode}: output mismatch')
            if samples:
                check(math.isclose(row['median_ms'][mode], statistics.median(s['wall_ms'] for s in samples), rel_tol=1e-9), f'{label} {mode}: median')
        profile = row['profile']
        check(Path(profile['file']).name == profile['file'] and digest(directory / profile['file'], profile['sha256']), f'{label}: trace mismatch')
        launches = sum(op['count'] for op in profile['operations'] if 'cudaGraphLaunch' in op['name'])
        check(launches >= count - 1, f'{label}: CUDA graph launches not observed')
        if version == 'real-model-graph-decode-v0.2':
            check(set(row['profiles']) == set(modes), f'{label}: matched profiles missing')
            for mode in modes:
                profile = row['profiles'][mode]
                check(Path(profile['file']).name == profile['file'] and digest(directory / profile['file'], profile['sha256']), f'{label} {mode}: trace mismatch')
                check(bool(profile['operations']), f'{label} {mode}: profile empty')
                trace_path = directory / profile['file']
                if trace_path.is_file() and Path(profile['file']).name == profile['file']:
                    opener = gzip.open if trace_path.suffix == '.gz' else open
                    with opener(trace_path, 'rt') as stream:
                        events = json.load(stream)['traceEvents']
                    actual_launches = sum(e.get('ph') == 'X' and 'cudaGraphLaunch' in e.get('name', '') for e in events)
                    reported_launches = sum(o['count'] for o in profile['operations'] if 'cudaGraphLaunch' in o['name'])
                    check(actual_launches == reported_launches, f'{label} {mode}: launch summary differs from raw trace')
                stages = row['stage_samples'][mode]
                check(len(stages) == repeats, f'{label} {mode}: stage samples missing')
                check(all(s['output_parity'] is True and all(math.isfinite(s[k]) and s[k] > 0 for k in ('prefill_ms','decode_ms')) for s in stages), f'{label} {mode}: stage validation')
                if mode != 'dynamic_eager':
                    logits = row['logit_checks'][mode]
                    check(logits['passed'] is True and len(logits['steps']) == count - 1 and
                          all(s['finite'] is True and s['allclose'] is True and math.isfinite(s['max_abs_error']) for s in logits['steps']), f'{label} {mode}: logits invalid')
    if version == 'real-model-graph-decode-v0.2':
        bundle = report['reproduction_bundle']
        check(Path(bundle['path']).name == bundle['path'] and digest(directory / bundle['path'], bundle['sha256']), 'reproduction bundle mismatch')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.report.read_text()), args.report.parent)
    except (KeyError, TypeError, ValueError) as exc:
        errors = [f'malformed report: {exc}']
    result = {'status': 'failed' if errors else 'passed', 'errors': errors,
              'scope': 'Captured fixed-batch graph experiment; no HTTP, dynamic admission, or independent replay acceptance'}
    (args.report.parent / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
