"""Deterministic reference semantics for cooperative verification coroutines."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import heapq
import json
from pathlib import Path
from typing import Callable, Iterator


@dataclass(frozen=True)
class WaitCycles:
    cycles: int


@dataclass(frozen=True)
class WaitEvent:
    name: str


@dataclass(frozen=True)
class EmitEvent:
    name: str


Yielded = WaitCycles | WaitEvent | EmitEvent | None
CoroutineFactory = Callable[[], Iterator[Yielded]]


def run_cooperative_scheduler(
    processes: dict[str, CoroutineFactory],
    *,
    run_root: str | Path,
    source_revision: str,
    max_time: int = 1000,
    max_steps: int = 10000,
) -> dict[str, object]:
    """Run named coroutines with deterministic cooperative scheduling.

    A process yields ``WaitCycles(n)`` to resume at a future simulated cycle,
    ``WaitEvent(name)`` to suspend until another process emits that event, or
    ``EmitEvent(name)`` to wake all processes waiting for it at the current
    cycle.  The scheduler never preempts a process between yields.  An empty
    runnable queue with waiting processes is a deadlock; exceeding either
    bound is a timeout.  This models scheduling behavior only and is not a
    claim of Verilator, UVM, or C++20 coroutine compatibility.
    """
    if not processes or not source_revision or max_time < 0 or max_steps < 1:
        raise ValueError("processes, source_revision, nonnegative max_time, and positive max_steps are required")
    if any(not name for name in processes):
        raise ValueError("coroutine process names must be non-empty")
    root = Path(run_root)
    iterators: dict[str, Iterator[Yielded]] = {}
    queue: list[tuple[int, int, str]] = []
    waiting: dict[str, set[str]] = {}
    done: set[str] = set()
    trace: list[dict[str, object]] = []
    order = 0
    for name in sorted(processes):
        try:
            iterator = processes[name]()
            iterators[name] = iterator
        except Exception as error:
            return _write_result(root, {"schema_version": "cooperative-scheduler-v1", "status": "blocked", "outcome": "process_initialization_error", "error": f"{name}: {error}", "source_revision": source_revision, "claim_boundary": "deterministic scheduler model only; not Verilator/UVM compatibility"})
        heapq.heappush(queue, (0, order, name))
        order += 1
    current_time = 0
    steps = 0
    status = "blocked"
    outcome = "deadlock"
    blocked_reason = None
    while queue:
        current_time, _, name = heapq.heappop(queue)
        if current_time > max_time:
            outcome, blocked_reason = "timeout", "scheduled work exceeded max_time"
            break
        steps += 1
        if steps > max_steps:
            outcome, blocked_reason = "timeout", "scheduler exceeded max_steps"
            break
        try:
            yielded = next(iterators[name])
        except StopIteration:
            done.add(name)
            trace.append({"time": current_time, "process": name, "action": "complete"})
            if len(done) == len(iterators):
                status, outcome = "passed", "normal_completion"
                break
            continue
        except Exception as error:
            outcome, blocked_reason = "process_failure", f"{name}: {error}"
            break
        if yielded is None:
            trace.append({"time": current_time, "process": name, "action": "yield"})
            heapq.heappush(queue, (current_time, order, name))
            order += 1
        elif isinstance(yielded, WaitCycles):
            if yielded.cycles < 0:
                outcome, blocked_reason = "invalid_wait", f"{name} yielded a negative cycle wait"
                break
            trace.append({"time": current_time, "process": name, "action": "wait_cycles", "cycles": yielded.cycles})
            heapq.heappush(queue, (current_time + yielded.cycles, order, name))
            order += 1
        elif isinstance(yielded, WaitEvent):
            if not yielded.name:
                outcome, blocked_reason = "invalid_wait", f"{name} yielded an unnamed event wait"
                break
            waiting.setdefault(yielded.name, set()).add(name)
            trace.append({"time": current_time, "process": name, "action": "wait_event", "event": yielded.name})
        elif isinstance(yielded, EmitEvent):
            if not yielded.name:
                outcome, blocked_reason = "invalid_event", f"{name} emitted an unnamed event"
                break
            trace.append({"time": current_time, "process": name, "action": "emit_event", "event": yielded.name})
            for waiting_name in sorted(waiting.pop(yielded.name, set())):
                heapq.heappush(queue, (current_time, order, waiting_name))
                order += 1
            heapq.heappush(queue, (current_time, order, name))
            order += 1
        else:
            outcome, blocked_reason = "invalid_yield", f"{name} yielded unsupported value {type(yielded).__name__}"
            break
    if status != "passed" and blocked_reason is None:
        if waiting:
            waiting_events = {event: sorted(names) for event, names in sorted(waiting.items())}
            blocked_reason = f"no runnable process; waiting events: {waiting_events}"
        else:
            blocked_reason = "scheduler stopped without normal completion"
    result: dict[str, object] = {
        "schema_version": "cooperative-scheduler-v1",
        "status": status,
        "outcome": outcome,
        "source_revision": source_revision,
        "processes": sorted(processes),
        "completed_processes": sorted(done),
        "simulated_time": current_time,
        "steps": steps,
        "trace": trace,
        "claim_boundary": "deterministic cooperative scheduler model only; not Verilator/UVM/C++20 compatibility",
    }
    if blocked_reason:
        result["blocked_reason"] = blocked_reason
    return _write_result(root, result)


def _write_result(root: Path, result: dict[str, object]) -> dict[str, object]:
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "cooperative-scheduler-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
