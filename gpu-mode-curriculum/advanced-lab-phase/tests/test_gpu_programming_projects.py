import sys
from pathlib import Path
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from verify_gpu_programming_projects import correctness_is_acceptable  # noqa: E402


class GPUProgrammingProjectContractTests(unittest.TestCase):
    def test_passed_measurement_is_acceptable(self):
        self.assertTrue(correctness_is_acceptable({"correctness": {"status": "passed"}}))

    def test_explicit_unavailable_measurement_is_acceptable(self):
        self.assertTrue(correctness_is_acceptable({
            "correctness": {"status": "not_executed"},
            "measured": False,
            "gpu_execution_accepted": False,
            "runtime_readiness": {"status": "source-only"},
        }))

    def test_unclassified_skip_is_rejected(self):
        self.assertFalse(correctness_is_acceptable({
            "correctness": {"status": "not_executed"},
            "measured": True,
            "gpu_execution_accepted": False,
            "runtime_readiness": {"status": "source-only"},
        }))


if __name__ == "__main__":
    unittest.main()
