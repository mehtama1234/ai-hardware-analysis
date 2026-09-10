"""Small remote entrypoint; upload with the two graph-decode source files."""
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

root = Path('/content/graph-decode')
root.mkdir(exist_ok=True)
for name in ('graph_decode.py', 'run_real_model_graph_decode.py', 'test_graph_decode.py'):
    shutil.copy2(Path('/content') / name, root / name)
output = root / 'reports'
output.mkdir(exist_ok=True)
commands = [
    [sys.executable, '-m', 'pip', 'install', '-q', 'transformers==5.12.1', 'pytest'],
    [sys.executable, '-m', 'pytest', 'test_graph_decode.py', '-q'],
    [sys.executable, 'run_real_model_graph_decode.py', '--output-dir', str(output)],
]
if Path('/content/graph-original.json').exists():
    shutil.copy2('/content/replay_graph_decode.py', root / 'replay_graph_decode.py')
    commands[-1] = [sys.executable, 'replay_graph_decode.py',
        '--original-report', '/content/graph-original.json', '--output-dir', str(output)]
if Path('/content/slot_decode.py').exists():
    for name in ('slot_decode.py', 'run_slot_decode.py', 'test_slot_decode.py'):
        shutil.copy2(Path('/content') / name, root / name)
    commands[1] = [sys.executable, '-m', 'pytest', 'test_graph_decode.py', 'test_slot_decode.py', '-q']
    commands[-1] = [sys.executable, 'run_slot_decode.py', '--output-dir', str(output)]
if Path('/content/continuous_service.py').exists():
    for name in ('continuous_service.py', 'real_model_service.py', 'run_continuous_http.py', 'test_continuous_service.py'):
        shutil.copy2(Path('/content') / name, root / name)
    commands[1] = [sys.executable, '-m', 'pytest', 'test_graph_decode.py', 'test_slot_decode.py', 'test_continuous_service.py', '-q']
    commands.append([sys.executable, 'run_continuous_http.py', '--output-dir', str(output)])
if Path('/content/run_continuous_load.py').exists():
    for name in ('continuous_http.py', 'run_continuous_load.py', 'test_continuous_http.py'):
        shutil.copy2(Path('/content') / name, root / name)
    commands[1] = [sys.executable, '-m', 'pytest', 'test_graph_decode.py', 'test_slot_decode.py',
                   'test_continuous_service.py', 'test_continuous_http.py', '-q']
    commands.append([sys.executable, 'run_continuous_load.py', '--output-dir', str(output)])
if Path('/content/run_serving_comparison.py').exists():
    for name in ('microbatch_control.py','run_serving_comparison.py','test_microbatch_control.py'):
        shutil.copy2(Path('/content') / name, root / name)
    commands[1].insert(-1,'test_microbatch_control.py')
    commands[-1] = [sys.executable,'run_serving_comparison.py','--output-dir',str(output)]
if Path('/content/serving-original.json').exists():
    for name in ('replay_serving_comparison.py','replay_graph_decode.py','verify_serving_comparison.py','verify_continuous_load.py'):
        shutil.copy2(Path('/content')/name,root/name)
    commands[-1]=[sys.executable,'replay_serving_comparison.py','--original-report','/content/serving-original.json','--output-dir',str(output)]
results = []
try:
    for i, command in enumerate(commands):
        log = output / f'command-{i}.log'
        with log.open('w') as stream:
            result = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT, timeout=1500)
        print(log.read_text()[-8000:], flush=True)
        results.append({'command': command, 'returncode': result.returncode, 'log': log.name})
        if result.returncode:
            break
finally:
    shutil.copy2(root / 'test_graph_decode.py', output / 'test_graph_decode.py')
    if (root / 'test_slot_decode.py').exists():
        shutil.copy2(root / 'test_slot_decode.py', output / 'test_slot_decode.py')
    if (root / 'test_continuous_service.py').exists():
        shutil.copy2(root / 'test_continuous_service.py', output / 'test_continuous_service.py')
    if (root / 'test_continuous_http.py').exists():
        shutil.copy2(root / 'test_continuous_http.py', output / 'test_continuous_http.py')
    if (root / 'test_microbatch_control.py').exists():
        shutil.copy2(root / 'test_microbatch_control.py', output / 'test_microbatch_control.py')
    if (root / 'replay_graph_decode.py').exists():
        shutil.copy2(root / 'replay_graph_decode.py', output / 'replay_graph_decode.py')
    if (root / 'replay_serving_comparison.py').exists():
        for name in ('replay_serving_comparison.py','verify_serving_comparison.py','verify_continuous_load.py'):
            shutil.copy2(root/name,output/name)
    (output / 'commands.json').write_text(json.dumps(results, indent=2) + '\n')
    with tarfile.open('/content/graph-decode-results.tar.gz', 'w:gz') as archive:
        archive.add(output, arcname='reports')
if len(results) != len(commands) or any(row['returncode'] for row in results):
    raise SystemExit('Graph experiment failed; inspect captured logs')
