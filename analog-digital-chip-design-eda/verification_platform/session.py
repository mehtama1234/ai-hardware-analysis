"""Auditable lifecycle state for an agentic verification session."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


STAGES = ("created", "planned", "executed", "triaged", "repair_review", "retested", "closed")


@dataclass(frozen=True)
class SessionEvent:
    stage: str
    metadata: dict[str, Any]


class VerificationSession:
    """Monotonic lifecycle ledger; tools still provide the actual evidence."""

    def __init__(self, *, session_id: str, run_root: str | Path, source_revision: str):
        if not session_id or not source_revision:
            raise ValueError("session_id and source_revision are required")
        self.session_id = session_id
        self.run_root = Path(run_root)
        self.source_revision = source_revision
        self.events = [SessionEvent("created", {})]

    @property
    def stage(self) -> str:
        return self.events[-1].stage

    def advance(self, stage: str, *, metadata: dict[str, Any] | None = None) -> SessionEvent:
        if stage not in STAGES:
            raise ValueError(f"unknown session stage: {stage}")
        if STAGES.index(stage) != STAGES.index(self.stage) + 1:
            raise ValueError(f"invalid transition {self.stage} -> {stage}")
        event = SessionEvent(stage, dict(metadata or {}))
        self.events.append(event)
        return event

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": "verification-session-v1",
            "session_id": self.session_id,
            "source_revision": self.source_revision,
            "events": [asdict(event) for event in self.events],
        }
        payload["session_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return payload

    def write(self, path: str | Path | None = None) -> Path:
        output = Path(path) if path else self.run_root / "session-ledger.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return output
