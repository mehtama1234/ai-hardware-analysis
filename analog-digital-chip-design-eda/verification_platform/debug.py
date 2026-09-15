"""Composed, evidence-gated logic-aware failure analysis."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from .alignment import align_signals, aligned_state_frontier
from .causal import bind_frontier_to_causal_graph, build_causal_timeline, causal_graph_from_vcd, rank_frontier_root_causes, state_frontier, verify_causal_graph, verify_causal_timeline
from .diagnosis import build_balanced_diagnosis
from .logic import _signals, dependency_cdfg, dependency_cone, dependency_graph, dependency_paths
from .rtl_ast import run_functional_equivalence
from .triage import Failure
from .hypothesis import build_competing_hypotheses


def build_replay_slice(
    rtl: str | Path,
    *,
    signal: str,
    source_revision: str,
    max_paths: int = 32,
) -> dict[str, object]:
    """Create a deterministic, source-hash-bound replay context for one signal.

    This is intentionally a conservative slice manifest rather than a guessed
    replacement module: it contains the exact source lines and dependency paths
    needed by a replay driver.  Callers can reject it if the source is changed
    or if the bounded context is insufficient.
    """
    if not signal or not source_revision:
        raise ValueError("signal and source_revision are required")
    source = Path(rtl)
    text = source.read_text(encoding="utf-8")
    paths = dependency_paths(source, signal)
    cdfg = dependency_cdfg(source, {signal})
    selected_signals = {name for path in paths for name in path}
    selected_lines: list[dict[str, object]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if signal in line or any(name in line for name in selected_signals):
            selected_lines.append({"line": number, "text": line})
    result: dict[str, object] = {
        "schema_version": "replay-slice-v1",
        "source_revision": source_revision,
        "rtl": str(source),
        "rtl_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "signal": signal,
        "dependency_paths": paths[:max_paths],
        "selected_signals": sorted(selected_signals),
        "selected_lines": selected_lines,
        "status": "ready" if selected_lines and paths else "blocked",
    }
    if result["status"] == "blocked":
        result["blocked_reason"] = "no bounded dependency context was extracted"
    result["slice_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return result


def generate_filtered_dut(rtl: str | Path, *, signal: str, source_revision: str, output: str | Path) -> dict[str, object]:
    """Generate a conservative compile-ready single-module dependency slice."""
    source = Path(rtl)
    target = Path(output)
    text = source.read_text(encoding="utf-8")
    selected = {signal, *dependency_cone(source, signal)}
    modules = list(re.finditer(r"\bmodule\s+([A-Za-z_]\w*)\b", text))
    result: dict[str, object] = {"schema_version": "filtered-dut-v1", "source_revision": source_revision, "source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "signal": signal, "selected_signals": sorted(selected), "status": "blocked", "reduction": "none"}
    reason = None
    if len(modules) != 1:
        reason = "filtered reconstruction requires exactly one module"
    else:
        module_end = text.find("endmodule", modules[0].end())
        header_end = text.find(";", modules[0].end(), module_end)
        if module_end < 0 or header_end < 0:
            reason = "module header or endmodule is not structurally bounded"
        else:
            header = text[modules[0].start():header_end + 1].strip()
            lines = text[header_end + 1:module_end].splitlines()
            kept: list[str] = []
            index = 0
            while index < len(lines):
                line = lines[index]
                stripped = line.strip()
                if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
                    index += 1
                    continue
                if re.match(r"(?:input|output|inout|wire|logic|reg|parameter|localparam|typedef)\b", stripped):
                    if _signals(line) & selected:
                        kept.append(line)
                    index += 1
                    continue
                if re.match(r"(?:assign\b|[A-Za-z_]\w*\s*(?:<=|=))", stripped):
                    assignment_lhs = re.match(r"(?:assign\s+)?([A-Za-z_]\w*)\s*(?:<=|=)", stripped)
                    if assignment_lhs and assignment_lhs.group(1) in selected:
                        kept.append(line)
                    index += 1
                    continue
                if stripped.startswith(("always", "always_ff", "always_comb")):
                    block = [line]
                    depth = line.count("begin") - line.count("end")
                    index += 1
                    while index < len(lines) and depth > 0:
                        block.append(lines[index])
                        depth += lines[index].count("begin") - lines[index].count("end")
                        index += 1
                    if depth != 0:
                        reason = "procedural block is not balanced"
                        break
                    if _signals("\n".join(block)) & selected:
                        kept.extend(block)
                    continue
                reason = f"unsupported statement in reconstruction: {stripped[:40]}"
                break
            if reason is None and kept:
                filtered = header + "\n" + "\n".join(kept) + "\nendmodule\n"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(filtered, encoding="utf-8")
                result.update({"status": "ready", "reduction": "dependency-cone", "output": str(target), "filtered_sha256": hashlib.sha256(filtered.encode()).hexdigest(), "selected_lines": len(kept)})
            elif reason is None:
                reason = "no supported statements intersect the dependency cone"
    if result["status"] == "blocked":
        result["blocked_reason"] = reason
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def generate_hierarchical_filtered_dut(rtl: str | Path, *, signal: str, source_revision: str, output: str | Path, top: str | None = None, module_targets: dict[str, str] | None = None) -> dict[str, object]:
    """Emit a hierarchy-preserving slice for statically instantiated modules.

    Complete selected module bodies are retained to preserve sequential and
    interface semantics.  Unrelated modules are removed; dynamic or malformed
    instance relationships block the operation.
    """
    source = Path(rtl)
    target = Path(output)
    text = source.read_text(encoding="utf-8")
    matches = list(re.finditer(r"\bmodule\s+([A-Za-z_]\w*)\b", text))
    modules: dict[str, tuple[int, int, str]] = {}
    for index, match in enumerate(matches):
        end = text.find("endmodule", match.end())
        if end < 0:
            continue
        modules[match.group(1)] = (match.start(), end + len("endmodule"), text[match.start():end + len("endmodule")])
    result: dict[str, object] = {"schema_version": "hierarchical-filtered-dut-v1", "source_revision": source_revision, "source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "signal": signal, "status": "blocked"}
    selected_top = top or (matches[-1].group(1) if matches else None)
    if not selected_top or selected_top not in modules:
        result["blocked_reason"] = "requested top module was not found or is malformed"
    else:
        selected = {selected_top}
        queue = [selected_top]
        while queue:
            module_name = queue.pop(0)
            body = modules[module_name][2]
            for child in re.findall(r"\b([A-Za-z_]\w*)\s+[A-Za-z_]\w*\s*\(", body):
                if child in modules and child not in selected:
                    selected.add(child)
                    queue.append(child)
        if not any(re.search(rf"\b{re.escape(signal)}\b", modules[name][2]) for name in selected):
            result["blocked_reason"] = "target signal is not present in the selected hierarchy"
        else:
            selected_text = {name: modules[name][2].strip() for name in selected}
            reduction = "hierarchy-preserving"
            sliced_modules: list[str] = []
            if module_targets is not None:
                if not module_targets or any(name not in selected for name in module_targets):
                    result["blocked_reason"] = "module dependency targets must name selected hierarchy modules"
                else:
                    for module_name, module_signal in sorted(module_targets.items()):
                        body = selected_text[module_name]
                        child_refs = [child for child in re.findall(r"\b([A-Za-z_]\w*)\s+[A-Za-z_]\w*\s*\(", body) if child in modules]
                        if child_refs:
                            result["blocked_reason"] = f"module target {module_name} contains child instances; slice the leaf module instead"
                            break
                        sliced, reason, selected_signals = _slice_leaf_module(body, module_signal)
                        if reason is not None or sliced is None:
                            result["blocked_reason"] = reason or f"module target {module_name} could not be sliced"
                            break
                        selected_text[module_name] = sliced
                        sliced_modules.append(module_name)
                        result.setdefault("module_selected_signals", {})[module_name] = sorted(selected_signals)
                    else:
                        reduction = "hierarchy-preserving-dependency-cone"
            if "blocked_reason" not in result:
                filtered = "\n\n".join(selected_text[name] for name in sorted(selected)) + "\n"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(filtered, encoding="utf-8")
                result.update({"status": "ready", "top": selected_top, "selected_modules": sorted(selected), "dropped_modules": sorted(set(modules) - selected), "sliced_modules": sliced_modules, "output": str(target), "filtered_sha256": hashlib.sha256(filtered.encode()).hexdigest(), "reduction": reduction})
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def _slice_leaf_module(module_text: str, signal: str) -> tuple[str | None, str | None, set[str]]:
    """Conservatively reduce a module containing no child instances."""
    match = re.search(r"\bmodule\s+[A-Za-z_]\w*\b", module_text)
    end = module_text.rfind("endmodule")
    if not match or end < 0:
        return None, "module boundaries are malformed", set()
    header_end = module_text.find(";", match.end(), end)
    if header_end < 0:
        return None, "module header is not structurally bounded", set()
    header = module_text[:header_end + 1].strip()
    lines = module_text[header_end + 1:end].splitlines()
    assignments = []
    for assignment in re.finditer(r"(?:assign\s+)?([A-Za-z_]\w*)\s*(?:<=|=)\s*([^;]+);", "\n".join(lines)):
        assignments.append((assignment.group(1), _signals(assignment.group(2))))
    selected = {signal}
    changed = True
    while changed:
        changed = False
        for lhs, drivers in assignments:
            if lhs in selected:
                before = len(selected)
                selected.update(drivers)
                changed |= len(selected) != before
    kept: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
            index += 1
            continue
        if stripped.count(";") > 1:
            return None, "multiple statements on one line are unsupported in leaf-module reconstruction", selected
        if re.match(r"(?:input|output|inout|wire|logic|reg|parameter|localparam|typedef)\b", stripped):
            if _signals(line) & selected:
                kept.append(line)
            index += 1
            continue
        assignment = re.match(r"(?:assign\s+)?([A-Za-z_]\w*)\s*(?:<=|=)", stripped)
        if assignment:
            if assignment.group(1) in selected:
                kept.append(line)
            index += 1
            continue
        if stripped.startswith(("always", "always_ff", "always_comb")):
            block = [line]
            depth = line.count("begin") - line.count("end")
            index += 1
            while index < len(lines) and depth > 0:
                block.append(lines[index])
                depth += lines[index].count("begin") - lines[index].count("end")
                index += 1
            if depth != 0:
                return None, "procedural block is not balanced", selected
            if _signals("\n".join(block)) & selected:
                kept.extend(block)
            continue
        return None, f"unsupported statement in leaf-module reconstruction: {stripped[:40]}", selected
    if not kept:
        return None, "no supported statements intersect the module dependency cone", selected
    return header + "\n" + "\n".join(kept) + "\nendmodule", None, selected


def prove_filtered_dut_equivalence(
    original: str | Path,
    filtered: str | Path,
    *,
    top: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
) -> dict[str, object]:
    """Require Yosys equivalence before accepting a reduced single-module DUT."""
    if not top or not source_revision:
        raise ValueError("top and source_revision are required")
    original_path, filtered_path = Path(original), Path(filtered)
    text = filtered_path.read_text(encoding="utf-8")
    renamed_top = f"{top}__filtered"
    renamed_text, count = re.subn(rf"(\bmodule\s+){re.escape(top)}\b", rf"\g<1>{renamed_top}", text, count=1)
    root = Path(run_root)
    renamed_path = root / "filtered-for-equivalence.sv"
    root.mkdir(parents=True, exist_ok=True)
    result: dict[str, object] = {"schema_version": "filtered-dut-equivalence-v1", "source_revision": source_revision, "original": str(original_path), "filtered": str(filtered_path), "original_sha256": hashlib.sha256(original_path.read_bytes()).hexdigest(), "filtered_sha256": hashlib.sha256(filtered_path.read_bytes()).hexdigest(), "status": "blocked"}
    if count != 1:
        result["blocked_reason"] = "filtered top module was not found exactly once"
    else:
        renamed_path.write_text(renamed_text, encoding="utf-8")
        equivalence = run_functional_equivalence([original_path], [renamed_path], reference_top=top, candidate_top=renamed_top, run_root=root / "solver", source_revision=source_revision, timeout_seconds=timeout_seconds)
        result["equivalence"] = equivalence
        result["status"] = "proven" if equivalence.get("status") == "proven" else "blocked"
        if result["status"] == "blocked":
            result["blocked_reason"] = "filtered DUT was not proven equivalent"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "filtered-dut-equivalence.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def prove_hierarchical_filtered_dut_equivalence(
    original: str | Path,
    filtered: str | Path,
    *,
    top: str,
    selected_modules: Iterable[str],
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
) -> dict[str, object]:
    """Prove a hierarchy-preserving filtered DUT equivalent to the original."""
    modules = sorted(set(selected_modules))
    original_path, filtered_path = Path(original), Path(filtered)
    root = Path(run_root)
    result: dict[str, object] = {"schema_version": "hierarchical-filtered-dut-equivalence-v1", "source_revision": source_revision, "original": str(original_path), "filtered": str(filtered_path), "original_sha256": hashlib.sha256(original_path.read_bytes()).hexdigest(), "filtered_sha256": hashlib.sha256(filtered_path.read_bytes()).hexdigest(), "selected_modules": modules, "status": "blocked"}
    if not top or top not in modules:
        result["blocked_reason"] = "top is not included in selected hierarchy"
    else:
        text = filtered_path.read_text(encoding="utf-8")
        renamed = {name: f"{name}__filtered" for name in modules}
        for name in sorted(renamed, key=len, reverse=True):
            text = re.sub(rf"\b{re.escape(name)}\b", renamed[name], text)
        candidate = root / "hierarchical-filtered-for-equivalence.sv"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(text, encoding="utf-8")
        equivalence = run_functional_equivalence([original_path], [candidate], reference_top=top, candidate_top=renamed[top], run_root=root / "solver", source_revision=source_revision, timeout_seconds=timeout_seconds, flatten=True)
        result["equivalence"] = equivalence
        result["status"] = "proven" if equivalence.get("status") == "proven" else "blocked"
        if result["status"] == "blocked":
            result["blocked_reason"] = "hierarchical filtered DUT was not proven equivalent"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "hierarchical-filtered-dut-equivalence.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def analyze_failure(
    waveform: str | Path,
    rtl: str | Path,
    *,
    signal: str,
    observed: Iterable[tuple[int, str]],
    reference: Iterable[tuple[int, str]],
    source_revision: str,
    for_evidence: Iterable[str],
    against_evidence: Iterable[str],
    reference_traces: dict[str, list[tuple[int, str]]] | None = None,
    rtl_traces: dict[str, list[tuple[int, str]]] | None = None,
    explicit_alignment: dict[str, str] | None = None,
    reference_neighbors: dict[str, set[str]] | None = None,
    rtl_neighbors: dict[str, set[str]] | None = None,
) -> dict[str, object]:
    """Produce causal, frontier, alignment, and balanced-diagnosis evidence."""
    if not signal or not source_revision:
        raise ValueError("signal and source_revision are required")
    observed_list, reference_list = list(observed), list(reference)
    frontier = state_frontier(observed_list, reference_list, signal=signal)
    graph = causal_graph_from_vcd(waveform, rtl, [signal])
    causal_errors = verify_causal_graph(graph)
    frontier_binding = bind_frontier_to_causal_graph(frontier, graph)
    root_cause_candidates = rank_frontier_root_causes(frontier_binding, rtl)
    hypotheses = build_competing_hypotheses(root_cause_candidates, for_evidence=for_evidence, against_evidence=against_evidence)
    timeline = build_causal_timeline(graph, frontier_node=frontier_binding.get("frontier_node"))
    timeline_errors = verify_causal_timeline(timeline, graph)
    paths = dependency_paths(rtl, signal)
    cdfg = dependency_cdfg(rtl, {signal})
    replay_slice = build_replay_slice(rtl, signal=signal, source_revision=source_revision)
    alignment = None
    if reference_traces is not None or rtl_traces is not None:
        if reference_traces is None or rtl_traces is None:
            raise ValueError("reference_traces and rtl_traces must be supplied together")
        alignment = align_signals(reference_traces, rtl_traces, explicit=explicit_alignment, reference_neighbors=reference_neighbors, rtl_neighbors=rtl_neighbors)
    result: dict[str, object] = {
        "schema_version": "logic-aware-debug-package-v1",
        "source_revision": source_revision,
        "signal": signal,
        "causal_graph": graph,
        "causal_graph_validation": {"status": "passed" if not causal_errors else "blocked", "errors": causal_errors},
        "replay_slice": replay_slice,
        "state_frontier": frontier,
        "causal_frontier_binding": frontier_binding,
        "root_cause_candidates": root_cause_candidates,
        "competing_hypotheses": hypotheses,
        "causal_timeline": timeline,
        "causal_timeline_validation": {"status": "passed" if not timeline_errors else "blocked", "errors": timeline_errors},
        "alignment": alignment,
        "aligned_state_frontier": aligned_state_frontier(reference_traces, rtl_traces, alignment) if alignment is not None else None,
        "dependency_paths": paths,
        "dependency_cdfg": cdfg,
        "diagnosis": None,
        "status": "blocked",
    }
    if causal_errors:
        result["blocked_reason"] = "causal graph validation failed: " + "; ".join(causal_errors)
    elif timeline_errors:
        result["blocked_reason"] = "causal timeline validation failed: " + "; ".join(timeline_errors)
    elif frontier["status"] != "diverged":
        result["blocked_reason"] = f"state frontier is {frontier['status']}, not a confirmed divergence"
    elif alignment is not None and (alignment["ambiguous_count"] or alignment["unresolved_count"]):
        result["blocked_reason"] = "signal alignment is ambiguous or unresolved"
    else:
        failure = Failure(frontier["cycle"], signal, str(frontier["reference"]), str(frontier["observed"]))
        diagnosis = build_balanced_diagnosis(failure, source_revision=source_revision, for_evidence=for_evidence, against_evidence=against_evidence, causal_paths=paths)
        result["diagnosis"] = diagnosis.record()
        result["status"] = "review_required"
    result["package_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def write_debug_package(package: dict[str, object], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
