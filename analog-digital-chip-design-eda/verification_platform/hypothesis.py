"""Evidence-balanced, deterministic root-cause hypothesis ranking."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable


def build_competing_hypotheses(
    candidates: dict[str, object],
    *,
    for_evidence: Iterable[str],
    against_evidence: Iterable[str],
) -> dict[str, object]:
    """Create ranked review hypotheses from source-bound frontier candidates.

    The ranking only reflects the strength of the deterministic localization
    edge (direct driver versus assignment fallback). It never promotes a
    hypothesis to a root-cause claim.
    """
    result: dict[str, object] = {
        "schema_version": "competing-root-cause-hypotheses-v1",
        "status": "blocked",
        "candidate_result_sha256": candidates.get("result_sha256"),
        "hypotheses": [],
        "claim_boundary": "ranked, balanced hypotheses for review; not a proven root cause or approved repair",
    }
    if candidates.get("status") != "available":
        result["blocked_reason"] = "available source-bound root-cause candidates are required"
    else:
        positive = [item.strip() for item in for_evidence if isinstance(item, str) and item.strip()]
        negative = [item.strip() for item in against_evidence if isinstance(item, str) and item.strip()]
        hypotheses: list[dict[str, object]] = []
        for candidate in candidates.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            reason = str(candidate.get("reason", ""))
            score = 1.0 if "direct structural driver" in reason else 0.5
            hypotheses.append({
                "rank": 0,
                "score": score,
                "file": candidate.get("file"),
                "line": candidate.get("line"),
                "text": candidate.get("text"),
                "for_evidence": [reason, *positive],
                "against_evidence": ["the source location is correlated with the frontier but does not establish causality", *negative],
                "status": "review_required",
            })
        hypotheses.sort(key=lambda item: (-float(item["score"]), str(item.get("file")), int(item.get("line", 0))))
        for rank, hypothesis in enumerate(hypotheses, 1):
            hypothesis["rank"] = rank
        result["hypotheses"] = hypotheses
        result["status"] = "available" if hypotheses else "blocked"
        if not hypotheses:
            result["blocked_reason"] = "candidate list contained no usable source locations"
    result["hypotheses_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result
