#!/usr/bin/env python3
"""Reject promoted or altered sequence results with refreshed artifact hashes."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile

from check_reference_bank_sequences import check
from characterize_switched_reference_dac import digest


def clone_for_check(source, destination):
    destination.mkdir()
    for path in source.iterdir():
        if path.is_dir():
            (destination / path.name).symlink_to(path.resolve(), target_is_directory=True)
        else:
            shutil.copyfile(path, destination / path.name)


def materialize_measurement(root, name):
    directory = root / name
    original = directory.resolve()
    assert directory.is_symlink()
    directory.unlink()
    directory.mkdir()
    for path in original.iterdir():
        if path.name == 'measurements.json':
            shutil.copyfile(path, directory / path.name)
        else:
            (directory / path.name).symlink_to(path.resolve())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    check(args.package)
    for name in ('physical_promotion', 'missing_case', 'duplicate_case', 'early_settling', 'changed_target', 'missing_transition'):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'package'; clone_for_check(args.package, root)
            result = json.loads((root / 'result.json').read_text())
            manifest = json.loads((root / 'manifest.json').read_text())
            if name == 'physical_promotion':
                result['physical_profile_qualified'] = True
            elif name == 'missing_case':
                result['cases'].pop()
            elif name == 'duplicate_case':
                result['cases'][-1] = result['cases'][0]
            else:
                # Use a newly simulated case, avoiding rejection merely because
                # recovered immutable measurements differ from their originals.
                recovery_path = root / 'recovery.json'
                if recovery_path.exists():
                    chosen = json.loads(recovery_path.read_text())['resumed_cases'][0]
                    case = next(c for c in result['cases'] if c['directory'] == chosen)
                else:
                    case = result['cases'][0]
                if name == 'early_settling':
                    row = next(r for r in case['rows'] if r['sampled_settling_after_edge_s'] and r['sampled_settling_after_edge_s'] > 0)
                    row['sampled_settling_after_edge_s'] = 0.0
                elif name == 'changed_target':
                    case['rows'][0]['target_v'] += .01
                else:
                    case['rows'].pop()
                materialize_measurement(root, case['directory'])
                path = root / case['directory'] / 'measurements.json'
                path.write_text(json.dumps(case))
                manifest[str(path.relative_to(root))] = digest(path)
            (root / 'result.json').write_text(json.dumps(result))
            manifest['result.json'] = digest(root / 'result.json')
            (root / 'manifest.json').write_text(json.dumps(manifest))
            try:
                with contextlib.redirect_stdout(io.StringIO()): check(root)
            except AssertionError:
                print('Rejected', name, flush=True)
            else:
                raise AssertionError('Accepted ' + name)


if __name__ == '__main__':
    main()
