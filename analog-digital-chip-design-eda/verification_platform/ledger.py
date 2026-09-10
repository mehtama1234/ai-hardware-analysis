"""Deterministic provenance helpers for verification runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

from .ir import EvidenceRef


def sha256_file(path: str | Path) -> str:
    """Hash a file in bounded chunks without loading it into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_for(path: str | Path, *, root: str | Path, kind: str, source_revision: str) -> EvidenceRef:
    """Create a validated relative evidence reference for a file under *root*."""
    root_path = Path(root).resolve()
    file_path = Path(path).resolve()
    try:
        relative = file_path.relative_to(root_path)
    except ValueError as exc:
        raise ValueError("evidence file must be inside the ledger root") from exc
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    ref = EvidenceRef(relative.as_posix(), sha256_file(file_path), kind, source_revision)
    ref.validate()
    return ref


@dataclass
class ToolRun:
    id: str
    tool: str
    command: list[str]
    status: str
    exit_code: int | None = None
    source_revision: str = "unknown"
    artifacts: list[EvidenceRef] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.id or not self.tool or not self.command:
            raise ValueError("tool run requires id, tool, and command")
        if self.status not in {"planned", "running", "passed", "failed", "blocked", "unknown"}:
            raise ValueError(f"invalid tool run status: {self.status}")
        for artifact in self.artifacts:
            artifact.validate()


@dataclass
class ProvenanceLedger:
    schema_version: str = "provenance-ledger-v1"
    runs: list[ToolRun] = field(default_factory=list)

    def validate(self) -> None:
        if self.schema_version != "provenance-ledger-v1":
            raise ValueError(f"unsupported schema version: {self.schema_version}")
        ids: set[str] = set()
        for run in self.runs:
            run.validate()
            if run.id in ids:
                raise ValueError(f"duplicate tool run id: {run.id}")
            ids.add(run.id)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def write(self, path: str | Path) -> str:
        self.validate()
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
