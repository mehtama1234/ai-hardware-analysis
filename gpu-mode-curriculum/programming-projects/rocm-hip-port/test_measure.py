import json
from pathlib import Path
import tempfile
import unittest
import sys
from unittest.mock import patch
from subprocess import CompletedProcess

import measure


class MeasurementTests(unittest.TestCase):
    def test_generator_preserves_native_source_and_readiness_boundary(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
        import build_gpu_programming_projects as builder
        project = next(p for p in builder.PROJECT_QUERIES if p["id"] == "rocm-hip-port")
        self.assertEqual(builder.SOURCE_TEMPLATES["kernel.hip.cpp"],
                         Path(__file__).with_name("kernel.hip.cpp").read_text())
        code = builder.measure_text(project, {"matched_bottleneck_class": "rocm-hip-portability"})
        with tempfile.TemporaryDirectory() as directory:
            namespace = {"__name__": "generated_measure", "__file__": str(Path(directory) / "measure.py")}
            exec(compile(code, "generated_measure.py", "exec"), namespace)
            payload = json.dumps({"status": "ready", "source": "kernel.hip.cpp"})
            with patch.object(measure.subprocess, "run", return_value=CompletedProcess([], 0, payload, "")):
                self.assertEqual(namespace["main"](), 0)
            report = json.loads((Path(directory) / "measurements.json").read_text())
            self.assertEqual(report["correctness"]["status"], "not_executed")
            self.assertFalse(report["gpu_execution_accepted"])

    def test_readiness_is_not_numerical_correctness(self):
        for status in ("ready", "source-only"):
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "measurements.json"
                payload = json.dumps({"status": status, "source": "kernel.hip.cpp"})
                with patch.object(measure, "OUT", output), patch.object(measure.subprocess, "run",
                        return_value=CompletedProcess([], 0, payload, "")):
                    self.assertEqual(measure.main(), 0)
                report = json.loads(output.read_text())
                self.assertEqual(report["correctness"]["status"], "not_executed")
                self.assertFalse(report["gpu_execution_accepted"])
                self.assertFalse(report["measured"])

    def test_bad_metadata_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(measure, "OUT", Path(directory) / "result.json"), \
                 patch.object(measure.subprocess, "run", return_value=CompletedProcess([], 0, "{}", "")):
                self.assertEqual(measure.main(), 1)


if __name__ == "__main__":
    unittest.main()
