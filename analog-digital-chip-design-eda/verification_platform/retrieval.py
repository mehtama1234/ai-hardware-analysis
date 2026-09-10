"""Evidence-linked lexical retrieval for verification collateral."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .ledger import EvidenceRef, evidence_for


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]+")


@dataclass(frozen=True)
class RetrievalDocument:
    path: str
    text: str
    evidence: EvidenceRef


def build_retrieval_index(paths: list[str | Path], *, root: str | Path, source_revision: str) -> dict[str, Any]:
    """Build a small deterministic index; typed parsers remain authoritative."""
    if not paths or not source_revision:
        raise ValueError("paths and source_revision are required")
    documents: list[RetrievalDocument] = []
    for path in paths:
        file_path = Path(path)
        relative = file_path.resolve().relative_to(Path(root).resolve()).as_posix()
        text = file_path.read_text(encoding="utf-8")
        documents.append(RetrievalDocument(relative, text, evidence_for(file_path, root=root, kind="retrieval-source", source_revision=source_revision)))
    index: dict[str, Any] = {"schema_version": "retrieval-index-v1", "source_revision": source_revision, "documents": [asdict(document) for document in documents]}
    index["index_sha256"] = hashlib.sha256(json.dumps(index, sort_keys=True, default=lambda value: value.__dict__, separators=(",", ":")).encode()).hexdigest()
    return index


def retrieve(index: dict[str, Any], query: str, *, limit: int = 5) -> list[dict[str, Any]]:
    """Return ranked snippets with source evidence; no result means no claim."""
    if not query.strip() or limit < 1:
        raise ValueError("query and positive limit are required")
    terms = {term.lower() for term in TOKEN_RE.findall(query)}
    hits = []
    for document in index.get("documents", []):
        lines = document["text"].splitlines()
        scored = [(sum(term in {token.lower() for token in TOKEN_RE.findall(line)} for term in terms), number, line) for number, line in enumerate(lines, 1)]
        scored = [item for item in scored if item[0]]
        if scored:
            score, line_number, line = max(scored)
            hits.append({"path": document["path"], "line": line_number, "snippet": line, "score": score, "evidence": document["evidence"]})
    return sorted(hits, key=lambda item: (-item["score"], item["path"], item["line"]))[:limit]


def write_retrieval_index(path: str | Path, index: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index, indent=2, sort_keys=True, default=lambda value: value.__dict__) + "\n", encoding="utf-8")
    return output
