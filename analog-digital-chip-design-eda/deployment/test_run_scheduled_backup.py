import pytest

from deployment.run_scheduled_backup import run_scheduled_backup
from deployment.evidence_store import EvidenceObject


def test_scheduled_backup_entrypoint_is_callable():
    assert callable(run_scheduled_backup)


def test_scheduled_backup_publishes_immutable_dump(monkeypatch, tmp_path):
    import deployment.run_scheduled_backup as module

    monkeypatch.setenv("VERIFICATION_BACKUP_POLICY", "daily-14d")
    monkeypatch.setenv("VERIFICATION_DR_RPO_MINUTES", "60")
    monkeypatch.setenv("VERIFICATION_DR_RTO_MINUTES", "120")
    monkeypatch.setenv("VERIFICATION_BACKUP_SCHEDULE", "0 * * * *")
    monkeypatch.setattr(module, "compatibility_plan", lambda *args, **kwargs: {"compatible": True})
    monkeypatch.setattr(module, "backup_database", lambda dsn, output: (output.write_bytes(b"dump"), {"backup": str(output), "sha256": "local", "bytes": 4})[1])

    class Store:
        def put(self, key, content):
            return EvidenceObject(key, content, "published")

    result = run_scheduled_backup("postgresql://user:secret@db:5432/verify", tmp_path, evidence_store=Store(), bucket="evidence")
    assert result["backup"]["object_key"].startswith("backups/verification-")
    assert result["backup"]["object_sha256"] == "published"


def test_scheduled_backup_stops_before_dump_on_compatibility_failure(monkeypatch, tmp_path):
    import deployment.run_scheduled_backup as module

    monkeypatch.setenv("VERIFICATION_BACKUP_POLICY", "daily-14d")
    monkeypatch.setenv("VERIFICATION_DR_RPO_MINUTES", "60")
    monkeypatch.setenv("VERIFICATION_DR_RTO_MINUTES", "120")
    monkeypatch.setenv("VERIFICATION_BACKUP_SCHEDULE", "0 * * * *")
    called = []

    def incompatible(*args, **kwargs):
        raise RuntimeError("PostgreSQL client/server major mismatch")

    monkeypatch.setattr(module, "compatibility_plan", incompatible)
    monkeypatch.setattr(module, "backup_database", lambda *args, **kwargs: called.append(True))

    with pytest.raises(RuntimeError, match="major mismatch"):
        run_scheduled_backup("postgresql://user:secret@db:5432/verify", tmp_path)
    assert called == []
    assert list(tmp_path.iterdir()) == []
