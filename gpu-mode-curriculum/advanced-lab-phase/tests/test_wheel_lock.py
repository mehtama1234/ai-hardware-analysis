import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from build_cpu_wheel_lock import inspect_wheel, build_lock


class WheelLockTests(unittest.TestCase):
    def wheel(self, directory, dependency="", metadata_name="example"):
        path = directory / "example-1.0-py3-none-any.whl"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("example-1.0.dist-info/METADATA", f"Name: {metadata_name}\nVersion: 1.0\n{dependency}")
        return path

    def test_hash_changes_with_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            path = self.wheel(directory)
            first = inspect_wheel(path)["sha256"]
            self.wheel(directory, "Summary: changed\n")
            self.assertNotEqual(first, inspect_wheel(path)["sha256"])

    def test_incomplete_dependency_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            pins = directory / "pins.txt"
            pins.write_text("example==1.0\n")
            self.wheel(directory)
            lock, manifest = build_lock(directory, pins)
            self.assertIn("--hash=sha256:", lock)
            self.assertEqual(len(manifest), 1)
            self.wheel(directory, "Requires-Dist: missing>=1\n")
            with self.assertRaises(ValueError):
                build_lock(directory, pins)

    def test_wrong_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                inspect_wheel(self.wheel(Path(directory), metadata_name="wrong"))
