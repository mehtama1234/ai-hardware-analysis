#!/usr/bin/env python3
"""Reject altered scientific claims even when their file hashes are refreshed."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile

from check_gpt2_reference_validation import check
from run_gpt2_hybrid_evaluation import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    check(args.package)
    mutations = {
        'false_test_qualification': lambda r: r.update(test_quality_established=True),
        'false_hardware_qualification': lambda r: r.update(physical_profile_qualified=True),
        'relabeled_split': lambda r: r.update(evaluation_split='validation' if r['evaluation_split'] == 'test' else 'test'),
        'changed_aggregate': lambda r: r['variants']['finite_reference_adc12'].update(argmax_agreement=1.0),
        'stale_effective_range': lambda r: r['variants']['finite_reference_adc12']['contract']['adc_range']['ranges'][0].update(selected_bound=0.0),
        'missing_fallback': lambda r: r['fallback_controls'].pop(),
    }
    for name, mutate in mutations.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'package'
            shutil.copytree(args.package, root)
            result = json.loads((root / 'result.json').read_text())
            mutate(result)
            (root / 'result.json').write_text(json.dumps(result))
            manifest = json.loads((root / 'manifest.json').read_text())
            manifest['result.json'] = digest(root / 'result.json')
            (root / 'manifest.json').write_text(json.dumps(manifest))
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    check(root)
            except AssertionError:
                print('Rejected', name)
            else:
                raise AssertionError('Accepted ' + name)


if __name__ == '__main__':
    main()
