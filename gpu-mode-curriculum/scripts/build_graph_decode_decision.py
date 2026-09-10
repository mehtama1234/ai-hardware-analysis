#!/usr/bin/env python3
"""Build a bounded graph-decode decision directly from validated captured reports."""
import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'batch1-decode-vertical-slice'))
from verify_graph_decode import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reports', type=Path, nargs='+')
    args = parser.parse_args()
    inputs, rows = [], []
    for path in args.reports:
        path = path.resolve()
        report = json.loads(path.read_text())
        errors = validate(report, path.parent)
        if errors or report['schema_version'] != 'real-model-graph-decode-v0.2':
            raise SystemExit(f'{path}: invalid v0.2 evidence: {errors}')
        inputs.append({'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'runtime': report['runtime']})
        for row in report['rows']:
            profiles = {}
            for mode, profile in row['profiles'].items():
                ops = profile['operations']
                profiles[mode] = {
                    'ordinary_launch_calls': sum(o['count'] for o in ops if 'cudaLaunchKernel' in o['name']),
                    'graph_launch_calls': sum(o['count'] for o in ops if 'cudaGraphLaunch' in o['name']),
                    'aten_cat_calls': sum(o['count'] for o in ops if o['name'] == 'aten::cat'),
                    'aten_self_cpu_us': sum(o['self_cpu_us'] for o in ops if o['name'].startswith('aten::')),
                    'trace': profile['file'], 'trace_sha256': profile['sha256']}
            rows.append({'session': path.parent.parent.name, 'batch': row['batch'], 'fixture': row['fixture'],
                'median_ms': row['median_ms'],
                'dynamic_over_graph': row['median_ms']['dynamic_eager'] / row['median_ms']['static_graph'],
                'stage_medians_ms': {mode: {k: statistics.median(s[k] for s in samples)
                    for k in ('prefill_ms','decode_ms')} for mode, samples in row['stage_samples'].items()},
                'max_logit_abs_error': max(s['max_abs_error'] for check in row['logit_checks'].values() for s in check['steps']),
                'profiles': profiles})
    result = {'status': 'measured', 'inputs': inputs, 'rows': rows,
        'scope': 'Pinned GPT-2 float32 on T4; fixed batches, 16 output tokens in the default protocol; no serving-capacity claim',
        'interpretation': 'Compare dynamic/static eager to isolate cache implementation effects; compare static eager/graph to isolate captured host dispatch. Graph replay still executes GPU kernels.',
        'timing_limits': 'Stage samples have extra synchronization and are not additive components of uninstrumented wall time. Dynamic prefill stage starts after initial cache/position setup; static prefill includes validation and cache reset. ATen self time excludes runtime attribution and is not end-to-end latency.',
        'open_gates': ['dynamic admission', 'per-slot cache reclamation', 'HTTP integration', 'sustained workload envelope']}
    output = ROOT / 'analysis/graph-decode-decision.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    lines = ['# Fixed-batch graph-decode decision', '', result['scope'], '', result['interpretation'], '',
        '| Session | Batch | Fixture | Native ms | Static ms | Graph ms | Native / graph | Max logit error |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for row in rows:
        times = row['median_ms']
        lines.append(f"| {row['session']} | {row['batch']} | {row['fixture']} | {times['dynamic_eager']:.2f} | {times['static_eager']:.2f} | {times['static_graph']:.2f} | {row['dynamic_over_graph']:.2f} | {row['max_logit_abs_error']:.6g} |")
    lines += ['', result['timing_limits'], '', 'Full stage measurements and launch counts: [JSON evidence](graph-decode-decision.json).', '',
              'Open gates: ' + ', '.join(result['open_gates']) + '.', '']
    output.with_suffix('.md').write_text('\n'.join(lines))
    print(output)


if __name__ == '__main__':
    main()
