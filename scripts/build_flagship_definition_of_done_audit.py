#!/usr/bin/env python3
"""Build a requirement-by-requirement audit of the flagship definition of done."""
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p:Path)->str:return str(p.resolve().relative_to(ROOT))
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 evidence={
  "release_manifest":ROOT/".artifacts/flagship-end-to-end-release.json",
  "clean_replay":ROOT/".artifacts/flagship-clean-checkout-replay.json",
  "human_review":ROOT/".artifacts/flagship-human-review-receipt.json",
  "real_model":ROOT/".artifacts/real-model-colab/evidence-check.json",
  "real_model_cpu_supplemental":ROOT/".artifacts/real-model-colab/local-cpu-supplemental-20260915/receipt.json",
  "real_model_cpu_supplemental_sweep":ROOT/".artifacts/real-model-colab/local-cpu-supplemental-sweep-20260915/receipt.json",
  "semantic_debugging":ROOT/".artifacts/semantic-debugging-breadth-20260915/receipt.json",
  "proof_closure":ROOT/".artifacts/flagship-closure-evidence-20260915/manifest.json",
  "physical_archive":ROOT/".artifacts/flagship-physical-evidence-20260915/archive-receipt.json",
  "model_to_chip_archive":ROOT/".artifacts/local-model-to-chip-qualification-20260915/archive-receipt.json",
  "historical_breadth":ROOT/".artifacts/historical-breadth-20260915/receipt.json",
  "heldout_historical_replay":ROOT/".artifacts/heldout-openlane-historical-replay-20260915/replay-report.json",
  "heldout_historical_config_replay":ROOT/".artifacts/heldout-openlane-config-path-replay-20260915/replay-report.json",
  "heldout_openroad_installer_replay":ROOT/".artifacts/heldout-openroad-installer-replay-20260915/replay-report.json",
  "heldout_openroad_issue_bundle_replay":ROOT/".artifacts/heldout-openroad-issue-bundle-replay-20260915/replay-report.json",
  "heldout_openroad_metrics_replay":ROOT/".artifacts/heldout-openroad-metrics-replay-20260915/replay-report.json",
 }
 records=[
  {"id":1,"requirement":"clean_checkout_reproduces_baseline","status":"passed","evidence":["clean_replay"],"finding":"clean archived-checkout replay passes all independent checks"},
  {"id":2,"requirement":"requirement_source_failure_and_agent_context_identified","status":"passed","evidence":["real_model","proof_closure"],"finding":"declared evidence packages retain source-bound model and closure context"},
  {"id":3,"requirement":"agent_output_grounded_bounded_and_checked","status":"passed","evidence":["real_model","proof_closure"],"finding":"authenticated primary proposals and closure evidence are independently checked"},
  {"id":4,"requirement":"human_approval_or_rejection_explicit_and_digest_bound","status":"pending","evidence":["human_review"],"finding":"pending receipt is digest-bound but approval=false and reviewer=null"},
  {"id":5,"requirement":"repair_disposable_copy_only","status":"passed","evidence":["proof_closure","real_model"],"finding":"canonical immutability and bounded retest evidence are retained"},
  {"id":6,"requirement":"identical_scope_retest","status":"passed_bounded_local","evidence":["proof_closure","physical_archive"],"finding":"declared local closure and physical handoff scope pass; no silicon scope claimed"},
  {"id":7,"requirement":"heldout_real_designs_test_generalization","status":"blocked","evidence":["real_model","real_model_cpu_supplemental","real_model_cpu_supplemental_sweep","semantic_debugging","historical_breadth","heldout_historical_replay","heldout_historical_config_replay","heldout_openroad_installer_replay","heldout_openroad_issue_bundle_replay","heldout_openroad_metrics_replay"],"finding":"the supplemental local CPU sweep closes 1/2 held-out seeded tasks and records one bounded repair rejection, authenticated T4 closure remains 0%/12.5%, and semantic localization has only four measured held-out real targets (4/10 required); no generalization claim is promoted"},
  {"id":8,"requirement":"proof_carrying_simulation_formal_mutation_coverage_security_assertion_integrity","status":"passed","evidence":["proof_closure"],"finding":"six required proof roles are bundled and independently checked"},
  {"id":9,"requirement":"accepted_rtl_hash_linked_to_physical_evidence","status":"passed_bounded_local","evidence":["physical_archive"],"finding":"source alignment and local OpenLane artifacts are hash-linked; commercial signoff excluded"},
  {"id":10,"requirement":"frozen_workload_compiler_runtime_replay_deterministic","status":"passed_bounded_local","evidence":["model_to_chip_archive"],"finding":"digital reference and deterministic fallback archive passes; analog/GPU gates remain open"},
  {"id":11,"requirement":"analog_gpu_energy_board_silicon_yield_production_claims_blocked_without_evidence","status":"passed","evidence":["release_manifest","model_to_chip_archive","physical_archive"],"finding":"release remains fail-closed and analog_authorized=false"},
  {"id":12,"requirement":"bounded_release_manifest_and_independent_recheck","status":"passed_but_blocked","evidence":["release_manifest","clean_replay","human_review"],"finding":"manifest and replay pass, but release decision remains blocked_pending_physical_and_measured_gates"},
 ]
 evidence_records={k:{"path":rel(v),"sha256":sha(v)} for k,v in evidence.items()}
 # The replay receipt includes this audit check, so bind its path but not its
 # digest to avoid a self-referential digest cycle.
 evidence_records["clean_replay"]={"path":rel(evidence["clean_replay"]),"binding":"independently checked committed replay receipt"}
 audit={"schema_version":"flagship-definition-of-done-audit-v1","generated_at":datetime.now(timezone.utc).isoformat(),"completion":False,"status":"blocked_pending_requirements","release_decision":"blocked_pending_physical_and_measured_gates","evidence":evidence_records,"requirements":records,"blocking_requirements":[4,7],"claim_boundary":"Requirement audit for the declared flagship evidence package; not human approval, held-out generalization, silicon signoff, commercial signoff, or production release."}
 audit["audit_sha256"]=hashlib.sha256(json.dumps(audit,sort_keys=True,separators=(",",":")).encode()).hexdigest();out=a.output.resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":audit["status"],"completion":False,"blocking_requirements":audit["blocking_requirements"],"output":str(out)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
