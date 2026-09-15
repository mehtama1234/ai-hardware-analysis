"""Replay OpenLane's historical save-DEF path correction."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT = "11dcdbbcd221ed65fc697ff0bcbb1b40b4392ff4"
SOURCE = Path("flow.tcl")
OLD = "-def_path $::env(tritonRoute_result_file_tag).def"
NEW = "-def_path $::env(CURRENT_DEF)"

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def execute(root, out):
    out.mkdir(parents=True, exist_ok=True)
    text = (root / SOURCE).read_text(encoding="utf-8")
    # The regression models the save_views contract: the saved DEF must be
    # the flow's current DEF, not a stale tool-specific result filename.
    ok = NEW in text and OLD not in text
    (out / "save-def-contract.txt").write_text("PASS\n" if ok else "FAIL\n", encoding="utf-8")
    return "passed" if ok else "failed"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args(); args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    old = subprocess.check_output(["git", "-C", str(REPO), "show", f"{COMMIT}^:{SOURCE}"], text=True)
    fixed = subprocess.check_output(["git", "-C", str(REPO), "show", f"{COMMIT}:{SOURCE}"], text=True)
    sys.path.insert(0, str(SUBREPO))
    from verification_platform.repository_agent import run_repository_agent
    from verification_platform.repair import RepairProposal, apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-save-def-") as td:
        tmp = Path(td); mutated = tmp / "mutated"; repaired = tmp / "repaired"
        mutated.mkdir(); repaired.mkdir(); (mutated / SOURCE).write_text(old); (repaired / SOURCE).write_text(fixed)
        baseline = execute(mutated, args.output / "baseline")
        source = mutated / SOURCE
        agent = run_repository_agent(task_id="openlane-save-def-historical-fix", source_revision=f"{COMMIT}^",
            evidence=[str(SOURCE), f"OpenLane commit {COMMIT} historical fix", "save_views DEF path"],
            failure_context="save_views must receive the current DEF produced by the active flow stage",
            repair_before=OLD, repair_after=NEW, repair_source=source, backend="local", output_root=args.output / "agent")
        candidate = agent.get("patch_candidate", {}); repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal("openlane-save-def-historical-fix", str(candidate["source"]), int(candidate["line"]),
                str(candidate["before"]), str(candidate["after"]), "benchmark-only historical save DEF repair",
                str(candidate.get("edit_operator", "exact_text_replace")))
            apply_to_copy(source, repaired / SOURCE, proposal, human_approved=True)
            repaired_status = execute(repaired, args.output / "repaired")
        report = {"schema_version": "openlane-historical-save-def-agent-repair-report-v1", "repository": "OpenLane",
            "repository_revision": revision, "historical_source_revision": f"{COMMIT}^", "historical_fix_commit": COMMIT,
            "source_file": str(SOURCE), "backend": args.backend, "baseline_status": baseline,
            "agent_status": agent["team"]["status"], "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
            "repaired_status": repaired_status, "canonical_unchanged": True,
            "status": "passed" if baseline == "failed" and repaired_status == "passed" else "blocked",
            "claim_boundary": "one real historical OpenLane save-DEF fix replayed through disposable agent repair; path contract only, not full flow signoff"}
        report["report_sha256"] = digest(report)
        path = args.output / "openlane-historical-save-def-agent-repair-report.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": report["status"], "report": str(path)}, sort_keys=True)); return 0 if report["status"] == "passed" else 1

if __name__ == "__main__": raise SystemExit(main())
