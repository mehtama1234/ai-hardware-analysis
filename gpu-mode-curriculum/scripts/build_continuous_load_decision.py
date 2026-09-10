#!/usr/bin/env python3
"""Publish bounded arrival-load measurements from a validated raw report."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'batch1-decode-vertical-slice'))
from verify_continuous_load import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    path = args.report.resolve()
    report = json.loads(path.read_text())
    errors = validate(report, path.parent)
    if errors:
        raise SystemExit(str(errors))
    result = {'status': 'bounded_measurement_validated', 'source_report': str(path.relative_to(ROOT)),
        'source_report_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'runtime': report['runtime'], 'protocol': report['protocol'], 'eos_probe_passed': report['eos_probe']['passed'],
        'runs': [{'run': r['round'], 'offered_rate': r['offered_rate'], **r['summary']} for r in report['runs']],
        'limitations': report['limitations'], 'next_gates': ['Matched native microbatch baseline comparison',
            'Exact-source replay of mixed-length dynamic serving', 'Longer workloads and broader model coverage']}
    destination = ROOT / 'analysis/continuous-load-decision.json'
    destination.write_text(json.dumps(result, indent=2) + '\n')
    lines = ['# Mixed-length continuous HTTP arrival measurements', '',
        'Pinned GPT-2 on T4, two slots, eight pending requests, output budgets 1/8/16/32.',
        'Two rounds of eight-second arrival windows. These are bounded loopback measurements.', '',
        '| Run | Offered requests/s | Completed | Rejected | TTFT p95 ms | Completion p95 ms | Goodput requests/s | Arrival lateness p95 ms |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in result['runs']:
        lines.append(f"| {row['run']} | {row['offered_rate']} | {row['completed']} | {row['rejected']} | {row['ttft_p95_ms']:.2f} | {row['completion_p95_ms']:.2f} | {row['goodput_requests_per_s']:.2f} | {row['arrival_lateness_p95_ms']:.2f} |")
    lines += ['', 'Goodput counts correct requests with TTFT <=1,000 ms, completion <=3,000 ms, and maximum inter-token gap <=500 ms. Its denominator includes drain time.', '',
        'Accepted requests match individual reference tokens; rejected requests and server records reconcile. Controlled HTTP EOS termination passes.', '',
        'No matched-baseline advantage or independent dynamic-engine replay is established here. Prefill remains synchronous and unchunked.', '',
        '[Machine-readable decision](continuous-load-decision.json) · [Run instructions](../batch1-decode-vertical-slice/SLOT-DECODE.md)', '']
    destination.with_suffix('.md').write_text('\n'.join(lines))
    print(destination)


if __name__ == '__main__':
    main()
