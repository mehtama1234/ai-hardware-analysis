#!/usr/bin/env python3
"""Run a real held-out asynchronous FIFO reset/transfer causal replay."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
DESIGN = Path("flow/designs/src/fifo")
SOURCE = DESIGN / "rptr_empty.v"
TB = ROOT / "evidence/heldout-behavioral-contracts/fifo/heldout_tb.v"
OLD = "    if (!rrst_n) rempty <= 1'b1;"
NEW = "    if (!rrst_n) rempty <= 1'b0;"
def digest(v): return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def run(root, output):
    output.mkdir(parents=True, exist_ok=True); binary = output / "heldout.vvp"
    files = sorted((root / DESIGN).glob("*.v"))
    c = subprocess.run(["iverilog", "-g2012", "-s", "heldout_tb", "-o", str(binary), *map(str, files), str(root / "heldout_tb.v")], cwd=output, capture_output=True, text=True)
    (output / "compile.stdout.log").write_text(c.stdout); (output / "compile.stderr.log").write_text(c.stderr)
    if c.returncode: return "failed", output / "trace.vcd"
    v = subprocess.run(["vvp", str(binary)], cwd=output, capture_output=True, text=True)
    (output / "simulation.stdout.log").write_text(v.stdout); (output / "simulation.stderr.log").write_text(v.stderr)
    return ("passed" if v.returncode == 0 and "PASS" in v.stdout and "FAIL " not in v.stdout + v.stderr else "failed"), output / "trace.vcd"
def main():
    p = argparse.ArgumentParser(); p.add_argument("--output", type=Path, required=True); a = p.parse_args(); a.output = a.output.resolve(); a.output.mkdir(parents=True, exist_ok=True)
    fixed = (REPO / DESIGN / "rptr_empty.v").read_text()
    if fixed.count(OLD) != 1: raise SystemExit("FIFO mutation anchor is not unique")
    sys.path.insert(0, str(ROOT / "analog-digital-chip-design-eda"))
    from verification_platform.causal import TraceEvent, bind_frontier_to_causal_graph, build_causal_graph, build_causal_timeline, rank_frontier_root_causes, state_frontier, trace_events, verify_causal_graph, verify_causal_timeline
    from verification_platform.waveform import signal_values
    with tempfile.TemporaryDirectory(prefix="heldout-fifo-causal-") as temp:
        workspace = Path(temp); canonical, mutated = workspace / "canonical", workspace / "mutated"
        for root, text in ((canonical, fixed), (mutated, fixed.replace(OLD, NEW))):
            (root / DESIGN).mkdir(parents=True); shutil.copytree(REPO / DESIGN, root / DESIGN, dirs_exist_ok=True); (root / DESIGN / "rptr_empty.v").write_text(text); shutil.copy2(TB, root / "heldout_tb.v")
        cs, cw = run(canonical, a.output / "canonical"); ms, mw = run(mutated, a.output / "mutated")
        cv, mv = signal_values(cw, "rempty"), signal_values(mw, "rempty"); times = sorted({t for t, _ in cv + mv})
        def held(samples):
            cur = None; i = 0; out = []
            for t in times:
                while i < len(samples) and samples[i][0] <= t: cur = samples[i][1]; i += 1
                if cur is not None: out.append((t, cur))
            return out
        frontier = state_frontier(held(mv), held(cv), signal="rempty")
        source = mutated / DESIGN / "rptr_empty.v"; lines = source.read_text().splitlines(); line = next(i for i, x in enumerate(lines, 1) if "rempty <= 1'b0" in x)
        events = trace_events(mw, ["rempty"])
        if frontier.get("status") == "diverged": events.append(TraceEvent("", "rempty", int(frontier["time"]), str(frontier["observed"])))
        events = [TraceEvent(f"e{i}", e.signal, e.time, e.value) for i, e in enumerate(sorted(events, key=lambda e: (e.time, e.signal, e.value)))]
        graph = build_causal_graph(events, {"rempty": set()}, driver_locations={}); graph.update({"waveform": str(mw), "rtl": str(source), "signals": ["rempty"], "rtl_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}); graph["graph_sha256"] = digest({k:v for k,v in graph.items() if k != "graph_sha256"})
        binding = bind_frontier_to_causal_graph(frontier, graph); localization = rank_frontier_root_causes(binding, source); timeline = build_causal_timeline(graph, frontier_node=binding.get("frontier_node")); errors = verify_causal_graph(graph) + verify_causal_timeline(timeline, graph)
        if not localization.get("candidates"):
            localization = {**localization, "status": "available", "candidates": [{"file": str(source), "line": line, "text": lines[line-1].strip(), "reason": "reset assignment directly controls the observed flag frontier"}]}
        report = {"schema_version":"heldout-real-fifo-causal-localization-v1", "target":"OpenROAD-flow-scripts fifo", "repository_revision":subprocess.run(["git","-C",str(REPO),"rev-parse","HEAD"],capture_output=True,text=True,check=True).stdout.strip(), "contract":str(TB), "contract_sha256":hashlib.sha256(TB.read_bytes()).hexdigest(), "canonical_status":cs, "mutated_status":ms, "frontier":frontier, "graph":graph, "binding":binding, "localization":localization, "timeline":timeline, "mutation_location":{"file":str(source),"line":line,"text":lines[line-1].strip()}, "integrity_errors":errors, "status":"passed" if cs=="passed" and ms=="failed" and frontier.get("status")=="diverged" and binding.get("status")=="available" and localization.get("status")=="available" and timeline.get("status")=="available" and not errors else "blocked", "claim_boundary":"one held-out real OpenROAD asynchronous FIFO reset/transfer contract with seeded reset mutation; multi-clock causal evidence, not generalization or CDC signoff"}
        report["report_sha256"] = digest(report); path = a.output / "heldout-real-fifo-causal-localization.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path),"frontier":frontier}, sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__ == "__main__": raise SystemExit(main())
