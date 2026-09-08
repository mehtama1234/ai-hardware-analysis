import sys
import threading
from pathlib import Path
import unittest


SERVING = Path(__file__).resolve().parents[3] / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
CUDA_RUNNER = Path(__file__).resolve().parents[1] / "run_serving_tail_load_cuda.py"
sys.path.insert(0, str(CUDA_RUNNER.parent))

from admission import AdmissionController  # noqa: E402
from microbatch import MicroBatchScheduler  # noqa: E402
import server  # noqa: E402
from run_serving_tail_load_cuda import tail_report_contract  # noqa: E402


class FakeGenerator:
    backend = "fake"

    def encode(self, prompt):
        return list(prompt)

    def complete(self, prompt, max_tokens):
        return {"text": prompt.upper(), "generated_tokens": max_tokens, "backend": self.backend}

    def complete_batch(self, prompts, max_tokens):
        return {
            "choices": [{"text": prompt.upper()} for prompt in prompts],
            "batch_mode": "vectorized",
            "backend": self.backend,
        }


class ServingControlTests(unittest.TestCase):
    def test_cuda_tail_report_contract_requires_device_events_and_parity(self):
        report = {
            "status": "passed", "measured": True,
            "concurrency_levels": [1], "requests_per_level": 2,
            "rows": [{
                "concurrency": 1, "accepted": 2, "rejected": 0,
                "output_parity": True, "batch_modes": ["vectorized"],
                "backend_labels": ["neural-microbatch-decode"],
                "cuda_event_ms": 1.5,
                "latency_ms": {"p50": 2.0, "p95_nearest_rank": 3.0, "max": 4.0},
            }],
            "scheduler": {"rejected_count": 0, "cancelled_count": 0},
        }
        self.assertTrue(tail_report_contract(report))
        report["rows"][0].pop("cuda_event_ms")
        self.assertFalse(tail_report_contract(report))

    def test_cuda_tail_report_contract_rejects_unavailable_or_incomplete_rows(self):
        self.assertFalse(tail_report_contract({"status": "unavailable:cuda-runtime"}))
        self.assertFalse(tail_report_contract({
            "status": "passed", "measured": True,
            "concurrency_levels": [1], "requests_per_level": 2,
            "rows": [{"concurrency": 1, "accepted": 2, "rejected": 0,
                       "output_parity": True, "batch_modes": ["scalar"],
                       "backend_labels": ["neural-microbatch-decode"],
                       "cuda_event_ms": 1.0,
                       "latency_ms": {"p50": 2.0, "p95_nearest_rank": 3.0, "max": 4.0}}],
            "scheduler": {"rejected_count": 0, "cancelled_count": 0},
        }))

    def test_request_validation_is_bounded(self):
        self.assertEqual(server.validate_request({"prompt": "hello", "max_tokens": 4}, batch=False), (["hello"], 4))
        with self.assertRaises(ValueError):
            server.validate_request({"prompt": "", "max_tokens": 4}, batch=False)
        with self.assertRaises(ValueError):
            server.validate_request({"prompts": ["hello"], "max_tokens": 129}, batch=True)

    def test_admission_rejects_without_waiting_when_queue_is_full(self):
        admission = AdmissionController(capacity=1, queue_limit=0)
        lease = admission.acquire()
        self.assertIsNotNone(lease)
        try:
            self.assertIsNone(admission.acquire(timeout=0.01))
            self.assertEqual(admission.snapshot()["active"], 1)
        finally:
            admission.release()
        self.assertEqual(admission.snapshot()["active"], 0)

    def test_microbatch_groups_compatible_requests_and_preserves_results(self):
        scheduler = MicroBatchScheduler(FakeGenerator(), max_batch=2, window_ms=20, max_pending=4)
        try:
            first = scheduler.submit("aa", 3)
            second = scheduler.submit("bb", 3)
            third = scheduler.submit("c", 3)
            self.assertEqual(first.result(timeout=2)["text"], "AA")
            self.assertEqual(second.result(timeout=2)["text"], "BB")
            self.assertEqual(third.result(timeout=2)["text"], "C")
            batches = scheduler.snapshot()["batches"]
            self.assertEqual(sum(row["size"] for row in batches), 3)
            self.assertIn("vectorized", [row["mode"] for row in batches])
        finally:
            scheduler.close()

    def test_microbatch_queue_is_bounded(self):
        started = threading.Event()
        unblock = threading.Event()

        class SlowGenerator(FakeGenerator):
            def complete(self, prompt, max_tokens):
                started.set()
                unblock.wait(timeout=2)
                return super().complete(prompt, max_tokens)

        scheduler = MicroBatchScheduler(SlowGenerator(), max_batch=1, window_ms=0, max_pending=1)
        try:
            first = scheduler.submit("a", 1)
            self.assertTrue(started.wait(timeout=2))
            second = scheduler.submit("b", 1)
            with self.assertRaises(Exception):
                scheduler.submit("c", 1)
            unblock.set()
            first.result(timeout=2)
            second.result(timeout=2)
        finally:
            scheduler.close()


if __name__ == "__main__":
    unittest.main()
