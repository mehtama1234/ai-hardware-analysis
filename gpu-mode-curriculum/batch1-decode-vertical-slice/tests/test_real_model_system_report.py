import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_real_model_system import validate

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / 'gpu-runs/imports/colab-real-model-profile-corrected-gpt2-20260909/real-model-profile.json'


def test_captured_profile_validates_and_rejects_changed_tokens_and_timings():
    report = json.loads(PROFILE.read_text())
    assert validate(report) == []
    damaged = copy.deepcopy(report)
    damaged['variants']['paged']['generated_token_ids'][0][0] += 1
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['variants']['persistent']['wall_ms_median'] /= 10
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['variants']['eager']['samples'][0]['cuda_event_ms'] = float('nan')
    assert validate(damaged)


def test_http_report_rejects_output_accounting_and_tail_corruption():
    path = ROOT / 'gpu-runs/imports/colab-real-model-http-gpt2-20260909/real-model-http.json'
    report = json.loads(path.read_text())
    assert validate(report) == []
    damaged = copy.deepcopy(report)
    damaged['modes']['eager_microbatch']['requests'][0]['token_ids'][0] += 1
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['modes']['sdpa_microbatch']['completion_ms_p95'] /= 2
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['controls']['cancellation_probe']['terminal']['status'] = 'completed'
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['modes']['eager_serial']['completed_count'] -= 1
    assert validate(damaged)


def repeated_fixture():
    # Synthetic validator fixture derived from an existing report. It is never
    # written into the measurement registry or used as accelerator evidence.
    source = json.loads((ROOT / 'gpu-runs/imports/colab-real-model-http-gpt2-20260909/real-model-http.json').read_text())
    names = ('eager_serial', 'eager_microbatch', 'sdpa_microbatch', 'paged_microbatch')
    source['schema_version'] = 'real-model-http-repeated-v0.1'
    source['protocol']['round_count'] = 4
    modes = source.pop('modes')
    modes['paged_microbatch'] = copy.deepcopy(modes['eager_microbatch'])
    for name, row in modes.items():
        for batch in row['scheduler']['batches']:
            batch['peak_kv_cache_bytes'] = 128
        row['custom_attention_calls'] = 12 * 15 * len(row['scheduler']['batches']) if name == 'paged_microbatch' else 0
        row['attention_backend'] = 'sdpa' if name == 'sdpa_microbatch' else 'eager'
    source['rounds'] = [{'index': i, 'order': list(names[i:] + names[:i]), 'modes': copy.deepcopy(modes)} for i in range(4)]
    source['summary_samples'] = {name: {key: [r['modes'][name][key] for r in source['rounds']]
                                         for key in ('completion_ms_p95', 'ttft_ms_median', 'output_tokens_per_second')}
                                for name in names}
    return source


def test_repeated_report_requires_counterbalancing_custom_execution_and_kv_evidence():
    report = repeated_fixture()
    assert validate(report) == []
    damaged = copy.deepcopy(report)
    damaged['rounds'][1]['order'] = damaged['rounds'][0]['order']
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['rounds'][0]['modes']['paged_microbatch']['custom_attention_calls'] = 0
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['rounds'][0]['modes']['paged_microbatch']['scheduler']['batches'][0]['peak_kv_cache_bytes'] = 0
    assert validate(damaged)
    damaged = copy.deepcopy(report)
    damaged['summary_samples']['paged_microbatch']['completion_ms_p95'][0] /= 2
    assert validate(damaged)
