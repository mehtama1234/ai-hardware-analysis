import pytest

from deployment.managed_state_contract import MIGRATION_STATEMENTS, SCHEMA_VERSION, migration_plan, validate_postgres_dsn


def test_postgres_dsn_is_validated_and_credentials_are_redacted():
    result = validate_postgres_dsn("postgresql://user:secret@db.internal:5432/verification?sslmode=require")
    assert result == "postgresql://db.internal:5432/verification?sslmode=require"


@pytest.mark.parametrize("dsn", ["", "sqlite:///pilot.db", "postgresql://db.internal", "postgresql:///verification"])
def test_postgres_dsn_rejects_non_managed_or_incomplete_values(dsn):
    with pytest.raises(ValueError):
        validate_postgres_dsn(dsn)


def test_migration_plan_preserves_state_contract():
    result = migration_plan("postgres://db.internal/verification")
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["statement_count"] == len(MIGRATION_STATEMENTS)
    assert any("verification_jobs" in statement for statement in result["statements"])
    assert any("verification_job_events" in statement for statement in result["statements"])
    assert "provider connection" in result["claim_boundary"]
