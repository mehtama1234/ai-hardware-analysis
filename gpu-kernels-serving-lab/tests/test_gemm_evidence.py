import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import json
import subprocess

import torch

spec = importlib.util.spec_from_file_location("gemm_lab", Path(__file__).resolve().parents[1] /
                                              "23-gpumode-shared-memory-gemm/run.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class GemmEvidenceTests(unittest.TestCase):
    def valid_payload(self):
        payload = {"shape": [5, 7, 11]}
        for prefix, duration in (("naive", 1), ("tiled", 2), ("cublas", 0.5)):
            payload.update({f"{prefix}_ms": duration, f"{prefix}_max_abs_error": 0,
                            f"{prefix}_samples_ms": [duration] * 7})
        return payload

    def test_cuda_runner_shape_and_provenance(self):
        payload = self.valid_payload()
        with patch.object(lab.shutil, "which", return_value="/mock/nvcc"), \
             patch.object(lab, "run_cmd", side_effect=[(0, "", ""),
                                                       (0, json.dumps(payload), "")]) as run:
            result = lab.cuda_result((5, 7, 11))
        self.assertTrue(lab.cuda_passes(result))
        self.assertIn("-DGEMM_K=11", run.call_args_list[0].args[0])
        self.assertEqual(len(result["source_sha256"]), 64)
        result["kernel"]["shape"] = [256, 256, 256]
        self.assertFalse(lab.cuda_passes(result))

    def test_cuda_runner_failures(self):
        with patch.object(lab.shutil, "which", return_value="/mock/nvcc"):
            with patch.object(lab, "run_cmd", return_value=(1, "", "compile error")) as run:
                self.assertEqual(lab.cuda_result()["status"], "compile_failed")
                self.assertEqual(run.call_count, 1)
            with patch.object(lab, "run_cmd", side_effect=subprocess.TimeoutExpired(["mock"], 180)):
                self.assertFalse(lab.cuda_passes(lab.cuda_result()))
            with patch.object(lab, "run_cmd", side_effect=[(0, "", ""), (0, "[]", "")]):
                self.assertFalse(lab.cuda_passes(lab.cuda_result()))

    def test_edge_cases(self):
        rows = lab.correctness_suite()
        self.assertEqual(len(rows), 15)
        self.assertTrue(all(row["passed"] for row in rows), rows)

    def test_wrong_and_nonfinite_outputs_fail(self):
        reference = torch.zeros((2, 2), dtype=torch.float64)
        for got in (torch.ones((2, 2)), torch.zeros((1, 2)),
                    torch.full((2, 2), float("nan")), torch.full((2, 2), float("inf"))):
            self.assertFalse(lab.comparison(got, reference)["passed"])

    def test_tile_rejected(self):
        for tile in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                lab.tiled_loop(torch.ones((1, 1)), torch.ones((1, 1)), tile)

    def test_samples_and_labels(self):
        result = lab.cpu_proxy(3, 5, 7, 4)
        self.assertEqual(result["traffic_model"]["evidence_kind"], "analytical")
        for row in result["rows"]:
            self.assertEqual(len(row["samples_seconds"]), row["repeat"])
            self.assertEqual(row["evidence_kind"], "measured_cpu")
            self.assertTrue(row["correctness"]["passed"])

    def test_cuda_errors_not_accepted(self):
        for result in ({"status": "compile_failed"}, {"status": "run_failed"},
                       {"status": "ran", "kernel": {}},
                       {"status": "ran", "kernel": {"naive_max_abs_error": float("nan")}}):
            self.assertFalse(lab.cuda_passes(result))
        self.assertTrue(lab.cuda_passes({"status": "skipped"}))
        self.assertTrue(lab.cuda_passes({"status": "ran", "kernel": self.valid_payload()}))

    def test_cuda_sample_integrity(self):
        for value in ([], [1] * 6, [float("nan")] * 7, [True] * 7, [20] * 7):
            payload = self.valid_payload()
            payload["cublas_samples_ms"] = value
            self.assertFalse(lab.cuda_passes({"status": "ran", "kernel": payload}))


if __name__ == "__main__":
    unittest.main()
