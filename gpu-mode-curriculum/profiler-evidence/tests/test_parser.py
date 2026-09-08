from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from profiler_evidence.parser import classify, parse_nsight_compute


class ProfilerParserTests(unittest.TestCase):
    def test_missing_counter_is_preserved_and_not_classified_as_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["kernel", "duration_us", "dram_util_pct", "sm_util_pct",
                                                             "tensor_util_pct", "l2_hit_pct", "launches", "bytes", "flops"])
                writer.writeheader()
                writer.writerow({"kernel": "partial", "duration_us": "10", "dram_util_pct": "90",
                                 "sm_util_pct": "20", "tensor_util_pct": "", "l2_hit_pct": "40",
                                 "launches": "1", "bytes": "100", "flops": "200"})
            row = parse_nsight_compute(path)[0]
            self.assertIsNone(row.metrics["tensor_util_pct"])
            self.assertEqual(classify(row), "insufficient-data")

    def test_complete_counter_row_can_be_classified(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "complete.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["kernel", "duration_us", "dram_util_pct", "sm_util_pct",
                                                             "tensor_util_pct", "l2_hit_pct", "launches", "bytes", "flops"])
                writer.writeheader()
                writer.writerow({"kernel": "memory", "duration_us": "10", "dram_util_pct": "90",
                                 "sm_util_pct": "20", "tensor_util_pct": "5", "l2_hit_pct": "40",
                                 "launches": "1", "bytes": "100", "flops": "200"})
            row = parse_nsight_compute(path)[0]
            self.assertEqual(classify(row), "memory-bandwidth")


if __name__ == "__main__":
    unittest.main()
