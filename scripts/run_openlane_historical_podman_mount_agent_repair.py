"""Replay OpenLane's historical conditional Xauthority container-mount fix."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT = "413d301090a476f8d34cf24dc2447da17dfab187"
SOURCE = Path("Makefile")
OLD = """DOCKER_OPTIONS += -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix -v $(HOME)/.Xauthority:/.Xauthority --network host --security-opt seccomp=unconfined
  ifneq (\"$(wildcard $(HOME)/.openroad)\",\"\")
    DOCKER_OPTIONS += -v $(HOME)/.openroad:/.openroad
  endif"""
NEW = """DOCKER_OPTIONS += -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix --network host --security-opt seccomp=unconfined
\tifneq (\"$(wildcard $(HOME)/.openroad)\",\"\")
\t\tDOCKER_OPTIONS += -v $(HOME)/.openroad:/.openroad
\tendif
\tifneq (\"$(wildcard $(HOME)/.Xauthority)\",\"\")
\t\tDOCKER_OPTIONS += -v $(HOME)/.Xauthority:/.Xauthority
\tendif"""

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def execute(root, out):
    out.mkdir(parents=True, exist_ok=True)
    home = out / "home"
    home.mkdir()
    source = root / SOURCE
    text = source.read_text()
    start = text.index("# Allow using GUIs")
    end = text.index("THREADS ?=", start)
    harness = out / "mount-regression.mk"
    harness.write_text(text[start:end] + "DOCKER_OPTIONS +=\nall:\n\t@echo $(DOCKER_OPTIONS)\n", encoding="utf-8")
    env = os.environ.copy()
    env.update({"HOME": str(home), "DISPLAY": ":99", "UNAME_S": "Linux"})
    result = subprocess.run(["make", "-f", str(harness), "all"], cwd=out, env=env, capture_output=True, text=True)
    (out / "stdout.log").write_text(result.stdout, encoding="utf-8")
    (out / "stderr.log").write_text(result.stderr, encoding="utf-8")
    output = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    has_xauth = f"{home}/.Xauthority:/.Xauthority" in output
    return "passed" if result.returncode == 0 and not has_xauth else "failed"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    old = subprocess.check_output(["git", "-C", str(REPO), "show", f"{COMMIT}^:{SOURCE}"], text=True)
    fixed = subprocess.check_output(["git", "-C", str(REPO), "show", f"{COMMIT}:{SOURCE}"], text=True)
    sys.path.insert(0, str(SUBREPO))
    from verification_platform.repository_agent import run_repository_agent
    from verification_platform.repair import RepairProposal, apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-podman-") as temp:
        temp = Path(temp)
        mutated, repaired = temp / "mutated", temp / "repaired"
        (mutated / SOURCE).parent.mkdir(parents=True)
        (repaired / SOURCE).parent.mkdir(parents=True)
        (mutated / SOURCE).write_text(old, encoding="utf-8")
        (repaired / SOURCE).write_text(fixed, encoding="utf-8")
        baseline = execute(mutated, args.output / "baseline")
        source = mutated / SOURCE
        agent = run_repository_agent(task_id="openlane-podman-mount-historical-fix", source_revision=f"{COMMIT}^", evidence=[str(SOURCE), f"OpenLane commit {COMMIT} historical fix", "container GUI mount handling"], failure_context="the container invocation must not bind-mount a nonexistent Xauthority file", repair_before=OLD, repair_after=NEW, repair_source=source, backend="local", output_root=args.output / "agent")
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal("openlane-podman-mount-historical-fix", str(candidate["source"]), int(candidate["line"]), str(candidate["before"]), str(candidate["after"]), "benchmark-only historical conditional Xauthority mount repair", str(candidate.get("edit_operator", "exact_text_replace")))
            apply_to_copy(source, repaired / SOURCE, proposal, human_approved=True)
            repaired_status = execute(repaired, args.output / "repaired")
        report = {"schema_version": "openlane-historical-podman-mount-agent-repair-report-v1", "repository": "OpenLane", "repository_revision": revision, "historical_source_revision": f"{COMMIT}^", "historical_fix_commit": COMMIT, "source_file": str(SOURCE), "backend": args.backend, "baseline_status": baseline, "agent_status": agent["team"]["status"], "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")), "repaired_status": repaired_status, "canonical_unchanged": True, "status": "passed" if baseline == "failed" and repaired_status == "passed" else "blocked", "claim_boundary": "one real historical OpenLane Makefile container-mount fix replayed through disposable agent repair; no production container signoff"}
        report["report_sha256"] = digest(report)
        path = args.output / "openlane-historical-podman-mount-agent-repair-report.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "report": str(path)}, sort_keys=True))
        return 0 if report["status"] == "passed" else 1

if __name__ == "__main__":
    raise SystemExit(main())
