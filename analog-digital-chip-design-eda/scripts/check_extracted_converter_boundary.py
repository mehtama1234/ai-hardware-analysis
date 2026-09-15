#!/usr/bin/env python3
"""Prevent intermediate aliases from masquerading as final connectivity."""

import unittest

from audit_extracted_converter_boundary import audit
from run_active_converter_macro_extracted_transient import measure


class BoundaryChecks(unittest.TestCase):
    def test_supply_measurements_do_not_match_name_suffixes(self):
        log = "supply_charge_c = -1e-15\nactive_supply_charge_c = -2e-13\n"
        self.assertEqual(measure(log, "supply_charge_c"), -1e-15)
        self.assertEqual(measure(log, "active_supply_charge_c"), -2e-13)
        self.assertIsNone(measure(log, "charge_c"))

    def test_connected_pair_allows_drain_source_reversal(self):
        text = """.subckt test row_drive sar_comparator_input
+ latch_sense_p_ext latch_sense_n_ext preamp_iso_tail_ext vss_escape
X0 latch_sense_p_ext row_drive preamp_iso_tail_ext vss_escape sky130_fd_pr__nfet_01v8 w=1 l=1
X1 preamp_iso_tail_ext sar_comparator_input latch_sense_n_ext vss_escape sky130_fd_pr__nfet_01v8 w=1 l=1
.ends
"""
        self.assertTrue(audit(text)["physical_preamp_routing_complete"])
        self.assertFalse(audit(text.replace("row_drive preamp_iso_tail_ext", "floating_gate preamp_iso_tail_ext"))["physical_preamp_routing_complete"])
        self.assertFalse(audit(text.replace("latch_sense_n_ext vss_escape sky130", "floating_output vss_escape sky130"))["physical_preamp_routing_complete"])

    def test_absent_and_hierarchical_views_are_unverified(self):
        self.assertFalse(audit("")["physical_preamp_routing_complete"])
        self.assertFalse(audit("X0 input output custom_preamp")["physical_preamp_routing_complete"])


if __name__ == "__main__":
    unittest.main()
