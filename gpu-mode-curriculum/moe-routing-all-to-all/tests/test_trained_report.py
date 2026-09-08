import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_trained_task import PROTOCOL
from verify_trained_task import validate


def fixture():
    return {"protocol": copy.deepcopy(PROTOCOL), "status": "passed",
            "gpu_execution_accepted": False, "test_targets": [[0.]] * 256,
            "dense_linear_test_mse": 1., "rows": [
                {"seed": seed, "status": "passed", "test_predictions": [[0.]] * 256,
                 "test_mse": 0., "ratio_to_dense_linear": 0., "train_losses": [0.] * 200,
                 "offered_loads": [256, 256, 0, 0], "dropped_assignments": 0}
                for seed in PROTOCOL["model_seeds"]]}


class TrainedReportTests(unittest.TestCase):
    def test_valid_contract(self):
        validate(fixture())

    def test_inconsistent_metrics_and_arrays_rejected(self):
        for change in (lambda r: r["rows"][0].update(test_mse=0.01),
                       lambda r: r["rows"][0]["test_predictions"].pop(),
                       lambda r: r["rows"][0]["test_predictions"].__setitem__(0, [float("nan")]),
                       lambda r: r["rows"][0]["train_losses"].pop(),
                       lambda r: r["rows"][0].update(offered_loads=[0, 0, 0, 0])):
            report = fixture()
            change(report)
            with self.assertRaises(ValueError):
                validate(report)

    def test_missing_seed_and_changed_protocol_rejected(self):
        report = fixture()
        report["rows"].pop()
        with self.assertRaises(ValueError):
            validate(report)
        report = fixture()
        report["protocol"]["max_test_mse"] = 10
        with self.assertRaises(ValueError):
            validate(report)
