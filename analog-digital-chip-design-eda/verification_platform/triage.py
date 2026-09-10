"""Small, deterministic failure parser and IR projection."""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from .ir import EvidenceRef, Requirement, VerificationIR
from .ledger import evidence_for

FAILURE_RE = re.compile(r"FAIL cycle=(?P<cycle>\d+) signal=(?P<signal>[A-Za-z_][\w$]*) expected=(?P<expected>[^ ]+) actual=(?P<actual>[^\s]+)")


@dataclass(frozen=True)
class Failure:
    cycle: int
    signal: str
    expected: str
    actual: str


def parse_failure(text: str) -> Failure | None:
    match = FAILURE_RE.search(text)
    if not match:
        return None
    return Failure(int(match["cycle"]), match["signal"], match["expected"], match["actual"])


def locate_source_marker(path: str | Path, marker: str) -> int:
    """Return the one-based line containing *marker*, rejecting ambiguity."""
    matches = [number for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1) if marker in line]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {marker!r} marker in {path}, found {len(matches)}")
    return matches[0]


def failure_to_ir(failure: Failure, *, root: str | Path, source_revision: str, artifact_paths: list[str]) -> VerificationIR:
    """Project a parsed failure and its artifacts into the common verification IR."""
    refs: list[EvidenceRef] = []
    for path in artifact_paths:
        refs.append(evidence_for(Path(root) / path, root=root, kind="failure-evidence", source_revision=source_revision))
    requirement = Requirement(
        id=f"FAIL-{failure.signal}-{failure.cycle}",
        text=f"{failure.signal} equals {failure.expected} at cycle {failure.cycle}",
        status="failed",
        evidence=refs,
    )
    run = {
        "id": f"triage-{failure.signal}-{failure.cycle}",
        "tool": "simulator",
        "status": "failed",
        "failure": {"cycle": failure.cycle, "signal": failure.signal, "expected": failure.expected, "actual": failure.actual},
        "artifacts": [ref.path for ref in refs],
    }
    ir = VerificationIR(design_revision=source_revision, requirements=[requirement], tool_runs=[run])
    ir.validate()
    return ir
