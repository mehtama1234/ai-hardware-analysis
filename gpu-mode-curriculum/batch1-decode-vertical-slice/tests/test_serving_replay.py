"""Replay acceptance and stale-artifact rejection without requiring CUDA."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from replay_serving_comparison import conclusions, prepare_output


class ServingReplayTests(unittest.TestCase):
    def test_each_performance_direction_is_required(self):
        runs = []
        for rate in (16, 48):
            for mode, goodput, latency in (
                ('native_microbatch', 4, 1700),
                ('graph_microbatch', 16, 226),
                ('graph_continuous', 26, 175),
            ):
                for _ in range(3):
                    runs.append(dict(mode=mode, offered_rate=rate, summary={
                        'goodput_requests_per_s': goodput,
                        'completion_p95_ms': latency}))
        report = {'runs': runs}
        self.assertTrue(all(conclusions(report).values()))
        for rate, metric, value, expected in (
            (48, 'goodput_requests_per_s', 16, 'high_rate_goodput'),
            (16, 'completion_p95_ms', 226, 'low_rate_tail_latency'),
        ):
            changed = copy.deepcopy(report)
            for run in changed['runs']:
                if run['mode'] == 'graph_continuous' and run['offered_rate'] == rate:
                    run['summary'][metric] = value
            self.assertFalse(conclusions(changed)[expected])

    def test_stale_results_cannot_be_reused(self):
        for name in ('serving-comparison.json', 'serving-reproduction.json', 'serving-replay.log'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp)
                (output / 'command-0.log').write_text('earlier harness tests are allowed')
                prepare_output(output)
                stale = output / name
                stale.write_text('old evidence')
                with self.assertRaisesRegex(ValueError, 'already exists'):
                    prepare_output(output)
                self.assertEqual(stale.read_text(), 'old evidence')


if __name__ == '__main__':
    unittest.main()
