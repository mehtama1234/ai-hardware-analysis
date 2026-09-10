import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_real_training import validate


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/real-data-cpu-smoke-01/real-training.json'


class TrainingReportVerifierTests(unittest.TestCase):
    def test_historical_smoke_is_valid(self):
        report = json.loads(REPORT.read_text())
        self.assertEqual(validate(report, REPORT.parent, ROOT / 'data'), [])

    def test_manifest_drift_and_unmatched_offsets_are_rejected(self):
        report = json.loads(REPORT.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for source in (REPORT.parent / 'sources').rglob('*'):
                if source.is_file():
                    target = directory / 'sources' / source.relative_to(REPORT.parent / 'sources')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
            data = copy.deepcopy(report)
            data['data_manifest_sha256'] = '0' * 64
            data['runs'][1]['training_starts'] = [999]
            errors = validate(data, directory, ROOT / 'data')
            self.assertIn('manifest checksum', errors)
            self.assertIn('7: unmatched training samples', errors)

    def test_step_loss_corruption_is_rejected(self):
        report = json.loads(REPORT.read_text())
        report['runs'][0]['steps'][0]['loss'] = float('nan')
        errors = validate(report, REPORT.parent, ROOT / 'data')
        self.assertTrue(any('finite step' in error for error in errors))

    def test_malformed_protocol_is_rejected_without_traceback(self):
        report = json.loads(REPORT.read_text())
        report['protocol'] = 'parity protocol string'
        errors = validate(report, REPORT.parent, ROOT / 'data')
        self.assertIn('protocol fields missing', errors)


if __name__ == '__main__':
    unittest.main()
