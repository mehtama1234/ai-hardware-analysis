from deployment.job_queue import DurableJobQueue
from datetime import datetime, timedelta, timezone

def test_durable_queue_claim_finish_and_cancel(tmp_path):
    queue = DurableJobQueue(tmp_path / "jobs.sqlite")
    queued = queue.enqueue("job-1", project_id="p1", kind="pilot", payload={"revision": "r1"})
    assert queued["status"] == "queued"
    claimed = queue.claim(); assert claimed["id"] == "job-1" and claimed["status"] == "running"
    assert queue.finish("job-1", status="passed")["status"] == "passed"
    queue.enqueue("job-2", project_id="p1", kind="pilot")
    assert queue.cancel("job-2")["status"] == "cancelled"
    assert queue.claim() is None
    queue.enqueue("job-3", project_id="p1", kind="pilot")
    assert queue.start("job-3")["status"] == "running"
    with queue._connect() as db:
        old = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        db.execute("UPDATE jobs SET updated_at=? WHERE id='job-3'", (old,))
    assert queue.requeue_stale(max_age_seconds=60) == 1
    assert queue.claim()["id"] == "job-3"
    assert queue.counts() == {"cancelled": 1, "passed": 1, "running": 1}
