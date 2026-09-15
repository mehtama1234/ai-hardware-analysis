"""Review or apply one repository-agent patch candidate to a disposable copy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.repair import RepairProposal, run_approved_repair_retest


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-run", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--command", nargs="+", required=True)
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--reviewer")
    parser.add_argument("--approval-note")
    args = parser.parse_args()
    run = json.loads(args.agent_run.read_text(encoding="utf-8"))
    candidate = run.get("patch_candidate")
    if not isinstance(candidate, dict) or candidate.get("status") != "review_required":
        raise SystemExit("agent run does not contain a validated review-required patch candidate")
    if Path(str(candidate.get("source"))).resolve() != args.source.resolve():
        raise SystemExit("candidate source does not match supplied source")
    proposal = RepairProposal(
        requirement_id=str(candidate.get("requirement_id") or "AGENT-REPAIR"),
        file=str(candidate["source"]), line=int(candidate["line"]),
        before=str(candidate["before"]), after=str(candidate["after"]),
        rationale=str(run.get("team", {}).get("results", [{}])[2].get("proposal", {}).get("rationale", "approved repository-agent repair")),
        edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
    )
    if not args.approve:
        review = {
            "schema_version": "repository-agent-repair-review-v1", "status": "review_required",
            "agent_run": str(args.agent_run.resolve()), "source": str(args.source.resolve()),
            "destination": str(args.destination.resolve()), "proposal": {"requirement_id": proposal.requirement_id, "file": proposal.file, "line": proposal.line, "before": proposal.before, "after": proposal.after, "rationale": proposal.rationale, "edit_operator": proposal.edit_operator},
            "human_approval": "not_requested",
            "claim_boundary": "review package only; no source mutation or retest",
        }
        review["review_sha256"] = digest(review)
        args.run_root.mkdir(parents=True, exist_ok=True)
        path = args.run_root / "repair-review.json"
        path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": review["status"], "review": str(path)}, sort_keys=True))
        return 0
    if not isinstance(args.reviewer, str) or not args.reviewer.strip() or not isinstance(args.approval_note, str) or not args.approval_note.strip():
        raise SystemExit("--approve requires --reviewer and --approval-note")
    result = run_approved_repair_retest(
        args.source, args.destination, proposal, args.command, run_root=args.run_root,
        source_revision=str(run["source_revision"]), human_approved=True,
    )
    result["reviewer"] = args.reviewer
    result["approval_note"] = args.approval_note
    result["result_sha256"] = digest({key: value for key, value in result.items() if key != "result_sha256"})
    path = args.run_root / "approved-repair-review.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "reviewer": args.reviewer, "report": str(path)}, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
