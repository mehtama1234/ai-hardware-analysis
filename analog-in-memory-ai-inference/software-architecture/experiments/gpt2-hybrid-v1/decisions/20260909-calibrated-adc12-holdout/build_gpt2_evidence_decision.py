#!/usr/bin/env python3
"""Join checked model quality with separately scoped compiler/physical evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from check_gpt2_wikitext_projection import check
from check_gpt2_adc_holdout import check as check_holdout

REPO = Path(__file__).resolve().parents[3]
EDA = REPO / "analog-digital-chip-design-eda/evidence"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_source(item):
    if digest(item["path"]) != item["sha256"]:
        raise ValueError(f"Source changed: {item['path']}")


def run(args):
    quality = json.loads((args.quality / "result.json").read_text())
    heldout = quality.get("schema_version") == "calibrated_adc_disjoint_holdout.v1"
    if heldout:
        check_holdout(args.quality)
        plan = json.loads((args.quality / "frozen_plan/plan.json").read_text())
        quality_protocol = {"model_revision":plan["model_revision"],"evaluation_split":"test"}
    else:
        check(args.quality)
        quality_protocol = quality["protocol"]
        if quality_protocol["evaluation_split"] != "test":
            raise ValueError("Validation development evidence cannot replace the test-set decision package")
    physical = json.loads(args.physical.read_text())
    for item in physical["sources"].values():
        checked_source(item)
    transient = json.loads(Path(physical["sources"]["transient"]["path"]).read_text())
    if digest(transient["netlist"]) != physical["netlist_sha256"]:
        raise ValueError("Current extracted netlist differs from physical evidence")
    compiler = json.loads((args.compiler / "execution_result.json").read_text())
    manifest = json.loads((args.compiler / "manifest.json").read_text())
    for item in manifest["files"]:
        checked_source(item)
    if compiler["model"]["revision"] != quality_protocol["model_revision"]:
        raise ValueError("Model revisions differ")
    args.output.mkdir(parents=True, exist_ok=False)
    inputs = {"quality": args.quality / "result.json", "quality_manifest": args.quality / "manifest.json",
              "physical": args.physical, "compiler": args.compiler / "execution_result.json",
              "compiler_manifest": args.compiler / "manifest.json",
              "candidate_schedule": args.compiler / "analog_candidate_schedule.json"}
    if heldout:
        inputs["quality_plan"] = args.quality / "frozen_plan/plan.json"
    for name, path in inputs.items():
        shutil.copy2(path, args.output / (name + ".json"))
    for name in [Path(__file__).name, "check_gpt2_wikitext_projection.py", "check_gpt2_adc_holdout.py"]:
        shutil.copy2(Path(__file__).with_name(name), args.output / name)
    candidates = {name: {k:value[k] for k in ["tokens", "nll_increase", "argmax_agreement", "screen_pass"]}
                  for name,value in quality["variants"].items() if name != "ideal"}
    passing = [name for name,value in candidates.items() if value["screen_pass"]]
    report = {"schema_version": "gpt2_hybrid_evidence_decision.v1", "decision": "retain_native_digital_execution",
              "model_revision": quality_protocol["model_revision"], "projection": compiler["model"]["target_module"],
              "quality": {"valid_numerical_controls": quality["ideal_control_pass"], "candidates": candidates,
                          "passing_provisional_candidates": passing, "task_acceptance_established": False,
                          "scope": "validation-selected profile on disjoint test contexts, noiseless" if heldout else "original sampled test profiles"},
              "compiler": {"saved_status": compiler["status"], "scope": "earlier authored fixture, shared bytecode and software SRAM interpreter; not this WikiText execution or physical firmware"},
              "physical": {k: physical[k] for k in ["status", "full_cell_drc_pass", "active_transistor_lvs_pass",
                            "complete_converter_lvs_pass", "logic_margin_pass_count", "measured_cases", "analog_allowed_for_physical_claim"]},
              "array_model_circuit_calibrated": quality["physical_profile_calibrated"],
              "matched_hardware_latency_energy_available": False,
              "analog_executor_bound": False, "analog_authorized": False,
              "next_required_evidence": ["candidate passing frozen quality contract on independent task-representative data",
                                         "qualified full converter/array transfer, noise and settling profile",
                                         "real analog target and compiler/controller execution",
                                         "same-workload digital/hybrid latency and energy including conversions, transfers and fallback"],
              "claim_boundary": "Joined evidence has distinct workloads and abstraction levels. No silicon execution, matched analog costs, or hybrid benefit is established.",
              "sources": {name:{"path":str(path.resolve()), "sha256":digest(path)} for name,path in inputs.items()}}
    if heldout:
        report["calibrated_range_hardware_gaps"] = plan["selected_contract"]["required_unqualified_hardware"] + [
            "mapping model partial-sum units to physical current and converter voltage",
            "fixed physical noise profile across range settings",
            "compiler/controller support for the selected range settings"]
        report["next_required_evidence"].insert(1,"realize the frozen per-tile ADC ranges in the physical array/converter and controller contract")
    (args.output / "decision.json").write_text(json.dumps(report,indent=2)+"\n")
    lines = ["# GPT-2 hybrid decision", "", "**Retain native digital execution.**", "",
             "| Candidate | NLL increase | Argmax agreement | Provisional screen |",
             "| --- | ---: | ---: | --- |"]
    for name,row in candidates.items():
        lines.append(f"| {name} | {row['nll_increase']:.6f} | {row['argmax_agreement']:.4%} | {row['screen_pass']} |")
    lines += ["", "Numerical controls passed for the sampled WikiText evaluation. Task acceptance remains unestablished.",
              report["quality"]["scope"] + ".",
              "The earlier compiler evidence proves software fallback on its own fixture. It is not WikiText hardware execution.",
              "The current layout passes full-cell DRC and active-transistor LVS, but fails electrical margin and complete converter qualification.",
              "The array error profile is provisional; no matched hardware latency/energy evidence or bound analog executor exists.",
              "", "See decision.json for hashed sources and remaining evidence requirements."]
    if heldout:
        lines += ["", "The calibrated profile also requires unqualified per-tile gain/reference settings, model-to-physical scaling, range switching/settling and controller support."]
    (args.output / "README.md").write_text("\n".join(lines)+"\n")
    (args.output / "manifest.json").write_text(json.dumps({p.name:digest(p) for p in args.output.iterdir() if p.is_file()},indent=2)+"\n")
    print(json.dumps({"output":str(args.output), "decision":report["decision"], "passing_candidates":passing}))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality",type=Path,required=True)
    parser.add_argument("--physical",type=Path,default=EDA / "aimc-simulator-adapters/converter-physical-repair-current.json")
    parser.add_argument("--compiler",type=Path,default=EDA / "aimc-hardware-lab/gpt2-compiled-runtime/20260909-shared-sram-frozen")
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args())
