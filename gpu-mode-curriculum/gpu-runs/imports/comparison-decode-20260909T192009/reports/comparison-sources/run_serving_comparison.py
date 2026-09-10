#!/usr/bin/env python3
"""Matched three-way serving comparison using the shared HTTP arrival harness."""
import argparse
import hashlib
import json
import platform
import shutil
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from continuous_service import ContinuousScheduler, SlotBackend
from microbatch_control import MicrobatchScheduler, NativeBatchBackend, GraphGroupBackend
from slot_decode import SlotDecode
from run_continuous_load import MODEL, REVISION, PROMPTS, BUDGETS, load


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=8)
    args = parser.parse_args()
    if not torch.cuda.is_available() or args.seconds < 4:
        raise SystemExit('CUDA and >=4-second windows required')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    torch.backends.cuda.matmul.allow_tf32 = False
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, padding_side='left')
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION,
        attn_implementation='eager', use_safetensors=True).cuda().eval()
    with torch.inference_mode():
        references = [model.generate(**tokenizer([p], return_tensors='pt').to('cuda'),
            max_new_tokens=32, do_sample=False, eos_token_id=None,
            pad_token_id=tokenizer.pad_token_id)[0,-32:].tolist() for p in PROMPTS]
    engine = SlotDecode(model, 2, 256)
    engine.capture()
    factories = {
        'native_microbatch': lambda: MicrobatchScheduler(NativeBatchBackend(model, tokenizer)),
        'graph_microbatch': lambda: MicrobatchScheduler(GraphGroupBackend(SlotBackend(engine, tokenizer))),
        'graph_continuous': lambda: ContinuousScheduler(SlotBackend(engine, tokenizer), slots=2, max_pending=8, max_tokens=32),
    }
    modes = list(factories)
    runs = []
    for round_index in range(3):
        for rate in ([16,48] if round_index % 2 == 0 else [48,16]):
            for position,mode in enumerate(modes[round_index:] + modes[:round_index]):
                row = load(engine, tokenizer, references, rate, args.seconds,
                    f'r{round_index}-rate{rate}-{mode}', factories[mode])
                row['mode'],row['round_index'],row['order_position'] = mode,round_index,position
                row['summary']['accepted_by_budget'] = {str(b): sum(r['http_status']==200 and r['max_new_tokens']==b for r in row['requests']) for b in BUDGETS}
                runs.append(row)
                print(json.dumps({'run':row['round'],'checks':row['checks'],'summary':row['summary']}),flush=True)
    sources = args.output_dir/'comparison-sources'
    sources.mkdir(exist_ok=True)
    hashes = {}
    for name in ('graph_decode.py','slot_decode.py','continuous_service.py','continuous_http.py',
                 'real_model_service.py','run_continuous_load.py','microbatch_control.py','run_serving_comparison.py'):
        source = Path(__file__).with_name(name)
        shutil.copy2(source,sources/name)
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    report = {'schema_version':'matched-serving-v0.1','evidence_kind':'measured_gpu',
        'status':'passed' if all(all(r['checks'].values()) for r in runs) else 'failed',
        'model_revision':REVISION,'tokenizer_revision':REVISION,'source_hashes':hashes,
        'runtime':{'torch':torch.__version__,'transformers':transformers.__version__,
            'python':platform.python_version(),'device':torch.cuda.get_device_name(),'dtype':str(model.dtype),'tf32':False},
        'prompts':PROMPTS,'references':references,'protocol':{'modes':modes,'rates':[16,48],
            'rounds':3,'seconds':args.seconds,'budgets':BUDGETS,'slots':2,'queue':8,
            'microbatch_window_ms':5,'ttft_ms':1000,'completion_ms':3000,'intertoken_ms':500,
            'order':'each mode occupies every position once for each rate',
            'memory':'graph allocations resident in every mode; native control additionally allocates dynamic cache'},
        'runs':runs,'limitations':['Bounded loopback comparison, not production capacity.',
            'Native microbatch compacts completed rows; fixed groups admit no new work until their peers finish.',
            'Graph modes prefill requests individually; native mode batches prefill. Comparison includes these execution choices.',
            'Stage fields in microbatch terminal records are not measured; compare client timings.',
            'Independent source-bundle replay remains open.']}
    (args.output_dir/'serving-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return int(report['status']!='passed')


if __name__=='__main__':
    raise SystemExit(main())
