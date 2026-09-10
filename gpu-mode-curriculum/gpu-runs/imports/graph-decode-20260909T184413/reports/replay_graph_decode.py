#!/usr/bin/env python3
"""Replay a captured graph experiment with verified sources and dependencies."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependencies(recorded):
    from packaging.requirements import Requirement
    norm = lambda name: re.sub(r'[-_.]+', '-', name).lower()
    pins = {norm(line.split('==', 1)[0]): line.split('==', 1)[1] for line in recorded.splitlines() if '==' in line and not line.startswith('#')}
    pending, checked, errors = ['torch', 'transformers'], {}, []
    while pending:
        name = norm(pending.pop())
        if name in checked:
            continue
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed = None
        checked[name] = {'recorded': pins.get(name), 'installed': installed}
        if installed is None or installed != pins.get(name):
            errors.append(f'dependency mismatch: {name}')
            continue
        for raw in metadata.requires(name) or []:
            requirement = Requirement(raw)
            if requirement.marker is None or requirement.marker.evaluate({'extra': ''}):
                pending.append(requirement.name)
    return checked, errors


def extract(bundle, original, destination):
    if sha(bundle) != original['reproduction_bundle']['sha256']:
        raise ValueError('bundle checksum mismatch')
    allowed = set(original['source_hashes']) | {'source-manifest.json','requirements.recorded.txt'}
    with tarfile.open(bundle) as archive:
        members = archive.getmembers()
        if len(members) != len(allowed) or {m.name for m in members} != allowed:
            raise ValueError('unexpected source closure')
        for member in members:
            if not member.isfile() or Path(member.name).name != member.name:
                raise ValueError('unsafe bundle member')
            (destination / member.name).write_bytes(archive.extractfile(member).read())
    manifest = json.loads((destination / 'source-manifest.json').read_text())
    if manifest['source_hashes'] != original['source_hashes']:
        raise ValueError('manifest mismatch')
    for name, digest in original['source_hashes'].items():
        if sha(destination / name) != digest:
            raise ValueError(f'source mismatch: {name}')
    if sha(destination / 'requirements.recorded.txt') != manifest['requirements_sha256']:
        raise ValueError('dependency manifest mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-report', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    original = json.loads(args.original_report.read_text())
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = {'original_report_sha256': sha(args.original_report), 'errors': [],
              'source_isolation': 'verified archive extracted into a new temporary directory',
              'performance_criterion': 'graph median lower than both eager modes for every recorded fixture; no absolute latency-equivalence claim'}
    errors = result['errors']
    with tempfile.TemporaryDirectory(prefix='graph-source-replay-') as temp:
        source = Path(temp)
        extract(args.original_report.parent / original['reproduction_bundle']['path'], original, source)
        checks, mismatches = dependencies((source / 'requirements.recorded.txt').read_text())
        result['dependency_checks'] = checks
        errors.extend(mismatches)
        if platform.python_version() != original['runtime']['python']:
            errors.append('Python version mismatch')
        if not errors:
            command = [sys.executable, str(source / 'run_real_model_graph_decode.py'), '--output-dir', str(output),
                       '--repeats', str(original['protocol']['repeats']), '--max-new-tokens', str(original['protocol']['max_new_tokens'])]
            env = dict(os.environ)
            env.pop('PYTHONPATH', None)
            env['PYTHONNOUSERSITE'] = '1'
            with (output / 'replay.log').open('w') as log:
                proc = subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=1500)
            result['returncode'] = proc.returncode
            if proc.returncode:
                errors.append('replayed experiment failed')
            path = output / 'real-model-graph-decode.json'
            if not path.exists():
                errors.append('replay report missing')
            else:
                replay = json.loads(path.read_text())
                result['replayed_report_sha256'] = sha(path)
                for key in ('source_hashes','model_revision','tokenizer_revision','runtime','protocol'):
                    if original[key] != replay[key]:
                        errors.append(f'replay mismatch: {key}')
                if len(replay['rows']) != len(original['rows']):
                    errors.append('fixture count mismatch')
                for before, after in zip(original['rows'], replay['rows']):
                    for key in ('batch','capacity','fixture','input_token_ids','attention_mask','reference_token_ids'):
                        if before[key] != after[key]:
                            errors.append(f'fixture mismatch: {key}')
                    if not after['output_parity']:
                        errors.append('output parity failed')
                    for row in (before, after):
                        if not all(row['median_ms']['static_graph'] < row['median_ms'][m] for m in ('dynamic_eager','static_eager')):
                            errors.append('performance conclusion did not reproduce')
                if replay['status'] != 'passed':
                    errors.append('replay correctness rejected')
    result['status'] = 'failed' if errors else 'passed'
    (output / 'graph-reproduction.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'dependencies': len(result.get('dependency_checks', {})), 'errors': errors}))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
