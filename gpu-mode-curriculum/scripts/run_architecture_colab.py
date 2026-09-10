#!/usr/bin/env python3
"""Remote T4 characterization for a genuinely different decoder architecture."""
import json
import subprocess
import tarfile
import os
from pathlib import Path

ROOT = Path('/content/architecture-characterization')
ROOT.mkdir(parents=True, exist_ok=True)
MODEL_ID = 'EleutherAI/pythia-70m'
REVISION = 'a39f36b100fe8a5377810d56c3f4789b9c53ac42'


def main():
    archive = Path('/content/architecture-characterization.tgz')
    if archive.exists():
        with tarfile.open(archive, 'r:gz') as bundle:
            bundle.extractall(ROOT)
    subprocess.run(['pip', 'install', '-q', 'transformers==5.12.1', 'safetensors'], check=True)
    mode_path = ROOT / 'architecture-mode.json'
    mode_config = json.loads(mode_path.read_text()) if mode_path.exists() else {}
    mode = mode_config.get('mode', 'full')
    profile = bool(mode_config.get('profile', 0))
    seconds = int(mode_config.get('seconds', 4))
    if seconds < 4:
        raise ValueError('architecture workload duration must be at least four seconds')
    output = ROOT / 'reports' / 'pythia-serving-characterization.json'
    commands = []
    if mode == 'full':
        load_command = ['python', 'run_continuous_load.py', '--model-id', MODEL_ID, '--revision', REVISION,
                        '--engine', 'hf', '--output-dir', 'reports/pythia-load', '--seconds', str(seconds)]
        if profile or os.environ.get('ARCHITECTURE_PROFILE') == '1':
            load_command.append('--profile')
        commands.extend([
            ['python', 'run_real_model_serving_characterization.py', '--model-id', MODEL_ID,
             '--revision', REVISION, '--output', str(output)],
            ['python', 'verify_serving_characterization.py', str(output), '--model-id', MODEL_ID,
             '--revision', REVISION],
            load_command,
            ['python', 'verify_continuous_load.py', 'reports/pythia-load/continuous-load.json',
             '--model-id', MODEL_ID, '--model-revision', REVISION],
        ])
    if mode == 'profile':
        commands.extend([
            ['python', 'run_continuous_load.py', '--model-id', MODEL_ID, '--revision', REVISION,
             '--engine', 'hf', '--output-dir', 'reports/pythia-load', '--seconds', str(seconds), '--profile'],
            ['python', 'verify_continuous_load.py', 'reports/pythia-load/continuous-load.json',
             '--model-id', MODEL_ID, '--model-revision', REVISION],
        ])
    if mode == 'capture':
        commands.append(['python', 'static_cache_graph_probe.py', '--model-id', MODEL_ID,
                         '--revision', REVISION, '--reuse-policy', 'recapture',
                         '--output', 'reports/static-cache-graph.json'])
        commands.append(['python', 'verify_static_cache_graph_probe.py', 'reports/static-cache-graph.json',
                         '--model-id', MODEL_ID, '--model-revision', REVISION])
    if mode == 'bucket':
        commands.append(['python', 'run_static_graph_bucket.py', '--model-id', MODEL_ID,
                         '--revision', REVISION, '--output', 'reports/static-graph-bucket.json'])
        commands.append(['python', 'verify_static_graph_bucket.py', 'reports/static-graph-bucket.json',
                         '--model-id', MODEL_ID, '--model-revision', REVISION])
    if mode in ('http-bucket', 'http-bucket-sustained', 'http-bucket-cancel'):
        bucket_args = (['--rounds', '3'] if mode == 'http-bucket-sustained' else
                       ['--cancel-probe'] if mode == 'http-bucket-cancel' else [])
        commands.append(['python', 'run_static_graph_http.py', '--model-id', MODEL_ID,
                         '--revision', REVISION, '--output', 'reports/static-graph-http.json', *bucket_args])
        commands.append(['python', 'verify_static_graph_http.py', 'reports/static-graph-http.json',
                         '--model-id', MODEL_ID, '--model-revision', REVISION])
    comparison_command = ['python', 'run_serving_comparison.py', '--model-id', MODEL_ID, '--revision', REVISION,
                          '--engine', 'hf', '--output-dir', 'reports/pythia-comparison', '--seconds', str(seconds)]
    if profile or os.environ.get('ARCHITECTURE_PROFILE') == '1':
        comparison_command.append('--profile')
        comparison_command.append('--native-cache-kind')
        comparison_command.append('static')
    commands.extend([
        comparison_command,
        ['python', 'verify_serving_comparison.py', 'reports/pythia-comparison/serving-comparison.json',
         '--model-id', MODEL_ID, '--model-revision', REVISION],
    ])
    log = ROOT / 'commands.log'
    statuses = []
    for command in commands:
        with log.open('a') as stream:
            stream.write('$ ' + ' '.join(command) + '\n')
            code = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT).returncode
        statuses.append({'command': command, 'returncode': code})
        if code:
            break
    (ROOT / 'driver-status.json').write_text(json.dumps({'statuses': statuses}, indent=2) + '\n')
    subprocess.run(['tar', '-czf', '/content/architecture-characterization-results.tgz', '.'], cwd=ROOT, check=False)
    return int(any(row['returncode'] for row in statuses))


if __name__ == '__main__':
    raise SystemExit(main())
