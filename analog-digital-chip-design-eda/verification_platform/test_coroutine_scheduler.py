from verification_platform.coroutine_scheduler import EmitEvent, WaitCycles, WaitEvent, run_cooperative_scheduler


def test_cooperative_scheduler_orders_time_zero_and_event_progress(tmp_path):
    observed = []

    def consumer():
        observed.append("consumer-t0")
        yield WaitEvent("clock")
        observed.append("consumer-after-clock")
        yield WaitCycles(2)
        observed.append("consumer-done")

    def clock():
        observed.append("clock-t0")
        yield WaitCycles(3)
        observed.append("clock-edge")
        yield EmitEvent("clock")

    result = run_cooperative_scheduler(
        {"consumer": consumer, "clock": clock},
        run_root=tmp_path / "run", source_revision="scheduler-v1", max_time=10,
    )
    assert result["status"] == "passed"
    assert result["outcome"] == "normal_completion"
    assert observed == ["clock-t0", "consumer-t0", "clock-edge", "consumer-after-clock", "consumer-done"]
    assert (tmp_path / "run/cooperative-scheduler-result.json").is_file()


def test_cooperative_scheduler_blocks_on_time_zero_deadlock(tmp_path):
    def waiting():
        yield WaitEvent("never_emitted")

    result = run_cooperative_scheduler(
        {"waiting": waiting}, run_root=tmp_path / "deadlock", source_revision="scheduler-deadlock-v1",
    )
    assert result["status"] == "blocked"
    assert result["outcome"] == "deadlock"
    assert "never_emitted" in result["blocked_reason"]


def test_cooperative_scheduler_bounds_zero_cycle_livelock(tmp_path):
    def livelock():
        while True:
            yield WaitCycles(0)

    result = run_cooperative_scheduler(
        {"livelock": livelock}, run_root=tmp_path / "timeout", source_revision="scheduler-timeout-v1", max_steps=4,
    )
    assert result["status"] == "blocked"
    assert result["outcome"] == "timeout"
