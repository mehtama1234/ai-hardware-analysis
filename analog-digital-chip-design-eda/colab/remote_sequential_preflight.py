#!/usr/bin/env python3
"""Bootstrap the focused source bundle and run the sequential preflight remotely."""
from __future__ import annotations

import runpy
import tarfile
from pathlib import Path


archive = Path("/content/aimc-sequential-source.tgz")
root = Path("/content")
if not (root / "analog-digital-chip-design-eda").exists():
    with tarfile.open(archive, "r:gz") as bundle:
        bundle.extractall("/content", filter="data")
runpy.run_path(str(root / "analog-digital-chip-design-eda/colab/validate_sequential_control_deck.py"), run_name="__main__")
