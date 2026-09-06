import unittest
from build_combined_latch_capture import geometry


class CaptureLayoutTests(unittest.TestCase):
    def fixture(self):
        return "magic\nmagscale 1 2\n<< labels >>\n"+"\n".join(
            f"flabel locali s {x-17} {y-17} {x+17} {y+17} 0 FreeSans 200 0 0 0 {name}"
            for name,x,y in (("D",306,238),("CLK",46,238),("Q",1407,102)))

    def test_capture_has_a_real_well_tap_and_separate_control_ports(self):
        result=geometry("magic\nmagscale 1 2\n",self.fixture())
        self.assertIn("<< nsubdiff >>",result)
        self.assertIn("rect 2940 36444 3060 36644",result)
        self.assertIn("rect 1046 36514 3000 36574",result)
        self.assertIn("port 19 nsew",result)

    def test_changed_library_pin_geometry_is_rejected(self):
        with self.assertRaises(ValueError):
            geometry("magic\nmagscale 1 2\n",self.fixture().replace(" CLK"," UNKNOWN"))


if __name__=="__main__":
    unittest.main()
