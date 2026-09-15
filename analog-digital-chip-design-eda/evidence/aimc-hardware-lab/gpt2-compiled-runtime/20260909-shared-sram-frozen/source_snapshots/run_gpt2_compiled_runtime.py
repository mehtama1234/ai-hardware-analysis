#!/usr/bin/env python3
"""Compile and execute the real GPT-2 projection through the shared SRAM contract."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download

from gpt2_compiled_runtime import EDA, CompiledProjection, candidate_schedule, sha256
from run_gpt2_hybrid_evaluation import evaluate, compare, replace_forward, source
from check_gpt2_hybrid_evaluation import check
from import_physical_converter_gate import import_gate, DEFAULT_GATE
from compile_hybrid_transformer_execution_package import main as compile_package
from run_target_bytecode_reference import main as verify_encoding

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def run(args):
    check(args.sensitivity_package)
    evidence = json.loads((args.sensitivity_package / "evaluation.json").read_text())
    fixture = evidence["fixture"]
    variant = next(v for v in evidence["variants"] if v["id"] == "dac10_weight8_adc12")
    output = args.output.resolve()
    if not output.is_relative_to(EDA):
        raise ValueError("shared compiler package must live under the EDA project")
    output.mkdir(parents=True, exist_ok=False)
    code_paths = [Path(__file__), ROOT / "scripts/gpt2_compiled_runtime.py",
                  ROOT / "scripts/run_gpt2_hybrid_evaluation.py", ROOT / "scripts/import_physical_converter_gate.py",
                  EDA / "scripts/compile_hybrid_transformer_execution_package.py", EDA / "scripts/run_target_bytecode_reference.py",
                  EDA / "scripts/audit_extracted_converter_boundary.py"]
    snapshots = output / "source_snapshots"
    snapshots.mkdir()
    frozen_sources = []
    for code_path in code_paths:
        snapshot_path = snapshots / code_path.name
        snapshot_path.write_bytes(code_path.read_bytes())
        frozen_sources.append({**source(snapshot_path), "original_path": str(code_path)})
    gate = import_gate(DEFAULT_GATE)
    write(output / "physical_gate.json", gate)
    schedule = candidate_schedule(variant["contract"])
    write(output / "analog_candidate_schedule.json", schedule)
    operator_id = fixture["target_module"]
    plan = {"schema_version": "gpt2_projection_lowering.v1", "model_revision": fixture["revision"],
            "physical_gate": gate,
            "operator_placements": [{"operator_id": operator_id, "operator": "Gemm",
                                     "activation_shape": [1, 768], "output_shape": [1, 3072],
                                     "analog_candidate": True, "placement": "digital_support",
                                     "reason": "No qualified array/converter profile or bound analog executor",
                                     "precision": "float32", "fallback": "native_digital_Gemm"}],
            "execution_scope": "selected projection only; all other GPT-2 modules execute in native PyTorch"}
    write(output / "execution_plan.json", plan)
    write(output / "compiler_source.json", {"target_package_id": "gpt2_projection_shared_runtime_v1",
          "physical_gate_status": "blocked_no_qualified_array_converter_or_executor",
          "models": [{"model_id": fixture["model_id"], "operator_count": 1,
                      "source_plan": str((output / "execution_plan.json").relative_to(EDA))}]})
    compile_package(output / "compiler_source.json", output)
    if verify_encoding(output):
        raise ValueError("shared bytecode verification failed")
    hashes = {name: sha256(output / name) for name in ("runtime_commands.json", "target_bytecode.json", "compiled_target_execution_package.json")}
    torch.set_num_threads(2)
    torch.manual_seed(fixture["seed"])
    snapshot = snapshot_download(fixture["model_id"], revision=fixture["revision"], local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(snapshot, local_files_only=True, use_safetensors=True,
                                               attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    module = model.get_submodule(operator_id)
    print("Running native GPT-2 baseline", flush=True)
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"])
    runtime = CompiledProjection(output, module.weight, module.bias, gate, hashes)
    print("Running decoded projection commands through SRAM", flush=True)
    with replace_forward(module, runtime):
        actual = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], runtime)
    quality = compare(baseline, actual)
    passed = all(row["maximum_logit_abs_error"] < 1e-3 and row["generation_exact_match"] for row in quality["rows"])
    phase_totals = {}
    for event in runtime.trace:
        phase = phase_totals.setdefault(event["phase"], {"vectors": 0, "executed_commands": 0,
                                                       "boundary_input_bytes": 0, "boundary_output_bytes": 0})
        for key in phase:
            phase[key] += event[key]
    report = {"schema_version": "gpt2_compiled_projection_execution.v1",
              "status": "compiled_projection_fallback_pass" if passed else "compiled_projection_fallback_failed",
              "created_at": datetime.now(timezone.utc).isoformat(), "model": evidence["model"],
              "sources": {"sensitivity": source(args.sensitivity_package / "evaluation.json"),
                          "code": frozen_sources},
              "runtime": {"torch": torch.__version__, "device": "cpu", "threads": 2, "command": sys.argv},
              "quality": quality, "trace": runtime.trace, "phase_totals": phase_totals,
              "sram_bytes": len(runtime.memory), "weight_location": "host_memory_not_in_SRAM_arena",
              "analog_instructions_executed": 0, "fallback_fraction": 1.0,
              "fallback_reasons": runtime.fallback_reasons,
              "candidate_accounting": {phase: {name: value*totals["vectors"] for name, value in schedule["per_vector_cost_counts"].items()}
                                       for phase, totals in phase_totals.items()},
              "accounting_scope": "Counterfactual analog counts follow this digital token trace. Different generated tokens, batching, or early EOS require a new trace.",
              "claim_boundary": "Real GPT-2 execution with selected projection using shared review bytecode and CPU SRAM interpreter. Remaining model runs native. No firmware, analog hardware, measured chip latency or energy."}
    write(output / "execution_result.json", report)
    write(output / "manifest.json", {"files": [source(p) for p in sorted(output.glob("*.json")) if p.name != "manifest.json"]})
    print(json.dumps({"output": str(output), "status": report["status"], "phase_totals": phase_totals,
                      "max_logit_error": max(row["maximum_logit_abs_error"] for row in quality["rows"])}), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sensitivity-package", type=Path,
                        default=ROOT / "experiments/gpt2-hybrid-v1/runs/20260909-recovery-projection")
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args())
