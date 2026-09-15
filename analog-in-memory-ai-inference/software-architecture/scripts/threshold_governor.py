"""Fail-closed per-vector analog/digital routing policy."""

from __future__ import annotations

from typing import Any


def decide_vector(
    *,
    relative_l2_error: float | None,
    relative_l2_limit: float,
    clipping_passed: bool,
    profile_supported: bool,
    timing_evidence_passed: bool,
    analog_authorized: bool,
) -> dict[str, Any]:
    """Return a deterministic route; analog requires every gate to pass."""
    if relative_l2_limit <= 0:
        raise ValueError("relative_l2_limit must be positive")
    quality_passed = relative_l2_error is not None and relative_l2_error <= relative_l2_limit
    reasons = []
    if not quality_passed:
        reasons.append("per_vector_relative_l2_exceeds_limit_or_missing")
    if not clipping_passed:
        reasons.append("recorded_clipping")
    if not profile_supported:
        reasons.append("open_converter_profile_cases")
    if not timing_evidence_passed:
        reasons.append("timing_profile_not_measured_for_this_vector")
    if not analog_authorized:
        reasons.append("analog_authorization_disabled")
    eligible = quality_passed and clipping_passed and profile_supported and timing_evidence_passed and analog_authorized
    return {
        "quality_gate": {"relative_l2_error": relative_l2_error,
                         "limit": relative_l2_limit, "passed": quality_passed},
        "clipping_gate": {"passed": clipping_passed},
        "profile_support_gate": {"passed": profile_supported},
        "timing_evidence_gate": {"passed": timing_evidence_passed},
        "authorization_gate": {"analog_authorized": analog_authorized,
                                "passed": analog_authorized},
        "eligible_for_analog_candidate": eligible,
        "rejection_reasons": reasons,
        "enforced_route": "analog_candidate" if eligible else "digital_fallback",
    }
