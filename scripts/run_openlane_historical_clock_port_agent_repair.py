"""Replay OpenLane's historical indexed-bus clock-port validation fix."""

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
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
HISTORICAL_COMMIT = "c5763988"
SOURCE_RELATIVE = Path("scripts/check_clock_ports.py")
OLD = """    top_module = netlist[\"modules\"][top]
    ports = top_module[\"ports\"]
    for clock_port in clock_ports:
        if clock_port not in ports:
            print(f\"{clock_port} \", end=\"\")
"""
NEW = """    valid_input_ports = set()
    for name, info in netlist[\"modules\"][top][\"ports\"].items():
        if info[\"direction\"] not in [\"input\", \"inout\"]:
            continue
        width = len(info[\"bits\"])
        offset = info.get(\"offset\", 0)
        if width == 1:
            valid_input_ports.add(name)
        msb = offset + width - 1
        lsb = offset
        for bit in range(lsb, msb + 1):
            valid_input_ports.add(f\"{name}[{bit}]\")
    for clock_port in clock_ports:
        if clock_port not in valid_input_ports:
            print(f\"{clock_port} \", end=\"\")
"""

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(root: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    netlist = root / "netlist.json"
    netlist.write_text(json.dumps({"modules": {"top": {"ports": {"clk_bus": {"direction": "input", "bits": [1, 2, 3, 4]}}}}}), encoding="utf-8")
    completed = subprocess.run([sys.executable, str(root / SOURCE_RELATIVE), "--netlist-in", str(netlist), "--top", "top", "clk_bus[0]"], cwd=root, capture_output=True, text=True, check=False)
    (output / "stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    return "passed" if completed.returncode == 0 and completed.stdout.strip() == "" else "failed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args(); args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    try:
        historical_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}^:{SOURCE_RELATIVE}"], text=True)
        fixed_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}:{SOURCE_RELATIVE}"], text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "reason": f"historical source unavailable: {exc}"}, sort_keys=True)); return 1
    canonical_hash = hashlib.sha256(fixed_source.encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="openlane-historical-clock-port-") as temporary:
        staging = Path(temporary); mutated_root, repaired_root = staging / "mutated", staging / "repaired"
        for root, source_text in ((mutated_root, historical_source), (repaired_root, fixed_source)):
            destination = root / SOURCE_RELATIVE; destination.parent.mkdir(parents=True, exist_ok=True); destination.write_text(source_text, encoding="utf-8")
        baseline_status = execute(mutated_root, args.output / "baseline")
        agent = run_repository_agent(task_id="openlane-clock-port-indexed-bus-historical-fix", source_revision=f"{HISTORICAL_COMMIT}^", evidence=[str(SOURCE_RELATIVE), f"OpenLane commit {HISTORICAL_COMMIT} historical fix", "indexed input-bus clock port regression"], failure_context="check_clock_ports must accept an indexed bit of a multi-bit input as a valid clock port", repair_before=OLD, repair_after=NEW, repair_source=mutated_root / SOURCE_RELATIVE, backend="local", output_root=args.output / "agent")
        candidate = agent.get("patch_candidate", {}); repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(requirement_id="openlane-clock-port-indexed-bus-historical-fix", file=str(candidate["source"]), line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]), rationale="benchmark-only historical OpenLane clock-port repair", edit_operator=str(candidate.get("edit_operator", "exact_text_replace")))
            apply_to_copy(mutated_root / SOURCE_RELATIVE, repaired_root / SOURCE_RELATIVE, proposal, human_approved=True); repaired_status = execute(repaired_root, args.output / "repaired")
        report = {"schema_version": "openlane-historical-clock-port-agent-repair-report-v1", "repository": "OpenLane", "repository_revision": f"{HISTORICAL_COMMIT}^", "historical_fix_commit": HISTORICAL_COMMIT, "source_file": str(SOURCE_RELATIVE), "canonical_fixed_source_sha256": canonical_hash, "backend": args.backend, "task_id": "openlane-clock-port-indexed-bus-historical-fix", "baseline_status": baseline_status, "agent_status": agent["team"]["status"], "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")), "repaired_status": repaired_status, "status": "passed" if baseline_status == "failed" and repaired_status == "passed" else "blocked", "claim_boundary": "one real historical OpenLane indexed-bus clock-port fix replayed through disposable agent repair; not repository-scale generalization"}
    report["report_sha256"] = digest(report); path = args.output / "openlane-historical-clock-port-agent-repair-report.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps({"status": report["status"], "historical_fix_commit": HISTORICAL_COMMIT, "report": str(path)}, sort_keys=True)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
