#!/usr/bin/env python3
import unittest

import numpy as np

from audit_latch_terminal_voltages import device_biases, ideal_source, range_summary, validate_device_coverage, peak_gate_event


class TerminalAuditTests(unittest.TestCase):
    def test_peak_event_preserves_absolute_time_and_clock_phase(self):
        t=np.array([0,55,60])*1e-9
        zero=np.zeros(3); gate=np.array([0,2.1,1.8])
        event=peak_gate_event(t,zero,gate,zero,zero,{"capture_clk":gate},50)
        self.assertAlmostEqual(event["time_ns"],55)
        self.assertAlmostEqual(event["phase_ns"],5)
        self.assertEqual(event["coincident_controls_v"],{"capture_clk":2.1})
        summary=range_summary(gate,t,(0,1.95))
        self.assertAlmostEqual(summary["max_time_ns"],55)

    def test_capture_requires_all_four_model_families(self):
        rows=[]
        for model,count in (("nfet_01v8",17),("special_nfet_01v8",4),
                            ("pfet_01v8",7),("pfet_01v8_hvt",12)):
            rows.extend({"model":"sky130_fd_pr__"+model,"terminals":{"g":"other"}}
                        for _ in range(count))
        rows[21]["terminals"]={"d":"latch_sense_p","g":"eq_reset",
                               "s":"latch_sense_n","b":"vdd_active"}
        validate_device_coverage(rows,True,True)
        rows[-1]["model"]="sky130_fd_pr__pfet_01v8"
        with self.assertRaises(ValueError):
            validate_device_coverage(rows,True,True)
        with self.assertRaises(ValueError):
            validate_device_coverage(rows[:-1],True,True)

    def test_equalizer_requires_full_device_and_body_coverage(self):
        rows=[{"terminals":{"g":"reset"}} for _ in range(15)]
        validate_device_coverage(rows,False)
        with self.assertRaises(ValueError):
            validate_device_coverage(rows,True)
        eq={"model":"sky130_fd_pr__pfet_01v8","terminals":
            {"d":"latch_sense_p","g":"eq_reset","s":"latch_sense_n","b":"vdd_active"}}
        validate_device_coverage(rows+[eq],True)
        eq["terminals"]["b"]="vss"
        with self.assertRaises(ValueError):
            validate_device_coverage(rows+[eq],True)

    def test_orientation_is_explicit_and_normalization_is_symmetric(self):
        d,g,s,b=[np.array(x) for x in ([0.0,1.8],[0.9,0.9],[1.8,0.0],[0.0,0.0])]
        self.assertEqual(device_biases(d,g,s,b,"nfet")["vds"].tolist(),[-1.8,1.8])
        for kind in ("nfet","pfet"):
            a=device_biases(d,g,s,b,kind,True)
            swapped=device_biases(s,g,d,b,kind,True)
            for key in a:
                np.testing.assert_array_equal(a[key],swapped[key])

    def test_reverse_gate_bias_is_not_hidden_by_magnitude_check(self):
        result=range_summary(np.array([-0.3,0.0,1.8]),np.array([0,1,2])*1e-9,(0,1.95))
        self.assertFalse(result["all_sampled_points_in_range"])
        self.assertAlmostEqual(result["max_excursion_v"],0.3)
        self.assertAlmostEqual(result["outside_duration_ns_trapezoid_estimate"],0.5)

    def test_source_reconstruction_and_missing_source_rejection(self):
        t=np.array([0,1,2])*1e-9
        np.testing.assert_allclose(ideal_source("VP sense 0 PWL(0n 0.8 2n 1.0)","sense",t),[0.8,0.9,1.0])
        np.testing.assert_allclose(ideal_source("VDD vdd 0 1.75","vdd",t),[1.75]*3)
        for text in ("", "VP sense 0 1\nVN sense 0 2", "VP sense 0 PWL(1n 1 0n 0)"):
            with self.assertRaises(ValueError):
                ideal_source(text,"sense",t)


if __name__=="__main__":
    unittest.main()
