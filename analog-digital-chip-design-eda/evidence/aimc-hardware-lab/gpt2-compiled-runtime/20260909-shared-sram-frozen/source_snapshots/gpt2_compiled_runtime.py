"""Execute a GPT-2 projection using the shared review bytecode and SRAM map."""

import hashlib
import json
from pathlib import Path
import sys

import torch

EDA = Path(__file__).resolve().parents[3] / "analog-digital-chip-design-eda"
if str(EDA / "scripts") not in sys.path:
    sys.path.insert(0, str(EDA / "scripts"))
from run_target_bytecode_reference import decode


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class CompiledProjection:
    """One-vector reusable SRAM arena; all other GPT-2 modules stay native.

    No physical analog executor exists here. Even an optimistic evidence flag
    cannot cause this software interpreter to dispatch analog hardware.
    """

    def __init__(self, package, weight, bias, physical_gate, expected_hashes):
        for filename in ("runtime_commands.json", "target_bytecode.json", "compiled_target_execution_package.json"):
            if sha256(package / filename) != expected_hashes[filename]:
                raise ValueError(f"compiled artifact hash mismatch: {filename}")
        commands = json.loads((package / "runtime_commands.json").read_text())["commands"]
        words = json.loads((package / "target_bytecode.json").read_text())["words"]
        compiled = json.loads((package / "compiled_target_execution_package.json").read_text())
        if len(commands) != 1 or len(words) != 1 or len(compiled["sram_memory_maps"]) != 1:
            raise ValueError("this executor requires exactly one compiled projection")
        self.command = commands[0]
        if self.command["encoding"] != words[0]["word"]:
            raise ValueError("command/image encoding mismatch")
        self.decoded = decode(words[0]["word"])
        if self.decoded["command"] != "RUN_DIGITAL_SUPPORT" or self.decoded["operator_index"] != 0 or self.decoded["model_index"] != 0:
            raise ValueError("unauthorized instruction or operator binding")
        maps = compiled["sram_memory_maps"][0]
        if len(maps["allocations"]) != 1:
            raise ValueError("one SRAM allocation required")
        self.allocation = maps["allocations"][0]
        a = self.allocation
        if self.decoded["activation_offset_bytes"] != a["activation_offset_bytes"]:
            raise ValueError("decoded SRAM address mismatch")
        if self.command["partial_sum_offset_bytes"] != a["partial_sum_offset_bytes"]:
            raise ValueError("partial sum address mismatch")
        if self.command["operator_id"] != a["operator_id"]:
            raise ValueError("operator allocation mismatch")
        self.weight, self.bias = weight.detach(), bias.detach()
        if weight.device.type != "cpu" or weight.dtype != torch.float32 or bias.dtype != torch.float32:
            raise ValueError("reference SRAM interpreter requires CPU float32")
        inputs, outputs = weight.shape
        if bias.shape != (outputs,):
            raise ValueError("projection bias shape mismatch")
        size = maps["sram_bytes_used"]
        if not isinstance(size, int) or not 0 < size <= 65536:
            raise ValueError("SRAM capacity exceeded")
        spans = []
        for prefix, required in (("activation", inputs * 4), ("partial_sum", outputs * 4)):
            start, length = a[f"{prefix}_offset_bytes"], a[f"{prefix}_size_bytes"]
            if start < 0 or start % 64 or length < required or start + length > size:
                raise ValueError("invalid SRAM span")
            spans.append((start, start + length))
        if max(spans[0][0], spans[1][0]) < min(spans[0][1], spans[1][1]):
            raise ValueError("overlapping SRAM buffers")
        self.memory = bytearray(size)
        self.trace = []
        self.phase = "unspecified"
        self.fallback_reasons = ["no_bound_analog_array_target", "physical_analog_executor_not_implemented"]
        if not physical_gate.get("analog_allowed_for_physical_claim", False):
            self.fallback_reasons.append("physical_converter_gate_blocked")
        if not physical_gate.get("active_macro_candidate", {}).get("physical_preamp_routing_complete", False):
            self.fallback_reasons.append("final_netlist_preamp_path_unverified")

    def __call__(self, value):
        if value.device.type != "cpu" or value.dtype != torch.float32 or value.shape[-1] != self.weight.shape[0]:
            raise ValueError("activation violates compiled CPU float32 shape contract")
        flat = value.reshape(-1, value.shape[-1])
        results = []
        a = self.allocation
        for vector in flat:
            encoded = vector.contiguous().numpy().tobytes()
            offset = a["activation_offset_bytes"]
            self.memory[offset:offset + len(encoded)] = encoded
            loaded = torch.frombuffer(self.memory, dtype=torch.float32, count=vector.numel(), offset=offset)
            result = torch.addmm(self.bias, loaded.reshape(1, -1), self.weight)
            encoded_result = result.contiguous().numpy().tobytes()
            partial = a["partial_sum_offset_bytes"]
            self.memory[partial:partial + len(encoded_result)] = encoded_result
            results.append(torch.frombuffer(self.memory, dtype=torch.float32, count=self.bias.numel(), offset=partial).clone())
        self.trace.append({"phase": self.phase, "vectors": len(results), "executed_commands": len(results),
                           "route": "digital_fallback", "instruction": self.decoded["command"],
                           "activation_offset_bytes": a["activation_offset_bytes"],
                           "partial_sum_offset_bytes": a["partial_sum_offset_bytes"],
                           "boundary_input_bytes": flat.numel() * 4,
                           "boundary_output_bytes": len(results) * self.bias.numel() * 4,
                           "fallback_reasons": self.fallback_reasons})
        return torch.stack(results).reshape(*value.shape[:-1], self.bias.numel())


def candidate_schedule(contract, active_tiles=8, adc_lanes_per_tile=16):
    """Explicit assumed resource schedule, with unknown physical durations."""
    if active_tiles < 1 or adc_lanes_per_tile < 1:
        raise ValueError("resources must be positive")
    inputs, outputs = contract["weight_shape_input_output"]
    profile = contract["profile"]
    tiles = []
    for r in range(0, inputs, profile["tile_rows"]):
        for c in range(0, outputs, profile["tile_columns"]):
            nr, nc = min(profile["tile_rows"], inputs-r), min(profile["tile_columns"], outputs-c)
            tiles.append({"tile_id": len(tiles), "input_range": [r, r+nr], "output_range": [c, c+nc],
                          "dac_conversions": nr, "adc_conversions": nc,
                          "adc_rounds": (nc+adc_lanes_per_tile-1)//adc_lanes_per_tile})
    waves = [{"wave": start//active_tiles, "tile_ids": [tile["tile_id"] for tile in tiles[start:start+active_tiles]],
              "adc_rounds": max(tile["adc_rounds"] for tile in tiles[start:start+active_tiles]),
              "steps": ["load_and_DAC", "array_settle", "ADC_rounds_with_sample_hold", "digital_accumulate"],
              "duration_ns": None} for start in range(0,len(tiles),active_tiles)]
    assert sum(tile["dac_conversions"] for tile in tiles) == contract["per_vector"]["dac_conversions_without_column_tile_broadcast"]
    assert sum(tile["adc_conversions"] for tile in tiles) == contract["per_vector"]["adc_conversions_after_differential_subtraction"]
    return {"status": "candidate_resource_schedule_not_physical_execution", "active_logical_tiles": active_tiles,
            "adc_lanes_per_logical_tile": adc_lanes_per_tile, "tiles": tiles, "waves_per_vector": waves,
            "partial_sum_storage_bytes_fp32": outputs*4, "host_weight_storage_bytes_fp32": inputs*outputs*4,
            "weight_policy": "all tile weights assumed resident; programming and calibration cost must be amortized separately",
            "latency_equation": "sum_over_waves(T_load_DAC + T_settle + ADC_rounds*T_ADC + T_accumulate) + boundary_transfers",
            "duration_status": "unresolved until converter sharing, sample-hold and bus timings are matched",
            "per_vector_cost_counts": contract["per_vector"]}
