import copy
import subprocess
import unittest
from unittest.mock import patch
import run_native


class NativeTests(unittest.TestCase):
    def payload(self):
        return {"status": "passed", "warmup": 3, "launches_per_sample": 100,
                "rows": [{"n": n, "max_abs_error": 0.0, "samples_ms": [0.01] * 7}
                         for n in (1, 255, 256, 257, 65539)]}

    def test_valid_and_corrupt_results(self):
        good = self.payload()
        self.assertTrue(run_native.validated(good))
        for bad in (float("nan"), float("inf"), -1, True, "0.1"):
            payload = copy.deepcopy(good)
            payload["rows"][0]["samples_ms"][0] = bad
            self.assertFalse(run_native.validated(payload))
        for field, value in (("n", 2), ("max_abs_error", .01), ("samples_ms", [])):
            payload = copy.deepcopy(good)
            payload["rows"][0][field] = value
            self.assertFalse(run_native.validated(payload))

    def test_missing_compiler(self):
        with patch.object(run_native.shutil, "which", return_value=None):
            result = run_native.run()
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["gpu_execution_accepted"])

    def test_compile_timeout(self):
        with patch.object(run_native, "source_provenance", return_value={}), \
             patch.object(run_native.shutil, "which", return_value="hipcc"), \
             patch.object(run_native.subprocess, "run", side_effect=subprocess.TimeoutExpired("hipcc", 120)):
            result = run_native.run()
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["gpu_execution_accepted"])


if __name__ == "__main__":
    unittest.main()
