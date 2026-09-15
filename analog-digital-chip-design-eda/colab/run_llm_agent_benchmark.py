#!/usr/bin/env python3
"""Run the real-model verification-agent benchmark inside Colab."""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path


CONTENT = Path("/content")
ARCHIVE = CONTENT / "aimc-llm-agent.tgz"
WORKDIR = CONTENT / "aimc-llm-agent"
CONFIG = CONTENT / "aimc-llm-agent-config.json"
SUMMARY = CONTENT / "aimc-llm-agent-colab-summary.json"


def run(command: list[str], *, cwd: Path, timeout: int = 7200, env: dict[str, str] | None = None) -> dict[str, object]:
    print("$ " + " ".join(command), flush=True)
    try:
        result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout, check=False)
        if result.stdout:
            print(result.stdout[-5000:], flush=True)
        if result.stderr:
            print(result.stderr[-5000:], file=sys.stderr, flush=True)
        return {
            "command": command,
            "returncode": result.returncode,
            "status": "passed" if result.returncode == 0 else "failed",
            "stdout_tail": result.stdout[-5000:],
            "stderr_tail": result.stderr[-5000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "returncode": None, "status": "blocked", "stdout_tail": "", "stderr_tail": f"timeout: {exc}"}


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def add_model_provenance(path: Path, *, model_id: str, gpu_probe: dict[str, object]) -> None:
    """Bind the downloaded benchmark to the runtime that actually ran it."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("evidence_sha256", None)
    payload["model_provenance"] = {
        "schema_version": "real-model-runtime-provenance-v1",
        "provider": "google-colab",
        "model_id": model_id,
        "accelerator": "cuda",
        "gpu": str(gpu_probe.get("stdout_tail", "")).strip(),
        "weights_downloaded_in_runtime": True,
        "source_archive_only": True,
        "claim_boundary": "Runtime provenance identifies the model execution only; it does not authorize RTL edits or release signoff.",
    }
    payload["evidence_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    write_json(path, payload)


def main() -> int:
    if not ARCHIVE.is_file():
        raise SystemExit(f"missing archive: {ARCHIVE}")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        archive.extractall(CONTENT, filter="data")
    if not WORKDIR.is_dir():
        raise SystemExit(f"archive did not create {WORKDIR}")

    config = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.is_file() else {}
    model_id = str(config.get("model_id") or "Qwen/Qwen2.5-0.5B-Instruct")
    model_cache = WORKDIR / ".artifacts" / "colab-model"
    model_cache.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update({"AIMC_MODEL_ID": model_id, "AIMC_MODEL_DIR": str(model_cache)})

    gpu_probe = run(["bash", "-lc", "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"], cwd=WORKDIR, timeout=60, env=environment)
    if gpu_probe["status"] != "passed":
        write_json(SUMMARY, {"status": "blocked", "model_id": model_id, "steps": [gpu_probe]})
        return 1

    install = run(["bash", "-lc", "apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iverilog verilator yosys"], cwd=WORKDIR, timeout=1800, env=environment)
    python_install = run([sys.executable, "-m", "pip", "install", "-q", "transformers==4.51.3", "huggingface_hub", "torch", "lm-format-enforcer"], cwd=WORKDIR, timeout=1800, env=environment)
    if install["status"] != "passed" or python_install["status"] != "passed":
        write_json(SUMMARY, {"status": "blocked", "model_id": model_id, "steps": [gpu_probe, install, python_install]})
        return 1

    download = run(
        [sys.executable, "-c", "from huggingface_hub import snapshot_download; import os; snapshot_download(os.environ['AIMC_MODEL_ID'], local_dir=os.environ['AIMC_MODEL_DIR'])"],
        cwd=WORKDIR,
        timeout=3600,
        env=environment,
    )
    if download["status"] != "passed":
        write_json(SUMMARY, {"status": "blocked", "model_id": model_id, "steps": [gpu_probe, install, python_install, download]})
        return 1

    output = WORKDIR / ".artifacts" / "llm-agent-benchmark-colab.json"
    environment.update({
        "VERIFICATION_LLM_BATCH_COMMAND": f"{sys.executable} scripts/hf_llm_batch_backend.py",
        "VERIFICATION_HF_MODEL": str(model_cache),
        "VERIFICATION_HF_DEVICE": "cuda",
        "VERIFICATION_HF_JSON_CONSTRAINED": "1",
        "VERIFICATION_HF_MAX_NEW_TOKENS": "512",
        "VERIFICATION_AIMC_MUTATION": "1",
        "VERIFICATION_AIMC_ROOT_CAUSE": "1",
        "VERIFICATION_AIMC_REPAIR": "1",
        "VERIFICATION_COUNTER_REPAIR": "1",
        "VERIFICATION_TIMEOUT_REPAIR": "1",
        "VERIFICATION_REGISTER_REPAIR": "1",
        "AIMC_MODEL_ID": model_id,
        "AIMC_MODEL_DIR": str(model_cache),
    })
    benchmark = subprocess.run(
        [sys.executable, "scripts/run_llm_agent_benchmark.py", "--output", str(output)],
        cwd=WORKDIR,
        env=environment,
        text=True,
        capture_output=True,
        timeout=7200,
        check=False,
    )
    benchmark_record = {
        "command": [sys.executable, "scripts/run_llm_agent_benchmark.py", "--output", str(output)],
        "returncode": benchmark.returncode,
        "status": "passed" if benchmark.returncode == 0 else "failed",
        "stdout_tail": benchmark.stdout[-5000:],
        "stderr_tail": benchmark.stderr[-5000:],
    }
    if benchmark_record["status"] == "passed":
        add_model_provenance(output, model_id=model_id, gpu_probe=gpu_probe)
    verify = run([sys.executable, "scripts/verify_llm_model_evaluation.py", str(output)], cwd=WORKDIR, timeout=180)
    # Exercise the same four-workstream orchestrator with the resident model
    # worker.  The provider-free matrices inside this demo retain their mock
    # fixture, while the main pipeline uses VERIFICATION_LLM_BATCH_COMMAND via
    # the validated single-request fallback.
    environment.pop("VERIFICATION_LLM_COMMAND", None)
    full_pipeline_path = WORKDIR / ".artifacts" / "real-four-workstream-colab.json"
    full_pipeline = subprocess.run(
        [sys.executable, "colab/run_four_workstream_colab.py"],
        cwd=WORKDIR, env=environment, text=True, capture_output=True,
        timeout=7200, check=False,
    )
    full_pipeline_record = {
        "command": [sys.executable, "colab/run_four_workstream_colab.py"],
        "returncode": full_pipeline.returncode,
        "status": "passed" if full_pipeline.returncode == 0 else "failed",
        "stdout_tail": full_pipeline.stdout[-5000:],
        "stderr_tail": full_pipeline.stderr[-5000:],
    }
    if full_pipeline.returncode == 0:
        try:
            write_json(full_pipeline_path, json.loads(full_pipeline.stdout))
        except (TypeError, ValueError) as error:
            full_pipeline_record["status"] = "failed"
            full_pipeline_record["parse_error"] = str(error)
    else:
        # The Colab wrapper persists the complete JSON result beside its
        # exception path when the model is rejected.  Prefer that structured
        # result over stderr/stdout tails in the durable benchmark artifact.
        result_match = re.search(r"complete result: (\S+)", full_pipeline.stderr)
        pipeline_result_path = Path(result_match.group(1)) if result_match else None
        if pipeline_result_path is not None and pipeline_result_path.exists():
            try:
                full_pipeline_record["pipeline_result"] = json.loads(pipeline_result_path.read_text(encoding="utf-8"))
            except (TypeError, ValueError) as error:
                full_pipeline_record["pipeline_result_parse_error"] = str(error)
        write_json(full_pipeline_path, full_pipeline_record)
    # Evaluate the same resident real-model worker on a declared held-out
    # repair split.  This is separate from the 11-case diagnosis benchmark so
    # a strong result cannot hide a repair-generalization failure.
    heldout_root = WORKDIR / ".artifacts" / "agent-repair-heldout-colab"
    heldout_command = [
        sys.executable, "scripts/run_heldout_agent_repair_evaluation.py",
        "--output", str(heldout_root), "--backend", "local",
    ]
    heldout = subprocess.run(
        heldout_command, cwd=WORKDIR, env=environment, text=True,
        capture_output=True, timeout=14400, check=False,
    )
    heldout_record = {
        "command": heldout_command,
        "returncode": heldout.returncode,
        "status": "passed" if heldout.returncode == 0 else "failed",
        "stdout_tail": heldout.stdout[-5000:],
        "stderr_tail": heldout.stderr[-5000:],
    }
    heldout_report_path = heldout_root / "agent-repair-heldout-evaluation-report.json"
    if heldout_report_path.is_file():
        try:
            heldout_record["report"] = json.loads(heldout_report_path.read_text(encoding="utf-8"))
        except (TypeError, ValueError) as error:
            heldout_record["report_parse_error"] = str(error)
    heldout_check = run(
        [sys.executable, "scripts/check_heldout_agent_repair_evaluation.py", str(heldout_report_path), "--require-real-backend"],
        cwd=WORKDIR, timeout=180,
    ) if heldout_report_path.is_file() else {"status": "blocked", "error": "held-out report was not produced"}
    summary = {
        "schema_version": "aimc-llm-agent-colab-run-v1",
        "status": "passed" if benchmark_record["status"] == "passed" and verify["status"] == "passed" and full_pipeline_record["status"] == "passed" and heldout_record["status"] == "passed" and heldout_check.get("status") == "passed" else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "model_weights": "downloaded inside Colab to a private runtime directory; not included in the source archive",
        "steps": [gpu_probe, install, python_install, download, benchmark_record, verify, full_pipeline_record, heldout_record, heldout_check],
        "benchmark_artifact": str(output),
        "full_pipeline_artifact": str(full_pipeline_path),
        "heldout_repair_artifact": str(heldout_report_path),
        "claim_boundary": "Real-model proposal quality is accepted only if every case is grounded, diagnosis-matching, review-required, and adversarially accepted. This does not prove silicon correctness or autonomous tapeout.",
    }
    write_json(SUMMARY, summary)
    write_json(WORKDIR / "aimc-llm-agent-colab-summary.json", summary)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
