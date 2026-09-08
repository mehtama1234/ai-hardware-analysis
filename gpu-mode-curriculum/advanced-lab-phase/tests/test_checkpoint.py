import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from run_advanced_evidence_regression import check_source_hashes, tasks, test_source_hashes


class CheckpointTests(unittest.TestCase):
    def test_primitive_suite_and_implementation_are_tracked(self):
        registered = {name: args for name, args, _ in tasks()}
        self.assertIn("primitive-reference-tests", registered)
        hashes = test_source_hashes()
        self.assertIn("gpu-mode-curriculum/parallel-primitives/tests/test_reference.py", hashes)
        self.assertIn("gpu-mode-curriculum/parallel-primitives/parallel_primitives/reference.py", hashes)

    def test_current_hash(self):
        path = Path(__file__).resolve()
        artifact = {"provenance": {"source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}}}
        self.assertEqual(check_source_hashes(artifact, path.parent), [])
        artifact["provenance"]["source_sha256"][path.name] = "stale"
        self.assertTrue(check_source_hashes(artifact, path.parent))

    def test_top_level_source_hash_schema(self):
        path = Path(__file__).resolve()
        artifact = {"source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}}
        self.assertEqual(check_source_hashes(artifact, path.parent), [])
        artifact["source_sha256"][path.name] = "stale"
        self.assertTrue(check_source_hashes(artifact, path.parent))

    def test_missing_and_escaping_sources(self):
        for hashes in ({}, {"missing-file.py": "abc"}, {"../../outside": "abc"}):
            self.assertTrue(check_source_hashes({"provenance": {"source_sha256": hashes}}, Path(__file__).parent))
