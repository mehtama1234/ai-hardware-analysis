from deployment.apply_managed_state_migration import INDEXES, TABLES


def test_migration_contract_names_all_expected_objects():
    assert TABLES == ("verification_projects", "verification_collateral", "verification_jobs", "verification_job_events")
    assert INDEXES == ("verification_jobs_project_status_idx", "verification_events_job_created_idx")
