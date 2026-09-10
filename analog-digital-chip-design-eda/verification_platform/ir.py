"""Typed, deterministic verification IR used by agents and tool adapters.

The IR deliberately stores claims separately from evidence.  Agents can propose
objects, but a closure decision is only valid when it references recorded tool
artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

Status = Literal["planned", "running", "passed", "failed", "blocked", "unknown"]


@dataclass(frozen=True)
class EvidenceRef:
    """A content-addressed reference to a repo-local or run-produced artifact."""

    path: str
    sha256: str
    kind: str
    source_revision: str = "unknown"

    def validate(self) -> None:
        if not self.path or Path(self.path).is_absolute():
            raise ValueError("evidence path must be a non-empty relative path")
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256):
            raise ValueError("evidence sha256 must be a lowercase 64-character hex digest")
        if not self.kind:
            raise ValueError("evidence kind is required")


@dataclass
class Requirement:
    id: str
    text: str
    status: Status = "planned"
    evidence: list[EvidenceRef] = field(default_factory=list)
    source: EvidenceRef | None = None

    def validate(self) -> None:
        if not self.id or not self.text:
            raise ValueError("requirement id and text are required")
        if self.source:
            self.source.validate()
        for ref in self.evidence:
            ref.validate()


@dataclass
class VerificationIR:
    """Versioned graph root; additional entity types can be added compatibly."""

    schema_version: str = "verification-ir-v1"
    design_revision: str = "unknown"
    requirements: list[Requirement] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)
    tool_runs: list[dict[str, Any]] = field(default_factory=list)
    closure_decisions: list[dict[str, Any]] = field(default_factory=list)

    def validate(self) -> None:
        if self.schema_version != "verification-ir-v1":
            raise ValueError(f"unsupported schema version: {self.schema_version}")
        ids: set[str] = set()
        for requirement in self.requirements:
            requirement.validate()
            if requirement.id in ids:
                raise ValueError(f"duplicate requirement id: {requirement.id}")
            ids.add(requirement.id)
        for check in self.checks:
            requirement_id = check.get("requirement_id")
            if requirement_id and requirement_id not in ids:
                raise ValueError(f"check references unknown requirement: {requirement_id}")
        for run in self.tool_runs:
            if not run.get("id") or not run.get("tool") or run.get("status") not in {
                "planned", "running", "passed", "failed", "blocked", "unknown"
            }:
                raise ValueError("tool run requires id, tool, and valid status")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def write(self, path: str | Path) -> str:
        """Write canonical JSON and return its digest."""
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.canonical_json() + "\n", encoding="utf-8")
        return self.digest()
