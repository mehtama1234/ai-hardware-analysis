"""Deterministic Markdown requirement ingestion."""

from __future__ import annotations

import re
from pathlib import Path

from .ir import Requirement, VerificationIR
from .ledger import evidence_for

REQUIREMENT_RE = re.compile(r"^\s*(?P<id>[A-Z][A-Z0-9_-]{2,}):\s*(?P<text>\S.*)$")


def ingest_markdown(path: str | Path, *, root: str | Path, source_revision: str = "unknown") -> VerificationIR:
    """Ingest explicit ``REQ-ID: text`` lines; ignore prose to avoid guessing intent."""
    source_path = Path(path)
    content = source_path.read_text(encoding="utf-8")
    source_ref = evidence_for(source_path, root=root, kind="specification", source_revision=source_revision)
    requirements: list[Requirement] = []
    seen: set[str] = set()
    for line_number, line in enumerate(content.splitlines(), 1):
        match = REQUIREMENT_RE.match(line)
        if not match:
            continue
        requirement_id = match["id"]
        if requirement_id in seen:
            raise ValueError(f"duplicate requirement id: {requirement_id}")
        seen.add(requirement_id)
        requirements.append(Requirement(requirement_id, match["text"], source=source_ref, evidence=[]))
    if not requirements:
        raise ValueError(f"no explicit requirements found in {source_path}")
    ir = VerificationIR(design_revision=source_revision, requirements=requirements)
    ir.validate()
    return ir
