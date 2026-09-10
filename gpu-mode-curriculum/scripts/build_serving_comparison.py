#!/usr/bin/env python3
"""Generate matched-serving findings from validated raw measurements."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'batch1-decode-vertical-slice'))
from verify_serving_comparison import validate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report',type=Path)
    args=parser.parse_args()
    path=args.report.resolve()
    report=json.loads(path.read_text())
    errors=validate(report,path.parent)
    if errors:
        raise SystemExit(str(errors[:10]))
    groups=[]
    for rate in report['protocol']['rates']:
        for mode in report['protocol']['modes']:
            runs=[r for r in report['runs'] if r['offered_rate']==rate and r['mode']==mode]
            groups.append({'rate':rate,'mode':mode,
                'completed':sum(r['summary']['completed'] for r in runs),
                'rejected':sum(r['summary']['rejected'] for r in runs),
                'median_window_goodput':statistics.median(r['summary']['goodput_requests_per_s'] for r in runs),
                'median_window_output_tokens_per_s':statistics.median(r['summary']['output_tokens_per_s'] for r in runs),
                'median_of_window_completion_p95_ms':statistics.median(r['summary']['completion_p95_ms'] for r in runs),
                'median_of_window_ttft_p95_ms':statistics.median(r['summary']['ttft_p95_ms'] for r in runs),
                'accepted_by_budget':{str(b):sum(r['summary']['accepted_by_budget'][str(b)] for r in runs) for b in report['protocol']['budgets']}})
    pairs=[]
    for rate in report['protocol']['rates']:
        for index in range(3):
            modes={r['mode']:r['summary'] for r in report['runs'] if r['offered_rate']==rate and r['round_index']==index}
            pairs.append({'rate':rate,'round':index,
                'continuous_over_native_goodput':modes['graph_continuous']['goodput_requests_per_s']/modes['native_microbatch']['goodput_requests_per_s'],
                'continuous_over_graph_group_goodput':modes['graph_continuous']['goodput_requests_per_s']/modes['graph_microbatch']['goodput_requests_per_s'],
                'native_over_continuous_completion_p95':modes['native_microbatch']['completion_p95_ms']/modes['graph_continuous']['completion_p95_ms']})
    result={'status':'bounded_matched_measurement_validated','source_report':str(path.relative_to(ROOT)),
        'source_report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'runtime':report['runtime'],
        'protocol':report['protocol'],'groups':groups,'paired_rounds':pairs,'limitations':report['limitations'],
        'interpretation':'Native vs graph includes execution and prefill implementation changes. Graph group vs continuous compares grouping/admission policies using the same slot engine. Overload accepted-budget mixes are retained; no universal capacity claim.',
        'next_gate':'Independent source-bundle replay of the matched dynamic serving experiment'}
    output=ROOT/'analysis/matched-serving-decision.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Matched native/graph serving comparison','',
        'Pinned GPT-2 on T4. Identical offered prompts, output budgets, rates, slot and queue limits; three counterbalanced rounds per rate.', '',
        '| Offered requests/s | Mode | Completed | Rejected | Median window goodput | Median window completion p95 ms |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    for row in groups:
        lines.append(f"| {row['rate']} | {row['mode']} | {row['completed']} | {row['rejected']} | {row['median_window_goodput']:.2f} | {row['median_of_window_completion_p95_ms']:.2f} |")
    lines += ['', 'Latency columns are medians of three per-window p95 values, not pooled request percentiles. Goodput uses the declared latency targets and includes drain time.', '',result['interpretation'],'',
        'Graph allocations remain resident in every mode; native microbatch adds its dynamic cache. These are not isolated minimum-memory measurements.', '',
        'Independent matched-serving replay remains open. [Raw-derived JSON, budget mixes, and paired comparisons](matched-serving-decision.json).','']
    output.with_suffix('.md').write_text('\n'.join(lines))
    print(output)


if __name__=='__main__':
    main()
