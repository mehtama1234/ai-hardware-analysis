#!/usr/bin/env python3
"""Check teaching arithmetic and selected paper calculations, not empirical validity."""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from course_spine import SECTIONS
from course_interactives import REQUEST_LATENCY_MODEL
from course_routes import ROUTES
from course_subtheme_notes import SUBTHEME_NOTES
from course_orientation import LEARNING_PATH


def main():
    # FCCM: retain units when converting clock rate to group duration.
    ns_per_second = 1_000_000_000
    assert F(ns_per_second, 200_000_000) == 5
    assert 8 * F(ns_per_second, 200_000_000) == 40
    assert 6 * F(ns_per_second, 100_000_000) == 60
    assert 6 * F(ns_per_second, 150_000_000) == 40
    # Recalculate QServe section 3.1's reported overflow example. This checks
    # the arithmetic, not the general protective-range proof or model quality.
    original_weight, code, offset, scale = 120, 15, 7, 16
    assert -128 <= original_weight <= 127 and 0 <= code <= 15
    assert (code - offset) * scale == 128 > 127
    # Training redistribution: averaging worker means is not the sample mean
    # when batch portions differ in size under the stated equal-example rule.
    sample_counts, worker_means = [1, 1, 1, 9], [2, 2, 2, 10]
    assert F(sum(worker_means), len(worker_means)) == 4
    weighted_mean = F(sum(n * m for n, m in zip(sample_counts, worker_means)), sum(sample_counts))
    assert weighted_mean == 8
    assert F(sum([2, 2, 2] + [10] * 9), 12) == weighted_mean
    # Storage arithmetic for the original one-host-copy-per-model example;
    # this does not test BlitzScale's implementation of that storage rule.
    assert 3 * 10 == 30 and 6 * 10 == 60
    # Glossary quorum example: check every pair, not just one majority.
    from itertools import combinations
    three_of_five = [set(group) for group in combinations(range(5), 3)]
    assert len(three_of_five) == 10
    assert min(len(left & right) for left in three_of_five for right in three_of_five) == 1
    # Cross-conference representation comparison: same stored forms and
    # conversion work, different connection rates (decimal MB per ms).
    for rate, original_time, compressed_time in ((10, 12, 13), (5, 24, 19), (20, 6, 10)):
        assert F(120, rate) == original_time
        assert F(60, rate) + 7 == compressed_time
    tie_rate = F(60, 7)
    assert 120 / tie_rate == 60 / tie_rate + 7 == 14
    # SC measurement lesson: identical per-worker distributions do not fix
    # the time to finish a job that waits for both workers.
    paired_cases = (
        ([(2, 2), (2, 18), (18, 2), (18, 18)], 14),
        ([(2, 2), (18, 18)], 10),
        ([(2, 18), (18, 2)], 18),
    )
    for pairs, expected_job_time in paired_cases:
        for worker in (0, 1):
            assert F(sum(pair[worker] for pair in pairs), len(pairs)) == 10
            assert F(sum(pair[worker] == 18 for pair in pairs), len(pairs)) == F(1, 2)
        assert F(sum(max(pair) for pair in pairs), len(pairs)) == expected_job_time
    # Original encrypted-traffic example: equalize the observable size only.
    visible_bytes = {'A': 100, 'B': 1000}
    padding_bytes = {choice: 1000 - size for choice, size in visible_bytes.items()}
    assert padding_bytes == {'A': 900, 'B': 0}
    assert {visible_bytes[choice] + padding_bytes[choice] for choice in visible_bytes} == {1000}
    # Separate early/late timing checks for the physical-design teaching path.
    earliest, hold = F('0.03'), F('0.08')
    assert hold - earliest == F('0.05')
    added_delay = F('0.06')
    assert earliest + added_delay == F('0.09') >= hold
    assert F('0.8') + added_delay == F('0.86') <= 1
    for next_clock in (1, 2):
        assert earliest < hold < next_clock  # next edge cannot fix current hold
    # Compiler lesson: overlapping input/output storage invalidates this
    # left-to-right fusion, even though the scalar arithmetic is unchanged.
    two_pass = [1, 2, 3, 0]
    temporary = [2 * value for value in two_pass[:3]]
    for index, value in enumerate(temporary):
        two_pass[index + 1] = value + 1
    fused = [1, 2, 3, 0]
    for index in range(3):
        fused[index + 1] = 2 * fused[index] + 1
    assert two_pass == [1, 3, 5, 7]
    assert fused == [1, 3, 7, 15]
    reverse_fused = [1, 2, 3, 0]
    for index in reversed(range(3)):
        reverse_fused[index + 1] = 2 * reverse_fused[index] + 1
    assert reverse_fused == two_pass
    retained = F(1)
    dropped = [F('0.10'), F('-0.08')]
    original_sum = retained + sum(dropped)
    signed_omission_error = retained - original_sum
    assert original_sum == F('1.02')
    assert signed_omission_error == F('-0.02')
    assert abs(signed_omission_error) <= sum(map(abs, dropped)) == F('0.18')
    # Shared resize/classify processor: count startup and show an attainable
    # schedule, rather than substituting steady-state rate for batch time.
    def shared_pipeline_completions(images, read_ms, resize_ms, classify_ms):
        processor_ready = 0
        completions = []
        for index in range(images):
            read_done = (index + 1) * read_ms
            processor_ready = max(processor_ready, read_done) + resize_ms + classify_ms
            completions.append(processor_ready)
        return completions
    assert shared_pipeline_completions(10, 2, 5, 3) == list(range(10, 83, 8))
    assert shared_pipeline_completions(10, 2, 2, 3) == list(range(7, 53, 5))
    # Queue lesson: exact-capacity regular traffic can have bounded waiting;
    # spare time determines whether a one-time service delay is absorbed.
    def queue_waits(arrival_gap, durations):
        ready = 0
        waits = []
        for index, duration in enumerate(durations):
            arrival = index * arrival_gap
            start = max(ready, arrival)
            waits.append(start - arrival)
            ready = start + duration
        return waits
    assert queue_waits(10, [10] * 6) == [0] * 6
    assert queue_waits(10, [15] + [10] * 5) == [0, 5, 5, 5, 5, 5]
    assert queue_waits(12, [15] + [10] * 5) == [0, 3, 1, 0, 0, 0]
    # Memory lesson's idealized in-flight-read bounds, decimal GB/s.
    read_bytes, read_seconds = 64, F(100, 10**9)
    one_read_gbps = F(read_bytes, 10**9) / read_seconds
    assert one_read_gbps == F('0.64')
    assert 8 * one_read_gbps == F('5.12')
    assert F(64 * 10**9) * read_seconds / read_bytes == 100
    # Opening lesson: staggered independent workers, each taking 10 ms.
    completions = sorted(start + 10 * job for start in range(10) for job in range(1, 4))
    assert completions == list(range(10, 40))
    assert F(1000, 10) == 100  # requests/s for one continuously busy worker
    assert 10 * F(1000, 10) == 1000
    # DATE's original two-answer sampler: validity does not imply equal odds.
    missing_rare_answer = F(99, 100) ** 100
    assert round(missing_rare_answer * 100, 1) == F('36.6')
    assert F(99, 100) + F(1, 100) == 1
    # FCCM manuscript v1, table II, 32x32 transpose: arithmetic on reported
    # counts, not a reproduction of the authors' experiment.
    fccm_read_reduction = F(168 - 106, 168)
    fccm_total_reduction = F(1613 - 1547, 1613)
    fccm_write_share = F(1050, 1547)
    assert round(100 * fccm_read_reduction) == 37
    assert round(100 * fccm_total_reduction) == 4
    assert round(100 * fccm_write_share) == 68
    assert 1613 - 168 - 1054 == 1547 - 106 - 1050 == 391
    dips_scores = {
        'BBH': [31.11, 29.52, 29.23, 29.46, 30.09, 30.47, 29.45, 28.94, 29.67],
        'MMLU': [24.38, 24.16, 24.18, 24.94, 24.61, 24.21, 24.66, 24.76, 26.34],
        'DROP': [31.77, 27.88, 31.45, 32.75, 31.02, 31.22, 31.53, 31.42, 29.94],
    }
    assert set(dips_scores) == {'BBH', 'MMLU', 'DROP'}
    assert all(len(values) == 9 for values in dips_scores.values())
    # Separate pass rates do not identify which requests pass both checks.
    request_ids = set(range(100))
    wrong = set(range(10))
    joint_pass_counts = []
    for overlap in range(11):
        late = set(range(overlap)) | set(range(10, 20-overlap))
        assert len(wrong) == len(late) == 10
        assert len(wrong & late) == overlap
        passing_both = len(request_ids - (wrong | late))
        assert passing_both == 100-(10+10-overlap)
        joint_pass_counts.append(passing_both)
    assert (min(joint_pass_counts), max(joint_pass_counts)) == (80, 90)
    assert joint_pass_counts[4] == 84
    orientation_lessons = [target for stage in LEARNING_PATH for target, _ in stage['links']]
    assert orientation_lessons == [section['id'] for section in SECTIONS], 'Opening lesson map must cover every core lesson in reading order'
    model = REQUEST_LATENCY_MODEL
    fixed_cost = sum(value for _, stage, value in model['stages'] if value is not None)
    baseline = fixed_cost + model['calculation_ms']
    floor = fixed_cost + model['calculation_min_ms']
    upper = fixed_cost + model['calculation_max_ms']
    assert (baseline, floor, upper) == (10, 8, 16)
    assert model['fixed_before_ms'] + model['fixed_after_ms'] == fixed_cost
    assert model['stages'][2][1:] == ('calculation', None)

    baseline = 6 + 8 + 4 + 2
    faster_compute = 6 + 8 + 2 + 2
    hit, miss = 6 + 1 + 2, 6 + 1 + 8 + 4 + 2
    assert (baseline, faster_compute, hit, miss) == (20, 18, 9, 21)
    assert F(hit + miss, 2) == 15
    assert faster_compute <= 19 and hit <= 19 < miss
    combined_miss = 6 + 1 + 8 + 2 + 2
    assert combined_miss == 19 and F(hit + combined_miss, 2) == 14
    solve = 2 + 100 * F('0.020') + 1
    smaller = 2 + 160 * F('0.010') + 1
    assert solve == 5 and smaller == F('4.6')
    assert smaller + F('0.6') == F('5.2')
    for conversion, limit in [(F(0), 199), (F('0.6'), 139)]:
        elapsed = lambda iterations: 3 + conversion + iterations * F('0.010')
        assert elapsed(limit) < solve
        assert elapsed(limit + 1) == solve
    assert 4 + 3 + 1 == 8
    assert F(10 - 8, 10) == F('0.2')
    assert 8 + 2/2 == 9
    assert 8/2 + 2 == 6
    assert 4 + 8/2 + 2 == 10
    assert 6 + 4 + 3 == 13
    assert 20 * 6 == 120 > 100
    candidates = [(8, 12), (10, 9), (12, 8)]
    feasible = [(area, delay) for area, delay in candidates if delay <= 10]
    assert min(feasible) == (10, 9)
    scores = [area + F(1, 2)*max(0, delay-10) for area, delay in candidates]
    assert scores == [9, 10, 12]
    assert F('9.5') + F('0.4') == F('9.9')
    iccad_predicted = list(map(F, ('9.7', '9.9', '10.2')))
    iccad_checked = list(map(F, ('10.1', '9.8', '9.95')))
    errors = [abs(a-b) for a, b in zip(iccad_predicted, iccad_checked)]
    assert errors == list(map(F, ('0.4', '0.1', '0.25')))
    assert sum(errors)/3 == F('0.25')
    assert [value <= 10 for value in iccad_predicted] == [True, True, False]
    assert [value <= 10 for value in iccad_checked] == [False, True, True]
    assert iccad_predicted.index(min(iccad_predicted)) == 0
    assert iccad_checked.index(min(iccad_checked)) == 1
    assert [n for n in range(256) if (n+1)%256 != min(n+1, 255)] == [255]
    assert 100*2+20 == 220 and 20*12+20 == 260
    assert 25*2+20 == 70 and 5*12+20 == 80
    assert 20*8+20 == 180 and 5*8+20 == 60
    assert 12+3+2+10 == 27
    assert 12+F(3, 2)+2+5 == F('20.5')
    assert 6+3+1+10 == 20
    assert max(12, 3)+max(2, 10) == 22
    assert max(12, F(3, 2))+max(2, 5) == 17
    assert 3+3+1 == 7 <= 8 < 3+3+1+2
    assert max(3+3+1, 3+1+2) == 7
    assert F(20, 10) + 3*F(1, 2) == F('3.5')
    assert F(12, 8) + 3 == F('4.5')
    assert 2 + F(1, 2) == F('1.5') + 1
    assert F('0.4') / 2 == F('0.2')
    assert F('2.3') - F('0.2') > 2
    assert F('2.1') - F('0.2') < 2
    assert 6*7 < 30+2*7 and 6*8 > 30+2*8
    assert 6*10 == 30+3*10 and 6*11 > 30+3*11
    assert 2+3+8+1 == 14 and 5+1+4+1 == 11
    assert F('0.2')+F('0.15')+F('0.1') == F('0.45')
    assert F('0.2')+F('0.05')+F('0.04') == F('0.29') < F('0.3')
    assert 3+2+10+2+3 == 20
    assert 3+2+5+2+3 == 15
    assert 2*(3+2+4+2+3)+4 == 32
    assert F(30, 10) == 3 and F(10, 6) == F(5, 3)
    assert F('0.6')+F(2, 4)+F('0.4') == F('1.5')
    assert F('0.6')+F(2, 16)+F('0.4') == F('1.125')
    assert F(8, 6) == 1+F(2, 6)
    assert 100*F('0.01') == 1
    for transfer_ends in ((4, 8, 12), (4, 8, 14)):
        completed = 0
        for ready in transfer_ends:
            completed = max(ready, completed)+6
        assert completed == 22
    assert 3*(4+6) == 30
    from decimal import Context, Decimal
    decimal_model = Context(prec=3)
    add = decimal_model.add
    a, b, c = map(Decimal, ('1000', '-1000', '1'))
    assert add(add(a, b), c) == 1
    assert add(a, add(b, c)) == 1
    assert add(add(a, c), b) == 0
    assert 4+5 > 8 and 4+5*2 < 8*2
    assert 4+5*10 == 54 < 80
    fixed_time = lambda p: F(80, p)+10+2*(p-1)
    assert [fixed_time(p) for p in (1, 4, 8, 16)] == [90, 36, 34, 45]
    assert fixed_time(6) == F(100, 3) < fixed_time(8)
    assert 80+10+2*(8-1) == 104
    assert F(10)/F('0.8') == F('12.5') > 12
    assert F(10)/F('0.9') == F(100, 9) < 12
    assert 100+3*2 == 106
    assert 60+2*2+3+(100-50)+2 == 119
    assert 10+2 == 8+4 == 12
    assert F(8+20, 2) == 14 and F(10+12, 2) == 11
    assert 20-12*F('0.8') == 12-2*F('0.8') == F('10.4')
    assert 3+2*F('0.25') == F('3.5')
    assert 2+F('0.25') == F('2.25')
    assert 12+2-1 == 13
    urgent_end = 3+F('0.5')+2
    assert urgent_end == F('5.5') and urgent_end-1 == F('4.5')
    assert urgent_end+F('0.5')+(12-3) == 15
    earlier_end = 1+F('0.5')+2
    assert earlier_end == F('3.5') <= 5
    assert earlier_end+F('0.5')+(12-1) == 15
    predicted = [(8, F('9.6')), (9, F('9.8')), (10, F('9.5'))]
    checked = [(8, F('10.4')), (9, F('9.7')), (10, F('9.4'))]
    assert min(area for area, delay in predicted if delay <= 10) == 8
    assert min(area for area, delay in checked if delay <= 10) == 9
    assert 100*F('0.1')+2*2 == 14
    assert (13-100*F('0.1'))//2 == 1
    assert F('1.2')+F('0.2')+F('0.2') == F('1.6')
    assert F('1.2')+F('0.6')+F('0.2') == 2
    assert 1+F('0.5')+F('0.2') == F('1.7')
    assert 1+F('0.65')+F('0.2')-F('1.8') == F('0.05')
    assert 8+6+1 == 15
    assert 8+7*3 == 29 < 30
    assert 8+7*4+6 == 42 > 40
    assert 8+7*5+6 == 49 < 50
    for factor, expected in (
        (F(2), list(map(F, ('0.01', '0.03', '0.07', '0.15', '0.31')))),
        (F('0.5'), list(map(F, ('0.01', '0.015', '0.0175', '0.01875', '0.019375')))),
    ):
        bounds, error = [], F(0)
        for _ in range(5):
            error = factor*error+F('0.01')
            bounds.append(error)
        assert bounds == expected
        from itertools import product
        final_errors = []
        for signs in product((-1, 1), repeat=5):
            actual_error = F(0)
            for sign in signs:
                actual_error = factor*actual_error+sign*F('0.01')
            final_errors.append(actual_error)
        assert max(map(abs, final_errors)) == expected[-1]
    fast_energy, slow_energy = 2*3+3*4, 2*3+5*2
    assert (fast_energy, slow_energy) == (18, 16)
    assert (fast_energy+2*5, slow_energy+2*7) == (28, 30)
    assert fast_energy+F('0.5')*5 == F('20.5')
    assert slow_energy+F('0.5')*7 == F('19.5')
    assert fast_energy+5 == slow_energy+7
    observed = {}
    for bit in (0, 1):
        for delay in (0, 2):
            time = 1+2*bit+delay
            observed.setdefault(time, [0, 0])[bit] += 1
    assert observed == {1: [1, 0], 3: [1, 1], 5: [0, 1]}
    assert F(sum(max(counts) for counts in observed.values()), 4) == F(3, 4)
    assert 2*(3+1) == 8 != 2*10
    assert 2*(3+1) == 2*4 and 2*(3+1) != 2*7
    assert F('1.25')+F('0.35')+F('0.2') == F('1.8')
    assert F('1.4')+F('0.5')+F('0.2') == F('2.1') > 2
    assert F('1.7')+F('0.2') == F('1.9')
    assert 2-(F('1.4')+F('0.35')+F('0.2')) == F('0.05')
    from itertools import permutations
    required = (7, 2, 7)
    candidates = set(permutations(required))
    assert len(candidates) == 3
    assert sum(sorted(candidate) == sorted(required) for candidate in candidates) == 3
    assert sum(candidate[0] == required[0] for candidate in candidates) == 2
    assert sum(candidate == required for candidate in candidates) == 1
    implementations = [(4, 6), (6, 3)]
    combinations = [(a[0]+b[0], a[1]+b[1]) for a in implementations for b in implementations]
    assert combinations == [(8, 12), (10, 9), (10, 9), (12, 6)]
    assert min(time for area, time in combinations if area <= 10) == 9
    restricted = [impl for impl in implementations if impl[0] <= 5]
    assert restricted == [(4, 6)] and 2*restricted[0][1] > 10
    assert max(1, 4)+1 == 5 and 5-1 == 4
    reserved_ends = [2+2*i for i in range(4)]
    assert reserved_ends == [2, 4, 6, 8] and reserved_ends[-1]-1 == 7
    assert (1+4)-1 == 4
    assert 10*F('0.1')+F('0.1') == F('1.1')
    assert 10*F('0.01')+F('0.1') == F('0.2') < F('0.25')
    assert 10*F('0.1')+F('0.01') == F('1.01') > F('0.25')
    assert 2+1+1 == 2+2 and 3+4 == 7 > 5
    from itertools import combinations
    stored = 5  # data 0101, parity bit zero at position four
    assert (stored ^ 1) == 4 and (stored ^ 3) == 6
    for bit_count, expected_detected in ((1, 5), (2, 0)):
        patterns = list(combinations(range(5), bit_count))
        detected = 0
        for bits in patterns:
            damaged = stored
            for bit in bits:
                damaged ^= 1 << bit
            detected += damaged.bit_count() % 2
        assert len(patterns) == (5 if bit_count == 1 else 10)
        assert detected == expected_detected
    correctness = next(section for section in SECTIONS if section['id'] == 's8')
    correctness_text = (' '.join(correctness['body']) + ' ' +
                        correctness['exercise']['question'] + ' ' +
                        correctness['exercise']['answer']).lower()
    assert 255 + 1 == 256 and (255 + 1) % 256 == 0
    assert 256 * 256 == 65_536
    assert 3*F('0.01')**2*F('0.99') + F('0.01')**3 == F('0.000298')
    encode_four_bit_even_parity = lambda value: value | ((value.bit_count() % 2) << 4)
    assert encode_four_bit_even_parity(5) == 5
    assert encode_four_bit_even_parity(6) == 6
    assert encode_four_bit_even_parity(7) == 23
    for phrase in ('a safety property: a forbidden event never occurs',
                   'a progress property: something required eventually happens',
                   'a queue that refuses every request can keep its item count in range and still fail to serve users',
                   'a bit stores one 0 or 1',
                   'the flag survives a crash but the new value does not',
                   'crash consistency means that related stored information still agrees after a power loss',
                   'parity catches some changed bits; it does not identify repeated requests',
                   'pmverify (asplos 2025)',
                   'pmverify asks whether a crash can leave a stored state that ordinary execution cannot reach',
                   'it is not a check of every application requirement',
                   'found 12 robustness violations, proved one case robust, and could not decide on 13',
                   'most undecided cases used operations the tool did not support',
                   'a result the tool could not decide is not a pass',
                   'power (osdi 2025)',
                   'for each storage operation, it states what must be true for safe recovery',
                   'tests show what happened in selected runs',
                   'pmverify checks which crash states its rules allow, but may leave some undecided',
                   'power\'s proofs show that a rule follows from their assumptions',
                   'it does not identify repeated requests, ensure updates happen in the right order'):
        assert phrase in correctness_text, f'Update the correctness lesson check when prose changes: {phrase}'
    security = next(section for section in SECTIONS if section['id'] == 's9')
    security_text = (' '.join(security['body']) + ' ' + security['exercise']['answer']).lower()
    # Reconstruct all outcomes from the supplied populations and conditional
    # rates. The false-alarm denominator is ordinary events, not all events
    # and not all alerts. These are stipulated counts, not detector evidence.
    for total, attacks, detection_rate, false_alarm_rate, expected in (
        (10_000, 100, F('0.90'), F('0.01'), (90, 10, 99, 9801)),
        (20_000, 200, F('0.95'), F('0.02'), (190, 10, 396, 19404)),
    ):
        ordinary = total - attacks
        detected = attacks * detection_rate
        missed = attacks - detected
        false_alerts = ordinary * false_alarm_rate
        correctly_ignored = ordinary - false_alerts
        assert (detected, missed, false_alerts, correctly_ignored) == expected
        assert detected + missed + false_alerts + correctly_ignored == total
        assert false_alerts / ordinary == false_alarm_rate
        assert false_alerts / (detected + false_alerts) != false_alarm_rate
    assert (4+0, 6+20, 9+0, 11+20) == (4, 26, 9, 31)
    assert max(4, 9) <= min(26, 31) and min(26, 31)-max(4, 9) == 17
    assert 100*F(90, 90+99) == F(1000, 21)
    assert 100*F(190, 190+396) > F(324, 10)
    assert 100*F(190, 190+396) < F(325, 10)
    assert 200-190 == 10
    assert 80+20 == 100 and max(0, 80-50) == 30
    for phrase in ('adds a variable delay from zero to 20 milliseconds in either case',
                   'they overlap from 9 to 26',
                   'needed to share memory pages and the last-level cache, but not an execution core',
                   'pinned the two virtual machines to the same physical processor and arranged for them to share pages',
                   'a quick read suggested the victim had used it',
                   'the first user\'s 80 entries of actively used data no longer fit',
                   'only 90/189'):
        assert phrase in security_text, f'Update the security lesson check when prose changes: {phrase}'
    assert 5+3 == 8 > 6
    assert 10*(2+3+1) == 60
    assert 10*(1+1)+4*12 == 68
    assert 20+4*8 == 52
    assert max(f for f in range(11) if 20+12*f < 60) == 3
    assert 4+4+2 == 10 and 1+4+1+1 == 7
    assert 6+3+1 == 10 > 8
    assert 7+F(4)/F('0.5') == 15
    assert 7+F(4, 2) == 9
    assert (1+4+1)+1-1 == 6
    assert 1000+256*2 == 1512
    assert F(2000-1512, 2000) == F('0.244')
    assert 1000+1000*2 == 3000
    assert 100+512 == 612 > 200
    assert 512+512 == 2*512 and 513+512 < 2*513
    assert [cycle+1 for cycle in range(1, 9)][-1] == 9
    for output_width, expected_end in ((4, 4), (2, 6), (1, 10)):
        ready_cycles = [2]*4+[3]*4
        last_cycle, used = 0, 0
        for ready in ready_cycles:
            earliest = ready+1
            if earliest > last_cycle:
                last_cycle, used = earliest, 0
            if used == output_width:
                last_cycle, used = last_cycle+1, 0
            used += 1
        assert last_cycle == expected_end
    assert 100+40*4+10*12 == 380 < 500
    assert 100+8*4+2*12 == 156 > 100
    assert 100+10*4+40*12 == 620 > 500
    assert min(s for s in range(51) if 100+4*s+12*(50-s) < 500) == 26
    assert 2*6 < 15 < 3*6 and 2*10 >= 15
    assert 3*40 == 80+40 == 120 < 2*80
    assert (15-2*6)*2 == 6 and F(6, 3*6-15) == 2
    assert 2*70 == 140 > 110
    assert 30+70 == 100 <= 110 and 100 > 90
    assert F(140*2+60*8, 10) == 76 < 110
    traces = [(2, 4, 6, 8), (5, 6, 7, 8), (2, 3, 4, 8)]
    gaps = [[b-a for a, b in zip(trace, trace[1:])] for trace in traces]
    assert gaps == [[2, 2, 2], [1, 1, 1], [1, 1, 4]]
    assert [t[0] <= 3 and max(g) <= 2 for t, g in zip(traces, gaps)] == [True, False, False]
    assert F(sum(gaps[2]), len(gaps[2])) == 2 < max(gaps[2])
    assert sum([2, 2, 2, 2]) == sum([5, 1, 1, 1]) == sum([8, 0, 0, 0]) == 8
    assert max([5, 1, 1, 1]) == 2+2+1 == 5
    assert max((n+1)//2 for n in [5, 1, 1, 1]) == 3 < 2+1+1
    assert max([8, 0, 0, 0])-(2+2+1) == 3
    def cache_trace(sequence, initial=()):
        recent, hits = list(initial), []
        for block in sequence:
            hit = block in recent
            hits.append(hit)
            if hit:
                recent.remove(block)
            elif len(recent) == 2:
                recent.pop(0)
            recent.append(block)
        return hits, sum(1 if hit else 10 for hit in hits)
    assert cache_trace('ABACA') == ([False, False, True, False, True], 32)
    assert cache_trace('ABACA', 'AB') == ([True, True, True, False, True], 14)
    assert cache_trace('ABCABC') == ([False]*6, 60)
    assert sum([1, 1, 1, 5]) == sum([2, 2, 2, 2]) == 8
    assert F(8, 2) == 4 > 2+F(2, 2)
    assert F(8, 8) == 1 < 2+F(2, 8) == F('2.25')
    assert F(8, 3) == 2+F(2, 3)
    for codes in ((3, 5), (2, 6)):
        decoded = [F('0.5')*(c-3) for c in codes]
        assert sum(decoded) == F('0.5')*(sum(codes)-len(codes)*3) == 1
        assert F('0.5')*(sum(codes)-3) == F('2.5')
    assert 4+2+2 == 4*2 and 16+2+2 == 20 < 16*2
    assert 2+4+2 == 8 > 7
    assert F('0.5')+4+F('0.5') == 5 < 7
    assert 4+3 == 7
    assert 8 % 4 == 0 and 10 % 4 == 2
    assert 10+8*4+2*10 == 62 < 100
    assert 10+10*10 == 110 > 100
    assert min(s for s in range(11) if 110-6*s < 100) == 2
    reference = [F(0), F(10)]
    for values, mean_error, decision_ok, bound_ok in (
        ([F('0.2'), F('9.8')], F('0.2'), False, True),
        ([F(0), F('9.5')], F('0.25'), True, False),
        ([F('0.05'), F('9.75')], F('0.15'), True, True),
    ):
        errors = [abs(a-b) for a, b in zip(values, reference)]
        assert sum(errors)/2 == mean_error
        assert ((values[0] > F('0.1')) == (reference[0] > F('0.1'))) == decision_ok
        assert (max(errors) <= F('0.3')) == bound_ok
    assert F(100, 1) == 100 and F(70)/F('0.5') == 140
    assert F(100-70, 100) == F('0.3') and F(140-100, 100) == F('0.4')
    assert 100+60 == 160 and 140+60 == 200
    assert F(70)/F('0.8')+60 == F('147.5')
    assert F(70)/F('0.7')+60 == 160
    assert 3*3 == 9 > 8
    first_comparison = ((100, 90), (70, 60))
    assert [old-new for old, new in first_comparison] == [10, 10]
    assert [first_comparison[0][i]-first_comparison[1][i] for i in (0, 1)] == [30, 30]
    assert 4+6 == 10 and 4+9 == 13
    second_comparison = ((100, 90), (70, 80))
    assert [old-new for old, new in second_comparison] == [10, -10]
    assert second_comparison[0][0]-second_comparison[1][1] == 20
    assert 12+8 == 20 and 6+8 == 14 and 12+4 == 16
    assert F(20, 14)*F(20, 16) == F(25, 14) != F(20, 10)
    assert 6+4+5 == 15 > 14
    assert 10-6 == 4 and F(10)/(F(10, 4)**2) != 4
    assert 7*10 == 70 < 32+4*10 == 72
    assert 7*11 == 77 > 32+4*11 == 76
    assert 10*(32+8*4) == 640 > 80*7 == 560
    assert 4+4+8+6 == 22 > 20
    assert 4+4+8+3 == 19 <= 20 < 19+2
    assert 50+12 == 62
    assert 50+F(4, 100)*1000 == 90
    assert 50+F(4, 400)*1000 == 60
    assert F(4)/F('0.012') == F(1000, 3)
    for preparation, training, expected in ((12, 8, 44), (12, 4, 40), (6, 8, 30), (6, 4, 22)):
        finished = 0
        for batch in range(1, 4):
            finished = max(batch*preparation, finished)+training
        assert finished == expected
    assert 12+8 == 20 < 24 and 12+8-6 == 14
    assert 6+20 == 26 > 24 and 24+20 == 44
    assert 15+10-4 == 21 < 24 < 15+10
    assert F(8+10+12, 3) == 10 and F(2+4+12, 3) == 6
    assert 8 <= 9 < 12 and 10 <= 12
    assert min(2*10, 12) == 12
    assert F(8+2+4, 3) == F(14, 3)
    assert F(4+8+2+4, 3) == 6
    assert 2*(3+1)+4 == 12 and 6+1 == 7 and 10+1+4 == 15
    assert 30*3 == 90 < 100 < 50*3
    assert max(n for n in range(101) if 3*n < 100) == 33
    assert max(n for n in range(101) if 20+3*n < 100) == 26
    assert 2+F(1000-2*100, 50) == 18
    assert 60*2+40*16 == 760
    assert F(1000, 60) == F(50, 3) < 18
    assert 45*F(1000, 60) == 750 < 760
    assert 2+F(1000, 60) == F(56, 3) > 18
    assert 100+750 == 850 > 760
    assert F(100, 100)*60 == 60 < F(100, 60)*45 == 75
    predictions, observed = [8, 9, 9, 12], [9, 11, 8, 10]
    assert F(sum(abs(a-b) for a, b in zip(predictions, observed)), 4) == F('1.5')
    assert sum(p <= 10 < a for p, a in zip(predictions, observed)) == 1
    assert sum(a <= 10 < p for p, a in zip(predictions, observed)) == 1
    assert F('8.5')+2 == F('10.5') > 10
    values = [1, 2, 4, 8]
    assert [sum(values[:i+1]) for i in range(4)] == [1, 3, 7, 15]
    assert sum(range(1, 5)) == 10 < 4*4
    assert 8+10 == 18 > 16 and 8+2*10 == 28 < 2*16
    assert sum(range(1, 6)) == 15 and 8+15 == 23 < 5*5
    pipeline = next(section for section in SECTIONS if section['id'] == 'dependencies-and-pipelines')
    body = ' '.join(pipeline['body'])
    def ideal_pipeline_finish(stage_times, items):
        return sum(stage_times) + (items - 1) * max(stage_times)
    assert [ideal_pipeline_finish([2, 5, 3], n) for n in (1, 2, 3, 10)] == [10, 15, 20, 55]
    assert ideal_pipeline_finish([2, 2, 3], 10) == 34
    assert all(phrase in body for phrase in (
        '1.23× over Plain-4D', '1.19× over Fixed-4D',
        '7.5% and 3.4% improvements over static per-sequence and per-document sharding',
        '1.18×–1.22×', '1.19×–3.01×', 'over their Tutel/PipeMoE baselines',
        'over DeepSpeed-MoE/Tutel',
    ))
    assert 'not directly comparable' in body and 'not been reproduced' in body
    assert 'aiming to reduce the time spent waiting for the worker that finishes last' in body
    assert 'forward pass (computing predictions)' in body
    assert 'backward pass (calculating model updates)' in body
    producer_rate, consumer_rate = F(1, 2), F(1, 5)
    assert producer_rate - consumer_rate == F(3, 10)
    assert producer_rate*10 - consumer_rate*10 == 3
    for phrase in ('0.5 images per millisecond', '0.2 per millisecond',
                   'about 0.3 image per millisecond', 'must be dropped or stored somewhere else'):
        assert phrase in body, f'Update the pipeline backlog check when prose changes: {phrase}'
    precision = next(section for section in SECTIONS if section['id'] == 's2')
    precision_text = ' '.join(precision['body'])
    assert F(1, 2*255) == F(1, 510)
    assert F(1, 2*15) == F(1, 30)
    assert 100*F('0.002') == F('0.2')
    original_scores = (F('0.502'), F('0.498'))
    shifted_scores = (original_scores[0]-F('0.003'), original_scores[1]+F('0.003'))
    assert shifted_scores == (F('0.499'), F('0.501'))
    assert original_scores[0] > original_scores[1] and shifted_scores[0] < shifted_scores[1]
    for phrase in ('If the additions themselves are exact',
                   'Rounding during the additions adds another source of error',
                   'so the lower score becomes the higher one',
                   'weights in 4 bits, values passed between model layers',
                   '20–90% runtime overhead associated with converting INT4 weights',
                   '1.2× maximum serving throughput',
                   'weights in 3 bits',
                   'small correction matrices, each represented by two smaller arrays',
                   '1.2× latency speedup over MARLIN',
                   'Do not compare its 1.2× with QServe',
                   'A compression ratio is not a speed result'):
        assert phrase in precision_text, f'Update the precision lesson check when prose changes: {phrase}'
    memory = next(section for section in SECTIONS if section['id'] == 's3')
    memory_text = ' '.join(memory['body'])
    assert 1 + F(1, 10)*20 == 3
    assert 3 + F(1, 20)*20 == 4
    def lru(capacity, trace):
        recent = []
        hits = []
        for item in trace:
            hit = item in recent
            hits.append(hit)
            if hit:
                recent.remove(item)
            elif len(recent) == capacity:
                recent.pop(0)
            recent.append(item)
        return hits
    assert lru(2, ('A', 'B', 'A', 'B')) == [False, False, True, True]
    assert lru(2, ('A', 'B', 'X', 'Y', 'A', 'B')) == [False]*6
    for phrase in ('its peak is 24 GB', 'when their last use occurs',
                   'these optimizer states alone use 28 GB',
                   'batches four times larger',
                   'not a result reproduced by this course',
                   'does not preserve its contents through power loss',
                   'write and flush rules',
                   'two-item cache', 'one-time read of X and then Y',
                   'the next reads of A and B miss', '50 pages in a cache that holds 49'):
        assert phrase in memory_text, f'Update the cache replacement check when prose changes: {phrase}'
    routing = next(section for section in SECTIONS if section['id'] == 's4')
    routing_text = ' '.join(routing['body'])
    assert F(20, 10) == 2
    assert max(F(18, 10), F(2, 10)) == F('1.8')
    assert max(F(10, 10), F(10, 10)) == 1
    assert F(3, 16-10) == F(1, 2)
    assert max(F(16, 5), F(4, 5)) == F('3.2')
    assert max(F(10, 5), F(10, 5)) == 2
    assert F(20, 5) == 4
    for phrase in ('Assume they start together', 'endpoints can supply and receive data fast enough',
                   'must cross the final link', 'six GB of excess work each second'):
        assert phrase in routing_text, f'Update the routing lesson check when prose changes: {phrase}'
    skipping = next(section for section in SECTIONS if section['id'] == 's5')
    skipping_text = ' '.join(skipping['body'])
    assert 100*F('0.2') + 30 == 50
    assert 100*F('0.8') + 30 == 110
    assert 100*F('0.7') + 30 == 100
    assert 20*3 == 60 < 200 and 80*3 == 240 > 200
    assert max(20, 0, 0, 0) == 20 and F(20, 4) == 5
    signed_error = -(F('0.10') - F('0.08'))  # retained minus original
    error_bound = F('0.10') + F('0.08')
    assert (signed_error, error_bound) == (F('-0.02'), F('0.18'))
    assert F('0.001')*1000 == 1
    for phrase in ('A pattern is sparse when many of its possible positions are zero',
                   'The new result minus the original is −0.02', 'the error bound is 0.10 + 0.08 = 0.18',
                   'weight 0.001 and input 1,000 removes a contribution of 1',
                   'graph of facts, such as “Paris — capital of → France.”',
                   'does not discard small values',
                   'not to pruning neural-network weights',
                   'gradient—the calculated signal for how model weights should change',
                   '40% gradient sparsity',
                   'does not exactly recreate the result of sending every gradient value',
                   '21% less time per step and 19% less total training time',
                   'Tensor Approximation via Structured Decomposition',
                   '39% speedup for sparse ResNet-34 on an NVIDIA RTX 3080',
                   'not a head-to-head ranking'):
        assert phrase in skipping_text, f'Update the omission-bound check when prose changes: {phrase}'
    compiler = next(section for section in SECTIONS if section['id'] == 's6')
    compiler_text = ' '.join(compiler['body'])
    assert 1_000_000 * 4 * 4 == 16_000_000
    assert 1_000_000 * 4 * 2 == 8_000_000
    with localcontext() as context:
        context.prec = 3
        a, b, c = Decimal('10000'), Decimal('-10000'), Decimal('1')
        left = context.add(context.add(a, b), c)
        right = context.add(a, context.add(b, c))
    assert (left, right) == (Decimal('1'), Decimal('0'))
    assert 5*100 == 200+3*100
    assert 120+4*60 == 6*60
    assert 120+4*50 > 6*50
    for phrase in ('internal forms between the program people write and the instructions a machine runs',
                   'intended to preserve the program\'s logical result',
                   'not TVM or Relax measurements',
                   'Relax (ASPLOS 2025)',
                   'one array has n rows and another has 4n values',
                   'records both sizes as simply unknown',
                   'not proof that every model becomes faster'):
        assert phrase in compiler_text, f'Update the compiler lesson check when prose changes: {phrase}'
    distributed = next(section for section in SECTIONS if section['id'] == 's7')
    distributed_text = ' '.join(distributed['body']).lower()
    assert 20 + F(80, 4) == 40 and 20 + F(80, 8) == 30
    assert 20 + F(80, 4) + 12 == 52
    assert 20 + F(80, 8) + 24 == 54
    assert F(4, 1) == 4  # 4 GB across one 1-GB/s shared link
    assert max(10, 10, 10, 30) == 30 and F(10+10+10+30, 4) == 15
    assert 30 - (12+10) == 8  # completion-time gain from the duplicate attempt
    assert 2 < F(200, 62) < F(33, 10)  # checkpoint overhead percentage, first interval
    assert 9 < F(200, 22) < F(92, 10)  # checkpoint overhead percentage, shorter interval
    assert F(60, 2) == 30 and F(20, 2) == 10
    assert 12 + F(72, 4) + 8 == 38
    assert 12 + F(72, 8) + 16 == 37
    assert 12 + F(72, 8) + 17 == 38
    for phrase in ('the mean worker time, 15 seconds, does not predict that wait',
                   'the system must accept one result for that task',
                   'equally likely anywhere within a calculation interval',
                   'earlier saves survive', 'accepting task outputs despite duplicate attempts', 'backup attempts',
                   'completed map tasks are rerun', 'their output is in a global file system',
                   'aborts the job if its master coordinator fails',
                   'checkmate (nsdi 2026)',
                   'reliable delivery of each update exactly once',
                   "llmtailor (sc workshops 2025)",
                   'a file that loads is not automatically an identical recovery',
                   'filtered qwen2.5-7b fine-tuning example',
                   'not every training job or every kind of failure'):
        assert phrase in distributed_text, f'Update the distributed-work check when prose changes: {phrase}'
    end_to_end = next(section for section in SECTIONS if section['id'] == 's10')
    service_text = (' '.join(end_to_end['body']) + ' ' +
                    end_to_end['exercise']['question'] + ' ' +
                    end_to_end['exercise']['answer']).lower()
    trace_rows = end_to_end['table']['rows']
    elapsed = 0
    cumulative = []
    for _, duration, _ in trace_rows:
        elapsed += int(duration.split()[0])
        cumulative.append(elapsed)
    assert cumulative == [8, 12, 32, 44, 47, 50]
    baseline_ms = sum(int(row[1].split()[0]) for row in trace_rows)
    assert baseline_ms == 50
    assert baseline_ms - 12 + 6 == 44
    assert F(50, 44) == F(25, 22) and F(113, 100) < F(25, 22) < F(114, 100)
    warm_fast, cold_fast = 8+4+6+3+3, 8+4+20+6+3+3
    warm_original, cold_original = 8+4+0+12+3+3, 8+4+20+12+3+3
    assert (warm_fast, cold_fast, warm_original, cold_original) == (24, 44, 30, 50)
    assert F(8, 10)*warm_fast + F(2, 10)*cold_fast == 28
    assert sum((F(8, 10), F(2, 10))) == 1
    assert F(2, 10) == F('0.2')  # cold requests miss a 40-ms deadline
    assert 8 + max(4, 20) + 6 + 3 + 3 == 40
    assert 16 - 10 == 6 and 3*2 == 6 and 4*2 > 6
    assert 2*3 == 6 and 3*3 > 6
    assert 8+4+10+5+6+3+3 == 39
    warm_worker, idle_cold = 18+4+6+6, 0+4+20+6+6
    idle_cold_overlap = max(4, 20)+6+6
    assert (warm_worker, idle_cold, idle_cold_overlap) == (34, 36, 32)
    assert 34 <= 35 and 36 > 35 and 32 <= 35
    for phrase in ('not measurements of any named paper',
                   'exactly meeting the stated deadline and leaving no margin',
                   'the mean cannot establish that every request meets the deadline',
                   'the request\'s model and input are preserved',
                   'record accepted, rejected, late, and failed requests',
                   'the linked service trace explicitly records that its proposed composition tests have not been run'):
        assert phrase in service_text, f'Update the end-to-end service check when prose changes: {phrase}'
    physical = next(section for section in SECTIONS if section['id'] == 'physical-design')
    physical_text = (' '.join(physical['body']) + ' ' +
                     physical['exercise']['question'] + ' ' +
                     physical['exercise']['answer']).lower()
    assert 100*2 == 200 and 150*1 == 150
    assert (150+80)*1 == 230
    assert F('0.8')**2 == F('0.64')
    assert 100*10 + 60*50 == 4_000
    assert F(4_000, 60) == F(200, 3)
    assert F(666, 10) < F(200, 3) < F(667, 10)
    assert 80*60 == 4_800 > 4_000
    assert F('0.6')+F('0.3')+F('0.2') == F('1.1') > 1
    assert F('0.6')/2+F('0.3')+F('0.2') == F('0.8') < 1
    device_a, device_b = 60*4, 75*3
    system_a, system_b = (60+20)*4, (75+20)*3
    system_b_with_prep = system_b + 50*1
    assert (device_a, device_b, system_a, system_b, system_b_with_prep) == (240, 225, 320, 285, 335)
    assert system_a < system_b_with_prep and 4 == 3+1
    for phrase in ('one watt is one joule per second',
                   'not a 36% whole-system energy guarantee',
                   'a design sustaining 80 per second completes 4,800',
                   'real analysis separately handles clock arrival, setup and hold constraints',
                   'the documentation is a source for the flow, not evidence that any design in this course has completed it',
                   'passing one does not imply passing the others',
                   'a chip measurement observes manufactured hardware, but only the sampled devices'):
        assert phrase in physical_text, f'Update the physical-design lesson check when prose changes: {phrase}'
    mlsys = next(route for route in ROUTES if route['id'] == 'mlsys-2025')
    assert len(mlsys['themes']) == 8
    assert [len(theme['subthemes']) for theme in mlsys['themes']] == [3]*8
    assert all(theme.get('worked_example') and theme.get('practice') for theme in mlsys['themes'])
    for theme_number, theme in enumerate(mlsys['themes'], 1):
        for subtheme_number, _ in enumerate(theme['subthemes'], 1):
            detail = SUBTHEME_NOTES.get(('mlsys-2025', theme_number, subtheme_number))
            assert detail and all(detail[field] for field in ('example', 'failure', 'evidence', 'source'))
    mlsys_manifest = json.loads((ROOT/'metadata/mlsys-2025-first-principles-atlas-manifest.json').read_text())
    mlsys_counts = mlsys_manifest['counts']
    assert (mlsys_manifest['paper_count'], mlsys_counts['source_text_records'],
            mlsys_counts['catalog_fulltext_records'], mlsys_counts['catalog_abstract_only_records'],
            mlsys_counts['local_source_text_records'], mlsys_counts['abstract_only_records']) == (61, 61, 56, 5, 61, 0)
    first_theme = mlsys['themes'][0]
    assert 3+1+4+3+1 == 12
    assert 6+1 == 7
    assert 10+1+4 == 15 > 12
    assert 30*3 == 90 < 100 and 50*3 == 150 > 100
    assert max(n for n in range(101) if 3*n < 100) == 33
    assert max(n for n in range(101) if 20+3*n < 100) == 26
    first_theme_text = ' '.join([first_theme['body'], *first_theme['worked_example'],
                                 first_theme['practice']['question'],
                                 first_theme['practice']['answer']]).lower()
    evidence_text = (mlsys['intro']+' '+mlsys['evidence']+' '+mlsys['status']).lower()
    for phrase in ('a smaller mathematical expression need not become a faster program',
                   'preserves this exact-arithmetic sum',
                   'approximate omission meets the task\'s quality target'):
        assert phrase in first_theme_text, f'Update the MLSys theme check when prose changes: {phrase}'
    for phrase in ('61 conference papers with extracted source text',
                   '56 full-text entries and five additional text-bearing records',
                   'those counts describe available source material, not independent reproduction',
                   'broader paper walkthroughs and full-corpus synthesis remain unfinished'):
        assert phrase in evidence_text, f'Update the MLSys evidence boundary check when prose changes: {phrase}'
    queue_theme = mlsys['themes'][3]
    fcfs_completions, short_first_completions = (8, 10, 12), (2, 4, 12)
    assert F(sum(fcfs_completions), 3) == 10
    assert F(sum(short_first_completions), 3) == 6
    assert (8 <= 9, 10 <= 12, 12 <= 12) == (True, True, True)
    assert (12 <= 9, 2 <= 12, 4 <= 12) == (False, True, True)
    assert min(10+10, 12) == 12
    ready_devices = (8, 2, 4)
    assert F(sum(ready_devices), 3) == F(14, 3)
    delayed_long_finish = 4+8
    assert delayed_long_finish == 12 and F(12+2+4, 3) == 6
    data_theme = mlsys['themes'][4]
    # Original pipeline model: one preparation worker and one trainer, with
    # batches consumed in order and no buffer-capacity bottleneck.
    def pipeline_finish(prep_ms, train_ms, batch_count):
        prep_ready = 0
        train_done = 0
        for _ in range(batch_count):
            prep_ready += prep_ms
            train_done = max(prep_ready, train_done) + train_ms
        return train_done
    assert pipeline_finish(12, 8, 3) == 44
    assert pipeline_finish(12, 4, 3) == 40
    assert pipeline_finish(6, 8, 3) == 30
    assert pipeline_finish(6, 4, 3) == 22
    data_theme_text = ' '.join([data_theme['body'], *data_theme['worked_example'],
                                data_theme['practice']['question'],
                                data_theme['practice']['answer']]).lower()
    for phrase in ('one preparation worker and one training device',
                   'completion takes 44 milliseconds',
                   'completion is now 30 milliseconds',
                   'finishing at 22 milliseconds',
                   'does not establish unchanged performance on that case'):
        assert phrase in data_theme_text, f'Update the MLSys data-supply check when prose changes: {phrase}'
    device_theme = mlsys['themes'][5]
    assert F(200, 100) == 2 and F(800, 50) == 16
    first_device_time = F(200, 100) + F(800, 50)
    first_device_energy = 60*2 + 40*16
    second_device_time = F(1000, 60)
    second_device_energy = 45*second_device_time
    second_device_total_time = second_device_time + 2
    second_device_total_energy = second_device_energy + 100
    assert (first_device_time, first_device_energy) == (18, 760)
    assert (second_device_time, second_device_energy) == (F(50, 3), 750)
    assert (second_device_total_time, second_device_total_energy) == (F(56, 3), 850)
    assert first_device_time < second_device_total_time
    assert first_device_energy < second_device_total_energy
    assert F(100, 100) == 1 and F(100, 60) == F(5, 3)
    assert 60*1 == 60 and 45*F(5, 3) == 75
    device_theme_text = ' '.join([device_theme['body'], *device_theme['worked_example'],
                                  device_theme['practice']['question'],
                                  device_theme['practice']['answer']]).lower()
    for phrase in ('treat that rate change as stipulated; it is not a thermal model',
                   'device energy is 60 × 2 + 40 × 16 = 760 joules',
                   'finishing in 50/3 seconds and using 750 joules',
                   'its total becomes 56/3 seconds',
                   'these figures exclude the rest of the system',
                   'the first wins both comparisons for this shorter workload'):
        assert phrase in device_theme_text, f'Update the MLSys sustained-device check when prose changes: {phrase}'
    device_notes = [SUBTHEME_NOTES[('mlsys-2025', 6, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in device_notes] == [
        'https://openreview.net/forum?id=fR7Plt5D7p',
        'https://openreview.net/forum?id=sFNRNTduKO',
        'https://openreview.net/forum?id=fLSlGn641R']
    for phrase, note in zip(('MEADOW', 'FlexInfer', 'MAS-Attention'), device_notes):
        assert phrase in note['evidence'], f'Add the correct MLSys theme-6 evidence boundary for {phrase}'
    trust_theme = mlsys['themes'][6]
    predictions, actuals = (8, 9, 9, 12), (9, 11, 8, 10)
    accepted = [actual <= 10 for actual in predictions]
    misses_when_accepted = sum(ok and actual > 10 for ok, actual in zip(accepted, actuals))
    rejected_but_would_meet = sum((not ok) and actual <= 10 for ok, actual in zip(accepted, actuals))
    mean_absolute_error = F(sum(abs(pred - actual) for pred, actual in zip(predictions, actuals)), len(predictions))
    assert (accepted, misses_when_accepted, rejected_but_would_meet, mean_absolute_error) == (
        [True, True, True, False], 1, 1, F(3, 2))
    assert 8+2 <= 10 and 8 < F(17, 2)+2
    trust_theme_text = ' '.join([trust_theme['body'], *trust_theme['worked_example'],
                                 trust_theme['practice']['question'],
                                 trust_theme['practice']['answer']]).lower()
    for phrase in ('mean absolute prediction error is only (1 + 2 + 1 + 2)/4 = 1.5 milliseconds',
                   'does not establish such a bound for future inputs',
                   'one of three accepted requests misses',
                   'prediction 8.5 plus the bound gives 10.5',
                   'this describes an invented interface'):
        assert phrase in trust_theme_text, f'Update the MLSys result-trust check when prose changes: {phrase}'
    trust_notes = [SUBTHEME_NOTES[('mlsys-2025', 7, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in trust_notes] == [
        'https://openreview.net/forum?id=3EXBLwGxtq',
        'https://openreview.net/forum?id=HPHrIBlJYw',
        'https://openreview.net/forum?id=EH5PZW6aCr']
    for phrase, note in zip(('AIOpsLab', 'abstract-only', 'supply-chain paper'), trust_notes):
        assert phrase.lower() in note['evidence'].lower(), f'Add the correct MLSys theme-7 source boundary for {phrase}'
    structure_theme = mlsys['themes'][7]
    assert [1, 3, 7, 15] == [sum((1, 2, 4, 8)[:i+1]) for i in range(4)]
    assert sum(range(1, 5)) == 10 and 4*4 == 16 and 16-10 == 6
    assert 16+16 == 32 and (8+10)+(8+10) == 36
    # One prepared plan reused twice pays its preparation cost only once.
    assert 8+10*2 == 28 < 32
    assert 8+10 == 18 > 16
    assert sum(range(1, 6)) == 15 and 5*5 == 25 and 8+15 == 23 < 25
    structure_theme_text = ' '.join([structure_theme['body'], *structure_theme['worked_example'],
                                     structure_theme['practice']['question'],
                                     structure_theme['practice']['answer']]).lower()
    for phrase in ('only values at positions zero through i',
                   'the required outputs are [1, 3, 7, 15]',
                   'if the same prepared plan serves two compatible uses',
                   'preparation may recur',
                   'this says nothing about floating-point reordering'):
        assert phrase in structure_theme_text, f'Update the MLSys structure-exposure check when prose changes: {phrase}'
    structure_notes = [SUBTHEME_NOTES[('mlsys-2025', 8, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in structure_notes] == [
        'https://openreview.net/forum?id=2QMYV4bA0R',
        'https://openreview.net/forum?id=rjQfX0YgDl',
        'https://openreview.net/forum?id=nddxAiToZn']
    for phrase, note in zip(('FlexAttention', 'XGrammar', 'Hidden Bloat'), structure_notes):
        assert phrase.lower() in note['evidence'].lower(), f'Add the correct MLSys theme-8 source boundary for {phrase}'
    osdi = next(route for route in ROUTES if route['id'] == 'osdi-2025')
    assert len(osdi['themes']) == 8 and len(osdi['themes'][0]['subthemes']) == 3
    translation_theme = osdi['themes'][0]
    original_values = [2, 5]
    saved_reference = original_values
    returned_values = original_values
    for index in range(len(returned_values)):
        returned_values[index] += 1
    assert returned_values == [3, 6] and saved_reference == [3, 6]
    allocating_observed, exclusive_observed = 8+1, 5+4
    assert (allocating_observed, exclusive_observed) == (9, 9)
    assert (8, 5) != (allocating_observed, exclusive_observed)
    assert (1, 4) == (allocating_observed-8, exclusive_observed-5)
    translation_text = ' '.join([translation_theme['body'], *translation_theme['worked_example'],
                                 translation_theme['practice']['question'],
                                 translation_theme['practice']['answer']]).lower()
    for phrase in ('caller keeps another reference to the input',
                   'the caller\'s saved reference now also sees [3, 6]',
                   'makes both observed totals nine',
                   'understanding its unequal effect',
                   'object identity can also check'):
        assert phrase in translation_text, f'Update the OSDI translation-theme check when prose changes: {phrase}'
    translation_notes = [SUBTHEME_NOTES[('osdi-2025', 1, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in translation_notes] == [
        'https://www.usenix.org/conference/osdi25/presentation/dong',
        'https://www.usenix.org/conference/osdi25/presentation/wu-mengdi',
        'https://www.usenix.org/conference/osdi25/presentation/guan']
    for phrase, note in zip(('QiMeng-Xpiler', 'Mirage', 'KPerfIR'), translation_notes):
        assert phrase in note['evidence'], f'Add the correct OSDI theme-1 source boundary for {phrase}'
    durability_theme = osdi['themes'][4]
    crash_table = durability_theme['worked_table']
    assert crash_table['rows'] == [
        ['Old only', 'Old', 'Old version'],
        ['Old and new', 'Old', 'Old version'],
        ['Old and new', 'New', 'New version'],
        ['Old only', 'New', 'Missing payload; forbidden'],
    ]
    assert 4 + 2 == 6
    replica_state = {'A': 1, 'B': 1, 'C': 0}
    assert sum(version == 1 for version in replica_state.values()) == 2
    assert replica_state['B'] == 1  # version 1 remains after A fails
    one_copy_then_failure = {'A': 0, 'B': 0, 'C': 0}
    assert sum(version == 1 for version in one_copy_then_failure.values()) == 0
    assert 3 > 2  # all-copy confirmation blocks progress if one replica is unavailable
    durability_text = ' '.join([durability_theme['body'], *durability_theme['worked_example'],
                                durability_theme['practice']['question'],
                                durability_theme['practice']['answer']]).lower()
    for phrase in ('the new index can survive while the new payload does not',
                   'a durable-success reply takes at least six milliseconds',
                   'the acknowledged update disappears',
                   'real protocols must also define version ordering',
                   'recorded intent and a defined recovery rule'):
        assert phrase in durability_text, f'Update the OSDI durability-theme check when prose changes: {phrase}'
    durability_notes = [SUBTHEME_NOTES[('osdi-2025', 5, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in durability_notes] == [
        'https://www.usenix.org/conference/osdi25/presentation/cui',
        'https://www.usenix.org/conference/osdi25/presentation/zhang-tony',
        'https://www.usenix.org/conference/osdi25/presentation/zhang-tianren']
    for phrase, note in zip(('F2FSJ', 'Basilisk', 'KRR'), durability_notes):
        assert phrase in note['evidence'], f'Add the correct OSDI theme-5 source boundary for {phrase}'
    assert 'not F2FSJ measurements' in durability_notes[0]['evidence']
    assert 'not a repair mechanism' in durability_notes[1]['evidence']
    assert 'does not imply that KRR captures remote service responses' in durability_notes[2]['evidence']
    security_theme = osdi['themes'][5]
    assert 1000 * 1_000_000 == 1_000_000_000
    security_text = ' '.join([security_theme['body'], *security_theme['worked_example'],
                              security_theme['practice']['question'],
                              security_theme['practice']['answer'],
                              security_theme['reading'],
                              *(title + ' ' + description for title, description in security_theme['subthemes'])]).lower()
    for phrase in ('another participant can change what the name refers to',
                   'a thousand live buffers use roughly a gigabyte',
                   'availability, functionality, and reproduced results as separate claims',
                   'does not establish that a live service runs that exact build',
                   'one thousand live one-megabyte buffers are roughly a gigabyte',
                   'which exact build was checked?',
                   'what can someone learn?'):
        assert phrase in security_text, f'Update the OSDI security-theme check when prose changes: {phrase}'
    security_notes = [SUBTHEME_NOTES[('osdi-2025', 6, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in security_notes] == [
        'https://www.usenix.org/conference/osdi25/presentation/adam',
        'https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng',
        'https://www.usenix.org/conference/osdi25/call-for-artifacts']
    for phrase, note in zip(('Paralegal', 'Extension Interface Model', 'OSDI 2025 artifact review'), security_notes):
        assert phrase in note['evidence'], f'Add the correct OSDI theme-6 source boundary for {phrase}'
    assert 'not one of its reported bugs' in security_notes[0]['evidence']
    assert 'not results from that system' in security_notes[1]['evidence']
    assert 'need separate evidence' in security_notes[2]['evidence']
    variation_theme = osdi['themes'][6]
    slow_trace_mean = F(9 * 2 + 20, 10)
    steady_trace_mean = F(10 * 4, 10)
    mixed_start_mean = F(5 * 2 + 5 * 20, 10)
    maximum_cold_fraction = F(5 - 2, 20 - 2)
    assert (slow_trace_mean, steady_trace_mean, mixed_start_mean) == (F(19, 5), 4, 11)
    assert slow_trace_mean == F('3.8') and steady_trace_mean == 4
    assert sum(time <= 5 for time in [2] * 9 + [20]) == 9
    assert sum(time <= 5 for time in [4] * 10) == 10
    assert maximum_cold_fraction == F(1, 6)
    assert 2 * (1 - maximum_cold_fraction) + 20 * maximum_cold_fraction == 5
    assert 2 * (1 - F(1, 5)) + 20 * F(1, 5) > 5
    variation_text = ' '.join([variation_theme['body'], *variation_theme['worked_example'],
                               variation_theme['practice']['question'],
                               variation_theme['practice']['answer'], variation_theme['reading'],
                               *(title + ' ' + description for title, description in variation_theme['subthemes'])]).lower()
    for phrase in ('their mean is 3.8 milliseconds', 'five-millisecond deadline is missed once',
                   'mean of eleven', 'time to first output', 'at most 1/6',
                   'serial performance optimization organizes ways to remove, replace, or reorder',
                   'does not supply the timing values in these exercises'):
        assert phrase in variation_text, f'Update the OSDI variation-theme check when prose changes: {phrase}'
    variation_notes = [SUBTHEME_NOTES[('osdi-2025', 7, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in variation_notes] == [
        'https://www.usenix.org/conference/osdi25/presentation/li',
        'https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu',
        'https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu']
    assert 'Tintin' in variation_notes[0]['evidence'] and 'does not supply this course’s request-delay distribution' in variation_notes[0]['evidence']
    assert 'Fork in the Road' in variation_notes[1]['evidence'] and 'original teaching values' in variation_notes[1]['evidence']
    assert 'original and not its measurement' in variation_notes[2]['evidence']
    whole_result_theme = osdi['themes'][7]
    cold_request = 6 + 4 + 3 + 2
    faster_execution = 6 + 4 + F(3, 2) + 2
    warm_request = 4 + 3 + 2
    idle_energy = 8 * 10
    assert (cold_request, faster_execution, warm_request, idle_energy) == (15, F('13.5'), 9, 80)
    assert (F(idle_energy, 20), F(idle_energy, 4)) == (4, 20)
    whole_result_text = ' '.join([whole_result_theme['body'], *whole_result_theme['worked_example'],
                                  whole_result_theme['practice']['question'],
                                  whole_result_theme['practice']['answer'], whole_result_theme['reading'],
                                  *(title + ' ' + description for title, description in whole_result_theme['subthemes'])]).lower()
    for phrase in ('after fifteen milliseconds', 'reduces the total to 13.5 milliseconds—not to half',
                   'reducing delay to nine milliseconds', 'the idle interval uses eighty joules',
                   'assigns four joules to each request', 'twenty joules each',
                   'new requests wait for reload, may use the old version, or should fail',
                   'their systems and measurements differ'):
        assert phrase in whole_result_text, f'Update the OSDI whole-result check when prose changes: {phrase}'
    whole_result_notes = [SUBTHEME_NOTES[('osdi-2025', 8, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in whole_result_notes] == [
        'https://www.usenix.org/conference/osdi25/presentation/cheng',
        'https://www.usenix.org/conference/osdi25/presentation/miemietz',
        'https://www.usenix.org/conference/osdi25/presentation/zhang-dingyan']
    for phrase, note in zip(('PipeThreader', 'MettEagle', 'BlitzScale'), whole_result_notes):
        assert phrase in note['evidence'], f'Add the correct OSDI theme-8 source boundary for {phrase}'
    assert 'do not supply the course’s multi-stage service timings' in whole_result_notes[0]['evidence']
    assert 'specific to those implementations and workloads' in whole_result_notes[1]['evidence']
    assert 'Neither yields the course’s 15-ms component sum' in whole_result_notes[2]['evidence']
    osdi_exercise = next(route for route in ROUTES if route['id'] == 'osdi-2025')['exercise'].lower()
    for phrase in ('trace a request or update', 'what must remain true',
                   'which event starts and stops the measurement',
                   'mark overlapping work separately',
                   'mark missing evidence instead of joining numbers from unrelated papers',
                   'one observation that would prove your prediction wrong'):
        assert phrase in osdi_exercise, f'Update the OSDI route exercise check when prose changes: {phrase}'
    asplos_route = next(route for route in ROUTES if route['id'] == 'asplos-2025')
    asplos_theme_one = asplos_route['themes'][0]
    asplos_notes = [SUBTHEME_NOTES[('asplos-2025', 1, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_notes] == [
        'https://www.microsoft.com/en-us/research/publication/coach-exploiting-temporal-patterns-for-all-resource-oversubscription-in-cloud-platforms/',
        'https://www.microsoft.com/en-us/research/publication/coach-exploiting-temporal-patterns-for-all-resource-oversubscription-in-cloud-platforms/',
        'https://dl.acm.org/doi/10.1145/3676641.3716264']
    assert 'snapshot or forecast' in asplos_notes[0]['failure']
    assert 'atomic reservation' in asplos_notes[1]['example']
    assert 'abstract-only' in asplos_notes[2]['evidence']
    assert 'reservation operation can instead check and subtract space as one indivisible step' in ' '.join(asplos_theme_one['worked_example'])
    assert 'a representation retaining those read and write relationships' in ' '.join(asplos_theme_one['worked_example']).lower()
    asplos_theme_two = asplos_route['themes'][1]
    asplos_theme_two_notes = [SUBTHEME_NOTES[('asplos-2025', 2, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_theme_two_notes] == [
        'https://doi.org/10.1145/3676642.3736121',
        'https://arxiv.org/abs/2412.10261',
        'https://doi.org/10.1145/3676641.3716011']
    assert 'abstract-only' in asplos_theme_two_notes[0]['evidence']
    assert 'does not provide a general early-stopping rule' in asplos_theme_two_notes[1]['evidence']
    assert 'adjacent-window stability' in asplos_theme_two_notes[2]['evidence']
    assert 'changed output-length distribution' in asplos_theme_two_notes[2]['failure']
    scalar_a, scalar_b, approximate_x = F('0.01'), F(1), F(99)
    residual = abs(scalar_b - scalar_a*approximate_x)
    answer_error = abs(approximate_x - scalar_b/scalar_a)
    assert (residual, answer_error, residual/scalar_a) == (F('0.01'), F(1), F(1))
    required_residual = scalar_a*F('0.1')
    practice_error = F('0.004')/F('0.02')
    practice_limit = F('0.02')*F('0.1')
    assert (required_residual, practice_error, practice_limit) == (F('0.001'), F('0.2'), F('0.002'))
    assert 4+4*F('0.5') == 6
    asplos_theme_two_text = ' '.join([asplos_theme_two['body'], *asplos_theme_two['worked_example'],
                                     asplos_theme_two['practice']['question'],
                                     asplos_theme_two['practice']['answer'], asplos_theme_two['reading']]).lower()
    for phrase in ('answer error equals residual divided by |a|', 'not measurements from a conference paper',
                   'not a faster solution to the same task', 'needs its own error argument',
                   'voyager as an abstract-only lead'):
        assert phrase in asplos_theme_two_text, f'Update the ASPLOS theme-2 check when prose changes: {phrase}'
    asplos_theme_three = asplos_route['themes'][2]
    asplos_theme_three_notes = [SUBTHEME_NOTES[('asplos-2025', 3, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_theme_three_notes] == [
        'https://gvavou5.github.io/Documents/Vavouliotis_ASPLOS25.pdf',
        'https://arxiv.org/abs/2508.02309',
        'https://doi.org/10.1145/3669940.3707223']
    assert '18.9%' in asplos_theme_three_notes[0]['evidence']
    assert 'abstract-only' in asplos_theme_three_notes[2]['evidence']
    assert 'does not reduce the bytes moved' in asplos_theme_three_notes[2]['failure']
    tlb_record = json.loads((ROOT/'analysis/per-paper/asplos-2025-025.json').read_text())
    assert tlb_record['pdf_url'] == asplos_theme_three_notes[0]['source']
    assert tlb_record['source_text_status'] == 'fulltext-candidate'
    assert 'increasing data STLB misses and page walks' in tlb_record['method']
    assert 'the other is informed and does the same' not in tlb_record['method']
    assert '18.9%' in tlb_record['metrics']['other'] and '11.4%' in tlb_record['metrics']['other']
    column_reads, row_reads = 6, 2
    original_transfers = 4*column_reads + row_reads
    converted_transfers = 8 + column_reads + 4*row_reads
    mixed_original = 4*4 + 4
    mixed_converted = 8 + 4 + 4*4
    first_winning_count = min(c for c in range(9) if 40-3*c < 8+3*c)
    assert (original_transfers, converted_transfers, mixed_original, mixed_converted) == (26, 22, 20, 28)
    assert first_winning_count == 6
    for phrase in ('row-by-row cpu transactions', 'column-oriented in-memory scans',
                   'overlap independent computation', 'local record has no full text'):
        assert phrase in asplos_theme_three['reading'].lower(), f'Update ASPLOS theme-3 reading limits for {phrase}'
    asplos_theme_four = asplos_route['themes'][3]
    asplos_theme_four_notes = [SUBTHEME_NOTES[('asplos-2025', 4, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_theme_four_notes] == [
        'https://arxiv.org/abs/2412.08137',
        'https://arxiv.org/abs/2410.15908',
        'https://arxiv.org/abs/2502.07578']
    assert 'three-operation' in asplos_theme_four_notes[0]['evidence']
    assert 'two-device formal model' in asplos_theme_four_notes[1]['evidence']
    assert '32k context' in asplos_theme_four_notes[2]['evidence'].lower()
    assert 'micro blossom' in asplos_theme_four['reading'].lower()
    assert 'weaker performance on compute-heavy prompt processing' in asplos_theme_four['reading'].lower()
    baseline_filter = 100/10 + 2
    exact_near_filter = lambda fraction: 3 + 10*fraction
    preliminary_filter = lambda fraction: 5 + 10*fraction
    assert baseline_filter == 12
    assert exact_near_filter(F('0.1')) == 4 and exact_near_filter(1) == 13
    assert exact_near_filter(F('0.89')) < baseline_filter == exact_near_filter(F('0.9'))
    assert preliminary_filter(F('0.69')) < baseline_filter == preliminary_filter(F('0.7'))
    assert 3+4+2 == 9
    assert 'dropping one true match violates exact filtering' in asplos_theme_four['practice']['answer'].lower()
    asplos_theme_five = asplos_route['themes'][4]
    asplos_theme_five_notes = [SUBTHEME_NOTES[('asplos-2025', 5, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_theme_five_notes] == [
        'https://arxiv.org/abs/2503.02354',
        'https://doi.org/10.1145/3669940.3707225',
        'https://arxiv.org/abs/2501.10714']
    assert 'known expert routes' in asplos_theme_five_notes[0]['evidence']
    assert 'abstract' in asplos_theme_five_notes[1]['evidence'].lower()
    assert '48 gpus' in asplos_theme_five_notes[2]['evidence'].lower()
    assert all(phrase in asplos_theme_five['reading'].lower() for phrase in (
        'not just which worker has the fewest tasks', 'known ahead of time',
        'abstract-only', 'lock prevents conflicting access; a barrier waits'))
    unbalanced_completion = max(6+6, 2+2)+3
    balanced_completion = max(6+2, 6+2)+3
    moved_balanced_completion = 5+balanced_completion
    two_piece_pipeline = 4+4+4
    four_piece_pipeline = 3+3+3*3
    eight_piece_pipeline = 2+2+7*2
    assert (unbalanced_completion, balanced_completion, moved_balanced_completion) == (15, 11, 16)
    assert (two_piece_pipeline, four_piece_pipeline, eight_piece_pipeline) == (12, 15, 18)
    asplos_theme_six = asplos_route['themes'][5]
    asplos_theme_six_notes = [SUBTHEME_NOTES[('asplos-2025', 6, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_theme_six_notes] == [
        'https://doi.org/10.1145/3669940.3707231',
        'https://www.microsoft.com/en-us/research/wp-content/uploads/2024/12/Coach-Resource-Oversubscription.pdf',
        'https://doi.org/10.1145/3676641.3716011']
    assert '2,823 j versus 2,709 j' in asplos_theme_six_notes[0]['evidence'].lower()
    assert 'azure traces' in asplos_theme_six_notes[1]['evidence'].lower()
    assert 'goodput' in asplos_theme_six_notes[2]['example'].lower()
    for phrase in ('not the 5.56% reduction in average soc power', 'guaranteed from oversubscribed allocation',
                   'goodput', 'tokens per joule and tokens per dollar'):
        assert phrase in asplos_theme_six['reading'].lower(), f'Update ASPLOS theme-6 source-boundary check for {phrase}'
    baseline_soc_j = F('250.04')*F('11.29')
    dvfs_soc_j = F('236.14')*F('11.47')
    assert (baseline_soc_j, dvfs_soc_j) == (F('2822.9516'), F('2708.5258'))
    assert round(float((baseline_soc_j-dvfs_soc_j)/baseline_soc_j*100), 2) == 4.05
    assert 60*10 == 600 and 50*10 == 500
    assert F(600, 90) == F(20, 3) and F(500, 60) == F(25, 3)
    assert F(560, 84) == F(20, 3) and 84 < 85
    assert [10*i for i in range(1, 21) if 10*i <= 50] == [10, 20, 30, 40, 50]
    asplos_theme_seven = asplos_route['themes'][6]
    asplos_theme_seven_notes = [SUBTHEME_NOTES[('asplos-2025', 7, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_theme_seven_notes] == [
        'https://arxiv.org/abs/2606.23905',
        'https://arxiv.org/abs/2502.05429',
        'https://feihe.github.io/materials/asplos25.pdf']
    assert all(phrase in asplos_theme_seven['reading'].lower() for phrase in (
        'two devices and one location', 'bounded-model counterexample',
        'does not model rtl or silicon', 'sibling smt thread',
        '13 unknown', 'unknown is not a pass'))
    assert 'not by itself' in asplos_theme_seven_notes[0]['failure']
    assert 'does not prevent every leak' in asplos_theme_seven_notes[1]['failure']
    assert 'one was verified robust, 12 had violations, and 13 remained unknown' in asplos_theme_seven_notes[2]['evidence']
    assert 'what has it shown' in asplos_theme_seven['practice']['question'].lower()
    assert 'unresolved' in asplos_theme_seven['practice']['answer'].lower()
    assert 'A = 10 and B = 0' in ' '.join(asplos_theme_seven['worked_example'])
    asplos_theme_eight = asplos_route['themes'][7]
    asplos_theme_eight_notes = [SUBTHEME_NOTES[('asplos-2025', 8, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in asplos_theme_eight_notes] == [
        'https://doi.org/10.1145/3676641.3716011',
        'https://arxiv.org/abs/2508.02309',
        'https://www.microsoft.com/en-us/research/wp-content/uploads/2024/12/Coach-Resource-Oversubscription.pdf']
    assert all(phrase in asplos_theme_eight['reading'].lower() for phrase in (
        'arrival', 'accepted answer', 'recent output lengths remaining representative', 'warm-up history', 'one memory layout',
        'detects contention', 'do not rank the same system'))
    assert 'short-window output-length stability' in asplos_theme_eight_notes[0]['evidence']
    assert '3.4× olap and 4.4× oltp' in asplos_theme_eight_notes[1]['evidence'].lower()
    assert 'reassignment or vm migration' in asplos_theme_eight_notes[2]['example'].lower()
    assert 'reconsider an action' in asplos_theme_eight['practice']['answer'].lower()
    # Fluid-queue model used by the lesson: backlog grows at arrivals-service,
    # then drains only at service-arrivals while the worker remains overloaded.
    queue_at_detection = (100-80)*3
    queue_at_activation = queue_at_detection + (100-80)*2
    drain_seconds = F(queue_at_activation, 140-100)
    temporary_queue = (100-80)*2
    temporary_drain = F(temporary_queue, 120-100)
    assert (queue_at_detection, queue_at_activation, drain_seconds) == (60, 100, F(5, 2))
    assert (temporary_queue, temporary_drain, 5) == (40, 2, 5)
    assert 5+drain_seconds == F(15, 2) and 2+temporary_drain == 4
    placement_theme = osdi['themes'][1]
    region_bytes = 64*1024
    page_bytes = 4*1024
    tracking_bytes = 64
    coarse_one_page = 4*region_bytes + 4*tracking_bytes
    fine_one_page = 4*page_bytes + 4*tracking_bytes
    fine_all_pages = 4*16*page_bytes + 4*16*tracking_bytes
    coarse_all_pages = 4*region_bytes + 4*tracking_bytes
    assert (coarse_one_page/1024, fine_one_page/1024) == (256.25, 16.25)
    assert (fine_all_pages/1024, coarse_all_pages/1024) == (260, 256.25)
    assert 16.25 <= 32 < 256.25
    local_hit, local_miss, remote = 1+2, 2+10, 10
    mean_half = 3*F(1, 2) + 12*F(1, 2)
    hit_fraction_break_even = F(2, 9)
    assert (local_hit, local_miss, remote, mean_half) == (3, 12, 10, F(15, 2))
    assert local_hit*hit_fraction_break_even + local_miss*(1-hit_fraction_break_even) == remote
    assert F(1, 4) > hit_fraction_break_even
    assert 3*F(1, 4)+12*(1-F(1, 4)) < remote
    assert F(1, 5) < hit_fraction_break_even
    assert 3*F(1, 5)+12*(1-F(1, 5)) > remote
    placement_text = ' '.join([placement_theme['body'], *placement_theme['worked_example'],
                               placement_theme['practice']['question'],
                               placement_theme['practice']['answer'], placement_theme['reading']]).lower()
    for phrase in ('tracked footprints are 256.25 and 16.25 kib',
                   'every page of all four regions is read',
                   'with half hits and half misses, mean cost is 7.5 microseconds',
                   'hit fraction h, mean time is 3h + 12',
                   'h exceeds 2/9', 'tigon\'s cxl setup as emulated'):
        assert phrase in placement_text, f'Update the OSDI placement-theme check when prose changes: {phrase}'
    placement_notes = [SUBTHEME_NOTES[('osdi-2025', 2, number)] for number in (1, 2, 3)]
    assert [note['source'] for note in placement_notes] == [
        'https://www.usenix.org/conference/osdi25/presentation/wang-xiaoyang',
        'https://www.usenix.org/conference/osdi25/presentation/athlur',
        'https://www.usenix.org/conference/osdi25/presentation/liu']
    for phrase, note in zip(('FineMem', 'Okapi', 'Tiered Memory Management'), placement_notes):
        assert phrase.lower() in note['evidence'].lower(), f'Add the correct OSDI theme-2 source boundary for {phrase}'
    communication_theme = osdi['themes'][2]
    initial_counter = 0
    after_first_r = initial_counter + 1
    after_unrecognized_retry = after_first_r + 1
    after_new_s = after_first_r + 1
    assert (after_first_r, after_unrecognized_retry, after_new_s) == (1, 2, 2)
    # The two separately durable pieces must describe one committed outcome.
    state_persisted_record_lost = (1, None)
    record_persisted_state_lost = (0, 'success')
    assert state_persisted_record_lost[0] == 1 and state_persisted_record_lost[1] is None
    assert record_persisted_state_lost == (0, 'success')
    read_your_write_value, stale_replica_value = 1, 0
    assert stale_replica_value != read_your_write_value
    communication_text = ' '.join([communication_theme['body'], *communication_theme['worked_example'],
                                   communication_theme['practice']['question'],
                                   communication_theme['practice']['answer'],
                                   communication_theme['reading']]).lower()
    for phrase in ('the client retries r', 'the counter becomes two',
                   'the remembered identifier and the counter update must survive consistently',
                   'a replica still has zero', 's names a new logical request',
                   'timeout alone cannot reveal whether the earlier operation executed'):
        assert phrase in communication_text, f'Update the OSDI communication-theme check when prose changes: {phrase}'
    communication_notes = [SUBTHEME_NOTES[('osdi-2025', 3, number)] for number in (1, 2, 3)]
    assert communication_notes[0]['source'] == 'https://www.usenix.org/conference/osdi25/presentation/frank'
    assert communication_notes[2]['source'] == 'https://www.usenix.org/conference/osdi25/presentation/lyerly'
    assert 'Picsou' in communication_notes[0]['evidence'] and 'not' in communication_notes[0]['evidence']
    assert 'Skybridge' in communication_notes[2]['evidence'] and 'original' in communication_notes[2]['evidence']
    allocation_notes = [SUBTHEME_NOTES[('osdi-2025', 4, number)] for number in (1, 2, 3)]
    assert allocation_notes[0]['source'] == 'https://www.usenix.org/conference/osdi25/presentation/domingo'
    assert allocation_notes[1]['source'] == 'https://www.usenix.org/system/files/osdi25-zhang-dingyan.pdf'
    assert allocation_notes[2]['source'] == 'https://www.usenix.org/conference/osdi25/presentation/lin-jinkun'
    assert 'original teaching values' in allocation_notes[0]['evidence']
    assert 'original' in allocation_notes[1]['evidence']
    assert 'Neither establishes the toy contention cause' in allocation_notes[2]['evidence']
    stay = lambda units: 5 * units
    migrate = lambda units: 12 + 3 * units
    assert (stay(6), migrate(6)) == (30, 30)
    assert (stay(7), migrate(7)) == (35, 33)
    assert migrate(7) + 8 - stay(7) == 6
    assert 12 + 3 * 11 + 8 == 53 < stay(11) == 55
    assert 2 * 12 == 24
    allocation_theme = osdi['themes'][3]
    allocation_text = ' '.join([allocation_theme['body'], *allocation_theme['worked_example'],
                                allocation_theme['practice']['question'],
                                allocation_theme['practice']['answer']]).lower()
    for phrase in ('six units tie at thirty milliseconds',
                   'the move is six milliseconds worse',
                   'two twelve-millisecond moves consume twenty-four milliseconds',
                   'n must exceed ten'):
        assert phrase in allocation_text, f'Update the OSDI allocation-theme check when prose changes: {phrase}'
    queue_text = ' '.join([queue_theme['body'], *queue_theme['worked_example'],
                           queue_theme['practice']['question'], queue_theme['practice']['answer'],
                           queue_theme['reading'],
                           *(definition for _, definition in queue_theme['subthemes'])]).lower()
    for phrase in ('with no switching cost', 'with a mean response time of 10',
                   'with a mean of 6', 'misses the long request\'s deadline',
                   'shared input connection supplies only twelve requests per second',
                   'the mean becomes 6', 'the long request misses its time-9 deadline',
                   'allocation time is not the same as readiness to execute'):
        assert phrase in queue_text, f'Update the MLSys scheduling-theme check when prose changes: {phrase}'
    memory_theme = mlsys['themes'][1]
    assert 4+4+8+6 == 22 > 20
    assert 4+4+8+3 == 19 <= 20
    recalculation_step = 50+12
    transfer_at_100, transfer_at_400 = 50+F(4, 100)*1000, 50+F(4, 400)*1000
    assert recalculation_step == 62
    assert (transfer_at_100, transfer_at_400) == (90, 60)
    assert transfer_at_100 > recalculation_step > transfer_at_400
    assert F(4, 100)*1000 == 40 and F(4, 400)*1000 == 10
    assert 50+40 == 90 and 50+10 == 60
    transfer_break_even = F(4, F(12, 1000))
    assert transfer_break_even == F(1000, 3)
    assert 100 < F(1000, 3) < 400
    assert 19+2 == 21 > 20
    memory_theme_text = ' '.join([memory_theme['body'], *memory_theme['worked_example'],
                                  memory_theme['practice']['question'],
                                  memory_theme['practice']['answer'],
                                  memory_theme['reading'],
                                  *(definition for _, definition in memory_theme['subthemes'])]).lower()
    for phrase in ('memory has both a space limit and a movement cost',
                   'assume the revised schedule has no additional peak allocation',
                   'making that path 90 milliseconds versus recalculation\'s 62',
                   'at 400 gb per second it takes 10 milliseconds',
                   'that prefix match alone does not establish that saved intermediate values mean the same thing',
                   'transfers 2 gb out and later retrieves them',
                   'they address different kinds of state'):
        assert phrase in memory_theme_text, f'Update the MLSys memory-theme check when prose changes: {phrase}'
    partition_theme = mlsys['themes'][2]
    assert 12+8 == 20 < 24
    assert 12+8-6 == 14
    assert 6+20 == 26 > 24
    assert 24+20 == 44
    assert 15+10-4 == 21 < 24 and 15+10 == 25 > 24
    partition_text = ' '.join([partition_theme['body'], *partition_theme['worked_example'],
                               partition_theme['practice']['question'],
                               partition_theme['practice']['answer'],
                               partition_theme['reading'],
                               *(definition for _, definition in partition_theme['subthemes'])]).lower()
    for phrase in ('an eight-millisecond exchange', 'fall to fourteen',
                   'completion takes 26 milliseconds',
                   'the sequential total becomes 44',
                   'only four milliseconds overlapping',
                   'without it, time is 25 and loses',
                   'an asynchronous call alone does not supply it'):
        assert phrase in partition_text, f'Update the MLSys partitioning-theme check when prose changes: {phrase}'
    training = next(section for section in SECTIONS if section['id'] == 'training-workflow')
    training_text = (' '.join(training['body']) + ' ' + training['exercise']['question'] +
                     ' ' + training['exercise']['answer']).lower()
    worker_times = (24, 24, 24, 40)
    baseline_step = 8 + max(worker_times) + 12 + 4
    mean_worker_step = 8 + F(sum(worker_times), len(worker_times)) + 12 + 4
    assert (baseline_step, mean_worker_step) == (64, 52)
    assert max(worker_times)-24 == 16
    assert 8+5+28+12+4 == 57
    assert 8+15+28+12+4 == 67
    assert 8+max(40, 12)+4 == 52
    assert 28+6 == 34 and 8+40 == 48
    assert 48+6 == 54 and 54+4 == 58
    assert 12-6 == 6  # first exchange chunk's hidden time; six more remain
    assert 8+40+3+6+4 == 61
    assert 64_000/61 > 1_049 and 64_000/61 < 1_050
    assert 1_049*61 == 63_989 < 64_000 < 64_050 == 1_050*61
    assert 1_000*64 == 64_000 and 1_200*61 == 73_200
    exercise_fast_step = 8+max(24, 20)+12+4
    assert exercise_fast_step == 48
    assert exercise_fast_step*1_300 == 62_400 < 64_000
    assert 0+max(4, 20)+6+6 == 32
    for phrase in ('the accepted model is the result',
                   'faster steps do not necessarily reduce time to that result',
                   'the step actually takes 58 ms',
                   'the final transfer cannot start before time 48',
                   'the next step uses the resulting version',
                   'do not establish that the systems compose',
                   'shared implementation, workload, quality rule, and failure policy',
                   'time to the accepted quality target'):
        assert phrase in training_text, f'Update the training-workflow check when prose changes: {phrase}'
    print('Opening exercise and cross-topic timing, deadline, and break-even calculations passed.')


if __name__ == '__main__':
    main()
