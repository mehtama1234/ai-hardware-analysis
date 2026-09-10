#!/usr/bin/env python3
"""Remote T4 characterization for a second pretrained decoder model."""
import json
import subprocess
import tarfile
from pathlib import Path

ROOT = Path('/content/alternate-model')
ROOT.mkdir(parents=True, exist_ok=True)
MODEL_ID = 'distilbert/distilgpt2'
REVISION = '2290a62682d06624634c1f46a6ad5be0f47f38aa'


def run(command, log):
    with log.open('a') as stream:
        stream.write('$ ' + ' '.join(command) + '\n')
        return subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT).returncode


def main():
    archive = Path('/content/alternate-model.tgz')
    if archive.exists():
        with tarfile.open(archive, 'r:gz') as bundle:
            bundle.extractall(ROOT)
    subprocess.run(['pip', 'install', '-q', 'transformers==5.12.1', 'safetensors'], check=True)
    log = ROOT / 'commands.log'
    commands = [
        ['python', 'run_continuous_load.py', '--model-id', MODEL_ID, '--revision', REVISION,
         '--output-dir', 'reports/alternate-load', '--seconds', '4'],
        ['python', 'verify_continuous_load.py', 'reports/alternate-load/continuous-load.json',
         '--model-id', MODEL_ID, '--model-revision', REVISION],
    ]
    statuses = []
    for command in commands:
        code = run(command, log)
        statuses.append({'command': command, 'returncode': code})
        if code:
            break
    (ROOT / 'driver-status.json').write_text(json.dumps({'statuses': statuses}, indent=2) + '\n')
    subprocess.run(['tar', '-czf', '/content/alternate-model-results.tar.gz', '.'], cwd=ROOT, check=False)
    return int(any(row['returncode'] for row in statuses))


if __name__ == '__main__':
    raise SystemExit(main())
