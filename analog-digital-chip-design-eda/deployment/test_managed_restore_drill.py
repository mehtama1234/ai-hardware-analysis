from deployment.managed_restore_drill import TABLES


def test_restore_drill_covers_all_managed_tables():
    assert TABLES == ("verification_projects", "verification_collateral", "verification_jobs", "verification_job_events")
