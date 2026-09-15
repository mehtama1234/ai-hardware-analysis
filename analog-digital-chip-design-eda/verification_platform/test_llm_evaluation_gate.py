import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def test_real_model_gate_accepts_complete_fixture():
    result = subprocess.run([sys.executable, str(ROOT / "scripts/verify_llm_model_evaluation.py"), str(ROOT / ".artifacts/llm-agent-benchmark-batch-mock.json")], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0

def test_real_model_gate_rejects_unconfigured_baseline():
    result = subprocess.run([sys.executable, str(ROOT / "scripts/verify_llm_model_evaluation.py"), str(ROOT / ".artifacts/llm-agent-benchmark.json")], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
