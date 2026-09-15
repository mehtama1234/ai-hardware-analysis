import pytest

from deployment.backup_policy import load_backup_policy


def test_backup_policy_requires_schedule_and_targets(monkeypatch):
    monkeypatch.setenv("VERIFICATION_BACKUP_POLICY", "daily-35d")
    monkeypatch.setenv("VERIFICATION_DR_RPO_MINUTES", "15")
    monkeypatch.setenv("VERIFICATION_DR_RTO_MINUTES", "60")
    monkeypatch.setenv("VERIFICATION_BACKUP_SCHEDULE", "0 * * * *")
    policy = load_backup_policy()
    assert policy.retention_days == 35
    assert policy.rpo_minutes == 15
    assert policy.schedule == "0 * * * *"


def test_backup_policy_rejects_short_retention(monkeypatch):
    monkeypatch.setenv("VERIFICATION_BACKUP_POLICY", "daily-1d")
    monkeypatch.setenv("VERIFICATION_DR_RPO_MINUTES", "15")
    monkeypatch.setenv("VERIFICATION_DR_RTO_MINUTES", "60")
    with pytest.raises(ValueError):
        load_backup_policy()
