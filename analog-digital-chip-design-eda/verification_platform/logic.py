"""Conservative RTL dependency extraction for focused debug context."""

from __future__ import annotations

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
    assignments: dict[str, set[str]] = {}
    text = Path(path).read_text(encoding="utf-8")
    for match in ASSIGN_RE.finditer(text):
        rhs = _signals(match["rhs"])
        rhs.discard("if")
        assignments.setdefault(match["lhs"], set()).update(rhs)
    for match in GUARDED_ASSIGN_RE.finditer(text):
        assignments.setdefault(match["lhs"], set()).update(_signals(match["guard"]))
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
