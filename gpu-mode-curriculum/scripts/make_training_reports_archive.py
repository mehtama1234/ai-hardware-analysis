#!/usr/bin/env python3
"""Create a small report-only archive after a remote training run."""
import tarfile
from pathlib import Path

ROOT = Path('/content/training-capstone')
OUTPUT = Path('/content/training-capstone-reports.tgz')

with tarfile.open(OUTPUT, 'w:gz') as archive:
    for path in (ROOT / 'commands.log', ROOT / 'driver-status.json'):
        if path.exists():
            archive.add(path, arcname=path.relative_to(ROOT))
    reports = ROOT / 'reports'
    if reports.exists():
        for path in reports.rglob('*'):
            if path.is_file() and 'checkpoints' not in path.parts:
                archive.add(path, arcname=path.relative_to(ROOT))
print(str(OUTPUT))
