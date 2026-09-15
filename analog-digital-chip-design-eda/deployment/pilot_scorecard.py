"""Validation rules for customer verification pilot scorecards."""
from __future__ import annotations

import re
import hashlib
import json
import math
from typing import Any


REQUIRED_METRICS = {
    "triage_latency",
    "root_cause_usefulness",
    "reproduction_time",
    "evidence_completeness",
    "manual_effort",
    "closure_integrity",
}


def _valid_confidence_interval(value: Any) -> bool:
    """Return whether a confidence interval is two finite ordered numbers."""
    if not isinstance(value, list) or len(value) != 2:
        return False
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item) for item in value):
        return False
    return value[0] <= value[1]


def validate_scorecard(scorecard: dict[str, Any], *, finalized: bool = False) -> list[str]:
    errors: list[str] = []
    if scorecard.get("schema_version") != "verification-pilot-scorecard-v1":
        errors.append("unsupported schema_version")
    self_digest = scorecard.get("scorecard_sha256")
    if self_digest is not None:
        if not isinstance(self_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", self_digest):
            errors.append("scorecard_sha256 must be a SHA-256 digest")
        else:
            payload = {key: value for key, value in scorecard.items() if key != "scorecard_sha256"}
            computed = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            if self_digest != computed:
                errors.append("scorecard_sha256 does not match scorecard content")
    pilot = scorecard.get("pilot") if isinstance(scorecard.get("pilot"), dict) else {}
    metrics = scorecard.get("metrics") if isinstance(scorecard.get("metrics"), list) else []
    names = {item.get("name") for item in metrics if isinstance(item, dict)}
    if names != REQUIRED_METRICS or len(metrics) != len(REQUIRED_METRICS):
        errors.append("all six required metrics must be present exactly once")
    if finalized and int(pilot.get("sample_size", 0) or 0) < 20:
        errors.append("finalized scorecard requires sample_size >= 20")
    for metric in metrics:
        if not isinstance(metric, dict):
            errors.append("metric entries must be objects")
            continue
        if finalized and (metric.get("baseline_median") is None or metric.get("workbench_median") is None):
            errors.append(f"{metric.get('name', 'metric')} requires baseline and workbench values")
        if finalized:
            for interval_name in ("baseline_confidence_95", "workbench_confidence_95"):
                interval = metric.get(interval_name)
                if not _valid_confidence_interval(interval):
                    errors.append(f"{metric.get('name', 'metric')} requires a valid {interval_name} interval")
        if finalized and not metric.get("evidence"):
            errors.append(f"{metric.get('name', 'metric')} requires evidence links")
    review = scorecard.get("review") if isinstance(scorecard.get("review"), dict) else {}
    digests = scorecard.get("evidence_sha256")
    if digests is not None:
        if not isinstance(digests, dict) or any(not isinstance(path, str) or not re.fullmatch(r"[0-9a-f]{64}", str(digest)) for path, digest in digests.items()):
            errors.append("evidence_sha256 must map evidence paths to SHA-256 digests")
        elif finalized and not digests:
            errors.append("finalized scorecard requires evidence digests")
    if finalized:
        if not str(review.get("lead_reviewer", "")).strip():
            errors.append("finalized scorecard requires a lead reviewer")
        receipt = str(review.get("receipt_sha256", ""))
        if not re.fullmatch(r"[0-9a-f]{64}", receipt):
            errors.append("finalized scorecard requires a SHA-256 receipt")
    return errors
