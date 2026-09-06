import unittest
import numpy as np
from pathlib import Path
from run_latch_capture_integration import check_logic_window,capture_clock_source,internal_capture_vectors,add_internal_charge_caps


class CaptureIntegrationTests(unittest.TestCase):
    def test_internal_caps_preserve_devices_and_reject_duplicate(self):
        root=Path(__file__).resolve().parents[1]
        source=(root/"evidence/aimc-simulator-adapters/combined-latch-capture/20260906T220543571833Z/extracted.spice").read_text()
        result=add_internal_charge_caps(source,1)
        self.assertEqual([x for x in source.splitlines() if x.startswith("X")],
                         [x for x in result.splitlines() if x.startswith("X")])
        self.assertEqual(sum(x.startswith("CCHARGE") for x in result.splitlines()),4)
        self.assertIn("CCHARGE0 a_1561_36413# vdd_capture 1f",result)
        self.assertIn("CCHARGE3 a_2017_36047# vss 1f",result)
        modeled=add_internal_charge_caps(source,1,True)
        self.assertEqual(sum(x.startswith("XCHARGE") for x in modeled.splitlines()),4)
        self.assertIn("XCHARGE0 a_1561_36413# vdd_capture sky130_fd_pr__cap_mim_m3_1 l=2 w=2",modeled)
        self.assertEqual(len(internal_capture_vectors(modeled)),19)
        self.assertIn("v(xu.xcharge3.b1)",internal_capture_vectors(modeled))
        with self.assertRaises(ValueError):
            internal_capture_vectors(modeled.replace("XCHARGE3", "XCHARGE4"))
        for text,value in ((result,1),(source,0),(source.replace("a_1561_36413#","renamed"),1)):
            with self.assertRaises(ValueError):
                add_internal_charge_caps(text,value)

    def test_capture_fall_slew_preserves_both_crossings(self):
        for rise in (100,500,1000):
            for fall in (100,500,1000):
                fields=capture_clock_source(rise,fall_ps=fall)[6:-1].split()
                delay=float(fields[2][:-1]); tr=float(fields[3][:-1])/1000
                tf=float(fields[4][:-1])/1000; width=float(fields[5][:-1])
                self.assertAlmostEqual(delay+tr/2,20.05)
                self.assertAlmostEqual(delay+tr+width+tf/2,25.15)

    def test_capture_slew_keeps_crossing_and_precharge_phase(self):
        self.assertEqual(capture_clock_source(100),"PULSE(0 1.8 20n 100p 100p 5n 50n)")
        self.assertEqual(capture_clock_source(500),"PULSE(0 1.8 19.8n 500p 100p 4.8n 50n)")
        self.assertEqual(capture_clock_source(500,True),"0")

    def test_internal_vector_selection_rejects_wrong_device_count(self):
        with self.assertRaises(ValueError):
            internal_capture_vectors(".subckt invalid d q\nX0 d q 0 0 model\n.ends\n")

    def test_retention_checks_whole_window_not_just_final_value(self):
        t=np.array([0.,1.,2.])*1e-9
        self.assertFalse(check_logic_window(t,np.array([1.8,.5,1.8]),0,2,1)["pass"])
        self.assertTrue(check_logic_window(t,np.array([0.,.01,0.]),0,2,0)["pass"])
        with self.assertRaises(ValueError):
            check_logic_window(t,np.zeros(3),0,3,0)


if __name__=="__main__":
    unittest.main()
