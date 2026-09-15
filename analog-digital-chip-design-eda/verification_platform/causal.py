"""Deterministic waveform-to-causal-graph and state-frontier utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from .logic import dependency_cone, dependency_graph, dependency_locations, signal_assignment_locations
from .waveform import signal_values


@dataclass(frozen=True)
class TraceEvent:
    id: str
    signal: str
    time: int
    value: str


def trace_events(path: str | Path, signals: Iterable[str]) -> list[TraceEvent]:
    """Read selected VCD signals and return stable time-ordered events."""
    events: list[TraceEvent] = []
    for signal in sorted(set(signals)):
        for time, value in signal_values(path, signal):
            events.append(TraceEvent("", signal, int(time), value))
    events.sort(key=lambda event: (event.time, event.signal, event.value))
    assigned: list[TraceEvent] = []
    for index, event in enumerate(events):
        assigned.append(TraceEvent(f"e{index}", event.signal, event.time, event.value))
    return assigned


def build_causal_graph(events: Iterable[TraceEvent], drivers: dict[str, set[str]], *, driver_locations: dict[tuple[str, str], list[dict[str, object]]] | None = None) -> dict[str, object]:
    """Build a conservative DAG from temporal and structural relationships."""
    ordered = list(events)
    signal_by_id = {event.id: event.signal for event in ordered}
    nodes = [asdict(event) for event in ordered]
    edges: set[tuple[str, str, str]] = set()
    latest: dict[str, TraceEvent] = {}
    for event in ordered:
        prior = latest.get(event.signal)
        if prior is not None and prior.time <= event.time:
            edges.add((prior.id, event.id, "temporal"))
        for driver in sorted(drivers.get(event.signal, set())):
            source = latest.get(driver)
            if source is not None and source.time <= event.time and source.id != event.id:
                edges.add((source.id, event.id, "structural"))
        latest[event.signal] = event
    graph = {
        "schema_version": "causal-graph-v1",
        "nodes": nodes,
        "edges": [
            {
                "source": source,
                "target": target,
                "kind": kind,
                **(
                    {"rtl_locations": driver_locations.get((signal_by_id[target], signal_by_id[source]), [])}
                    if kind == "structural" and driver_locations is not None
                    else {}
                ),
            }
            for source, target, kind in sorted(edges)
        ],
    }
    graph["graph_sha256"] = hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return graph


def causal_graph_from_vcd(path: str | Path, rtl_path: str | Path, signals: Iterable[str], *, extra_events: Iterable[tuple[str, int, str]] = ()) -> dict[str, object]:
    """Build a graph while binding it to the RTL dependency source."""
    source = Path(rtl_path)
    requested = sorted(set(signals))
    selected = sorted(set(requested).union(*(dependency_cone(source, signal) for signal in requested)))
    waveform_text = Path(path).read_text(encoding="utf-8")
    declared = {
        match.group(1)
        for match in re.finditer(r"\$var\s+\S+\s+\d+\s+\S+\s+([^\s\[]+)", waveform_text)
    }
    available = [signal for signal in selected if signal in declared]
    missing = [signal for signal in selected if signal not in declared]
    events = trace_events(path, available)
    existing = {(event.signal, event.time) for event in events}
    for signal, time, value in extra_events:
        if signal in available and (signal, int(time)) not in existing:
            events.append(TraceEvent("", signal, int(time), str(value)))
    events.sort(key=lambda event: (event.time, event.signal, event.value))
    events = [TraceEvent(f"e{index}", event.signal, event.time, event.value) for index, event in enumerate(events)]
    graph = build_causal_graph(events, dependency_graph(source), driver_locations=dependency_locations(source))
    graph["waveform"] = str(Path(path))
    graph["rtl"] = str(Path(rtl_path))
    graph["signals"] = selected
    graph["available_signals"] = available
    graph["missing_signals"] = missing
    graph["rtl_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    body = {key: value for key, value in graph.items() if key != "graph_sha256"}
    graph["graph_sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return graph


def verify_causal_graph(graph: dict[str, object]) -> list[str]:
    """Independently validate causal-graph integrity before agent use."""
    errors: list[str] = []
    if graph.get("schema_version") != "causal-graph-v1":
        errors.append("unsupported causal graph schema")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return errors + ["causal graph nodes and edges must be lists"]
    node_ids: set[str] = set()
    times: dict[str, int] = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node.get("id"):
            errors.append("causal graph node has no valid id")
            continue
        node_id = node["id"]
        if node_id in node_ids:
            errors.append(f"duplicate causal graph node: {node_id}")
        node_ids.add(node_id)
        if not isinstance(node.get("signal"), str) or not node.get("signal"):
            errors.append(f"causal graph node has no signal: {node_id}")
        if not isinstance(node.get("time"), int):
            errors.append(f"causal graph node has invalid time: {node_id}")
        else:
            times[node_id] = node["time"]
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append("causal graph edge is not an object")
            continue
        source, target, kind = edge.get("source"), edge.get("target"), edge.get("kind")
        if source not in node_ids or target not in node_ids:
            errors.append("causal graph edge references an unknown node")
            continue
        if source == target:
            errors.append("causal graph contains a self-edge")
        if kind not in {"temporal", "structural"}:
            errors.append("causal graph edge has an unsupported kind")
        if kind == "temporal" and source in times and target in times and times[source] > times[target]:
            errors.append("temporal causal edge runs backward in time")
        adjacency[source].append(target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            errors.append("causal graph contains a cycle")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for target in adjacency[node_id]:
            visit(target)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in node_ids:
        visit(node_id)
    body = {key: value for key, value in graph.items() if key != "graph_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if graph.get("graph_sha256") != expected:
        errors.append("causal graph self-digest does not match")
    return sorted(set(errors))


def state_frontier(
    observed: Iterable[tuple[int, str]],
    reference: Iterable[tuple[int, str]],
    *,
    signal: str,
) -> dict[str, object]:
    """Return the first aligned value divergence without guessing on truncation."""
    left, right = list(observed), list(reference)
    for index, (actual, expected) in enumerate(zip(left, right)):
        actual_time, actual_value = actual
        expected_time, expected_value = expected
        if actual_time != expected_time:
            return {"status": "unreliable", "reason": "trace timestamps are not aligned", "signal": signal, "index": index, "observed_time": actual_time, "reference_time": expected_time}
        if actual_value != expected_value:
            return {"status": "diverged", "signal": signal, "index": index, "cycle": index, "time": actual_time, "observed": actual_value, "reference": expected_value, "prior_cycles_agreed": index}
    if len(left) != len(right):
        return {"status": "incomplete", "reason": "trace lengths differ", "signal": signal, "observed_samples": len(left), "reference_samples": len(right), "prior_cycles_agreed": min(len(left), len(right))}
    return {"status": "identical", "signal": signal, "samples": len(left)}


def bind_frontier_to_causal_graph(frontier: dict[str, object], graph: dict[str, object]) -> dict[str, object]:
    """Bind a value frontier to its waveform event and structural source lines."""
    graph_errors = verify_causal_graph(graph)
    if graph_errors:
        return {"status": "blocked", "reason": "causal graph validation failed", "errors": graph_errors}
    if frontier.get("status") != "diverged":
        return {"status": "blocked", "reason": "a divergent frontier is required", "frontier_status": frontier.get("status")}
    signal, time = frontier.get("signal"), frontier.get("time")
    nodes = graph.get("nodes", [])
    node = next((item for item in nodes if isinstance(item, dict) and item.get("signal") == signal and item.get("time") == time), None)
    if node is None:
        return {"status": "blocked", "reason": "frontier event is absent from causal graph", "signal": signal, "time": time}
    node_id = node.get("id")
    incoming = [
        edge for edge in graph.get("edges", [])
        if isinstance(edge, dict) and edge.get("target") == node_id and edge.get("kind") == "structural"
    ]
    locations = [location for edge in incoming for location in edge.get("rtl_locations", []) if isinstance(location, dict)]
    result: dict[str, object] = {
        "status": "available",
        "frontier_node": node_id,
        "signal": signal,
        "time": time,
        "incoming_structural_edges": incoming,
        "source_locations": locations,
        "graph_sha256": graph.get("graph_sha256"),
        "rtl_sha256": graph.get("rtl_sha256"),
        "claim_boundary": "waveform frontier bound to causal event and available RTL driver locations; not proof of root cause",
    }
    result["binding_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def rank_frontier_root_causes(binding: dict[str, object], rtl: str | Path) -> dict[str, object]:
    """Rank source statements directly feeding a confirmed frontier.

    This is deliberately a localization result, not an LLM-generated root-cause
    claim.  Only source locations already attached to a validated causal edge
    are admitted, and each candidate includes the exact source text and source
    digest that an agent or reviewer must use for the next check.
    """
    source = Path(rtl)
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    result: dict[str, object] = {
        "schema_version": "frontier-root-cause-candidates-v1",
        "status": "blocked",
        "rtl": str(source),
        "rtl_sha256": source_digest,
        "binding_sha256": binding.get("binding_sha256"),
        "candidates": [],
        "claim_boundary": "ranked RTL statements feeding the observed frontier; not proof that any candidate is the root cause",
    }
    expected_binding_body = {key: value for key, value in binding.items() if key != "binding_sha256"}
    binding_integrity_ok = bool(binding.get("binding_sha256")) and binding.get("binding_sha256") == hashlib.sha256(json.dumps(expected_binding_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if binding.get("status") != "available":
        result["blocked_reason"] = "a validated causal-frontier binding is required"
    elif not binding_integrity_ok:
        result["blocked_reason"] = "causal-frontier binding digest does not match"
    elif binding.get("graph_sha256") and binding.get("rtl_sha256") != source_digest:
        result["blocked_reason"] = "causal frontier and current RTL source revisions differ"
    else:
        lines = source.read_text(encoding="utf-8").splitlines()
        candidates: dict[tuple[str, int], dict[str, object]] = {}
        for location in binding.get("source_locations", []):
            if not isinstance(location, dict) or not isinstance(location.get("line"), int):
                continue
            line_number = int(location["line"])
            if not 1 <= line_number <= len(lines):
                continue
            location_file = str(location.get("file", source))
            if Path(location_file).resolve() != source.resolve():
                continue
            key = (location_file, line_number)
            candidates[key] = {
                "rank": 0,
                "file": key[0],
                "line": line_number,
                "text": lines[line_number - 1].strip(),
                "reason": "direct structural driver of the first divergent frontier event",
            }
        ranked = sorted(candidates.values(), key=lambda item: (int(item["line"]), str(item["file"])))
        if not ranked:
            for location in signal_assignment_locations(source, str(binding.get("signal", ""))):
                line_number = int(location["line"])
                ranked.append({
                    "rank": 0,
                    "file": str(location["file"]),
                    "line": line_number,
                    "text": lines[line_number - 1].strip(),
                    "reason": "direct RTL assignment to the first divergent frontier signal; selector/data dependencies require review",
                })
            ranked.sort(key=lambda item: (int(item["line"]), str(item["file"])))
        for index, candidate in enumerate(ranked, 1):
            candidate["rank"] = index
        result["candidates"] = ranked
        result["status"] = "available" if ranked else "blocked"
        if not ranked:
            result["blocked_reason"] = "frontier has no source-bound structural driver locations"
    body = {key: value for key, value in result.items() if key != "result_sha256"}
    result["result_sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def build_causal_timeline(graph: dict[str, object], *, frontier_node: str | None = None) -> dict[str, object]:
    """Emit a deterministic event timeline ending at a validated frontier."""
    errors = verify_causal_graph(graph)
    if errors:
        return {"schema_version": "causal-timeline-v1", "status": "blocked", "errors": errors}
    nodes = [item for item in graph.get("nodes", []) if isinstance(item, dict)]
    node_map = {str(item.get("id")): item for item in nodes}
    target = frontier_node or (str(nodes[-1].get("id")) if nodes else "")
    if target not in node_map:
        return {"schema_version": "causal-timeline-v1", "status": "blocked", "blocked_reason": "frontier node is absent from causal graph"}
    incoming: dict[str, list[dict[str, object]]] = {node_id: [] for node_id in node_map}
    for edge in graph.get("edges", []):
        if isinstance(edge, dict) and edge.get("target") in incoming:
            incoming[str(edge["target"])].append(edge)
    ancestors: set[str] = set()
    queue = [target]
    while queue:
        current = queue.pop(0)
        if current in ancestors:
            continue
        ancestors.add(current)
        queue.extend(str(edge["source"]) for edge in incoming.get(current, []) if edge.get("source") in node_map)
    timeline = []
    for node_id in sorted(ancestors, key=lambda item: (int(node_map[item].get("time", 0)), str(node_map[item].get("signal", "")), item)):
        node = node_map[node_id]
        timeline.append({"event_id": node_id, "signal": node.get("signal"), "time": node.get("time"), "value": node.get("value"), "predecessors": sorted(str(edge["source"]) for edge in incoming.get(node_id, []) if edge.get("source") in ancestors)})
    result: dict[str, object] = {"schema_version": "causal-timeline-v1", "status": "available", "frontier_node": target, "events": timeline, "graph_sha256": graph.get("graph_sha256"), "claim_boundary": "ordered causal evidence for review; not a proof of fault causality"}
    result["timeline_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def verify_causal_timeline(timeline: dict[str, object], graph: dict[str, object]) -> list[str]:
    """Independently validate a timeline before it is used by an agent."""
    errors: list[str] = []
    if timeline.get("schema_version") != "causal-timeline-v1":
        errors.append("unsupported causal timeline schema")
    if timeline.get("status") != "available":
        errors.append("causal timeline is not available")
    graph_errors = verify_causal_graph(graph)
    if graph_errors:
        errors.extend(f"causal graph: {error}" for error in graph_errors)
    if timeline.get("graph_sha256") != graph.get("graph_sha256"):
        errors.append("causal timeline is bound to a different causal graph")
    nodes = {str(item.get("id")): item for item in graph.get("nodes", []) if isinstance(item, dict) and item.get("id")}
    events = timeline.get("events")
    if not isinstance(events, list) or not events:
        errors.append("causal timeline has no events")
    else:
        event_ids: list[str] = []
        previous_key: tuple[int, str, str] | None = None
        for event in events:
            if not isinstance(event, dict) or not isinstance(event.get("event_id"), str):
                errors.append("causal timeline contains an invalid event")
                continue
            event_id = event["event_id"]
            event_ids.append(event_id)
            node = nodes.get(event_id)
            if node is None:
                errors.append(f"causal timeline references unknown event: {event_id}")
                continue
            if event.get("signal") != node.get("signal") or event.get("time") != node.get("time") or event.get("value") != node.get("value"):
                errors.append(f"causal timeline event disagrees with graph: {event_id}")
            key = (int(node.get("time", 0)), str(node.get("signal", "")), event_id)
            if previous_key is not None and key < previous_key:
                errors.append("causal timeline events are not deterministically ordered")
            previous_key = key
            predecessors = event.get("predecessors", [])
            if not isinstance(predecessors, list) or any(str(item) not in event_ids and str(item) not in {str(other.get("event_id")) for other in events if isinstance(other, dict)} for item in predecessors):
                errors.append(f"causal timeline has an invalid predecessor list: {event_id}")
        frontier = timeline.get("frontier_node")
        if not isinstance(frontier, str) or not event_ids or event_ids[-1] != frontier:
            errors.append("causal timeline does not end at its declared frontier")
        if len(event_ids) != len(set(event_ids)):
            errors.append("causal timeline contains duplicate events")
    body = {key: value for key, value in timeline.items() if key != "timeline_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if timeline.get("timeline_sha256") != expected:
        errors.append("causal timeline self-digest does not match")
    return sorted(set(errors))


def write_causal_graph(path: str | Path, graph: dict[str, object]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
