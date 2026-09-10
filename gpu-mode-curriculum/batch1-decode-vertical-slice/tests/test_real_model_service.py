import json
import queue
import sys
import threading
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from real_model_service import StreamingScheduler, make_server


class Backend:
    def batch_events(self, prompts, max_tokens, cancellations):
        for step in range(max_tokens):
            if all(event.is_set() for event in cancellations):
                break
            yield {'token_ids': [len(prompt) + step for prompt in prompts], 'step_ms': 1.0}


def done(request):
    while True:
        event = request.events.get(timeout=3)
        if event['type'] == 'done':
            return event


def test_mixed_length_streams_preserve_request_identity():
    scheduler = StreamingScheduler(Backend(), window_ms=100, max_tokens=3)
    try:
        a = scheduler.submit('a', 'x')
        b = scheduler.submit('b', 'long')
        assert done(a)['token_ids'] == [1, 2, 3]
        assert done(b)['token_ids'] == [4, 5, 6]
        state = scheduler.snapshot()
        assert state['batches'][0]['size'] == 2
        assert state['active_or_queued'] == 0
        with pytest.raises(ValueError):
            scheduler.submit('a', 'duplicate')
    finally:
        scheduler.close()


def test_queue_rejection_and_queued_cancellation_do_not_execute_cancelled_work():
    started, release = threading.Event(), threading.Event()
    class BlockingBackend(Backend):
        def batch_events(self, prompts, max_tokens, cancellations):
            started.set()
            assert release.wait(timeout=3)
            yield from super().batch_events(prompts, max_tokens, cancellations)
    scheduler = StreamingScheduler(BlockingBackend(), max_batch=1, max_pending=1, max_tokens=3)
    try:
        first = scheduler.submit('first', 'one')
        assert started.wait(timeout=3)
        queued = scheduler.submit('queued', 'two')
        with pytest.raises(queue.Full):
            scheduler.submit('rejected', 'three')
        assert scheduler.cancel('queued')
        release.set()
        assert done(first)['status'] == 'completed'
        assert done(queued)['status'] == 'cancelled_queued'
        assert scheduler.snapshot()['rejected'] == 1
    finally:
        release.set()
        scheduler.close()


def test_inflight_cancellation_stops_next_token_and_keeps_peer_output():
    first_token, resume = threading.Event(), threading.Event()
    class SteppedBackend(Backend):
        def batch_events(self, prompts, max_tokens, cancellations):
            for step, event in enumerate(super().batch_events(prompts, max_tokens, cancellations)):
                yield event
                if step == 0:
                    first_token.set()
                    assert resume.wait(timeout=3)
    scheduler = StreamingScheduler(SteppedBackend(), window_ms=100, max_tokens=3)
    try:
        cancelled = scheduler.submit('cancel', 'x')
        peer = scheduler.submit('peer', 'abc')
        assert first_token.wait(timeout=3)
        assert scheduler.cancel('cancel')
        resume.set()
        assert done(cancelled)['status'] == 'cancelled_inflight'
        assert scheduler.snapshot()['records']['cancel']['token_ids'] == [1]
        assert done(peer)['token_ids'] == [3, 4, 5]
    finally:
        resume.set()
        scheduler.close()


def test_actual_http_stream_carries_token_events_and_terminal_accounting():
    scheduler = StreamingScheduler(Backend(), max_tokens=3)
    server = make_server(scheduler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        data = json.dumps({'request_id': 'http', 'prompt': 'abcd'}).encode()
        with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{server.server_port}/stream', data,
                                     headers={'Content-Type': 'application/json'}), timeout=3) as response:
            events = [json.loads(line) for line in response]
        assert [e['token_id'] for e in events[:-1]] == [4, 5, 6]
        assert events[-1]['status'] == 'completed'
        assert events[-1]['prefill_batch_ms'] == 1
        assert events[-1]['decode_batch_ms'] == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        scheduler.close()
