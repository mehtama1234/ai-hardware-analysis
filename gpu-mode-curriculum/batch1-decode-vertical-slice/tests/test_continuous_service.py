from dataclasses import dataclass
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from continuous_service import ContinuousScheduler
from microbatch_control import MicrobatchScheduler


@dataclass(frozen=True)
class Handle:
    slot: int
    generation: int
    request_id: str


class ControlledBackend:
    def __init__(self):
        self.entries = {}
        self.generation = 0
        self.prefill_started = threading.Event()
        self.allow_prefill = threading.Event()
        self.tick_started = threading.Event()
        self.allow_tick = threading.Event()
        self.first_tick = True

    def admit(self, request_id, prompt, count):
        if request_id == 'peer':
            self.prefill_started.set()
            assert self.allow_prefill.wait(5)
        slot = next(i for i in range(2) if all(h.slot != i for h in self.entries))
        self.generation += 1
        handle = Handle(slot, self.generation, request_id)
        self.entries[handle] = [len(prompt), 1, count]
        return {'handle': handle, 'token_id': len(prompt), 'index': 0, 'status': 'active'}

    def cancel(self, handle):
        return self.entries.pop(handle, None) is not None

    def tick(self):
        if self.first_tick:
            self.first_tick = False
            self.tick_started.set()
            assert self.allow_tick.wait(5)
        events = []
        for handle, (value, index, count) in list(self.entries.items()):
            status = 'completed' if index + 1 == count else 'active'
            events.append({'handle': handle, 'token_id': value + index, 'index': index, 'status': status})
            if status == 'completed':
                del self.entries[handle]
            else:
                self.entries[handle][1] += 1
        return events


def collect(request):
    events = []
    while True:
        event = request.events.get(timeout=5)
        events.append(event)
        if event['type'] == 'done':
            return events


def test_replacement_admitted_before_peer_completes():
    backend = ControlledBackend()
    scheduler = ContinuousScheduler(backend, slots=2, max_tokens=5)
    try:
        peer = scheduler.submit('peer', 'abcd')
        assert backend.prefill_started.wait(5)
        cancelled = scheduler.submit('cancel', 'xy')
        backend.allow_prefill.set()
        assert backend.tick_started.wait(5)
        assert scheduler.cancel('cancel')
        replacement = scheduler.submit('replacement', 'abcdef')
        backend.allow_tick.set()
        first, second, third = collect(peer), collect(cancelled), collect(replacement)
        assert first[-1]['token_ids'] == [4, 5, 6, 7, 8]
        assert second[-1]['status'] == 'cancelled_inflight'
        assert second[-1]['token_ids'] == [2]
        assert third[-1]['token_ids'] == [6, 7, 8, 9, 10]
        state = scheduler.snapshot()
        admission = next(a for a in state['admissions'] if a['request_id'] == 'replacement')
        assert admission['peers'] == ['peer']
        assert state['active_or_queued'] == 0
        assert not backend.entries
    finally:
        backend.allow_prefill.set()
        backend.allow_tick.set()
        scheduler.close()


class CancelAwareGroupBackend:
    def __init__(self):
        self.second_row = threading.Event()
        self.release = threading.Event()

    def cancel(self, _handle):
        return True

    def batch_events(self, requests):
        yield [{'request_id': r.request_id, 'token_id': i, 'index': 0, 'status': 'active'}
               for i, r in enumerate(requests)]
        self.second_row.set()
        assert self.release.wait(5)
        yield [{'request_id': r.request_id, 'token_id': i + 2, 'index': 1,
                'status': 'completed'} for i, r in enumerate(requests)]


def test_microbatch_cancellation_discards_late_group_row():
    backend = CancelAwareGroupBackend()
    scheduler = MicrobatchScheduler(backend, slots=2, max_pending=2, max_tokens=2, window_ms=50)
    try:
        first = scheduler.submit('first', 'a', 2)
        second = scheduler.submit('second', 'b', 2)
        assert backend.second_row.wait(5)
        assert scheduler.cancel('first')
        backend.release.set()
        first_done = collect(first)[-1]
        second_done = collect(second)[-1]
        assert first_done['status'] == 'cancelled_inflight'
        assert first_done['token_ids'] == [0]
        assert second_done['status'] == 'completed'
        assert second_done['token_ids'] == [1, 3]
        assert scheduler.snapshot()['active_or_queued'] == 0
    finally:
        backend.release.set()
        scheduler.close()
