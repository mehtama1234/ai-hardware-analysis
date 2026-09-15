import pytest

from .security_closure import evaluate_security_task, validate_security_suite


TASK = {
    "task_id": "privilege-register-write",
    "threat_class": "unauthorized-register-access",
    "source_revision": "soc-v1",
    "origin_seed": "seed-0042",
    "detection_mechanism": "assertion-and-directed-test",
}


def test_security_task_requires_all_machine_checks_before_review():
    suite = {"schema_version": "security-task-suite-v1", "tasks": [TASK]}
    validate_security_suite(suite)
    result = evaluate_security_task(TASK, detected=True, localized=True, repaired_copy_passed=True, regression_passed=True, evidence=["cex.json", "repair-retest.json"])
    assert result["status"] == "review_required"
    assert result["machine_checks_passed"] is True


def test_security_task_cannot_sign_off_when_detection_or_regression_fails():
    result = evaluate_security_task(TASK, detected=False, localized=True, repaired_copy_passed=True, regression_passed=False, evidence=["run.json"], human_review="approved")
    assert result["status"] == "blocked"


def test_human_approval_is_required_for_signed_off_state():
    result = evaluate_security_task(TASK, detected=True, localized=True, repaired_copy_passed=True, regression_passed=True, evidence=["audit.json"], human_review="approved")
    assert result["status"] == "signed_off"


def test_security_evidence_and_review_state_are_validated():
    with pytest.raises(ValueError, match="evidence"):
        evaluate_security_task(TASK, detected=True, localized=True, repaired_copy_passed=True, regression_passed=True, evidence=[])
    with pytest.raises(ValueError, match="human_review"):
        evaluate_security_task(TASK, detected=True, localized=True, repaired_copy_passed=True, regression_passed=True, evidence=["audit.json"], human_review="auto")
