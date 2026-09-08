import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_cpu_correctness import OPERATIONS, validate_rank_reports


def reports():
    # Literal vectors, independent of the validator's formula construction.
    arrays = [
        [[100,102,104,106,108,110,112,114],
         [0,1,2,3,4,5,6,7,100,101,102,103,104,105,106,107],
         [100,102,104,106,108,110,112,114],
         [0,1,2,3,100,101,102,103], [100,101,102,103,104,105,106,107]],
        [[100,102,104,106,108,110,112,114],
         [0,1,2,3,4,5,6,7,100,101,102,103,104,105,106,107],
         [116,118,120,122,124,126,128,130],
         [4,5,6,7,104,105,106,107], [100,101,102,103,104,105,106,107]],
    ]
    return [{"rank": rank, "rows": [
        {"operation": name, "status": "passed", "actual": list(values), "expected": list(values)}
        for name, values in zip(OPERATIONS, arrays[rank])]} for rank in range(2)]


class CollectiveReportTests(unittest.TestCase):
    def test_matching_but_wrong_output_rejected(self):
        data = reports()
        data[0]["rows"][0].update(actual=[0] * 8, expected=[0] * 8)
        with self.assertRaises(ValueError):
            validate_rank_reports(data)
        data = reports()
        data[0]["rank"] = False
        with self.assertRaises(ValueError):
            validate_rank_reports(data)

    def test_valid_report_contract(self):
        validate_rank_reports(reports())

    def test_rank_and_operation_coverage(self):
        for mutation in (lambda r: r.pop(),
                         lambda r: r[1].update(rank=0),
                         lambda r: r[0]["rows"].pop(),
                         lambda r: r[0]["rows"][0].update(operation="broadcast")):
            data = reports()
            mutation(data)
            with self.assertRaises(ValueError):
                validate_rank_reports(data)

    def test_bad_outputs_fail(self):
        for value in (float("nan"), float("inf"), True, "1", -123):
            data = reports()
            data[0]["rows"][0]["actual"][0] = value
            with self.assertRaises(ValueError):
                validate_rank_reports(data)
        data = reports()
        data[0]["rows"][0]["status"] = "skipped"
        with self.assertRaises(ValueError):
            validate_rank_reports(data)

    def test_matching_malformed_arrays_fail(self):
        for values in ([], [float("inf")] * 8, [True] * 8):
            data = reports()
            data[0]["rows"][0].update(actual=values, expected=copy.copy(values))
            with self.assertRaises(ValueError):
                validate_rank_reports(data)


if __name__ == "__main__":
    unittest.main()
