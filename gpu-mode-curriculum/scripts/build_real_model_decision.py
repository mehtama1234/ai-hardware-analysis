#!/usr/bin/env python3
"""Publish verified real-model measurements and their bounded engineering decision."""
from __future__ import annotations
import hashlib
import html
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLICE = ROOT / 'batch1-decode-vertical-slice'
sys.path.insert(0, str(SLICE))
from verify_real_model_system import validate

RUNS = {
    'profile': 'colab-real-model-profile-corrected-gpt2-20260909/real-model-profile.json',
    'http': 'colab-real-model-http-gpt2-20260909/real-model-http.json',
}
OPTIMIZED = 'colab-real-model-profile-offsets-gpt2-20260909/real-model-profile.json'


def main():
    inputs, reports = {}, {}
    paths = dict(RUNS)
    if (ROOT / 'gpu-runs/imports' / OPTIMIZED).is_file():
        paths['optimized_profile'] = OPTIMIZED
    for name, relative in {
        'http_repeated': 'colab-real-model-http-repeated-gpt2-20260909/real-model-http-repeated.json',
        'http_replay': 'colab-real-model-http-replay-gpt2-20260909/real-model-http-repeated.json',
    }.items():
        if (ROOT / 'gpu-runs/imports' / relative).is_file():
            paths[name] = relative
    for name, relative in paths.items():
        path = ROOT / 'gpu-runs/imports' / relative
        report = json.loads(path.read_text())
        errors = validate(report, path.parent)
        if errors:
            raise ValueError(f'{path}: {errors}')
        inputs[name] = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        reports[name] = report
    initial, serving = reports['profile'], reports['http']
    findings = []
    for name, row in initial['variants'].items():
        ops = {op['name']: op for op in row['profile']['operators']}
        findings.append({'variant': name, 'wall_ms_median': row['wall_ms_median'],
                         'latency_over_eager_ratio': row['latency_over_eager_ratio'],
                         'nonzero_calls': ops.get('aten::nonzero', {}).get('count', 0),
                         'stream_synchronizations': ops.get('cudaStreamSynchronize', {}).get('count', 0)})
    http_rows = [{'mode': name, **{key: row[key] for key in ('completed_count', 'ttft_ms_median', 'completion_ms_p95', 'output_tokens_per_second')}}
                 for name, row in serving['modes'].items()]
    optimized = []
    if 'optimized_profile' in reports:
        for name, row in reports['optimized_profile']['variants'].items():
            ops = {op['name']: op for op in row['profile']['operators']}
            optimized.append({'variant': name, 'wall_ms_median': row['wall_ms_median'],
                              'latency_over_eager_ratio': row['latency_over_eager_ratio'],
                              'nonzero_calls': ops.get('aten::nonzero', {}).get('count', 0),
                              'stream_synchronizations': ops.get('cudaStreamSynchronize', {}).get('count', 0)})
    attribution = []
    if 'optimized_profile' in reports:
        for name in ('eager', 'paged'):
            prof = reports['optimized_profile']['variants'][name]['profile']
            for category, values in prof['categories'].items():
                attribution.append({'variant': name, 'category': category, 'self_cpu_ms': values['self_cpu_us'] / 1000, 'self_device_ms': values['self_device_us'] / 1000})
            operators = {op['name']: op for op in prof['operators']}
            for operation in ('cudaLaunchKernel', 'cudaStreamSynchronize'):
                values = operators.get(operation, {})
                attribution.append({'variant': name, 'category': operation, 'self_cpu_ms': values.get('self_cpu_us', 0) / 1000, 'self_device_ms': values.get('self_device_us', 0) / 1000})
    repeated_rows = []
    for label in ('http_repeated', 'http_replay'):
        if label not in reports:
            continue
        for name, samples in reports[label]['summary_samples'].items():
            eager = reports[label]['summary_samples']['eager_microbatch']['completion_ms_p95']
            values = samples['completion_ms_p95']
            repeated_rows.append({'run': label, 'mode': name, 'rounds': len(values),
                                  'round_p95_min_ms': min(values), 'round_p95_median_ms': statistics.median(values),
                                  'round_p95_max_ms': max(values),
                                  'rounds_faster_than_eager_microbatch': sum(a < b for a, b in zip(values, eager))})
    reproduction = None
    if 'http_replay' in reports:
        path = ROOT / inputs['http_replay']['path']
        proof_path = path.with_name('real-model-reproduction.json')
        reproduction = json.loads(proof_path.read_text())
        if reports['http_replay']['runtime'] != reports['http_repeated']['runtime']:
            raise ValueError('Replayed execution runtime differs from the original')
        if reproduction['status'] != 'passed' or reproduction['errors']:
            raise ValueError('Independent replay failed')
        if reproduction['original_report_sha256'] != inputs['http_repeated']['sha256'] or reproduction['replayed_report_sha256'] != inputs['http_replay']['sha256']:
            raise ValueError('Independent replay report hash mismatch')
        if not reproduction['dependency_checks'] or any(d['recorded'] != d['installed'] or not d['recorded'] for d in reproduction['dependency_checks'].values()):
            raise ValueError('Independent replay dependency mismatch')
        inputs['reproduction'] = {'path': str(proof_path.relative_to(ROOT)), 'sha256': hashlib.sha256(proof_path.read_bytes()).hexdigest()}
    summary = 'Real GPT-2/T4 HTTP microbatching preserves exact outputs and reduces recorded completion tails; custom paged wrappers incur additional mask-scan synchronization in the initial profile.'
    data = {'schema_version': 'real-model-inference-decision-v0.1', 'status': 'passed', 'correctness': 'passed',
            'evidence_kind': 'measured_gpu', 'summary': summary, 'inputs': inputs,
            'profile': findings, 'http': http_rows, 'optimized_profile': optimized,
            'repeated_http': repeated_rows, 'reproduction': reproduction, 'operator_attribution': attribution,
            'decision': 'Bounded HTTP batching improvement established. General backend superiority and production capacity remain unproven.',
            'next_action': 'Compare the optimized custom path through the same HTTP workload, repeat/interleave modes, and package an independently rerunnable dependency closure.',
            'limitations': ['16 HTTP requests per mode; p95 is a small-sample observation.',
                           'Fixed-order mode blocks can contain clock/load drift; profiling is captured separately from timing.',
                           'Custom direct-generation and HTTP protocols use different prompts/token counts; do not compare their absolute latencies.',
                           'Cancellation stops token delivery at boundaries; mixed-batch GPU slots persist until batch completion.',
                           'Profiler category totals in the initial raw report include overlapping event types; use individual operator counts and raw traces, not summed GPU categories.',
                           'No production language-quality, multi-GPU, portability, or analog hardware acceptance.']}
    if repeated_rows:
        data['selected_path'] = {'mode': 'eager_microbatch', 'max_batch': 4, 'max_pending': 32, 'window_ms': 5, 'max_tokens': 16, 'reason': 'Native eager batching improves every recorded round versus serial eager; a custom-kernel or universal backend advantage is not established.'}
        data['summary'] = 'Counterbalanced real GPT-2/T4 HTTP runs preserve outputs and establish a batching benefit; optimized paged attention does not consistently beat equally batched native attention.'
        data['next_action'] = 'Complete independent replay and the final evidence audit.' if reproduction is None else 'Run the selected native microbatch endpoint, or extend the measured workload with longer generations and sustained arrivals before generalizing the result.'
        data['limitations'][0] = 'Each mode has four 16-request rounds per session; round p95 remains a small-sample tail statistic.'
        data['limitations'][1] = 'Repeated HTTP mode order is counterbalanced; earlier direct profiles used fixed-order blocks and separate instrumented captures.'
    summary = data['summary']
    target = ROOT / 'analysis/real-model-inference-decision.json'
    target.write_text(json.dumps(data, indent=2) + '\n')
    e = html.escape
    def table(rows):
        if not rows:
            return '<p>Awaiting measured evidence.</p>'
        keys = list(rows[0])
        labels = {'wall_ms_median': 'Median generation (ms)', 'latency_over_eager_ratio': 'Latency / eager', 'nonzero_calls': 'Mask scans', 'stream_synchronizations': 'Stream synchronizations', 'completed_count': 'Completed requests', 'ttft_ms_median': 'Median TTFT (ms)', 'completion_ms_p95': 'Completion p95 (ms)', 'output_tokens_per_second': 'Output tokens/s', 'round_p95_min_ms': 'Best round p95 (ms)', 'round_p95_median_ms': 'Median round p95 (ms)', 'round_p95_max_ms': 'Worst round p95 (ms)', 'rounds_faster_than_eager_microbatch': 'Rounds beating eager batches'}
        return '<table><thead><tr>' + ''.join(f'<th>{e(labels.get(k, k.replace("_", " ")))}</th>' for k in keys) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{e(str(round(row[k], 3) if isinstance(row[k], float) else row[k]))}</td>' for k in keys) + '</tr>' for row in rows) + '</tbody></table>'
    links = ''.join(f'<li><a href="../{e(item["path"])}">{e(name)} raw report</a> — SHA-256 <code>{item["sha256"]}</code></li>' for name, item in inputs.items())
    repeated_section = '<h2>Counterbalanced HTTP comparisons</h2><p>Each mode occupies each position once. These are distributions of per-round p95 values, not a pooled p95. Kernel-call and actual KV-byte checks are required in every round.</p>' + table(repeated_rows)
    replay_section = '<h2>Source-bundle reproduction</h2><p>' + (f'Passed in a fresh Colab session from a checksum-verified temporary source tree, with {len(reproduction["dependency_checks"])} required dependency versions checked and identical reference outputs.' if reproduction else 'Fresh-session replay is pending.') + '</p>'
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Real-model inference decision</title>
<style>body{{font:17px/1.6 system-ui;max-width:1150px;margin:40px auto;padding:0 22px;color:#182b3a}}table{{border-collapse:collapse;display:block;overflow:auto}}th,td{{border:1px solid #b8c5ce;padding:9px;text-align:left}}th{{background:#eaf2f8}}code{{overflow-wrap:anywhere}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}a{{color:#075b9a}}</style>
<a href="workbench.html">GPU systems workbench</a><h1>Real-model inference: from correctness to serving evidence</h1><p>{e(summary)}</p>
<h2>Reference and correctness</h2><p>The workload uses revision-pinned pretrained GPT-2 and its tokenizer. Greedy library generation is the reference. Cached decoding supplies positions derived from the attention mask so left padding cannot shift a request's positions. Every timed candidate must preserve the reference token IDs, including when prompts share a batch.</p>
<h2>What the original profile explains</h2>{table(findings)}<p>For 31 one-token decode steps, 12 attention layers and four requests, the wrapper performs 31 × 12 × 4 = 1,488 per-request mask scans. The observed nonzero calls and stream synchronizations support a host/device coordination bottleneck in this wrapper. This does not imply that paged attention inherently requires those synchronizations.</p>
<h2>Targeted change and remeasurement</h2><p>The next implementation replaces per-request nonzero scans with a vectorized GPU argmax over allowed mask entries. Correctness checks include mixed-length, unpadded and fully masked offset cases.</p>{table(optimized)}
<h2>Operator attribution in the corrected profile</h2><p>ATen self-time groups distinguish matrix multiplication, attention, movement, allocation, and coordination. Launch and stream-wait runtime rows are shown separately. These are instrumented profile attributions, not additive components of the uninstrumented end-to-end wall time.</p>{table(attribution)}<h2>Actual HTTP serving</h2>{table(http_rows)}<p>Requests arrive over loopback HTTP and receive token events while the GPU worker executes. TTFT is measured at the client on its first received token. Completion tails include queuing and transport. The overload probe rejected {serving['controls']['rejected_count']} requests, and explicit in-flight cancellation stopped delivery before the requested token count.</p>
{repeated_section}{replay_section}<h2>Reproduce and inspect</h2><ul>{links}</ul><pre>python3 batch1-decode-vertical-slice/verify_real_model_system.py gpu-runs/imports/{RUNS['http']}
COLAB_HANDOFF_MODE=real-model-profile COLAB_RUN_ID=&lt;new-run-id&gt; COLAB_SESSION_NAME=&lt;new-session&gt; bash scripts/run_colab_gpu_handoff_local.sh
COLAB_HANDOFF_MODE=real-model-http COLAB_RUN_ID=&lt;new-run-id&gt; COLAB_SESSION_NAME=&lt;new-session&gt; bash scripts/run_colab_gpu_handoff_local.sh</pre>
<h2>Run the selected endpoint</h2><pre>python3 batch1-decode-vertical-slice/serve_real_model.py --backend eager
curl -N http://127.0.0.1:8088/stream -H 'Content-Type: application/json' -d '{{"request_id":"example-1","prompt":"The system bottleneck is"}}'</pre><p>The bounded default uses batches of up to four, a 5 ms window, a queue limit of 32 and 16 output tokens. Cancel by posting the request ID to <code>/cancel</code>. Custom paging remains an experimental option.</p><h2>Learning path</h2><ol><li><a href="lesson-107.html">FlashAttention lecture</a>: connect the attention reference to the <a href="../batch1-decode-vertical-slice/run_real_model_paged_attention_kernel.py">paged-attention correctness harness</a>.</li><li><a href="lesson-118.html">Profiling CUDA kernels</a>: explain why launch and synchronization overhead can outweigh arithmetic improvements.</li><li><a href="lesson-058.html">Kernel benchmarking tales</a>: compare equal workloads and retain losing candidates.</li><li><a href="lesson-056.html">Disaggregated LLM inference</a>: connect kernel measurements to queues, TTFT and completion tails.</li></ol>
<p>Related paper: <a href="../../analysis/per-paper/asplos-2025-049.json">Past-Future Scheduler for LLM Serving under SLA Guarantees</a>. Use its corpus record to extend the exercise from bounded request batching to memory-aware serving; this experiment does not reproduce that paper.</p><h2>Decision and remaining work</h2><p>{e(data['decision'])}</p><p>{e(data['next_action'])}</p><ul>{''.join(f'<li>{e(text)}</li>' for text in data['limitations'])}</ul></html>'''
    (ROOT / 'site/real-model-inference-decision.html').write_text(page)
    print(json.dumps({'status': 'passed', 'decision': str(target), 'verified_inputs': list(inputs)}))


if __name__ == '__main__':
    main()
