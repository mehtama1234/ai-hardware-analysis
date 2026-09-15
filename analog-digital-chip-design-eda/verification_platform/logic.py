"""Conservative RTL dependency extraction for focused debug context."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ASSIGN_RE = re.compile(r"(?:assign\s+)?(?P<lhs>[A-Za-z_]\w*)\s*(?:<=|=)\s*(?P<rhs>[^;]+);")
IDENT_RE = re.compile(r"\b[A-Za-z_]\w*\b")
GUARDED_ASSIGN_RE = re.compile(r"if\s*\((?P<guard>[^)]+)\)\s*(?P<lhs>[A-Za-z_]\w*)\s*(?:<=|=)")


def _signals(expression: str) -> set[str]:
    """Extract identifiers while dropping Verilog literal suffixes."""
    return {name for name in IDENT_RE.findall(expression) if not re.fullmatch(r"[dbho][0-9a-fA-F_xXzZ]+", name)}


def dependency_cone(path: str | Path, signal: str, *, max_depth: int = 8) -> set[str]:
    """Return source signals that can feed *signal* through simple assignments."""
    assignments = dependency_graph(path)
    result: set[str] = set()
    frontier = {signal}
    for _ in range(max_depth):
        next_frontier = set()
        for name in frontier:
            for dependency in assignments.get(name, set()):
                if dependency not in result and dependency != signal:
                    result.add(dependency)
                    next_frontier.add(dependency)
        if not next_frontier:
            break
        frontier = next_frontier
    return result


def dependency_graph(path: str | Path) -> dict[str, set[str]]:
    """Return a conservative driver graph for simple RTL expressions."""
    assignments: dict[str, set[str]] = {}
    text = Path(path).read_text(encoding="utf-8")
    for match in ASSIGN_RE.finditer(text):
        rhs = _signals(match["rhs"])
        rhs.discard("if")
        assignments.setdefault(match["lhs"], set()).update(rhs)
    for match in GUARDED_ASSIGN_RE.finditer(text):
        assignments.setdefault(match["lhs"], set()).update(_signals(match["guard"]))
    return {name: set(drivers) for name, drivers in assignments.items()}


def dependency_locations(path: str | Path) -> dict[tuple[str, str], list[dict[str, object]]]:
    """Return source locations for conservative signal-driver relationships."""
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    locations: dict[tuple[str, str], list[dict[str, object]]] = {}
    matches = list(ASSIGN_RE.finditer(text))
    matches.extend(GUARDED_ASSIGN_RE.finditer(text))
    for match in matches:
        lhs = str(match["lhs"])
        expression = str(match["rhs"]) if match.groupdict().get("rhs") is not None else str(match["guard"])
        line = text.count("\n", 0, match.start()) + 1
        for driver in sorted(_signals(expression) - {"if"}):
            locations.setdefault((lhs, driver), []).append({"file": str(source), "line": line})
    return locations


def signal_assignment_locations(path: str | Path, signal: str) -> list[dict[str, object]]:
    """Return exact source locations assigning *signal*, including constants."""
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    locations: list[dict[str, object]] = []
    for match in ASSIGN_RE.finditer(text):
        if str(match["lhs"]) == signal:
            locations.append({"file": str(source), "line": text.count("\n", 0, match.start()) + 1})
    return locations


def dependency_cdfg(path: str | Path, roots: set[str] | None = None, *, max_depth: int = 8) -> dict[str, object]:
    """Build a bounded, source-location-bound expression dependency graph."""
    graph = dependency_graph(path)
    locations = dependency_locations(path)
    root_set = set(roots or graph)
    selected = set(root_set)
    frontier = set(selected)
    for _ in range(max_depth):
        next_frontier = {driver for node in frontier for driver in graph.get(node, set()) if driver not in selected}
        if not next_frontier:
            break
        selected.update(next_frontier)
        frontier = next_frontier
    result: dict[str, object] = {
        "schema_version": "dependency-cdfg-v1",
        "scope": "expression-level-conservative",
        "roots": sorted(root_set),
        "nodes": [{"id": name, "kind": "signal", "root": name in root_set} for name in sorted(selected)],
        "edges": [{"source": driver, "target": target, "locations": locations.get((target, driver), [])} for target in sorted(selected) for driver in sorted(graph.get(target, set()) & selected)],
        "max_depth": max_depth,
    }
    result["cdfg_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def dependency_paths(path: str | Path, signal: str, *, max_depth: int = 8) -> list[list[str]]:
    """Return deterministic acyclic backtrace paths from *signal* to drivers."""
    graph = dependency_graph(path)
    paths: list[list[str]] = []
    queue: list[list[str]] = [[signal]]
    while queue:
        current = queue.pop(0)
        node = current[-1]
        drivers = sorted(graph.get(node, set()))
        if len(current) >= max_depth or not drivers:
            paths.append(current)
            continue
        extended = False
        for driver in drivers:
            if driver in current or driver == "if":
                continue
            queue.append(current + [driver])
            extended = True
        if not extended:
            paths.append(current)
    return paths
