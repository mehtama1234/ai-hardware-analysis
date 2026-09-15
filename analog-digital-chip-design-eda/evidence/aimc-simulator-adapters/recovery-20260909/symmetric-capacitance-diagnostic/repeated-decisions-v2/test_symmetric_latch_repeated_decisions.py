#!/usr/bin/env python3
"""Repeat decision histories in a synthetic-capacitance schematic diagnostic."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPOSITORY_ROOT / 'scripts'))

from characterize_switched_reference_dac import digest
from run_active_converter_macro_extracted_transient import measure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-deck', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    text = args.source_deck.read_text()
    seq = [-100., 100., -.1529705854, .1529705854, .1529705854, -.1529705854, 100., -100.]
    for name, sign in [('VROW', 1), ('VCOMP', -1)]:
        values = [.9 + sign * diff / 2000 for diff in seq]
        points = [(0, values[0])]
        for i in range(1, len(seq)):
            points.extend([(i*60e-9, values[i-1]), (i*60e-9+1e-9, values[i])])
        points.append((480e-9, values[-1]))
        text, count = re.subn(r'(?m)^('+name+r'\s+\S+\s+0)\s+.*$',
            lambda m: m[1]+' PWL('+' '.join(f'{t:.15g} {v:.15g}' for t, v in points)+')', text)
        assert count == 1
    text, count = re.subn(r'(?m)^(VEVAL .*?)30n\)', r'\g<1>60n)', text)
    assert count == 1 and '.tran 20p 20n uic' in text
    text = text.replace('.tran 20p 20n uic', '.tran 20p 480n uic')
    measures = [f'.measure tran cycle{i}_{side} FIND v(decision_{side}) AT={18+i*60}n'
                for i in range(8) for side in ('p', 'n')]
    text = text.replace('.control', '\n'.join(measures)+'\n.control')
    assert 'run\n.endc' in text
    text = text.replace('run\n.endc', 'set numdgt=15\nset wr_singlescale\nset wr_vecnames\nrun\nwrdata waveform.txt v(decision_p) v(decision_n) v(row_drive) v(sar_comparator_input)\n.endc')
    args.output.mkdir(parents=True, exist_ok=False)
    root = args.output.resolve()
    (root / 'deck.spice').write_text(text)
    shutil.copyfile(__file__, root / Path(__file__).name)
    shutil.copyfile(Path(__file__).with_name('run_active_converter_macro_extracted_transient.py'), root / 'measurement_helper.py')
    protocol = dict(input_diffs_mv=seq, cycles=8, period_ns=60, input_transition_ns=1,
                    decision_sample_ns=18, nominal_transient_step_ns=.02, logic_margin_v=.9,
                    description='Synthetic symmetric parasitics and drain-isolated sample/regeneration schematic; not layout qualification',
                    source_deck=str(args.source_deck.resolve()), source_deck_sha256=digest(args.source_deck), analog_authorized=False)
    (root / 'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    try:
        proc = subprocess.run(['ngspice', '-b', str(root / 'deck.spice')], cwd=root, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired as exc:
        (root / 'stdout.log').write_bytes(exc.stdout or b'')
        (root / 'stderr.log').write_bytes(exc.stderr or b'')
        raise
    (root / 'stdout.log').write_text(proc.stdout); (root / 'stderr.log').write_text(proc.stderr)
    assert proc.returncode == 0, proc.stderr[-1000:]
    rows = []
    for i, diff in enumerate(seq):
        vp, vn = [measure(proc.stdout, f'cycle{i}_{side}') for side in ('p', 'n')]
        assert vp is not None and vn is not None
        delta = vn-vp
        rows.append(dict(cycle=i, input_diff_mv=diff, decision_p_v=vp, decision_n_v=vn,
                         output_diff_v=delta, polarity_pass=(delta>0)==(diff<0), margin_pass=abs(delta)>=.9))
    (root / 'result.json').write_text(json.dumps(dict(rows=rows, returncode=proc.returncode,
        all_cycles_pass=all(r['polarity_pass'] and r['margin_pass'] for r in rows), physical_qualified=False,
        analog_authorized=False), indent=2)+'\n')
    (root / 'manifest.json').write_text(json.dumps({f.name:digest(f) for f in root.iterdir() if f.is_file()}, indent=2)+'\n')
    print(json.dumps(rows), flush=True)


if __name__ == '__main__':
    main()
