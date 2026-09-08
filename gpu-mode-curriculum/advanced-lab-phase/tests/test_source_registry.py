import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from verify_source_registry import validate


class SourceRegistryTests(unittest.TestCase):
    def test_registry_has_all_handbook_topics(self):
        path = Path(__file__).resolve().parents[1] / "source-registry.json"
        errors = validate(json.loads(path.read_text()))
        self.assertEqual(errors, [])

    def test_missing_topic_is_rejected(self):
        path = Path(__file__).resolve().parents[1] / "source-registry.json"
        data = json.loads(path.read_text())
        data["topics"] = data["topics"][:-1]
        self.assertTrue(validate(data))
