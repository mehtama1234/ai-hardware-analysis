"""Typed collateral inventory for the AIMC mixed-signal case study."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .claims import Claim, claim_status
from .ledger import EvidenceRef, evidence_for


@dataclass(frozen=True)
class CollateralEntry:
    path: str
    kind: str
    evidence: EvidenceRef


def build_mixed_signal_manifest(root: str | Path, entries: list[tuple[str, str]], *, source_revision: str, claims: list[Claim] | None = None) -> dict[str, Any]:
    """Hash an explicit AIMC evidence selection and evaluate domain claims."""
    repo = Path(root).resolve()
    if not source_revision or not entries:
        raise ValueError("source_revision and at least one collateral entry are required")
    seen: set[str] = set()
    artifacts: list[CollateralEntry] = []
    for relative, kind in entries:
        if not relative or Path(relative).is_absolute() or not kind:
            raise ValueError("collateral paths must be relative and kinds are required")
        if relative in seen:
            raise ValueError(f"duplicate collateral path: {relative}")
        seen.add(relative)
        artifacts.append(CollateralEntry(relative, kind, evidence_for(repo / relative, root=repo, kind=kind, source_revision=source_revision)))
    observed = {item.kind for item in artifacts}
    report: dict[str, Any] = {
        "schema_version": "mixed-signal-manifest-v1",
        "source_revision": source_revision,
        "artifacts": [asdict(item) for item in artifacts],
        "observed_evidence_kinds": sorted(observed),
        "claims": [{"text": claim.text, "domain": claim.domain, "evidence_kinds": list(claim.evidence_kinds), "status": claim_status(claim, observed)} for claim in (claims or [])],
    }
    report["manifest_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return report


def write_mixed_signal_manifest(path: str | Path, manifest: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
