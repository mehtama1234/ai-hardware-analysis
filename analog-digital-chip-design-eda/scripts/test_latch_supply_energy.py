import unittest
import numpy as np
from analyze_latch_supply_energy import integrate_power,constant_supply,source_power_traces


class EnergyTests(unittest.TestCase):
    def test_ideal_source_delivery_absorption_and_missing_current(self):
        names=["time","v(sense)","i(vp)"]
        wave=np.array([[0,1,-2],[1,2,-3]],dtype=float)
        traces,missing=source_power_traces("VP sense 0 PWL(0n 1 1n 2)\nIBIAS sense 0 4u",names,wave)
        self.assertEqual(missing,[])
        np.testing.assert_allclose(traces["VP"],[2,6])
        np.testing.assert_allclose(traces["IBIAS"],[-4e-6,-8e-6])
        _,missing=source_power_traces("VDD vdd 0 1.8",names,wave)
        self.assertEqual(missing,["VDD"])
        with self.assertRaises(ValueError):
            source_power_traces("IBIAS sense 0 PULSE(0 1)",names,wave)

    def test_signed_energy_and_zero_crossing(self):
        r=integrate_power(np.array([0.,2.]),np.array([-1.,1.]),0,2)
        self.assertAlmostEqual(r["net_delivered_j"],0)
        self.assertAlmostEqual(r["positive_delivered_j"],.5)
        self.assertAlmostEqual(r["returned_j"],.5)

    def test_exact_window_endpoints_and_missing_coverage(self):
        t=np.array([0.,2.]); p=np.array([3.,3.])
        self.assertAlmostEqual(integrate_power(t,p,.5,1.5)["net_delivered_j"],3)
        with self.assertRaises(ValueError):
            integrate_power(t,p,0,3)
        self.assertEqual(constant_supply("VDD vdd 0 1.75","VDD","vdd"),1.75)
        with self.assertRaises(ValueError):
            constant_supply("VDD vdd 0 PULSE(0 1)","VDD","vdd")


if __name__=="__main__":
    unittest.main()
