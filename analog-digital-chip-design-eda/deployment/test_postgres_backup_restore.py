import pytest

from deployment.postgres_backup_restore import _command_args, ensure_distinct_restore_target


def test_backup_command_keeps_password_out_of_process_arguments():
    args, env = _command_args("postgresql://user:secret@db.internal:5432/verification")
    assert "secret" not in " ".join(args)
    assert env["PGPASSWORD"] == "secret"
    assert args[-1] == "verification"


def test_restore_target_must_be_distinct_from_source():
    with pytest.raises(ValueError, match="distinct"):
        ensure_distinct_restore_target(
            "postgresql://user:secret@db.internal:5432/verification",
            "postgresql://user:other@db.internal/verification",
        )


def test_restore_target_accepts_disposable_database():
    ensure_distinct_restore_target(
        "postgresql://user:secret@db.internal:5432/verification",
        "postgresql://user:other@db.internal:5432/verification_restore",
    )
