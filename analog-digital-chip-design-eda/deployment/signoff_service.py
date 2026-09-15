"""Human sign-off records bound to an exact proof-of-value report."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


def create_signoff(report_path: str | Path, *, reviewer: str, notes: str, approved: bool, reviewer_subject: str | None = None) -> dict[str, Any]:
    path = Path(report_path)
    if not reviewer.strip() or not notes.strip():
        raise ValueError("reviewer and notes are required")
    report = json.loads(path.read_text(encoding="utf-8"))
    report_hash = str(report.get("report_sha256") or report.get("comparison_sha256") or report.get("scorecard_sha256"))
    if len(report_hash) != 64:
        raise ValueError("report must contain a valid self-digest")
    result = {"schema_version": "verification-signoff-v1", "status": "approved" if approved else "review_required", "reviewer": reviewer.strip(), "notes": notes.strip(), "report_path": str(path), "report_sha256": report_hash, "signed_at": datetime.now(timezone.utc).isoformat()}
    if reviewer_subject is not None:
        if not reviewer_subject.strip() or len(reviewer_subject.strip()) > 256:
            raise ValueError("reviewer subject must be non-empty and at most 256 characters")
        result["reviewer_subject"] = reviewer_subject.strip()
    return result


def write_signoff(report_path: str | Path, *, reviewer: str, notes: str, approved: bool, reviewer_subject: str | None = None) -> Path:
    report = Path(report_path)
    signoff = create_signoff(report, reviewer=reviewer, notes=notes, approved=approved, reviewer_subject=reviewer_subject)
    output = report.parent / "pilot-signoff.json"
    output.write_text(json.dumps(signoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def verify_signoff(signoff_path: str | Path) -> bool:
    """Verify both the report self-digest and the digest recorded at sign-off."""
    try:
        signoff = json.loads(Path(signoff_path).read_text(encoding="utf-8"))
        report_path = Path(signoff["report_path"])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        digest_key = next((key for key in ("report_sha256", "comparison_sha256", "scorecard_sha256") if isinstance(report.get(key), str)), None)
        if digest_key is None:
            return False
        stored = report[digest_key]
        payload = {key: value for key, value in report.items() if key != digest_key}
        computed = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return signoff.get("report_sha256") == stored == computed
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
