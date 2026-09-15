"""Run a bounded agent repair on a native OpenROAD asynchronous FIFO."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
REVISION = "be0dca0b1"
SOURCES = [
    Path("flow/designs/src/fifo/fifo.v"),
    Path("flow/designs/src/fifo/fifo1.v"),
    Path("flow/designs/src/fifo/fifomem.v"),
    Path("flow/designs/src/fifo/rptr_empty.v"),
    Path("flow/designs/src/fifo/wptr_full.v"),
    Path("flow/designs/src/fifo/sync_r2w.v"),
    Path("flow/designs/src/fifo/sync_w2r.v"),
]
SOURCE_RELATIVE = Path("flow/designs/src/fifo/rptr_empty.v")
OLD = "    if (!rrst_n) rempty <= 1'b1;"
NEW = "    if (!rrst_n) rempty <= 1'b0;"

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(root: Path, source_root: Path, output: Path) -> str:
    binary = output / "fifo.vvp"
    output.mkdir(parents=True, exist_ok=True)
    compile_run = subprocess.run(
        ["iverilog", "-g2012", "-o", str(binary),
         *[str(source_root / source) for source in SOURCES],
         str(root / "openroad_fifo_tb.sv")],
        cwd=root, capture_output=True, text=True, check=False,
    )
    compile_text = compile_run.stdout + compile_run.stderr
    (output / "compile.log").write_text(compile_text, encoding="utf-8")
    if compile_run.returncode != 0:
        (output / "simulation.log").write_text("", encoding="utf-8")
        return "blocked"
    simulated = subprocess.run(["vvp", str(binary)], cwd=root, capture_output=True, text=True, check=False)
    simulation_text = simulated.stdout + simulated.stderr
    (output / "simulation.log").write_text(simulation_text, encoding="utf-8")
    if "PASS fifo reset state" in simulation_text and "FAIL " not in simulation_text and simulated.returncode == 0:
        return "passed"
    return "failed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    if not REPO.is_dir() or not (REPO / SOURCES[0]).is_file():
        report = {"status": "blocked", "reason": "OpenROAD FIFO source or checkout missing"}
        (args.output / "openroad-fifo-agent-repair-closure-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, sort_keys=True))
        return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True))
        return 1
    canonical_hash = hashlib.sha256((REPO / SOURCE_RELATIVE).read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="openroad-fifo-agent-repair-") as temporary:
        staging = Path(temporary)
        roots = {name: staging / name for name in ("mutated", "repaired")}
        for root in roots.values():
            for source in SOURCES:
                destination = root / source
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPO / source, destination)
        shutil.copy2(ROOT / "benchmarks/repository_scale/openroad_fifo_reset_tb.sv", staging / "openroad_fifo_tb.sv")
        mutated_source = roots["mutated"] / SOURCE_RELATIVE
        repaired_source = roots["repaired"] / SOURCE_RELATIVE
        text = mutated_source.read_text(encoding="utf-8")
        if text.count(OLD) != 1:
            raise RuntimeError("OpenROAD FIFO reset anchor was not unique")
        mutated_source.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
        baseline_status = execute(staging, roots["mutated"], args.output / "baseline")
        agent = run_repository_agent(
            task_id="openroad-fifo-reset-empty",
            source_revision=REVISION,
            evidence=[str(SOURCE_RELATIVE), "native OpenROAD checkout", "FIFO reset baseline failure"],
            failure_context="the native asynchronous FIFO must report empty immediately after active-low read reset",
            repair_before=NEW, repair_after=OLD, repair_source=mutated_source,
            backend="local", output_root=args.output / "agent",
        )
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(
                requirement_id="openroad-fifo-reset-empty", file=str(candidate["source"]),
                line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]),
                rationale="benchmark-only native FIFO repair evaluation",
                edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
            )
            apply_to_copy(mutated_source, repaired_source, proposal, human_approved=True)
            repaired_status = execute(staging, roots["repaired"], args.output / "repaired")
        report = {
            "schema_version": "openroad-fifo-agent-repair-closure-report-v1",
            "repository": "OpenROAD-flow-scripts", "repository_revision": revision,
            "backend": args.backend, "task_id": "openroad-fifo-reset-empty",
            "source_file": str(SOURCE_RELATIVE), "canonical_source_sha256": canonical_hash,
            "baseline_status": baseline_status, "agent_status": agent["team"]["status"],
            "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
            "repaired_status": repaired_status,
            "canonical_unchanged": canonical_hash == hashlib.sha256((REPO / SOURCE_RELATIVE).read_bytes()).hexdigest(),
            "status": "passed" if baseline_status == "failed" and repaired_status == "passed" and canonical_hash == hashlib.sha256((REPO / SOURCE_RELATIVE).read_bytes()).hexdigest() else "blocked",
            "claim_boundary": "one native OpenROAD asynchronous FIFO reset mutation and bounded repair; not CDC stress or full project regression",
        }
    report["report_sha256"] = digest(report)
    path = args.output / "openroad-fifo-agent-repair-closure-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "repository_revision": revision, "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
