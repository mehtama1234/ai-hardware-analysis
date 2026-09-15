"""Remote Colab entry point for a real-model next-stage agent matrix run."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

CONTENT = Path("/content")
ARCHIVE = CONTENT / "next-stage-agent-matrix.tgz"
WORKDIR = CONTENT / "next-stage-agent-matrix"
CONFIG = CONTENT / "next-stage-agent-matrix-config.json"
SUMMARY = WORKDIR / ".artifacts/next-stage-agent-matrix-remote-summary.json"


def write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 7200) -> dict[str, object]:
    try:
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
        return {"command": command, "returncode": None, "status": "blocked", "error": "timeout", "stdout_tail": stdout[-5000:], "stderr_tail": stderr[-5000:]}
    except OSError as error:
        return {"command": command, "returncode": None, "status": "blocked", "error": type(error).__name__, "stdout_tail": "", "stderr_tail": str(error)[-5000:]}
    return {"command": command, "returncode": result.returncode, "status": "passed" if result.returncode == 0 else "blocked", "stdout_tail": result.stdout[-5000:], "stderr_tail": result.stderr[-5000:]}


def main() -> int:
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        archive.extractall(CONTENT, filter="data")
    config = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.is_file() else {}
    model_id = str(config.get("model_id", "Qwen/Qwen2.5-0.5B-Instruct"))
    start_index = int(config.get("start_index", 0))
    max_tasks = config.get("max_tasks")
    model_dir = WORKDIR / ".artifacts/colab-next-stage-model"
    model_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    steps = [run(["bash", "-lc", "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"], cwd=WORKDIR, env=environment, timeout=60)]
    steps.append(run([sys.executable, "-m", "pip", "install", "-q", "transformers==4.51.3", "huggingface_hub", "torch", "lm-format-enforcer"], cwd=WORKDIR, env=environment, timeout=1800))
    environment["NEXT_STAGE_MODEL_ID"] = model_id
    environment["NEXT_STAGE_MODEL_DIR"] = str(model_dir)
    steps.append(run([sys.executable, "-c", "from huggingface_hub import snapshot_download; import os; snapshot_download(os.environ['NEXT_STAGE_MODEL_ID'], local_dir=os.environ['NEXT_STAGE_MODEL_DIR'])"], cwd=WORKDIR, env=environment, timeout=3600))
    environment.update({
        "VERIFICATION_LLM_BATCH_COMMAND": f"{sys.executable} scripts/hf_llm_batch_backend.py",
        "VERIFICATION_HF_MODEL": str(model_dir), "VERIFICATION_HF_DEVICE": "cuda",
        "VERIFICATION_HF_JSON_CONSTRAINED": "1", "VERIFICATION_HF_MAX_NEW_TOKENS": "512",
        "VERIFICATION_LLM_TIMEOUT_SECONDS": "300",
    })
    output = WORKDIR / ".artifacts/next-stage-real"
    command = [sys.executable, "colab/run_next_stage_colab.py", "--agent-backend", "local", "--require-real-agent", "--start-index", str(start_index)]
    if max_tasks is not None:
        command.extend(["--max-tasks", str(int(max_tasks))])
    command.extend(["--output", str(output)])
    execution = run(command, cwd=WORKDIR, env=environment, timeout=14400)
    steps.append(execution)
    report_path = output / "next-stage-colab-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    summary = {
        "schema_version": "next-stage-real-colab-summary-v2", "model_id": model_id,
        "task_range": {"start_index": start_index, "max_tasks": max_tasks},
        "steps": steps, "report": report,
        "status": "passed" if all(step["status"] == "passed" for step in steps) and isinstance(report, dict) and report.get("all_machine_stages_passed") is True else "blocked",
        "claim_boundary": "real-model Colab execution of the declared next-stage seeded matrix; not general repository SOTA, physical signoff, or autonomous release",
    }
    summary["summary_sha256"] = hashlib.sha256(json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    write(SUMMARY, summary)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
