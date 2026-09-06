#!/usr/bin/env python3
"""Negative controls for the topology acceptance boundary."""
from pathlib import Path
import tempfile
import unittest

from audit_isolated_latch_connectivity import audit, audit_substrate_capacitance

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_isolated_latch_v2_reference.spice"


class ConnectivityTests(unittest.TestCase):
    def test_missing_exported_output_cap_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            ext = Path(directory) / "cell.ext"
            spice = Path(directory) / "cell.spice"
            ext.write_text('scale 1000 1 500000\nnode "out_p" 0 15000\nnode "out_n" 0 16000\n')
            spice.write_text('C0 out_p vss 15f\n')
            self.assertFalse(audit_substrate_capacitance(ext, spice)["pass"])
            spice.write_text('C0 out_p vss 15f\nC1 vss out_n 16f\n')
            self.assertTrue(audit_substrate_capacitance(ext, spice)["pass"])

    def check_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.spice"
            path.write_text(text)
            return audit(path)

    def test_reference_and_source_drain_reversal(self):
        original = REFERENCE.read_text()
        for text in (original, original.replace("Xiso_p latch_sense_p sense_p iso_tail", "Xiso_p iso_tail sense_p latch_sense_p")):
            result = self.check_text(text)
            self.assertTrue(result["topology_pass"])
            self.assertTrue(result["body_ties_pass"])

    def test_merged_outputs_are_rejected(self):
        result = self.check_text(REFERENCE.read_text().replace("out_n", "out_p"))
        self.assertFalse(result["topology_pass"])

    def test_wrong_input_gate_is_rejected(self):
        result = self.check_text(REFERENCE.read_text().replace("Xsense_n out_n latch_sense_n", "Xsense_n out_n out_p"))
        self.assertFalse(result["topology_pass"])

    def test_floating_body_is_rejected(self):
        result = self.check_text(REFERENCE.read_text().replace("iso_tail vss sky130", "iso_tail floating_bulk sky130"))
        self.assertTrue(result["topology_pass"])
        self.assertFalse(result["body_ties_pass"])

    def test_recovered_candidate_is_rejected(self):
        path = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_isolated_frontend_active_load_latch_extracted.spice"
        result = audit(path)
        self.assertFalse(result["topology_pass"])


if __name__ == "__main__":
    unittest.main()
