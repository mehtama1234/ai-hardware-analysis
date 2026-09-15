#!/usr/bin/env python3
"""Reject zero selected-box counts when the full cell contains violations."""

import unittest
from audit_converter_layout_drc import parse_full_cell_drc
from build_active_converter_macro_candidate import parse_drc


class DrcChecks(unittest.TestCase):
    def test_error_tiles_override_zero_summary(self):
        self.assertEqual(parse_drc("Cell macro has 1266 error tiles.\nTotal DRC errors found: 0"),1266)

    def test_detailed_rules_block_pass(self):
        result=parse_full_cell_drc("Total DRC errors found: 0\nDRC_RULE\tMetal overlap rule\t12\nDRC_AUDIT_COMPLETE\n")
        self.assertEqual(result["rule_region_count"],12)
        self.assertFalse(result["drc_pass"])

    def test_missing_completion_cannot_pass(self):
        self.assertFalse(parse_full_cell_drc("Total DRC errors found: 0")["drc_pass"])

    def test_completed_empty_full_cell_report(self):
        self.assertTrue(parse_full_cell_drc("DRC_AUDIT_COMPLETE\n")["drc_pass"])


if __name__ == '__main__': unittest.main()
