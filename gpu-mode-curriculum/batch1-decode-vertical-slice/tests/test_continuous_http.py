from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import threading
import urllib.error
import urllib.request

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from continuous_http import make_server
from continuous_service import ContinuousScheduler
from test_continuous_service import Handle, ControlledBackend


class BudgetBackend:
    def __init__(self):
        self.live = {}
        self.serial = 0

    def admit(self, request_id, prompt, count):
        self.serial += 1
        handle = Handle(self.serial, 1, request_id)
        if count > 1:
            self.live[handle] = [prompt, count, 1]
        return {'handle': handle, 'token_id': len(prompt), 'index': 0,
                'status': 'completed' if count == 1 else 'active'}

    def cancel(self, handle):
        return self.live.pop(handle, None) is not None

    def tick(self):
        events = []
        for handle, (prompt, count, index) in list(self.live.items()):
            status = 'eos' if prompt == 'eos' else 'completed' if index + 1 == count else 'active'
            events.append({'handle': handle, 'token_id': len(prompt) + index, 'index': index, 'status': status})
            if status != 'active':
                del self.live[handle]
            else:
                self.live[handle][2] += 1
        return events


def post(url, path, payload):
    return urllib.request.urlopen(urllib.request.Request(url + path,
        json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}), timeout=10)


@pytest.fixture
def serving():
    servers = []
    def start(backend, **kwargs):
        scheduler = ContinuousScheduler(backend, **kwargs)
        server = make_server(scheduler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        servers.append((scheduler, server, thread, backend))
        return scheduler, f'http://127.0.0.1:{server.server_port}'
    yield start
    for scheduler, server, thread, backend in servers:
        if isinstance(backend, ControlledBackend):
            backend.allow_prefill.set()
            backend.allow_tick.set()
        scheduler.close()
        server.shutdown()
        server.server_close()
        thread.join(5)


def test_mixed_output_limits_and_eos_are_streamed(serving):
    scheduler, url = serving(BudgetBackend(), slots=2, max_tokens=6)
    for count in (1, 3, 6):
        with post(url, '/stream', {'request_id': str(count), 'prompt': 'abcd', 'max_new_tokens': count}) as response:
            events = [json.loads(line) for line in response]
        assert [e['token_id'] for e in events[:-1]] == list(range(4, 4 + count))
        assert events[-1]['max_new_tokens'] == count
        assert events[-1]['finish_reason'] == 'length'
    with post(url, '/stream', {'request_id': 'eos', 'prompt': 'eos', 'max_new_tokens': 6}) as response:
        events = [json.loads(line) for line in response]
    assert events[-1]['token_ids'] == [3, 4]
    assert events[-1]['finish_reason'] == 'eos'
    assert scheduler.snapshot()['active_or_queued'] == 0


@pytest.mark.parametrize('limit', [0, -1, True, 1.5, None, 7, '2'])
def test_invalid_limit_rejected_before_admission(serving, limit):
    scheduler, url = serving(BudgetBackend(), max_tokens=6)
    with pytest.raises(urllib.error.HTTPError) as caught:
        post(url, '/stream', {'request_id': 'bad', 'prompt': 'x', 'max_new_tokens': limit})
    assert caught.value.code == 400
    assert scheduler.snapshot()['active_or_queued'] == 0


def test_full_queue_and_cancelled_queued_request(serving):
    backend = ControlledBackend()
    scheduler, url = serving(backend, slots=1, max_pending=1, max_tokens=5)
    def peer():
        with post(url, '/stream', {'request_id': 'peer', 'prompt': 'abcd', 'max_new_tokens': 3}) as response:
            return [json.loads(line) for line in response]
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(peer)
        assert backend.prefill_started.wait(5)
        with post(url, '/stream', {'request_id': 'queued', 'prompt': 'x', 'max_new_tokens': 2}) as queued:
            with pytest.raises(urllib.error.HTTPError) as caught:
                post(url, '/stream', {'request_id': 'overload', 'prompt': 'x', 'max_new_tokens': 2})
            assert caught.value.code == 429
            with post(url, '/cancel', {'request_id': 'queued'}) as cancelled:
                assert json.load(cancelled)['cancelled'] is True
            backend.allow_prefill.set()
            backend.allow_tick.set()
            events = [json.loads(line) for line in queued]
        assert future.result()[-1]['token_ids'] == [4, 5, 6]
    assert len(events) == 1 and events[0]['status'] == 'cancelled_queued'
    assert events[0]['token_ids'] == []
    assert scheduler.snapshot()['rejected'] == 1
