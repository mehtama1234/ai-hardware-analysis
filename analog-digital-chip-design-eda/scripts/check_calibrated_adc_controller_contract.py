#!/usr/bin/env python3
import copy
import unittest

from calibrated_adc_controller_contract import pack_ranges,unpack_ranges,make_program,replay
from compile_hybrid_transformer_execution_package import validate_range_lowering


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract={"profile":{"adc_bits":12,"tile_rows":2,"tile_columns":2},
                       "weight_shape_input_output":[2,4],"logical_tiles":2,
                       "adc_range":{"ranges":[{"row":0,"column":0,"selected_bound":.125},
                                                {"row":0,"column":2,"selected_bound":7.25}]}}
        self.descriptors=unpack_ranges(pack_ranges(self.contract))
        self.program=make_program(self.descriptors,banks=1,lanes=1,columns=2)

    def replay(self,program):
        return replay(program,self.descriptors,banks=1,lanes=1,columns=2)

    def test_exact_range_roundtrip_and_coverage(self):
        self.assertEqual([d["bound_model_units"] for d in self.descriptors],[.125,7.25])
        result=self.replay(self.program)
        self.assertEqual(result["adc_conversions"],4)
        self.assertEqual(result["range_configurations"],2)
        self.assertFalse(result["physical_io_performed"])

    def test_read_before_range_ready(self):
        p=[e for e in self.program if e["operation"]!="range_ready"]
        with self.assertRaises(ValueError):self.replay(p)

    def test_read_before_array_ready(self):
        p=[e for e in self.program if e["operation"]!="array_ready"]
        with self.assertRaises(ValueError):self.replay(p)

    def test_stale_ack_from_previous_vector(self):
        p=make_program(self.descriptors,banks=1,lanes=1,columns=2,epoch_base=2)
        next(e for e in p if e["operation"]=="range_ready")["binding_epoch"]=1
        with self.assertRaises(ValueError):self.replay(p)

    def test_incomplete_or_duplicate_round(self):
        p=copy.deepcopy(self.program)
        next(e for e in p if e["operation"]=="read_adc")["round"]=1
        with self.assertRaises(ValueError):self.replay(p)
        with self.assertRaises(ValueError):self.replay(self.program[:-1])

    def test_invalid_range_or_tile_table(self):
        bad=copy.deepcopy(self.contract);bad["adc_range"]["ranges"][0]["selected_bound"]=float("nan")
        with self.assertRaises(ValueError):pack_ranges(bad)
        bad=copy.deepcopy(self.contract);bad["adc_range"]["ranges"].reverse()
        with self.assertRaises(ValueError):pack_ranges(bad)
        with self.assertRaises(ValueError):unpack_ranges(pack_ranges(self.contract)[:-1])

    def test_compiler_cannot_drop_range_requirement(self):
        with self.assertRaisesRegex(ValueError,"unsupported_adc_range_programming"):
            validate_range_lowering({"placement":"analog_memory","adc_range_contract":self.contract})
        validate_range_lowering({"placement":"digital_support","adc_range_contract":self.contract})
        validate_range_lowering({"placement":"analog_memory"})


if __name__=="__main__":unittest.main()
