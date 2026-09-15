#!/usr/bin/env python3
"""Ensure hypothetical wiring cannot become the latest physical transient."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import import_physical_converter_gate as gate


class SelectionChecks(unittest.TestCase):
    def test_newer_hypothetical_result_does_not_replace_extracted_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, kind in (("001", "extracted_netlist_transient"), ("002", "hypothetical_netlist_reconnection")):
                (root/name).mkdir()
                (root/name/"result.json").write_text(json.dumps({"evidence_kind":kind,"status":name,"accepted_converter":False}))
            with patch.object(gate, "DEFAULT_ACTIVE_MACRO_TRANSIENT_ROOT", root):
                result = gate.latest_active_macro_transient()
                self.assertEqual(result["status"], "001")
                self.assertFalse(result["accepted_converter"])

    def test_only_hypothetical_results_leave_physical_evidence_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"001").mkdir()
            (root/"001/result.json").write_text(json.dumps({"evidence_kind":"hypothetical_netlist_reconnection"}))
            with patch.object(gate, "DEFAULT_ACTIVE_MACRO_TRANSIENT_ROOT", root):
                self.assertIsNone(gate.latest_active_macro_transient())


if __name__ == "__main__":
    unittest.main()
