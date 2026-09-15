"""Replay the historical OpenROAD report-gallery fix through agent closure."""

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
SOURCE_RELATIVE = Path("flow/util/genReportTable.py")
OLD = '        if file.endswith(".webp"):'
NEW = '        if file.lower().endswith(IMAGE_EXTENSIONS):'

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def populate_fixture(root: Path) -> None:
    (root / "logs" / "sky130" / "gcd" / "base").mkdir(parents=True, exist_ok=True)
    report = root / "reports" / "sky130" / "gcd" / "base"
    report.mkdir(parents=True, exist_ok=True)
    (report / "design-dir.txt").write_text("designs/sky130/gcd\n", encoding="utf-8")
    design = root / "designs" / "sky130" / "gcd"
    design.mkdir(parents=True, exist_ok=True)
    (design / "metadata-base-ok.json").write_text('{"finish__timing__wns": 0}\n', encoding="utf-8")
    (design / "rules-base.json").write_text('{}\n', encoding="utf-8")
    (report / "metadata.json").write_text('{"finish__timing__wns": 0}\n', encoding="utf-8")
    # Qt can produce a doubled extension when a WebP writer is unavailable.
    (report / "final_clocks.webp.png").write_bytes(b"synthetic image fixture\n")


def execute(root: Path, source_root: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    # genReportTable.py changes its working directory to the directory that
    # contains ``logs`` and ``reports`` (the checkout's flow/ directory).
    flow_root = root / "flow"
    populate_fixture(flow_root)
    command = [sys.executable, str(source_root / SOURCE_RELATIVE)]
    completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    (output / "stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    gallery = flow_root / "reports" / "report-gallery-gcd.html"
    return "passed" if completed.returncode == 0 and gallery.is_file() and "final_clocks.webp.png" in gallery.read_text(encoding="utf-8") else "failed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    source = REPO / SOURCE_RELATIVE
    if not REPO.is_dir() or not source.is_file():
        report = {"status": "blocked", "reason": "OpenROAD checkout or gallery generator missing"}
        (args.output / "openroad-historical-gallery-agent-repair-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, sort_keys=True)); return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True)); return 1
    canonical_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="openroad-historical-gallery-") as temporary:
        staging = Path(temporary)
        mutated_root, repaired_root = staging / "mutated", staging / "repaired"
        for root in (mutated_root, repaired_root):
            destination = root / SOURCE_RELATIVE
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        mutated_source = mutated_root / SOURCE_RELATIVE
        repaired_source = repaired_root / SOURCE_RELATIVE
        text = mutated_source.read_text(encoding="utf-8")
        if text.count(NEW) != 1:
            raise RuntimeError("OpenROAD gallery generator does not contain the historical fixed expression")
        mutated_source.write_text(text.replace(NEW, OLD, 1), encoding="utf-8")
        baseline_status = execute(mutated_root, mutated_root, args.output / "baseline")
        agent = run_repository_agent(
            task_id="openroad-report-gallery-image-extension-historical-fix",
            source_revision=REVISION,
            evidence=[str(SOURCE_RELATIVE), "OpenROAD commit bad83a4f1 historical fix", "doubled image-extension gallery regression"],
            failure_context="report-gallery generation must include images emitted as .webp.png and retain their intended view name",
            repair_before=OLD, repair_after=NEW, repair_source=mutated_source,
            backend="local", output_root=args.output / "agent",
        )
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(
                requirement_id="openroad-report-gallery-image-extension-historical-fix", file=str(candidate["source"]),
                line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]),
                rationale="benchmark-only historical OpenROAD repair evaluation",
                edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
            )
            apply_to_copy(mutated_source, repaired_source, proposal, human_approved=True)
            repaired_status = execute(repaired_root, repaired_root, args.output / "repaired")
        report = {
            "schema_version": "openroad-historical-gallery-agent-repair-report-v1",
            "repository": "OpenROAD-flow-scripts", "repository_revision": revision,
            "historical_fix_commit": "bad83a4f1", "source_file": str(SOURCE_RELATIVE),
            "canonical_source_sha256": canonical_hash, "backend": args.backend,
            "task_id": "openroad-report-gallery-image-extension-historical-fix",
            "baseline_status": baseline_status, "agent_status": agent["team"]["status"],
            "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
            "repaired_status": repaired_status,
            "canonical_unchanged": canonical_hash == hashlib.sha256(source.read_bytes()).hexdigest(),
            "status": "passed" if baseline_status == "failed" and repaired_status == "passed" and canonical_hash == hashlib.sha256(source.read_bytes()).hexdigest() else "blocked",
            "claim_boundary": "one real historical OpenROAD report-gallery fix replayed through a disposable agent repair; not repository-scale generalization",
        }
    report["report_sha256"] = digest(report)
    path = args.output / "openroad-historical-gallery-agent-repair-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "repository_revision": revision, "historical_fix_commit": "bad83a4f1", "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
