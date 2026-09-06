import unittest
from verify_latch_calibration_contract import profile_mismatches


class CalibrationContractTests(unittest.TestCase):
    def test_changed_correction_timing_and_input_axis_are_rejected(self):
        frozen={"logical_validation_sequence_mv":[-.5,.5],"correction_mv":3.125,
                "corner":"tt","temperature_c":27,"reset_early_ns":.5,
                "mismatch_seed":102,"period_ns":50,"equalizer_release_ns":2,
                "reset_high_v":1.75,"clock_fall_ps":1000,"input_setup_ns":5,
                "reltol":1e-4,"max_step_ps":None}
        mapping={"logical_validation_sequence_mv":"input_diffs_mv","correction_mv":"calibration_offset_mv",
                 "corner":"effective_model_corner","temperature_c":"effective_temperature_c",
                 "reset_early_ns":"reset_advance_ns"}
        actual={mapping.get(k,k):v for k,v in frozen.items()}
        actual.update(applied_input_diffs_mv=[2.625,3.625],mismatch_seed_method="startup_seed_plus_control_setseed_reset")
        self.assertEqual(profile_mismatches(frozen,actual),[])
        for key,value in (("calibration_offset_mv",3.0),("equalizer_release_ns",3),
                          ("applied_input_diffs_mv",[-.5,.5]),("mismatch_seed_method","startup_only"),
                          ("reset_rise_ps",500),("reset_fall_ps",2000)):
            with self.subTest(key=key):
                self.assertTrue(profile_mismatches(frozen,{**actual,key:value}))


if __name__=="__main__":
    unittest.main()
