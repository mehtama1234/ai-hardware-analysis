#!/usr/bin/env python3
"""Run the provider-free LLM diagnosis-to-human-review boundary."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import re


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(f"command failed ({completed.returncode}): {' '.join(command)}\n{detail}")
    return completed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="fresh directory for the run artifacts")
    parser.add_argument(
        "--backend-command",
        default="python3 scripts/mock_llm_backend.py",
        help="JSONL batch backend command; defaults to the deterministic fixture",
    )
    parser.add_argument(
        "--model-report",
        type=Path,
        help="use an existing verified benchmark report (for example, a real Colab artifact)",
    )
    decision = parser.add_mutually_exclusive_group()
    decision.add_argument("--approve", action="store_true", help="apply the bounded repair to the disposable output copy")
    decision.add_argument("--reject", action="store_true", help="record a human rejection without applying either repair")
    parser.add_argument("--reviewer", help="human reviewer identity required with --approve")
    parser.add_argument("--approval-note", help="human approval note required with --approve")
    parser.add_argument("--physical-handoff", type=Path, help="optional passed seeded-counter RTL-to-GDS handoff to hash-link")
    parser.add_argument(
        "--run-physical",
        action="store_true",
        help="after approval, run formal and OpenLane on the disposable repaired RTL",
    )
    parser.add_argument("--physical-tag", help="OpenLane run tag; defaults to a tag derived from --output")
    args = parser.parse_args()
    if args.run_physical and not args.approve:
        raise SystemExit("--run-physical requires --approve")
    if args.run_physical and args.physical_handoff:
        raise SystemExit("--run-physical and --physical-handoff are mutually exclusive")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to reuse non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    benchmark = output / "llm-agent-benchmark.json"
    if args.model_report:
        model_report = args.model_report.resolve()
        if not model_report.is_file():
            raise SystemExit(f"model report does not exist: {model_report}")
        verification = run([sys.executable, "scripts/verify_llm_model_evaluation.py", str(model_report), "--require-real-model"])
        shutil.copy2(model_report, benchmark)
        benchmark_stdout = verification.stdout.strip()
    else:
        environment = os.environ.copy()
        environment.update(
            {
                "VERIFICATION_LLM_BATCH_COMMAND": args.backend_command,
                "VERIFICATION_COUNTER_REPAIR": "1",
                "VERIFICATION_TIMEOUT_REPAIR": "1",
                "VERIFICATION_REGISTER_REPAIR": "1",
            }
        )
        benchmark_result = run(
            [sys.executable, "scripts/run_llm_agent_benchmark.py", "--output", str(benchmark)],
            env=environment,
        )
        benchmark_stdout = benchmark_result.stdout.strip()
    benchmark_payload = json.loads(benchmark.read_text(encoding="utf-8"))
    model_provenance = benchmark_payload.get("model_provenance")
    model_execution = {
        "kind": "real_model" if isinstance(model_provenance, dict) else "provider_free_fixture",
        "benchmark_sha256": digest(benchmark),
        "provenance": model_provenance,
    }

    review_dir = output / "repair-review"
    repair_command = [
        sys.executable,
        "scripts/run_llm_approved_counter_repair.py",
        "--model-report",
        str(benchmark),
        "--output",
        str(review_dir),
    ]
    if args.approve or args.reject:
        if not args.reviewer or not args.approval_note:
            raise SystemExit("--approve/--reject requires --reviewer and --approval-note")
        repair_command.extend(["--approve" if args.approve else "--reject", "--reviewer", args.reviewer, "--approval-note", args.approval_note])
    review_result = run(repair_command)
    review = json.loads((review_dir / "repair-review.json").read_text(encoding="utf-8"))
    held_out_dir = output / "held-out-timeout-repair"
    held_out_command = [
        sys.executable,
        "scripts/run_llm_approved_timeout_repair.py",
        "--model-report",
        str(benchmark),
        "--output",
        str(held_out_dir),
    ]
    if args.approve or args.reject:
        held_out_command.extend(["--approve" if args.approve else "--reject", "--reviewer", args.reviewer, "--approval-note", args.approval_note])
    held_out_result = run(held_out_command)
    held_out_review_path = held_out_dir / "repair-review.json"
    held_out_review = json.loads(held_out_review_path.read_text(encoding="utf-8"))
    physical = None
    if args.physical_handoff:
        physical_path = args.physical_handoff.resolve()
        physical = json.loads(physical_path.read_text(encoding="utf-8"))
        repaired_hash = review.get("retest", {}).get("repaired_sha256")
        if (
            physical.get("schema_version") != "seeded-counter-model-repair-rtl2gds-handoff-v1"
            or physical.get("status") != "passed"
            or physical.get("design") != "seeded_counter"
            or physical.get("physical", {}).get("source_match") is not True
            or physical.get("physical", {}).get("lvs_errors") != 0
            or physical.get("source", {}).get("physical_staged_sha256") != repaired_hash
        ):
            raise SystemExit("physical handoff is not passed or does not match the repaired-source hash")
        physical = {
            "path": str(physical_path),
            "sha256": digest(physical_path),
            "status": physical["status"],
            "source_hash_match": True,
            "lvs_errors": physical["physical"]["lvs_errors"],
            "claim_boundary": "Imported local physical evidence; not a same-run physical execution.",
        }
    check_result = run(
        [
            sys.executable,
            "scripts/check_llm_approved_counter_repair.py",
            str(review_dir / "repair-review.json"),
            "--model-report",
            str(benchmark),
            "--source",
            str(ROOT / "benchmarks/seeded_counter/counter.sv"),
        ]
    )
    physical_report_path = None
    if args.run_physical:
        repaired_source = review_dir / "counter_repaired.sv"
        if not repaired_source.is_file():
            raise SystemExit("approved repair did not produce counter_repaired.sv")
        formal_dir = output / "formal"
        run(
            [
                sys.executable,
                "scripts/run_seeded_counter_formal.py",
                "--repaired-source",
                str(repaired_source),
                "--output",
                str(formal_dir),
            ]
        )
        tag = args.physical_tag or f"agentic_closure_{re.sub(r'[^A-Za-z0-9_]+', '_', output.name)}"
        physical_env = os.environ.copy()
        physical_env.update(
            {
                "AIMC_OPENLANE_DESIGN": "counter",
                "AIMC_OPENLANE_PREP": "seeded-counter-openlane-prep",
                "AIMC_OPENLANE_VERILOG_SOURCE_DIR": str(review_dir),
                "TAG": tag,
            }
        )
        run(["bash", "scripts/run_aimc_openlane_flow.sh"], env=physical_env)
        openlane_root = Path(os.environ.get("OPENLANE_ROOT", str(Path.home() / "eda-tools/OpenLane")))
        physical_run = openlane_root / "designs" / "counter" / "runs" / tag
        physical_report_path = output / "physical-handoff.json"
        run(
            [
                sys.executable,
                "scripts/build_seeded_counter_rtl2gds_handoff.py",
                "--model-report",
                str(benchmark),
                "--repair-report",
                str(review_dir / "repair-review.json"),
                "--formal-report",
                str(formal_dir / "formal-report.json"),
                "--physical-run",
                str(physical_run),
                "--repaired-source",
                str(repaired_source),
                "--output",
                str(physical_report_path),
            ]
        )
        run([sys.executable, "scripts/check_seeded_counter_rtl2gds_handoff.py", str(physical_report_path)])
        physical = {
            "path": str(physical_report_path.relative_to(output)),
            "sha256": digest(physical_report_path),
            "status": "passed",
            "source_hash_match": True,
            "lvs_errors": 0,
            "same_run": True,
            "claim_boundary": "Same-run local OpenLane evidence from the approved disposable repaired RTL; not commercial signoff or silicon evidence.",
        }
    summary = {
        "schema_version": "agentic-hardware-closure-run-v1",
        "status": "passed" if review.get("retest", {}).get("status") == "passed" and held_out_review.get("retest", {}).get("status") == "passed" else ("rejected" if args.reject else "review_required"),
        "benchmark": str(benchmark.relative_to(output)),
        "model_execution": model_execution,
        "repair_review": str((review_dir / "repair-review.json").relative_to(output)),
        "held_out_repair_review": str(held_out_review_path.relative_to(output)),
        "artifacts": {
            "benchmark_sha256": digest(benchmark),
            "repair_review_sha256": digest(review_dir / "repair-review.json"),
            "held_out_repair_review_sha256": digest(held_out_review_path),
        },
        "benchmark_stdout": benchmark_stdout,
        "repair_review_stdout": review_result.stdout.strip(),
        "held_out_repair_review_stdout": held_out_result.stdout.strip(),
        "verification_stdout": check_result.stdout.strip(),
        "approval": review.get("approval", {"status": "required"}),
        "canonical_source_unchanged": review.get("retest", {}).get("original_unchanged", True) and held_out_review.get("retest", {}).get("original_unchanged", True),
        "canonical_source_sha256": digest(ROOT / "benchmarks/seeded_counter/counter.sv"),
        "held_out": {
            "design": "seeded_timeout",
            "status": held_out_review.get("retest", {}).get("status", "review_required"),
            "approval": held_out_review.get("approval", {"status": "required"}),
            "canonical_source_unchanged": held_out_review.get("retest", {}).get("original_unchanged", True),
        },
        "physical_handoff": physical,
        "claim_boundary": "Provider-free diagnosis and bounded copy-only repair/retest evidence; no autonomous signoff, analog authorization, or silicon claim.",
    }
    summary_path = output / "closure-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    run(
        [
            sys.executable,
            "scripts/check_agentic_hardware_closure.py",
            str(summary_path),
            "--source",
            str(ROOT / "benchmarks/seeded_counter/counter.sv"),
        ]
    )
    release_manifest = output / "agentic-hardware-release-manifest.json"
    run(
        [
            sys.executable,
            "scripts/build_agentic_hardware_release_manifest.py",
            "--closure-summary",
            str(summary_path),
            "--output",
            str(release_manifest),
        ]
    )
    run([sys.executable, "scripts/check_agentic_hardware_release_manifest.py", str(release_manifest)])
    print(json.dumps({"status": summary["status"], "output": str(output), "canonical_source_unchanged": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
