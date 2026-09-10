"""Coverage evidence parsing and conservative closure metrics."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class CoverageResult:
    kind: str
    covered: int
    total: int
    percentage: float
    evidence_path: str


def rank_coverage_gaps(results: Iterable[CoverageResult | dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank uncovered work by missing items, then by coverage kind.

    This is a planning signal, not proof of reachability: every returned item
    still requires a new executable run and evidence before closure.
    """
    ranked: list[dict[str, Any]] = []
    for item in results:
        if isinstance(item, CoverageResult):
            kind, covered, total = item.kind, item.covered, item.total
        else:
            kind, covered, total = item.get("kind"), item.get("covered"), item.get("total")
        if not isinstance(kind, str) or not kind or not isinstance(covered, int) or not isinstance(total, int) or total <= 0 or covered < 0 or covered > total:
            raise ValueError("coverage gap requires valid kind, covered, and total")
        missing = total - covered
        if missing:
            ranked.append({"kind": kind, "covered": covered, "total": total, "missing": missing, "priority": missing / total, "next_action": f"run or generate checks targeting uncovered {kind} items"})
    return sorted(ranked, key=lambda item: (-item["missing"], -item["priority"], item["kind"]))


def parse_coverage(path: str | Path, *, root: str | Path) -> CoverageResult:
    """Parse a small JSON coverage payload: ``{kind, covered, total}``."""
    file_path = Path(path)
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    kind, covered, total = payload.get("kind"), payload.get("covered"), payload.get("total")
    if not isinstance(kind, str) or not kind or not isinstance(covered, int) or not isinstance(total, int) or total <= 0 or covered < 0 or covered > total:
        raise ValueError("coverage requires kind, integer covered/total, and 0 <= covered <= total")
    try:
        relative = file_path.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("coverage evidence must be inside the run root") from exc
    return CoverageResult(kind, covered, total, round(100.0 * covered / total, 4), relative)


def write_coverage(result: CoverageResult, path: str | Path) -> None:
    Path(path).write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
