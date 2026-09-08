import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kernel_benchmarks.harness import validate


class ChecksumTests(unittest.TestCase):
    def test_nonfinite_and_nonnumeric_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), True, "1", None):
            with self.subTest(value=value):
                self.assertFalse(validate({"result": {"checksum": value}},
                                          ["checksum"])["checksum_finite"])

    def test_finite_accepted(self):
        for value in (0, -2, 1.25):
            self.assertTrue(validate({"result": {"checksum": value}},
                                     ["checksum"])["checksum_finite"])


if __name__ == "__main__":
    unittest.main()
