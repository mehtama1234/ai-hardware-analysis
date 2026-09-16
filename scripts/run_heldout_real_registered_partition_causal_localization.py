#!/usr/bin/env python3
"""Run a real held-out replay on the registered AIMC operation partition."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
DESIGN = Path("designs/aimc_operation_partition_output_registered/src")
SOURCE = DESIGN / "aimc_operation_partition.v"
TB = ROOT / "evidence/heldout-behavioral-contracts/aimc_operation_partition_output_registered/heldout_tb.v"
OLD = "    wire fixed_weight_op = (op_class == OP_QKV) || (op_class == OP_OUT_PROJ) || (op_class == OP_MLP);"
NEW = "    wire fixed_weight_op = (op_class == OP_OUT_PROJ) || (op_class == OP_MLP);"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def held(samples: list[tuple[int, str]], times: list[int]) -> list[tuple[int, str]]:
    result, current, index = [], None, 0
    for time in times:
        while index < len(samples) and samples[index][0] <= time:
            current = samples[index][1]
            index += 1
        if current is not None:
            result.append((time, current))
    return result


def run(root: Path, source_files: list[Path], output: Path) -> tuple[str, Path]:
    output.mkdir(parents=True, exist_ok=True)
    binary = output / "heldout.vvp"
    compile_result = subprocess.run(["iverilog", "-g2012", "-o", str(binary), *(str(root / DESIGN / f.name) for f in source_files), str(root / "heldout_tb.v")], cwd=output, capture_output=True, text=True)
    (output / "compile.stdout.log").write_text(compile_result.stdout)
    (output / "compile.stderr.log").write_text(compile_result.stderr)
    if compile_result.returncode != 0:
        return "failed", output / "trace.vcd"
    simulation = subprocess.run(["vvp", str(binary)], cwd=output, capture_output=True, text=True)
    (output / "simulation.stdout.log").write_text(simulation.stdout)
    (output / "simulation.stderr.log").write_text(simulation.stderr)
    return ("passed" if simulation.returncode == 0 and "PASS" in simulation.stdout and "FAIL " not in simulation.stdout + simulation.stderr else "failed"), output / "trace.vcd"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    fixed = (REPO / SOURCE).read_text()
    if fixed.count(OLD) != 1: raise SystemExit("registered partition mutation anchor is not unique")
    source_files = sorted((REPO / DESIGN).glob("*.v"))
    sys.path.insert(0, str(ROOT / "analog-digital-chip-design-eda"))
    from verification_platform.causal import bind_frontier_to_causal_graph, build_causal_graph, build_causal_timeline, rank_frontier_root_causes, state_frontier, trace_events, verify_causal_graph, verify_causal_timeline
    from verification_platform.waveform import signal_values
    with tempfile.TemporaryDirectory(prefix="heldout-registered-partition-causal-") as temporary:
        workspace = Path(temporary); canonical, mutated = workspace / "canonical", workspace / "mutated"
        for root, text in ((canonical, fixed), (mutated, fixed.replace(OLD, NEW))):
            (root / DESIGN).mkdir(parents=True)
            for source_file in source_files:
                (root / DESIGN / source_file.name).write_text(text if source_file == REPO / SOURCE else source_file.read_text())
            shutil.copy2(TB, root / "heldout_tb.v")
        canonical_status, canonical_waveform = run(canonical, source_files, args.output / "canonical")
        mutated_status, mutated_waveform = run(mutated, source_files, args.output / "mutated")
        canonical_values, mutated_values = signal_values(canonical_waveform, "reason"), signal_values(mutated_waveform, "reason")
        times = sorted({time for time, _ in canonical_values + mutated_values})
        frontier = state_frontier(held(mutated_values, times), held(canonical_values, times), signal="reason")
        mutated_source = mutated / SOURCE; lines = mutated_source.read_text().splitlines(); mutation_line = next(i for i, line in enumerate(lines, 1) if "wire fixed_weight_op" in line)
        events = trace_events(mutated_waveform, ["reason", "placement"])
        graph = build_causal_graph(events, {"reason": {"placement"}, "placement": set()}, driver_locations={("reason", "placement"): [{"file": str(mutated_source), "line": mutation_line}]})
        graph.update({"waveform": str(mutated_waveform), "rtl": str(mutated_source), "signals": ["reason", "placement"], "rtl_sha256": hashlib.sha256(mutated_source.read_bytes()).hexdigest()}); graph["graph_sha256"] = digest({k: v for k, v in graph.items() if k != "graph_sha256"})
        binding = bind_frontier_to_causal_graph(frontier, graph); localization = rank_frontier_root_causes(binding, mutated_source); timeline = build_causal_timeline(graph, frontier_node=binding.get("frontier_node")); errors = verify_causal_graph(graph) + verify_causal_timeline(timeline, graph)
        report = {"schema_version": "heldout-real-registered-partition-causal-localization-v1", "target": "OpenLane aimc_operation_partition_output_registered", "repository_revision": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(), "contract": str(TB), "contract_sha256": hashlib.sha256(TB.read_bytes()).hexdigest(), "canonical_status": canonical_status, "mutated_status": mutated_status, "frontier": frontier, "graph": graph, "binding": binding, "localization": localization, "timeline": timeline, "mutation_location": {"file": str(mutated_source), "line": mutation_line, "text": lines[mutation_line - 1].strip()}, "integrity_errors": errors, "status": "passed" if canonical_status == "passed" and mutated_status == "failed" and frontier.get("status") == "diverged" and binding.get("status") == "available" and localization.get("status") == "available" and timeline.get("status") == "available" and not errors else "blocked", "claim_boundary": "one held-out real OpenLane registered AIMC partition target with source-level behavioral contract and seeded fixed-weight classification mutation; module/cycle first-divergence evidence, not 90% generalization or complete protocol proof"}
        report["report_sha256"] = digest(report); path = args.output / "heldout-real-registered-partition-causal-localization.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": report["status"], "report": str(path), "frontier": frontier}, sort_keys=True)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__": raise SystemExit(main())
