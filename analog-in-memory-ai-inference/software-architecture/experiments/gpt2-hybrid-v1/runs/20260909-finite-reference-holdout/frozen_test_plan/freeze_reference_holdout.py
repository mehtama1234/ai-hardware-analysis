#!/usr/bin/env python3
"""Freeze finite-reference quality testing after excluding 64 scored contexts."""
import argparse
import json
from pathlib import Path
import shutil

import pyarrow.parquet as pq
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

from check_gpt2_reference_validation import check as check_validation
from freeze_adc_range_holdout import select_disjoint_windows
from run_gpt2_hybrid_evaluation import digest


def check_plan(root):
    read = lambda name: json.loads((root / name).read_text())
    for name, expected in read('manifest.json').items():
        assert digest(root / name) == expected
    plan = read('plan.json')
    assert plan['schema_version'] == 'finite_reference_holdout_plan.v1'
    for source in plan['sources'].values():
        assert digest(source['path']) == source['sha256']
    ids = read('test_tokens.json')
    excluded = plan['excluded_previous_test_windows']
    first = json.loads(Path(plan['sources']['first_test_protocol']['path']).read_text())
    second = json.loads(Path(plan['sources']['second_test_plan']['path']).read_text())
    assert excluded == first['test']['windows'] + second['windows'] and len(excluded) == 64
    starts = select_disjoint_windows(len(ids), excluded, 32, 128)
    assert plan['windows'] == [dict(start=s, ids=ids[s:s+129]) for s in starts]
    for window in excluded:
        assert ids[window['start']:window['start']+len(window['ids'])] == window['ids']
    validation = json.loads(Path(plan['sources']['validation_result']['path']).read_text())
    assert validation['evaluation_split'] == 'validation'
    candidate = validation['variants']['finite_reference_adc12']
    assert candidate['screen_pass'] and plan['selected_contract'] == candidate['contract']
    assert plan['binding_sha256'] == digest(Path(plan['sources']['validation_result']['path']).parent / 'binding.json')
    print('Verified frozen finite-reference contract and 32 contexts disjoint from all 64 previously scored contexts')
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('validation', 'first-test', 'second-test-plan', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    check_validation(args.validation)
    for root in (args.first_test, args.second_test_plan):
        for name, expected in json.loads((root / 'manifest.json').read_text()).items():
            assert digest(root / name) == expected
    result = json.loads((args.validation / 'result.json').read_text())
    protocol = json.loads((args.validation / 'protocol.json').read_text())
    first = json.loads((args.first_test / 'protocol.json').read_text())
    second = json.loads((args.second_test_plan / 'plan.json').read_text())
    assert first['evaluation_split'] == 'test'
    assert first['revision'] == second['dataset_revision'] == protocol['dataset_revision']
    assert first['model_revision'] == second['model_revision'] == protocol['model_revision']
    assert result['variants']['finite_reference_adc12']['screen_pass']
    snapshot = snapshot_download('openai-community/gpt2', revision=protocol['model_revision'], local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    data = args.first_test / 'test.parquet'
    ids = tokenizer.encode('\n'.join(pq.read_table(data)['text'].to_pylist()), add_special_tokens=False, verbose=False)
    assert len(ids) == first['test']['total_tokens']
    excluded = first['test']['windows'] + second['windows']
    assert len(excluded) == 64
    for window in excluded:
        assert ids[window['start']:window['start']+len(window['ids'])] == window['ids']
    starts = select_disjoint_windows(len(ids), excluded, 32, 128)
    plan = dict(schema_version='finite_reference_holdout_plan.v1', status='frozen_before_test_inference',
                selected_contract=result['variants']['finite_reference_adc12']['contract'],
                binding_sha256=protocol['binding_sha256'], model_revision=protocol['model_revision'],
                dataset_revision=protocol['dataset_revision'], screen=protocol['screen'], numerical_control=protocol['numerical_control'],
                windows=[dict(start=s, ids=ids[s:s+129]) for s in starts], excluded_previous_test_windows=excluded,
                claim_boundary='Previously unscored token contexts, not necessarily unseen articles; static noiseless numerical profile only',
                sources={name: dict(path=str(path.resolve()), sha256=digest(path)) for name, path in {
                    'validation_result': args.validation / 'result.json', 'validation_manifest': args.validation / 'manifest.json',
                    'first_test_protocol': args.first_test / 'protocol.json', 'second_test_plan': args.second_test_plan / 'plan.json',
                    'test_data': data}.items()})
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    (args.output / 'test_tokens.json').write_text(json.dumps(ids) + '\n')
    shutil.copyfile(__file__, args.output / Path(__file__).name)
    (args.output / 'manifest.json').write_text(json.dumps({p.name: digest(p) for p in args.output.iterdir()}, indent=2) + '\n')
    check_plan(args.output)


if __name__ == '__main__':
    main()
