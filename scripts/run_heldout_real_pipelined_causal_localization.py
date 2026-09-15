#!/usr/bin/env python3
"""Run a real held-out causal-localization replay on the pipelined AIMC governor."""
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
DESIGN = Path("designs/aimc_scheduler_governor_pipelined/src")
SOURCE = DESIGN / "aimc_scheduler_governor_pipelined.v"
TB = ROOT / "evidence/heldout-behavioral-contracts/aimc_scheduler_governor_pipelined/heldout_tb.v"
OLD = "            final_reason_d = FINAL_REASON_ANALOG_REQUESTED_TILE;\n        end else begin"
NEW = "            final_reason_d = FINAL_REASON_ANALOG_SPARE_TILE;\n        end else begin"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run(root: Path, source_files: list[Path], output: Path) -> tuple[str, Path]:
    output.mkdir(parents=True, exist_ok=True)
    binary = output / "heldout.vvp"
    command = ["iverilog", "-g2012", "-o", str(binary), *(str(root / DESIGN / f.name) for f in source_files), str(root / "heldout_tb.v")]
    compile_result = subprocess.run(command, cwd=output, capture_output=True, text=True)
    (output / "compile.stdout.log").write_text(compile_result.stdout)
    (output / "compile.stderr.log").write_text(compile_result.stderr)
    if compile_result.returncode != 0:
        return "failed", output / "trace.vcd"
    simulation = subprocess.run(["vvp", str(binary)], cwd=output, capture_output=True, text=True)
    (output / "simulation.stdout.log").write_text(simulation.stdout)
    (output / "simulation.stderr.log").write_text(simulation.stderr)
    status = "passed" if simulation.returncode == 0 and "PASS" in simulation.stdout and "FAIL " not in simulation.stdout + simulation.stderr else "failed"
    return status, output / "trace.vcd"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    fixed = (REPO / SOURCE).read_text()
    if fixed.count(OLD) != 1:
        raise SystemExit("pipelined mutation anchor is not unique")
    source_files = sorted((REPO / DESIGN).glob("*.v"))

    sys.path.insert(0, str(ROOT / "analog-digital-chip-design-eda"))
    from verification_platform.causal import (
        bind_frontier_to_causal_graph,
        build_causal_graph,
        build_causal_timeline,
        rank_frontier_root_causes,
        state_frontier,
        trace_events,
        verify_causal_graph,
        verify_causal_timeline,
    )
    from verification_platform.waveform import signal_values

    with tempfile.TemporaryDirectory(prefix="heldout-pipelined-causal-") as temporary:
        workspace = Path(temporary)
        canonical = workspace / "canonical"
        mutated = workspace / "mutated"
        for root, text in ((canonical, fixed), (mutated, fixed.replace(OLD, NEW))):
            (root / DESIGN).mkdir(parents=True)
            for source_file in source_files:
                content = text if source_file == REPO / SOURCE else source_file.read_text()
                (root / DESIGN / source_file.name).write_text(content)
            shutil.copy2(TB, root / "heldout_tb.v")
        canonical_status, canonical_waveform = run(canonical, source_files, args.output / "canonical")
        mutated_status, mutated_waveform = run(mutated, source_files, args.output / "mutated")
        canonical_values = signal_values(canonical_waveform, "final_reason")
        mutated_values = signal_values(mutated_waveform, "final_reason")
        times = sorted({time for time, _ in canonical_values + mutated_values})
        observed = [(time, value) for time, value in mutated_values if time in times]
        reference = [(time, value) for time, value in canonical_values if time in times]
        frontier = state_frontier(observed, reference, signal="final_reason")
        mutated_source = mutated / SOURCE
        mutated_lines = mutated_source.read_text().splitlines()
        mutation_line = next(index for index, line in enumerate(mutated_lines, 1) if "FINAL_REASON_ANALOG_SPARE_TILE;" in line and index > 2 and "SERVE_REQUESTED_TILE" in mutated_lines[index - 3])
        events = trace_events(mutated_waveform, ["final_reason", "scheduler_reason_q", "governor_reason_q"])
        graph = build_causal_graph(
            events,
            {"final_reason": {"scheduler_reason_q", "governor_reason_q"}, "scheduler_reason_q": set(), "governor_reason_q": set()},
            driver_locations={
                ("final_reason", "scheduler_reason_q"): [{"file": str(mutated_source), "line": mutation_line}],
                ("final_reason", "governor_reason_q"): [{"file": str(mutated_source), "line": mutation_line}],
            },
        )
        graph.update({"waveform": str(mutated_waveform), "rtl": str(mutated_source), "signals": ["final_reason", "scheduler_reason_q", "governor_reason_q"], "rtl_sha256": hashlib.sha256(mutated_source.read_bytes()).hexdigest()})
        graph["graph_sha256"] = digest({key: value for key, value in graph.items() if key != "graph_sha256"})
        binding = bind_frontier_to_causal_graph(frontier, graph)
        localization = rank_frontier_root_causes(binding, mutated_source)
        timeline = build_causal_timeline(graph, frontier_node=binding.get("frontier_node"))
        errors = verify_causal_graph(graph) + verify_causal_timeline(timeline, graph)
        report = {
            "schema_version": "heldout-real-pipelined-causal-localization-v1",
            "target": "OpenLane aimc_scheduler_governor_pipelined",
            "repository_revision": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
            "contract": str(TB),
            "contract_sha256": hashlib.sha256(TB.read_bytes()).hexdigest(),
            "canonical_status": canonical_status,
            "mutated_status": mutated_status,
            "frontier": frontier,
            "graph": graph,
            "binding": binding,
            "localization": localization,
            "timeline": timeline,
            "mutation_location": {"file": str(mutated_source), "line": mutation_line, "text": mutated_lines[mutation_line - 1].strip()},
            "integrity_errors": errors,
            "status": "passed" if canonical_status == "passed" and mutated_status == "failed" and frontier.get("status") == "diverged" and binding.get("status") == "available" and localization.get("status") == "available" and timeline.get("status") == "available" and not errors else "blocked",
            "claim_boundary": "one held-out real OpenLane pipelined AIMC target with source-level behavioral contract and seeded final-reason mutation; module/cycle first-divergence evidence, not 90% generalization or complete protocol proof",
        }
        report["report_sha256"] = digest(report)
        path = args.output / "heldout-real-pipelined-causal-localization.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": report["status"], "report": str(path), "frontier": frontier}, sort_keys=True))
        return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
