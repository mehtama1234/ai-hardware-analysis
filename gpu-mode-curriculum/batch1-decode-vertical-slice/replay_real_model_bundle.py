#!/usr/bin/env python3
"""Replay the captured HTTP experiment from verified sources in an isolated folder."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def normalized(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def dependency_check(recorded):
    from packaging.requirements import Requirement
    pins = {}
    for line in recorded.splitlines():
        if '==' in line and not line.startswith('#'):
            name, version = line.split('==', 1)
            pins[normalized(name)] = version
    pending = ['torch', 'transformers', 'ninja']
    checked, errors = {}, []
    while pending:
        name = normalized(pending.pop())
        if name in checked:
            continue
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed = None
        checked[name] = {'recorded': pins.get(name), 'installed': installed}
        if not pins.get(name) or installed != pins[name]:
            errors.append(f'{name}: recorded={pins.get(name)!r}, installed={installed!r}')
            continue
        for raw in importlib.metadata.requires(name) or []:
            requirement = Requirement(raw)
            if requirement.marker is None or requirement.marker.evaluate({'extra': ''}):
                pending.append(requirement.name)
    return checked, errors


def extract_verified(bundle, report, destination):
    if hashlib.sha256(bundle.read_bytes()).hexdigest() != report['reproduction_bundle']['sha256']:
        raise ValueError('bundle checksum mismatch')
    with tarfile.open(bundle) as archive:
        for member in archive.getmembers():
            if not member.isfile() or Path(member.name).name != member.name:
                raise ValueError(f'unexpected bundle member: {member.name}')
            data = archive.extractfile(member).read()
            (destination / member.name).write_bytes(data)
    manifest = json.loads((destination / 'source-manifest.json').read_text())
    if manifest['source_hashes'] != report['source_hashes']:
        raise ValueError('source manifest does not match original report')
    for name, expected in report['source_hashes'].items():
        if hashlib.sha256((destination / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'source checksum mismatch: {name}')
    requirements = destination / 'requirements.recorded.txt'
    if hashlib.sha256(requirements.read_bytes()).hexdigest() != manifest['requirements_sha256']:
        raise ValueError('requirements checksum mismatch')
    return requirements.read_text()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-report', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--host-label', required=True)
    args = parser.parse_args()
    original_path = args.original_report.resolve()
    original = json.loads(original_path.read_text())
    bundle = original_path.parent / original['reproduction_bundle']['path']
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gpt2-bundle-replay-') as temp:
        source = Path(temp)
        recorded = extract_verified(bundle, original, source)
        dependencies, errors = dependency_check(recorded)
        if sys.version.split()[0] != original['runtime']['python'].split()[0]:
            errors.append('Python version differs from recorded environment')
        result = {'schema_version': 'real-model-bundle-replay-v0.1', 'host_label': args.host_label,
                  'original_report_sha256': hashlib.sha256(original_path.read_bytes()).hexdigest(),
                  'bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
                  'dependency_checks': dependencies, 'errors': errors,
                  'source_isolation': 'temporary directory populated only from checksum-verified bundle',
                  'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        if not errors:
            command = [sys.executable, str(source / 'run_real_model_http_repeated.py'), '--output-dir', str(output),
                       '--rounds', str(original['protocol']['round_count'])]
            env = dict(os.environ)
            env.pop('PYTHONPATH', None)
            env['PYTHONNOUSERSITE'] = '1'
            with (output / 'replay.log').open('w') as log:
                process = subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=1200)
            result['returncode'] = process.returncode
            if process.returncode:
                errors.append(f'extracted experiment exited {process.returncode}')
            replay_path = output / 'real-model-http-repeated.json'
            if replay_path.exists():
                replay = json.loads(replay_path.read_text())
                for key in ('source_hashes', 'model_revision', 'tokenizer_revision', 'dtype', 'reference_token_ids'):
                    if replay[key] != original[key]:
                        errors.append(f'replayed {key} differs')
                if replay.get('gpu_execution_accepted') is not True:
                    errors.append('replayed GPU experiment failed validation')
                result['replayed_report_sha256'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
            else:
                errors.append('replayed report missing')
        result['status'] = 'failed' if errors else 'passed'
        (output / 'real-model-reproduction.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'status': result['status'], 'dependency_count': len(dependencies), 'errors': errors}), flush=True)
        return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
