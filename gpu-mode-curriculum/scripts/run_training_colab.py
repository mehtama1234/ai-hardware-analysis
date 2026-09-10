#!/usr/bin/env python3
"""Remote Colab driver for the real-data training capstone."""
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path('/content/training-capstone')
ROOT.mkdir(parents=True, exist_ok=True)


def run(command, log):
    with log.open('a') as stream:
        stream.write('$ ' + ' '.join(command) + '\n')
        return subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT).returncode


def main():
    archive = Path('/content/training-capstone.tgz')
    if archive.exists():
        with tarfile.open(archive, 'r:gz') as bundle:
            bundle.extractall(ROOT)
    log = ROOT / 'commands.log'
    packages = [['transformers==5.12.1', 'safetensors']]
    subprocess.run(['pip', 'install', '-q', *packages[0]], check=True)
    package = ROOT / 'fused_training_kernels'
    package.mkdir(exist_ok=True)
    (package / '__init__.py').touch()
    for name in ('linear_cross_entropy.py', 'evaluation.py'):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, package / name)
    (ROOT / 'data').mkdir(exist_ok=True)
    corpus = ROOT / 'tinyshakespeare.txt'
    if corpus.exists():
        shutil.copy2(corpus, ROOT / 'data' / corpus.name)
    serving = ROOT / 'serving'
    serving.mkdir(exist_ok=True)
    for name in ('continuous_http.py', 'continuous_service.py', 'real_model_service.py',
                 'slot_decode.py', 'graph_decode.py'):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, serving / name)
    config_path = ROOT / 'training-config.json'
    config = {
        'steps': 16,
        'sequence': 64,
        'chunk_size': 16,
        'seeds': [7, 19],
        'load_seconds': 4,
    }
    if config_path.exists():
        config.update(json.loads(config_path.read_text()))
    steps = str(int(config['steps']))
    sequence = str(int(config['sequence']))
    chunk_size = str(int(config['chunk_size']))
    seeds = [str(int(seed)) for seed in config['seeds']]
    load_seconds = str(int(config['load_seconds']))
    commands = [
        ['python', 'prepare_training_data.py', '--data-dir', 'data'],
        ['python', 'run_real_training.py', '--data-dir', 'data', '--output-dir', 'reports/gpu-run',
         '--device', 'cuda', '--steps', steps, '--sequence', sequence, '--chunk-size', chunk_size,
         '--seeds', *seeds, '--save-checkpoints'],
        ['python', 'run_gpu_checkpoint_serving.py', '--checkpoint',
         'reports/gpu-run/7-recomputed', '--output',
         'reports/gpu-run/gpu-checkpoint-serving.json', '--serving-dir', 'serving'],
        ['python', 'verify_gpu_checkpoint_serving.py',
         'reports/gpu-run/gpu-checkpoint-serving.json'],
        ['python', 'run_continuous_load.py', '--checkpoint', 'reports/gpu-run/7-recomputed',
         '--output-dir', 'reports/gpu-run/checkpoint-load', '--seconds', load_seconds],
        ['python', 'verify_continuous_load.py',
         'reports/gpu-run/checkpoint-load/continuous-load.json'],
        ['python', 'run_serving_comparison.py', '--checkpoint', 'reports/gpu-run/7-recomputed',
         '--output-dir', 'reports/gpu-run/checkpoint-comparison', '--seconds', load_seconds],
        ['python', 'verify_serving_comparison.py',
         'reports/gpu-run/checkpoint-comparison/serving-comparison.json'],
        ['python', 'replay_serving_comparison.py', '--original-report',
         'reports/gpu-run/checkpoint-comparison/serving-comparison.json', '--checkpoint',
         'reports/gpu-run/7-recomputed', '--output-dir', 'reports/gpu-run/checkpoint-replay'],
        ['python', 'verify_real_training.py', 'reports/gpu-run/real-training.json', '--data-dir', 'data'],
        ['python', 'verify_checkpoint_artifacts.py', 'reports/gpu-run/real-training.json'],
        ['python', 'build_training_decision.py', 'reports/gpu-run/real-training.json',
         '--output', 'reports/gpu-run/training-decision.json', '--data-dir', 'data'],
    ]
    statuses = []
    for command in commands:
        code = run(command, log)
        statuses.append({'command': command, 'returncode': code})
        if code:
            break
    (ROOT / 'driver-status.json').write_text(json.dumps({'statuses': statuses}, indent=2) + '\n')
    # Keep the imported artifact small enough for the Colab contents API. The
    # CUDA gate is the training/evaluation report; checkpoint persistence has a
    # separate CPU smoke with full hash and reload verification.
    subprocess.run([
        'tar', '-czf', '/content/training-capstone-results.tar.gz',
        '--exclude=./reports/gpu-run/7-standard',
        '--exclude=./reports/gpu-run/7-recomputed',
        '--exclude=./reports/gpu-run/19-standard',
        '--exclude=./reports/gpu-run/19-recomputed', '.',
    ], cwd=ROOT, check=False)
    return int(any(row['returncode'] for row in statuses))


if __name__ == '__main__':
    raise SystemExit(main())
