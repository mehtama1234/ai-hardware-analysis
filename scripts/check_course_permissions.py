#!/usr/bin/env python3
"""Exhaustive check of an original finite teaching model, NOT CXL or its proof.

One upgrade by A; initially A/B/C read. Reliable messages, no new readers,
no failures, no data values. A single transition represents one delivery.
"""
from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    readers: frozenset = frozenset('ABC')
    writer: str = ''
    phase: str = 'idle'
    revokes: frozenset = frozenset()
    acks: frozenset = frozenset()
    awaited: frozenset = frozenset()


def successors(s, mode):
    if s.phase == 'idle':
        yield 'request write; send revokes to B,C', replace(s, phase='waiting', revokes=frozenset('BC'), awaited=frozenset('BC'))
    if s.phase != 'waiting':
        return
    for device in sorted(s.revokes):
        yield f'{device} revokes; sends acknowledgement', replace(s, readers=s.readers-{device}, revokes=s.revokes-{device}, acks=s.acks|{device})
    for device in sorted(s.acks):
        yield f'receive {device} acknowledgement', replace(s, acks=s.acks-{device}, awaited=s.awaited-{device})
    allowed = not s.awaited
    if mode == 'on_send':
        allowed = True
    elif mode == 'after_one_ack':
        allowed = len(s.awaited) <= 1
    if allowed:
        yield 'grant A write permission', replace(s, writer='A', phase='done')


def explore(mode):
    todo = deque([(State(), ())])
    seen = {State()}
    witness = None
    while todo:
        state, path = todo.popleft()
        safe = not state.writer or state.readers <= {state.writer}
        if not safe and witness is None:
            witness = path
        if mode == 'correct' and state.phase != 'idle':
            assert state.readers - {'A'} <= state.awaited
            assert state.awaited == state.revokes | state.acks
            assert not state.revokes & state.acks
            assert not state.acks & state.readers
        for event, target in successors(state, mode):
            if target not in seen:
                seen.add(target)
                todo.append((target, path + (event,)))
    return seen, witness


def main():
    states, witness = explore('correct')
    assert witness is None
    assert any(s.writer == 'A' for s in states), 'No reachable successful grant'
    print(f'Correct toy protocol: {len(states)} reachable states; no conflicting permission.')
    for mode in ('on_send', 'after_one_ack'):
        states, witness = explore(mode)
        assert witness is not None, f'Broken rule not detected: {mode}'
        print(f'{mode}: counterexample: ' + ' -> '.join(witness))
    print('No claim about CXL, repeated operations, data correctness, or eventual progress.')


if __name__ == '__main__':
    main()
