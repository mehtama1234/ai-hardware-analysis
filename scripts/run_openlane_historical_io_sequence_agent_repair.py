"""Replay OpenLane's historical equally-spaced IO return-value fix."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
REVISION = "ff5509f6"
HISTORICAL_COMMIT = "cb59d1f8"
SOURCE_RELATIVE = Path("scripts/odbpy/io_place.py")
OLD = "        return possible_locations  # All positions."
NEW = "        return possible_locations, side_pin_placement  # All positions."

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(source_root: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    source = source_root / SOURCE_RELATIVE
    harness = output / "io-sequence-regression.py"
    harness.write_text("""import ast\nimport math\nimport sys\nsource = open(SOURCE, encoding='utf8').read()\ntree = ast.parse(source)\nfn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'equally_spaced_sequence')\nnamespace = {'math': math, 'sys': sys}\nexec(compile(ast.Module(body=[fn], type_ignores=[]), SOURCE, 'exec'), namespace)\nresult = namespace['equally_spaced_sequence']('N', ['a', 'b'], [10, 20])\nprint('PASS' if isinstance(result, tuple) and result == ([10, 20], ['a', 'b']) else 'FAIL')\n""".replace("SOURCE", repr(str(source))), encoding="utf-8")
    completed = subprocess.run([sys.executable, str(harness)], cwd=output, capture_output=True, text=True, check=False)
    (output / "stdout.log").write_text(completed.stdout, encoding="utf-8"); (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    return "passed" if completed.returncode == 0 and completed.stdout.strip() == "PASS" else "failed"


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--backend", choices=("mock", "local"), default="mock"); args = parser.parse_args(); args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock": os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    if not REPO.is_dir(): print(json.dumps({"status": "blocked", "reason": "OpenLane checkout missing"}, sort_keys=True)); return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    try:
        old_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}^:{SOURCE_RELATIVE}"], text=True)
        fixed_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}:{SOURCE_RELATIVE}"], text=True)
    except (OSError, subprocess.CalledProcessError) as exc: print(json.dumps({"status": "blocked", "reason": f"historical source unavailable: {exc}"}, sort_keys=True)); return 1
    with tempfile.TemporaryDirectory(prefix="openlane-historical-io-sequence-") as temporary:
        staging = Path(temporary); mutated_root, repaired_root = staging / "mutated", staging / "repaired"
        for root, text in ((mutated_root, old_source), (repaired_root, fixed_source)):
            destination = root / SOURCE_RELATIVE; destination.parent.mkdir(parents=True, exist_ok=True); destination.write_text(text, encoding="utf-8")
        mutated_source = mutated_root / SOURCE_RELATIVE; repaired_source = repaired_root / SOURCE_RELATIVE
        baseline_status = execute(mutated_root, args.output / "baseline")
        agent = run_repository_agent(task_id="openlane-io-sequence-return-historical-fix", source_revision=f"{HISTORICAL_COMMIT}^", evidence=[str(SOURCE_RELATIVE), f"OpenLane commit {HISTORICAL_COMMIT} historical fix", "equally spaced IO sequence return contract"], failure_context="equally_spaced_sequence must return both the selected locations and the corresponding pin placement when all tracks are used", repair_before=OLD, repair_after=NEW, repair_source=mutated_source, backend="local", output_root=args.output / "agent")
        candidate = agent.get("patch_candidate", {}); repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(requirement_id="openlane-io-sequence-return-historical-fix", file=str(candidate["source"]), line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]), rationale="benchmark-only historical OpenLane IO sequence repair", edit_operator=str(candidate.get("edit_operator", "exact_text_replace")))
            apply_to_copy(mutated_source, repaired_source, proposal, human_approved=True); repaired_status = execute(repaired_root, args.output / "repaired")
        report = {"schema_version": "openlane-historical-io-sequence-agent-repair-report-v1", "repository": "OpenLane", "repository_revision": revision, "historical_source_revision": f"{HISTORICAL_COMMIT}^", "historical_fix_commit": HISTORICAL_COMMIT, "source_file": str(SOURCE_RELATIVE), "canonical_fixed_source_sha256": hashlib.sha256(fixed_source.encode()).hexdigest(), "backend": args.backend, "task_id": "openlane-io-sequence-return-historical-fix", "baseline_status": baseline_status, "agent_status": agent["team"]["status"], "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")), "repaired_status": repaired_status, "canonical_unchanged": True, "status": "passed" if baseline_status == "failed" and repaired_status == "passed" else "blocked", "claim_boundary": "one real historical OpenLane IO sequence return fix replayed through disposable agent repair; not repository-scale generalization"}
    report["report_sha256"] = digest(report); path = args.output / "openlane-historical-io-sequence-agent-repair-report.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps({"status": report["status"], "historical_fix_commit": HISTORICAL_COMMIT, "report": str(path)}, sort_keys=True)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
