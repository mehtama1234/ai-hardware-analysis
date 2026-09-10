#!/usr/bin/env python3
"""Audit the six gates of this bounded real-model vertical slice."""
import hashlib
import json
from pathlib import Path

from verify_real_model_system import validate

ROOT = Path(__file__).resolve().parents[1]
SLICE = Path(__file__).resolve().parent


def main():
    gates = []
    def gate(name, checks, evidence):
        gates.append({'gate': name, 'status': 'passed' if all(checks.values()) else 'incomplete',
                      'checks': checks, 'evidence': evidence})
    decision_path = ROOT / 'analysis/real-model-inference-decision.json'
    decision = json.loads(decision_path.read_text())
    reports, errors = {}, {}
    for name, item in decision['inputs'].items():
        path = ROOT / item['path']
        content = path.read_bytes()
        report = json.loads(content)
        reports[name] = report
        errors[name] = [] if hashlib.sha256(content).hexdigest() == item['sha256'] else ['decision input hash mismatch']
        if name != 'reproduction':
            errors[name].extend(validate(report, path.parent))
    tests_path = SLICE / 'reports/real-model-local-validation.json'
    tests = json.loads(tests_path.read_text()) if tests_path.exists() else {}
    tests_current = bool(tests.get('source_hashes')) and all((SLICE / name).is_file() and hashlib.sha256((SLICE / name).read_bytes()).hexdigest() == expected for name, expected in tests.get('source_hashes', {}).items())
    profile = reports.get('optimized_profile', {})
    repeated = reports.get('http_repeated', {})
    replay = reports.get('http_replay', {})
    proof = reports.get('reproduction', {})
    gate('1_trusted_model_baseline', {
        'profile_valid': bool(profile) and not errors.get('optimized_profile'),
        'local_tests_passed_and_current': tests.get('status') == 'passed' and tests.get('returncode') == 0 and tests_current,
        'batch_individual_library_parity': profile.get('batch_vs_individual_output_parity') is True,
        'model_and_tokenizer_pinned': bool(repeated.get('model_revision')) and repeated.get('tokenizer_revision') == repeated.get('model_revision'),
        'dtype_recorded': bool(repeated.get('dtype')),
    }, ['optimized_profile', 'http_repeated'])
    gate('2_fair_candidate_comparison', {
        'repeated_http_valid': bool(repeated) and not errors.get('http_repeated'),
        'all_four_profile_candidates': set(profile.get('variants', {})) == {'eager', 'sdpa', 'paged', 'persistent'},
        'native_custom_outputs_timing_kv_and_dispatch_validated': bool(repeated) and not errors.get('http_repeated'),
    }, ['http_repeated', 'optimized_profile'])
    original = reports.get('profile', {}).get('variants', {})
    optimized = profile.get('variants', {})
    original_ops = {r['name']: r for r in original.get('paged', {}).get('profile', {}).get('operators', [])}
    optimized_ops = {r['name']: r for r in optimized.get('paged', {}).get('profile', {}).get('operators', [])}
    gate('3_bottleneck_explanation', {
        'raw_profiles_verified': bool(original) and not errors.get('profile') and not errors.get('optimized_profile'),
        'mask_scans_removed': original_ops.get('aten::nonzero', {}).get('count', 0) > 0 and optimized_ops.get('aten::nonzero', {}).get('count', 0) == 0,
        'projection_cache_allocation_and_launch_evidence': all(name in original_ops for name in ('aten::addmm', 'aten::mm', 'aten::cat', 'aten::empty', 'cudaLaunchKernel')),
    }, ['profile', 'optimized_profile'])
    rounds = repeated.get('rounds', []) + replay.get('rounds', [])
    gate('4_application_boundary', {
        'two_valid_measured_http_sessions': bool(repeated) and bool(replay) and not errors.get('http_repeated') and not errors.get('http_replay'),
        'native_batching_beats_serial_each_round': bool(rounds) and all(r['modes']['eager_microbatch']['completion_ms_p95'] < r['modes']['eager_serial']['completion_ms_p95'] for r in rounds),
        'selected_endpoint_implemented': (SLICE / 'serve_real_model.py').is_file() and decision.get('selected_path', {}).get('mode') == 'eager_microbatch',
    }, ['http_repeated', 'http_replay'])
    session_paths = [ROOT / 'gpu-runs/imports' / name / 'colab-session.txt' for name in ('colab-real-model-http-repeated-gpt2-20260909', 'colab-real-model-http-replay-gpt2-20260909')]
    sessions = [path.read_text().strip() if path.exists() else '' for path in session_paths]
    gate('5_reproduction_and_decision', {
        'reproduction_passed': proof.get('status') == 'passed' and proof.get('errors') == [],
        'all_input_hashes_and_reports_valid': all(not error for error in errors.values()),
        'reproduction_report_hashes_match': proof.get('original_report_sha256') == decision['inputs'].get('http_repeated', {}).get('sha256') and proof.get('replayed_report_sha256') == decision['inputs'].get('http_replay', {}).get('sha256'),
        'dependency_versions_match': bool(proof.get('dependency_checks')) and all(v['installed'] == v['recorded'] and v['recorded'] for v in proof.get('dependency_checks', {}).values()),
        'same_reference_and_source': bool(replay) and repeated.get('source_hashes') == replay.get('source_hashes') and repeated.get('reference_token_ids') == replay.get('reference_token_ids'),
        'separate_provider_sessions_observed': all(sessions) and len({s.split('] ', 1)[-1].split(' |')[0] for s in sessions}) == 2,
        'decision_and_limits_present': bool(decision.get('decision')) and bool(decision.get('limitations')),
    }, ['http_repeated', 'http_replay', 'reproduction', *[str(p.relative_to(ROOT)) for p in session_paths]])
    workbench = json.loads((ROOT / 'analysis/gpu-systems-workbench.json').read_text())
    selected = [p for p in workbench['profiles'] if p['id'] in ('attention-serving', 'serving-scheduler', 'profiling-roofline')]
    page_path = ROOT / 'site/real-model-inference-decision.html'
    page = page_path.read_text()
    gate('6_teaching_workbench_integration', {
        'three_profiles_recommend_evidence': len(selected) == 3 and all(p['latest_measurements'][0]['session'] == 'real-model-inference-decision' for p in selected),
        'workbench_summary_and_action_current': all(p['latest_measurements'][0]['summary'] == decision['summary'] and p['next_action'] == decision['next_action'] for p in selected),
        'reference_lessons_paper_and_reproduction_linked': all(x in page for x in ('run_real_model_paged_attention_kernel.py', 'lesson-107.html', 'lesson-118.html', 'asplos-2025-049.json', 'Source-bundle reproduction')),
        'decision_page_in_workbench': 'real-model-inference-decision.html' in (ROOT / 'site/workbench.html').read_text(),
    }, ['analysis/gpu-systems-workbench.json', 'site/real-model-inference-decision.html'])
    result = {'schema_version': 'real-model-goal-audit-v0.1', 'scope': 'Six gates of batch1-decode-vertical-slice/END-TO-END-GOAL.md; not the full advanced curriculum',
              'status': 'passed' if all(g['status'] == 'passed' for g in gates) else 'incomplete', 'gates': gates,
              'input_validation_errors': errors, 'decision_sha256': hashlib.sha256(decision_path.read_bytes()).hexdigest(),
              'workbench_sha256': hashlib.sha256((ROOT / 'analysis/gpu-systems-workbench.json').read_bytes()).hexdigest(),
              'goal_sha256': hashlib.sha256((SLICE / 'END-TO-END-GOAL.md').read_bytes()).hexdigest(),
              'local_validation_sha256': hashlib.sha256(tests_path.read_bytes()).hexdigest() if tests_path.exists() else None,
              'page_sha256': hashlib.sha256(page_path.read_bytes()).hexdigest(),
              'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT / 'analysis/real-model-goal-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'gates': {g['gate']: g['status'] for g in gates}}, indent=2))
    return int(result['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
