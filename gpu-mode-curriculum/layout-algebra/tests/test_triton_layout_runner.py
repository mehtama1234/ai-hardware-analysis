import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "run_triton_layout_cuda.py"
spec = importlib.util.spec_from_file_location("triton_layout_runner", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TritonLayoutRunnerTests(unittest.TestCase):
    def test_source_hashes_include_both_layout_sources(self):
        hashes = module.source_hashes()
        self.assertEqual(len(hashes), 2)
        self.assertTrue(all(len(value) == 64 for value in hashes.values()))


if __name__ == "__main__":
    unittest.main()
