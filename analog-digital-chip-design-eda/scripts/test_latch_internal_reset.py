import unittest
from types import SimpleNamespace
from audit_isolated_latch_connectivity import audit_substrate_capacitance
from build_combined_latch_receiver import geometry


class InternalResetTests(unittest.TestCase):
    def test_equalizer_is_opt_in_and_has_a_separate_port(self):
        latch="magic\ntech sky130A\n<< end >>\n"
        receiver="magic\ntech sky130A\nmagscale 1 2\n<< end >>\n"
        self.assertNotIn("eq_reset",geometry(latch,receiver))
        candidate=geometry(latch,receiver,True)
        self.assertIn("port 16 nsew",candidate)
        self.assertIn("0 eq_reset",candidate)
        self.assertIn("rect -600 4000 600 4240",candidate)

    def test_missing_internal_capacitance_fails_export_audit(self):
        ext=SimpleNamespace(read_text=lambda:'scale 1 1 1\nnode "latch_sense_p" 0 1000\nnode "latch_sense_n" 0 2000\n')
        def audit(text):
            return audit_substrate_capacitance(ext,SimpleNamespace(read_text=lambda:text),
                                               ("latch_sense_p","latch_sense_n"))
        self.assertTrue(audit("C0 latch_sense_p vss 1f\nC1 latch_sense_n vss 2f\n")["pass"])
        self.assertFalse(audit("C0 latch_sense_p vss 1f\n")["pass"])


if __name__=="__main__":
    unittest.main()
