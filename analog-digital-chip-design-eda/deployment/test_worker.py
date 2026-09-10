from deployment import worker


def test_worker_process_once_empty_queue(tmp_path, monkeypatch):
    monkeypatch.setattr(worker, "JOB_ROOT", tmp_path / "jobs")
    assert worker.process_once() is False
