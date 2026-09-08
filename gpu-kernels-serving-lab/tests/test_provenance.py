import hashlib
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.provenance import source_provenance, loaded_local_sources


class ProvenanceTests(unittest.TestCase):
    def test_imported_helper_captured_without_explicit_listing(self):
        path = Path(__file__).resolve()
        with patch.dict(sys.modules, {"_local_helper_test": SimpleNamespace(__file__=str(path))}), \
             patch("common.provenance.subprocess.run", side_effect=FileNotFoundError):
            result = source_provenance(path.parent, [])
        self.assertIn(path.name, result["source_sha256"])
        self.assertIn(path.name, result["imported_source_files"])

    def test_external_modules_excluded(self):
        root = Path(__file__).resolve().parent
        self.assertTrue(all(path.is_relative_to(root) for path in loaded_local_sources(root)))

    def test_hash_and_missing_git(self):
        path = Path(__file__).resolve()
        with patch("common.provenance.subprocess.run", side_effect=FileNotFoundError):
            result = source_provenance(path.parent, [path])
        self.assertIsNone(result["git_revision"])
        self.assertIsNone(result["worktree_dirty"])
        self.assertEqual(result["source_sha256"][path.name], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_outside_root_rejected(self):
        with self.assertRaises(ValueError):
            source_provenance(Path(__file__).resolve().parent, [Path(__file__).resolve().parents[1] / "common/bench.py"])
