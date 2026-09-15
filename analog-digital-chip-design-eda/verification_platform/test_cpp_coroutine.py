from pathlib import Path

from verification_platform.cpp_coroutine import run_cpp_coroutine_probe


COROUTINE_SOURCE = r'''
#include <coroutine>
#include <cstdio>
#include <exception>
struct task {
  struct promise_type {
    task get_return_object() { return task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_never initial_suspend() noexcept { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }
    void return_void() noexcept {}
    void unhandled_exception() { std::terminate(); }
  };
  std::coroutine_handle<promise_type> handle;
  ~task() { if (handle) handle.destroy(); }
};
task work(int& value) { value = 1; co_await std::suspend_always{}; value = 2; }
int main() {
  int value = 0; auto coroutine = work(value);
  if (value != 1) return 1;
  coroutine.handle.resume();
  if (value != 2) return 2;
  std::puts("CPP_COROUTINE_PASS"); return 0;
}
'''


def test_cpp20_coroutine_probe_compiles_and_runs(tmp_path: Path):
    source = tmp_path / "probe.cpp"
    source.write_text(COROUTINE_SOURCE, encoding="utf-8")
    result = run_cpp_coroutine_probe(source, run_root=tmp_path / "run", source_revision="cpp20-v1")
    assert result["status"] == "passed"
    assert result["pass_marker_present"] is True
    assert (tmp_path / "run/cpp-coroutine-result.json").is_file()


def test_cpp20_coroutine_probe_blocks_without_runtime_marker(tmp_path: Path):
    source = tmp_path / "probe.cpp"
    source.write_text("int main() { return 0; }\n", encoding="utf-8")
    result = run_cpp_coroutine_probe(source, run_root=tmp_path / "run", source_revision="cpp20-no-marker-v1")
    assert result["status"] == "blocked"
    assert result["pass_marker_present"] is False


def test_cpp20_coroutine_probe_records_time_zero_and_event_progress(tmp_path: Path):
    source = tmp_path / "scheduler.cpp"
    source.write_text(r'''
#include <coroutine>
#include <cstdio>
#include <exception>
struct task {
  struct promise_type {
    task get_return_object() { return task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_never initial_suspend() noexcept { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }
    void return_void() noexcept {}
    void unhandled_exception() { std::terminate(); }
  };
  std::coroutine_handle<promise_type> handle;
  ~task() { if (handle) handle.destroy(); }
};
task event_process(int& state) {
  std::puts("CPP_TIME_ZERO");
  co_await std::suspend_always{};
  state = 1;
  std::puts("CPP_EVENT_PROGRESS");
}
int main() {
  int state = 0; auto process = event_process(state);
  if (state != 0) return 1;
  process.handle.resume();
  if (state != 1) return 2;
  std::puts("CPP_SCHEDULER_PASS"); return 0;
}
''', encoding="utf-8")
    result = run_cpp_coroutine_probe(
        source, run_root=tmp_path / "run", source_revision="cpp20-scheduler-v1",
        pass_marker="CPP_SCHEDULER_PASS",
        required_markers=("CPP_TIME_ZERO", "CPP_EVENT_PROGRESS", "CPP_SCHEDULER_PASS"),
    )
    assert result["status"] == "passed"
    assert result["missing_markers"] == []
    assert result["required_markers_present"] is True
