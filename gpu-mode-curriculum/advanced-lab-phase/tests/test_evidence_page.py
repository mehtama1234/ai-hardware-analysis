import sys
import unittest
import hashlib
import json
import tempfile
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.build_executable_evidence_page import render_experiment, checkpoint_current


class EvidencePageTests(unittest.TestCase):
    def test_stale_metrics_not_rendered(self):
        page = render_experiment("example", "example.json", {"rows": [{"accuracy": 0.999}]}, ["stale source"])
        self.assertIn("Not current", page)
        self.assertNotIn("0.999", page)

    def test_escape_report_values(self):
        page = render_experiment("<script>", "x.json", {"scope": "<script>alert(1)</script>", "rows": []}, [])
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_missing_checkpoint_not_current(self):
        self.assertFalse(checkpoint_current({}))

    def test_changed_tests_invalidate_checkpoint(self):
        with patch("scripts.build_executable_evidence_page.test_source_hashes", return_value={"test.py": "new"}):
            self.assertFalse(checkpoint_current({"test_sources_unchanged_during_run": True,
                                                 "test_source_sha256": {"test.py": "old"}}))

    def test_source_change_and_missing_artifact_invalidate_checkpoint(self):
        from scripts import build_executable_evidence_page as page
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            runner = root / "scripts/run_advanced_evidence_regression.py"
            runner.write_text("# runner\n")
            source = root / "candidate.py"
            source.write_text("# original\n")
            artifact = root / "result.json"
            artifact.write_text(json.dumps({"provenance": {"source_sha256": {
                "candidate.py": hashlib.sha256(source.read_bytes()).hexdigest()}}}))
            step = {"name": "experiment", "artifact": "result.json",
                    "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}
            report = {"test_sources_unchanged_during_run": True, "test_source_sha256": {},
                      "steps": [step], "runner_source_sha256": hashlib.sha256(runner.read_bytes()).hexdigest()}
            original_checker = page.check_source_hashes
            with patch.object(page, "ROOT", root), patch.object(page, "REPO", root), \
                 patch.object(page, "tasks", return_value=[("experiment", [], "result.json")]), \
                 patch.object(page, "test_source_hashes", return_value={}), \
                 patch.object(page, "check_source_hashes", side_effect=lambda a: original_checker(a, root)):
                self.assertTrue(checkpoint_current(report))
                source.write_text("# changed\n")
                self.assertFalse(checkpoint_current(report))
                source.write_text("# original\n")
                del step["artifact"]
                self.assertFalse(checkpoint_current(report))
