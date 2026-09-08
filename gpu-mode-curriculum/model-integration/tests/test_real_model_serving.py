import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "model-integration/reports/real-model-serving-cpu.json"


class RealModelServingReportTests(unittest.TestCase):
    def test_committed_real_model_report_is_scoped_and_hash_current(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")
        self.assertTrue(report["measured"])
        self.assertTrue(report["local_files_only"])
        self.assertGreaterEqual(report["model_parameters"], 100_000_000)
        self.assertGreaterEqual(report["quality"]["accuracy"], 0.50)
        http_rows = report["http_direct"] + report["http_microbatch"]
        self.assertGreaterEqual(len(http_rows), 5)
        self.assertTrue(all(row["output_parity"] for row in http_rows))
        self.assertTrue(any(row["mode"] == "microbatch" for row in http_rows))
        self.assertEqual(report["cancellation"]["mode"], "boundary-only")
        self.assertFalse(report["cancellation"]["inflight_interruption_proven"])
        for relative, expected in report["source_sha256"].items():
            path = ROOT.parent / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, relative)


if __name__ == "__main__":
    unittest.main()
