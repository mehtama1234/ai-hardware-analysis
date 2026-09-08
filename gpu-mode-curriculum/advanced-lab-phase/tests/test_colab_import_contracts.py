import json
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
GPU_RUNS = ROOT / "gpu-runs"
sys.path.insert(0, str(GPU_RUNS))

from gpu_runs.import_linter import _lint_run, promotion_step_ids  # noqa: E402


class ColabImportContractTests(unittest.TestCase):
    def test_trained_end_to_end_mode_is_exposed_by_both_handoff_entrypoints(self):
        local = (ROOT / "scripts" / "run_colab_gpu_handoff_local.sh").read_text(encoding="utf-8")
        remote = (ROOT / "scripts" / "run_colab_gpu_handoff.py").read_text(encoding="utf-8")
        self.assertIn('"trained-e2e"', local)
        self.assertIn('mode == "trained-e2e"', remote)
        self.assertIn("run_serving_bridge.py", remote)
        self.assertIn("run_serving_tail_load_cuda.py", remote)
        self.assertIn("--trained", remote)

    def test_linter_uses_promotion_manifest_and_accepts_partial_scope(self):
        step_ids = promotion_step_ids()
        self.assertIn("tensor-core-gemm", step_ids)
        self.assertIn("eager-kernel-suite-cuda", step_ids)
        run = {
            "run_id": "synthetic-colab-contract",
            "generated_at": "2026-09-08T00:00:00Z",
            "provenance": {"kind": "real-measured", "measured": True},
            "host": {"name": "Google Colab", "vendor": "NVIDIA", "cuda_available": True},
            "promotion_steps": [{
                "id": "eager-kernel-suite-cuda",
                "status": "partial:matmul-only",
                "evidence": ["fixture.json"],
                "metrics": {"rows": 1},
            }],
        }
        result = _lint_run("import", ROOT / "gpu-runs" / "imports" / "synthetic.json", run, step_ids)
        self.assertEqual(result["errors"], [])

    def test_promoted_index_records_missing_colab_artifact(self):
        path = ROOT / "gpu-runs" / "imports" / "colab-t4-promoted.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        missing = {row["id"]: row["status"] for row in report.get("missing_artifacts", [])}
        self.assertNotIn("serving-tail-load-cuda", missing)
        self.assertTrue(any(row.get("id") == "serving-tail-load-cuda" for row in report.get("promotion_steps", [])))


if __name__ == "__main__":
    unittest.main()
