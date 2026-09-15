#!/usr/bin/env python3
"""Evaluate frozen nominal references on validation or a separately frozen holdout."""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import shutil
import sys

import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM

from calibrated_adc_projection import CalibratedADCProjection
from tiled_projection_model import Profile, TiledProjection
from projection_numerical_control import CONTRACT, assess
from run_gpt2_hybrid_evaluation import digest, replace_forward


def verify(root):
    for name, expected in json.loads((root / 'manifest.json').read_text()).items():
        if digest(root / name) != expected:
            raise ValueError(f'Changed input: {root / name}')


def apply_reference_binding(projection, binding):
    original = projection.contract()
    if len(projection.tiles) != len(binding['tiles']):
        raise ValueError('Incomplete reference map')
    adjusted = []
    ranges = deepcopy(projection.range_calibration)
    for index, ((r, c, qw, bound), row) in enumerate(zip(projection.tiles, binding['tiles'])):
        if (row['tile_id'], row['row'], row['column'], row['frozen_bound_model_units']) != (index, r, c, bound):
            raise ValueError('Reference map does not match frozen calibration')
        target, actual = row['target_reference_fraction'], row['simulated_reference_fraction']
        effective = row['effective_bound_model_units']
        if not all(math.isfinite(x) and x > 0 for x in (target, actual, effective)):
            raise ValueError('Invalid reference scale')
        if not math.isclose(effective, bound * actual / target, rel_tol=1e-14):
            raise ValueError('Inconsistent effective scale')
        adjusted.append((r, c, qw, effective))
        ranges['ranges'][index]['selected_bound'] = effective
        ranges['ranges'][index]['range_reduction_factor'] = ranges['ranges'][index]['conservative_bound'] / effective
    ranges['method'] = 'Frozen nominal reference DAC curve applied to original training-derived ranges'
    ranges['original_training_contract'] = original
    ranges['reference_binding'] = deepcopy(binding)
    projection.tiles = adjusted
    projection.range_calibration = ranges


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'validation', 'binding', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--test-plan', type=Path)
    args = parser.parse_args()
    for root in (args.plan, args.validation, args.binding):
        verify(root)
    plan = json.loads((args.plan / 'plan.json').read_text())
    validation = json.loads((args.validation / 'protocol.json').read_text())
    binding = json.loads((args.binding / 'binding.json').read_text())
    if validation['evaluation_split'] != 'validation' or validation['numerical_control'] != CONTRACT:
        raise ValueError('Validation split and numerical controls required')
    if validation['model_revision'] != plan['model_revision'] or validation['revision'] != plan['dataset_revision']:
        raise ValueError('Model or dataset mismatch')
    for source in binding['sources'].values():
        if digest(source['path']) != source['sha256']:
            raise ValueError('Binding source changed')
    contract = plan['selected_contract']
    protocol = dict(schema_version='circuit_reference_validation.v1', evaluation_split='validation',
                    scope='Development evaluation of nominal static reference discretization only',
                    windows=validation['validation']['windows'], screen=plan['screen'], numerical_control=CONTRACT,
                    model_revision=plan['model_revision'], dataset_revision=plan['dataset_revision'], seed=plan['seed'],
                    binding_sha256=digest(args.binding / 'binding.json'), physical_profile_qualified=False,
                    claim_boundary='No test-set qualification, physical noise, dynamic settling or hardware inference benefit')
    test_plan = None
    if args.test_plan:
        from freeze_reference_holdout import check_plan
        test_plan = check_plan(args.test_plan)
        for key in ('binding_sha256', 'model_revision', 'dataset_revision', 'screen', 'numerical_control'):
            if test_plan[key] != protocol[key]:
                raise ValueError('Holdout plan mismatch: ' + key)
        protocol.update(schema_version='circuit_reference_disjoint_holdout.v1', evaluation_split='test',
                        scope='Frozen finite-reference profile on separately selected disjoint test contexts',
                        windows=test_plan['windows'], claim_boundary=test_plan['claim_boundary'],
                        test_plan_sha256=digest(args.test_plan / 'plan.json'))
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    inputs = {label: dict(path=str(root.resolve()), manifest=json.loads((root / 'manifest.json').read_text()))
              for label, root in [('training_plan', args.plan), ('validation', args.validation), ('binding', args.binding)]}
    if args.test_plan:
        shutil.copytree(args.test_plan, args.output / 'frozen_test_plan')
        inputs['test_plan'] = dict(path=str(args.test_plan.resolve()), manifest=json.loads((args.test_plan / 'manifest.json').read_text()))
    (args.output / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    for name, path in {'binding.json': args.binding / 'binding.json', 'training_plan.json': args.plan / 'plan.json',
                       'validation_source.json': args.validation / 'protocol.json'}.items():
        shutil.copyfile(path, args.output / name)
    source_dir = args.output / 'source_snapshot'; source_dir.mkdir()
    for name in (Path(__file__).name, 'calibrated_adc_projection.py', 'tiled_projection_model.py',
                 'projection_numerical_control.py', 'run_gpt2_hybrid_evaluation.py'):
        shutil.copyfile(Path(__file__).with_name(name), source_dir / name)
    torch.set_num_threads(2); torch.manual_seed(plan['seed'])
    snapshot = Path(snapshot_download('openai-community/gpt2', revision=plan['model_revision'], local_files_only=True))
    for name, expected in plan['model_files'].items():
        if digest(snapshot / name) != expected:
            raise ValueError('Model file changed')
    print('Loading GPT-2 and reproducing training calibration', flush=True)
    model = AutoModelForCausalLM.from_pretrained(snapshot, local_files_only=True, attn_implementation='eager').eval()
    module = model.get_submodule('transformer.h.0.mlp.c_fc')
    calibration = torch.load(args.plan / 'calibration_inputs.pt', weights_only=True, map_location='cpu')
    def calibrated():
        obj = CalibratedADCProjection(module.weight, module.bias, contract['calibrated_activation_abs_max'],
              Profile(**contract['profile']), calibration, seed=plan['seed'], headroom=contract['adc_range']['headroom'])
        if obj.contract() != contract:
            raise ValueError('Training calibration does not reproduce frozen contract')
        return obj
    frozen, finite = calibrated(), calibrated()
    apply_reference_binding(finite, binding)
    if test_plan and finite.contract() != test_plan['selected_contract']:
        raise ValueError('Finite reference contract differs from frozen holdout profile')
    ideal = TiledProjection(module.weight, module.bias, contract['calibrated_activation_abs_max'], Profile(), plan['seed'])
    candidates = [('ideal', ideal), ('frozen_adc12', frozen), ('finite_reference_adc12', finite)]
    before = {name: obj.contract() for name, obj in candidates}
    del calibration
    rows, fallback = [], []
    with torch.inference_mode(), (args.output / 'rows.jsonl').open('w') as stream:
        for index, window in enumerate(protocol['windows']):
            tokens = torch.tensor([window['ids']]); target = tokens[:, 1:].reshape(-1)
            captured = []
            hook = module.register_forward_hook(lambda _m, _i, value: captured.append(value.clone()))
            try: baseline = model(tokens, use_cache=False).logits[:, :-1].float()
            finally: hook.remove()
            loss = lambda logits: float(torch.nn.functional.cross_entropy(logits.reshape(-1, logits.shape[-1]), target, reduction='sum'))
            baseline_nll = loss(baseline)
            for name, obj in candidates:
                outputs = []
                def forward(x):
                    value = obj(x, ideal=name == 'ideal')
                    if name == 'ideal': outputs.append(value.clone())
                    return value
                with replace_forward(module, forward):
                    logits = model(tokens, use_cache=False).logits[:, :-1].float()
                row = dict(window=index, start=window['start'], variant=name, tokens=target.numel(),
                           baseline_nll_sum=baseline_nll, candidate_nll_sum=loss(logits),
                           argmax_matches=int((baseline.argmax(-1) == logits.argmax(-1)).sum()))
                if name == 'ideal': row['numerical_control'] = assess(captured[0], outputs[0], baseline, logits, target)
                rows.append(row); stream.write(json.dumps(row) + '\n'); stream.flush()
            exact = torch.equal(model(tokens, use_cache=False).logits[:, :-1].float(), baseline)
            fallback.append(dict(window=index, exact=exact))
            if not exact: raise RuntimeError('Digital fallback changed')
            print(f'Completed {protocol["evaluation_split"]} context {index+1}/{len(protocol["windows"])}', flush=True)
    if not all(r['numerical_control']['pass'] for r in rows if r['variant'] == 'ideal'):
        raise RuntimeError('Ideal numerical control failed')
    summaries = {}
    for name, obj in candidates:
        if obj.contract() != before[name]: raise RuntimeError('Evaluation changed ranges')
        subset = [r for r in rows if r['variant'] == name]; count = sum(r['tokens'] for r in subset)
        delta = sum(r['candidate_nll_sum'] - r['baseline_nll_sum'] for r in subset) / count
        agreement = sum(r['argmax_matches'] for r in subset) / count
        summaries[name] = dict(tokens=count, nll_increase=delta, argmax_agreement=agreement,
                               screen_pass=delta <= protocol['screen']['maximum_nll_increase_nats'] and agreement >= protocol['screen']['minimum_argmax_agreement'],
                               contract=obj.contract(), trace=obj.trace)
    result = dict(schema_version=protocol['schema_version'], variants=summaries, fallback_controls=fallback,
                  ideal_control_pass=True, evaluation_split=protocol['evaluation_split'], analog_authorized=False,
                  physical_profile_qualified=False, test_quality_established=False, command=sys.argv)
    if test_plan:
        result['sampled_holdout_screen_pass'] = summaries['finite_reference_adc12']['screen_pass']
    (args.output / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    (args.output / 'manifest.json').write_text(json.dumps({str(p.relative_to(args.output)): digest(p)
        for p in args.output.rglob('*') if p.is_file()}, indent=2) + '\n')
    print(json.dumps({name: {k:v for k,v in row.items() if k not in ('contract','trace')} for name,row in summaries.items()}), flush=True)


if __name__ == '__main__':
    main()
