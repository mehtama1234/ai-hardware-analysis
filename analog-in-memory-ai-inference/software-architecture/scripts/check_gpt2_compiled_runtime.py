#!/usr/bin/env python3
"""Exercise SRAM execution and reject forged commands, addresses and capacity."""

import json
from pathlib import Path
import tempfile
import unittest

import torch

from gpt2_compiled_runtime import CompiledProjection, candidate_schedule, sha256
from compile_hybrid_transformer_execution_package import encode_command


class RuntimeChecks(unittest.TestCase):
    def package(self, path, opcode=7, offset=0, partial=64, operator=0):
        word = encode_command(opcode, 0, operator, None, 3, offset)
        documents = {
            "runtime_commands.json": {"commands": [{"encoding": word, "partial_sum_offset_bytes": partial, "operator_id": "projection"}]},
            "target_bytecode.json": {"words": [{"word": word}]},
            "compiled_target_execution_package.json": {"sram_memory_maps": [{"sram_bytes_used": 128,
                "allocations": [{"operator_id": "projection", "activation_offset_bytes": 0, "activation_size_bytes": 64,
                                 "partial_sum_offset_bytes": partial, "partial_sum_size_bytes": 64}]}]},
        }
        for name, value in documents.items():
            (path/name).write_text(json.dumps(value))
        return {name: sha256(path/name) for name in documents}

    def test_real_arithmetic_memory_and_forced_digital_even_if_flag_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            hashes = self.package(path)
            torch.manual_seed(9)
            w, b, x = torch.randn(5,7), torch.randn(7), torch.randn(2,3,5)
            runtime = CompiledProjection(path,w,b,{"analog_allowed_for_physical_claim": True},hashes)
            with torch.inference_mode():
                actual = runtime(x)
            torch.testing.assert_close(actual, x@w+b)
            self.assertEqual(runtime.trace[0]["executed_commands"], 6)
            self.assertEqual(runtime.trace[0]["boundary_input_bytes"], 120)
            self.assertEqual(runtime.trace[0]["boundary_output_bytes"], 168)
            self.assertIn("physical_analog_executor_not_implemented",runtime.fallback_reasons)
            self.assertEqual(runtime.trace[0]["route"], "digital_fallback")

    def test_unauthorized_instructions_and_addresses_fail_closed(self):
        for mutation in ({"opcode": 3}, {"offset": 64}, {"partial": 0}, {"partial": 128}, {"operator": 1}):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp)
                hashes = self.package(path, **mutation)
                with self.assertRaises(ValueError):
                    CompiledProjection(path,torch.eye(5),torch.zeros(5),{},hashes)

    def test_artifact_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            hashes = self.package(path)
            (path/"target_bytecode.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                CompiledProjection(path,torch.eye(5),torch.zeros(5),{},hashes)

    def test_repaired_connections_do_not_override_failed_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            hashes=self.package(path)
            gate={"physical_repair_evidence":{"final_preamp_connections_pass":True,"full_cell_drc_pass":False}}
            runtime=CompiledProjection(path,torch.eye(5),torch.zeros(5),gate,hashes)
            self.assertIn("full_cell_layout_drc_failed",runtime.fallback_reasons)
            self.assertNotIn("final_netlist_preamp_path_unverified",runtime.fallback_reasons)

    def test_buffer_and_input_shape_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            hashes = self.package(path)
            with self.assertRaisesRegex(ValueError,"SRAM span"):
                CompiledProjection(path,torch.eye(17),torch.zeros(17),{},hashes)
            runtime = CompiledProjection(path,torch.eye(5),torch.zeros(5),{},hashes)
            with self.assertRaisesRegex(ValueError,"shape contract"):
                runtime(torch.zeros(1,6))

    def test_resource_sharing_covers_ragged_tiles(self):
        contract = {"weight_shape_input_output": [5,7], "profile": {"tile_rows": 3,"tile_columns": 4},
                    "per_vector": {"dac_conversions_without_column_tile_broadcast": 10,
                                   "adc_conversions_after_differential_subtraction": 14}}
        schedule = candidate_schedule(contract,active_tiles=3,adc_lanes_per_tile=2)
        self.assertEqual(len(schedule["waves_per_vector"]),2)
        self.assertEqual([t["adc_rounds"] for t in schedule["tiles"]],[2,2,2,2])
        self.assertEqual([t["tile_ids"] for t in schedule["waves_per_vector"]],[[0,1,2],[3]])
        with self.assertRaises(ValueError):
            candidate_schedule(contract,active_tiles=0)


if __name__ == "__main__":
    torch.set_num_threads(2)
    unittest.main()
