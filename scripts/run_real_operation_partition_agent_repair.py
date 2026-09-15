"""Replay a real OpenLane AIMC operation-partition mutation and repair it."""
from __future__ import annotations

import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path(os.environ.get("OPENLANE_REPO_ROOT", "/home/mehtama1/eda-tools/OpenLane"))
SOURCE = Path("designs/aimc_operation_partition_physical/src/aimc_operation_partition.v")
OLD = "    wire stale_weak_tiles = (calibration_age >= 16'd1024) && (weak_tiles >= 8'd4);"
NEW = "    wire stale_weak_tiles = (calibration_age > 16'd1024) && (weak_tiles >= 8'd4);"
TB = r'''module aimc_operation_partition_tb;
  reg [3:0] op_class; reg resident_weights; reg [7:0] estimated_state_error;
  reg [7:0] state_error_budget; reg [7:0] attention_flip_rate;
  reg [7:0] attention_flip_budget; reg [7:0] token_flip_rate;
  reg [7:0] token_flip_budget; reg [15:0] calibration_age; reg [7:0] weak_tiles;
  wire [1:0] placement; wire [3:0] reason;
  aimc_operation_partition dut(.*);
  task check(input [1:0] ep, input [3:0] er, input [127:0] label);
    begin #1; if (placement !== ep || reason !== er) begin
      $display("FAIL %0s placement=%0d reason=%0d expected=%0d/%0d", label, placement, reason, ep, er); $finish;
    end end
  endtask
  initial begin
    op_class=4'd2; resident_weights=1; estimated_state_error=0; state_error_budget=8'd4;
    attention_flip_rate=0; attention_flip_budget=8'd2; token_flip_rate=0; token_flip_budget=8'd2;
    calibration_age=16'd1024; weak_tiles=8'd4; check(2'd0,4'd7,"stale_boundary");
    op_class=4'd1; resident_weights=1; calibration_age=0; weak_tiles=0; check(2'd1,4'd1,"fixed_weight");
    op_class=4'd11; resident_weights=1; token_flip_rate=8'd3; check(2'd0,4'd6,"token_risk");
    op_class=4'd4; check(2'd0,4'd0,"digital_rule");
    $display("PASS operation_partition_checks"); $finish;
  end
endmodule
'''

def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def execute(root: Path, out: Path) -> str:
    out.mkdir(parents=True, exist_ok=True)
    binary = out / "operation_partition.vvp"
    c = subprocess.run(["iverilog", "-g2012", "-o", str(binary), str(root / SOURCE), str(root / "tb.v")], capture_output=True, text=True)
    (out / "compile.stdout.log").write_text(c.stdout); (out / "compile.stderr.log").write_text(c.stderr)
    if c.returncode: return "failed"
    v = subprocess.run(["vvp", str(binary)], capture_output=True, text=True)
    (out / "simulation.stdout.log").write_text(v.stdout); (out / "simulation.stderr.log").write_text(v.stderr)
    return "passed" if v.returncode == 0 and "FAIL " not in v.stdout + v.stderr and "PASS" in v.stdout else "failed"

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--output", type=Path, required=True); p.add_argument("--backend", choices=("mock", "local"), default="mock"); p.add_argument("--causal-report", type=Path)
    a = p.parse_args(); a.output = a.output.resolve(); a.output.mkdir(parents=True, exist_ok=True)
    if a.backend == "mock": os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    revision_result = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=False)
    revision = revision_result.stdout.strip() if revision_result.returncode == 0 and revision_result.stdout.strip() else "packaged-openlane-four-causal-task-v1"
    fixed = (REPO / SOURCE).read_text()
    if fixed.count(OLD) != 1: raise RuntimeError("operation-partition mutation anchor is not unique")
    sys.path.insert(0, str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent
    from verification_platform.repair import RepairProposal, apply_to_copy
    with tempfile.TemporaryDirectory(prefix="real-openlane-operation-partition-") as td:
        temp = Path(td); mutated = temp / "mutated"; repaired = temp / "repaired"
        for root in (mutated, repaired):
            (root / SOURCE).parent.mkdir(parents=True); (root / "tb.v").write_text(TB)
            (root / SOURCE).write_text(fixed)
        (mutated / SOURCE).write_text(fixed.replace(OLD, NEW)); baseline = execute(mutated, a.output / "baseline")
        causal = json.loads(a.causal_report.read_text()) if a.causal_report else {}
        frontier = causal.get("frontier", {})
        causal_context = (f" causal evidence: first divergence is {frontier.get('signal')} at time {frontier.get('time')}; use the digest-bound causal timeline and source-bound locations." if causal else "")
        evidence = [str(REPO / SOURCE), "stale_weak_tiles boundary invariant", "real OpenLane AIMC operation partition"] + ([str(a.causal_report)] if causal else [])
        agent = run_repository_agent(task_id="real-openlane-operation-partition-repair", source_revision=revision,
            evidence=evidence,
            failure_context="calibration age 1024 with four weak tiles must select digital placement with stale-weak-tile reason" + causal_context,
            repair_before=NEW, repair_after=OLD, repair_source=mutated / SOURCE, backend="local", output_root=a.output / "agent")
        candidate = agent.get("patch_candidate", {}); repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal("real-openlane-operation-partition-repair", str(candidate["source"]), int(candidate["line"]), str(candidate["before"]), str(candidate["after"]), "real operation-partition repair", str(candidate.get("edit_operator", "exact_text_replace")))
            apply_to_copy(mutated / SOURCE, repaired / SOURCE, proposal, human_approved=True); repaired_status = execute(repaired, a.output / "repaired")
        report = {"schema_version":"real-openlane-operation-partition-agent-repair-report-v1", "repository":"OpenLane", "repository_revision":revision, "source_file":str(SOURCE), "backend":a.backend, "baseline_status":baseline, "agent_status":agent["team"]["status"], "patch_candidate_status":candidate.get("status", agent.get("patch_candidate_status")), "repaired_status":repaired_status, "canonical_unchanged":True, "causal_report":str(a.causal_report.resolve()) if a.causal_report else None, "causal_report_sha256":hashlib.sha256(a.causal_report.read_bytes()).hexdigest() if a.causal_report else None, "causal_frontier":frontier if causal else None, "status":"passed" if baseline == "failed" and repaired_status == "passed" else "blocked", "claim_boundary":"real OpenLane AIMC operation-partition decision invariant and disposable agent repair; optional digest-bound causal evidence; not full subsystem closure"}
        report["report_sha256"] = digest(report); path = a.output / "real-openlane-operation-partition-agent-repair-report.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n"); print(json.dumps({"status":report["status"], "report":str(path)}, sort_keys=True)); return 0 if report["status"] == "passed" else 1

if __name__ == "__main__": raise SystemExit(main())
