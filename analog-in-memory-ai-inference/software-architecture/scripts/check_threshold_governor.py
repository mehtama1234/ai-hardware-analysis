#!/usr/bin/env python3
"""Unit checks for the local fail-closed threshold governor."""

from threshold_governor import decide_vector


def check(name, expected_route, **kwargs):
    result = decide_vector(**kwargs)
    assert result["enforced_route"] == expected_route, (name, result)
    assert result["eligible_for_analog_candidate"] is (expected_route == "analog_candidate")


def main():
    base = dict(relative_l2_error=0.005, relative_l2_limit=0.01,
                clipping_passed=True, profile_supported=True,
                timing_evidence_passed=True, analog_authorized=True)
    check("all gates pass", "analog_candidate", **base)
    for field in ("clipping_passed", "profile_supported", "timing_evidence_passed", "analog_authorized"):
        case = dict(base, **{field: False})
        check(field, "digital_fallback", **case)
    check("quality fail", "digital_fallback", **dict(base, relative_l2_error=0.011))
    check("missing quality", "digital_fallback", **dict(base, relative_l2_error=None))
    print("THRESHOLD GOVERNOR OK: all-pass and five fail-closed cases")


if __name__ == "__main__":
    main()
