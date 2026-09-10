"""Human sign-off records bound to an exact proof-of-value report."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


def create_signoff(report_path: str | Path, *, reviewer: str, notes: str, approved: bool) -> dict[str, Any]:
    path = Path(report_path)
    if not reviewer.strip() or not notes.strip():
        raise ValueError("reviewer and notes are required")
    report = json.loads(path.read_text(encoding="utf-8"))
    report_hash = str(report.get("report_sha256") or report.get("comparison_sha256"))
    if len(report_hash) != 64:
        raise ValueError("report must contain a valid self-digest")
    return {"schema_version": "verification-signoff-v1", "status": "approved" if approved else "review_required", "reviewer": reviewer.strip(), "notes": notes.strip(), "report_path": str(path), "report_sha256": report_hash, "signed_at": datetime.now(timezone.utc).isoformat()}


def write_signoff(report_path: str | Path, *, reviewer: str, notes: str, approved: bool) -> Path:
    report = Path(report_path)
    signoff = create_signoff(report, reviewer=reviewer, notes=notes, approved=approved)
    output = report.parent / "pilot-signoff.json"
    output.write_text(json.dumps(signoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
