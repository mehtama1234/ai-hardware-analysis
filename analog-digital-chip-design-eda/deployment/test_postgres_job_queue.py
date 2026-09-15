from deployment.postgres_job_queue import PostgresJobQueue


def test_postgres_queue_surface_matches_durable_queue_contract():
    for method in ("enqueue", "get", "counts", "claim", "requeue_stale", "start", "finish", "cancel"):
        assert callable(getattr(PostgresJobQueue, method))
