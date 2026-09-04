#!/usr/bin/env python3
"""Lower the hybrid review package into deterministic target commands."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence" / "aimc-hybrid-compiler-runtime" / "hybrid_compiler_runtime_package.json"
OUT = ROOT / "evidence" / "aimc-hybrid-compiler-runtime"
PHYSICAL_GATE = "blocked_sar_source_common_mode"
SRAM_CAPACITY_BYTES = 65536
SRAM_ALIGNMENT_BYTES = 64

OPCODES = {
    "LOAD_ACTIVATION": 0x01,
    "SET_DAC": 0x02,
    "RUN_ANALOG_TILE": 0x03,
    "READ_ADC": 0x04,
    "APPLY_CALIBRATION": 0x05,
    "STORE_PARTIAL_SUM": 0x06,
    "RUN_DIGITAL_SUPPORT": 0x07,
}


def align(value: int, boundary: int = SRAM_ALIGNMENT_BYTES) -> int:
    return ((value + boundary - 1) // boundary) * boundary


def buffer_bytes(row: dict[str, object]) -> int:
    shape = row.get("weight_shape_in_out")
    if isinstance(shape, list) and len(shape) == 2 and all(isinstance(item, int) for item in shape):
        # Four bytes per element is an explicit planning representation for
        # activation/partial-sum buffers; it is not a claim about SRAM timing.
        return max(shape) * 4
    return 16 * 4


def encode_command(opcode: int, model_index: int, op_index: int, tile_id: int | None, duration: int, buffer_offset: int) -> str:
    """Encode the deterministic target bytecode word used by the review image."""
    word = (
        (opcode & 0xFF) << 56
        | (model_index & 0xFF) << 48
        | (op_index & 0xFFFF) << 32
        | ((tile_id or 0) & 0xFF) << 24
        | (duration & 0xFF) << 16
        | ((buffer_offset // SRAM_ALIGNMENT_BYTES) & 0xFFFF)
    )
    return f"0x{word:016x}"


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    commands: list[dict[str, object]] = []
    registers: list[dict[str, object]] = []
    bytecode: list[dict[str, object]] = []
    model_memory_maps: list[dict[str, object]] = []
    cycle = 0
    tile_id = 0
    for model_index, model in enumerate(source["models"]):
        model_id = model["model_id"]
        plan = json.loads((ROOT / model["source_plan"]).read_text(encoding="utf-8"))
        sram_cursor = 0
        allocations: list[dict[str, object]] = []
        for op_index, row in enumerate(plan["operator_placements"]):
            operator_id = row["operator_id"]
            activation_offset = align(sram_cursor)
            activation_size = align(buffer_bytes(row))
            sram_cursor = activation_offset + activation_size
            partial_offset = align(sram_cursor)
            partial_size = align(buffer_bytes(row))
            sram_cursor = partial_offset + partial_size
            if sram_cursor > SRAM_CAPACITY_BYTES:
                raise SystemExit(f"{model_id}: SRAM allocation exceeds {SRAM_CAPACITY_BYTES} bytes")
            allocations.append({
                "operator_id": operator_id,
                "activation_offset_bytes": activation_offset,
                "activation_size_bytes": activation_size,
                "partial_sum_offset_bytes": partial_offset,
                "partial_sum_size_bytes": partial_size,
            })
            if row["placement"] == "analog_memory":
                tile_id += 1
                address = f"sram:model{model_index}:op{op_index}"
                register_values = {
                    "MODEL_ID": model_index,
                    "OP_INDEX": op_index,
                    "TILE_ID": tile_id,
                    "TILE_COUNT": row.get("tile_count", 1),
                    "DAC_BITS": model["converter_plan"]["simulator_dac_bits"],
                    "ADC_BITS": model["converter_plan"]["simulator_adc_bits"],
                    "CALIBRATION_ID": row["calibration_profile"],
                    "FALLBACK_ID": row["fallback"],
                    "ACTIVATION_OFFSET": activation_offset,
                    "PARTIAL_SUM_OFFSET": partial_offset,
                }
                for name, value in register_values.items():
                    registers.append({"model_id": model_id, "operator_id": operator_id, "register": name, "value": value})
                steps = [
                    ("LOAD_ACTIVATION", "local_sram", 2),
                    ("SET_DAC", "converter", 1),
                    ("RUN_ANALOG_TILE", "analog_memory", 4),
                    ("READ_ADC", "converter", 2),
                    ("APPLY_CALIBRATION", "digital_support", 1),
                    ("STORE_PARTIAL_SUM", "local_sram", 2),
                ]
            else:
                tile_id_value = None
                steps = [("RUN_DIGITAL_SUPPORT", "digital_memory_and_sram", 3)]
            for command, unit, duration in steps:
                command_record = {
                        "sequence": len(commands) + 1,
                        "model_index": model_index,
                        "operator_index": op_index,
                        "model_id": model_id,
                        "operator_id": operator_id,
                        "command": command,
                        "unit": unit,
                        "start_cycle": cycle,
                        "estimated_cycles": duration,
                        "tile_id": tile_id if row["placement"] == "analog_memory" else tile_id_value,
                        "activation_buffer": "local_sram",
                        "activation_offset_bytes": activation_offset,
                        "partial_sum_offset_bytes": partial_offset,
                        "opcode": OPCODES[command],
                    }
                command_record["encoding"] = encode_command(
                    OPCODES[command], model_index, op_index,
                    command_record["tile_id"], duration, activation_offset,
                )
                commands.append(command_record)
                bytecode.append({"sequence": command_record["sequence"], "word": command_record["encoding"]})
                cycle += duration
        model_memory_maps.append({"model_id": model_id, "sram_bytes_used": sram_cursor, "allocations": allocations})
    compiled = {
        "schema_version": "aimc_target_execution_package.v1",
        "package_id": "hybrid_transformer_target_execution_v1",
        "source_package": str(SOURCE.relative_to(ROOT)),
        "target_profile": "educational-hybrid-tile-v1",
        "status": "target_bytecode_generated_firmware_not_generated",
        "models": [model["model_id"] for model in source["models"]],
        "operator_count": sum(model["operator_count"] for model in source["models"]),
        "command_count": len(commands),
        "register_write_count": len(registers),
        "estimated_cycles": cycle,
        "commands_artifact": "runtime_commands.json",
        "registers_artifact": "register_writes.json",
        "trace_artifact": "target_execution_trace.json",
        "bytecode_artifact": "target_bytecode.json",
        "sram_memory_maps": model_memory_maps,
        "assumptions": {
            "cycle_counts": "planning values for command ordering, not measured timing",
            "sram_addresses": "deterministic aligned offsets within the educational 64 KiB SRAM contract",
            "bytecode_encoding": "64-bit review encoding with opcode, model, operator, tile, duration, and activation-buffer fields",
            "converter": f"uses simulator DAC/ADC widths; physical converter compatibility remains {PHYSICAL_GATE}",
        },
        "claim_boundary": {
            "allowed": "deterministic target command and register ordering was generated from the shared hybrid plans",
            "blocked": "hardware instruction-set binary, firmware execution, board runtime, measured latency/energy, calibrated silicon, and production readiness",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    trace = {
        "schema_version": "aimc_target_execution_trace.v1",
        "trace_id": "hybrid_transformer_target_execution_trace_v1",
        "package_id": compiled["package_id"],
        "commands": commands,
        "estimated_cycles": cycle,
        "status": "static_target_bytecode_schedule_only",
        "physical_converter_gate": PHYSICAL_GATE,
        "claim_boundary": "estimated target schedule, not an observed runtime trace",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    bytecode_image = {
        "schema_version": "aimc_target_bytecode.v1",
        "image_id": "hybrid_transformer_target_bytecode_v1",
        "package_id": compiled["package_id"],
        "word_width_bits": 64,
        "word_count": len(bytecode),
        "words": bytecode,
        "status": "review_bytecode_generated_hardware_binary_not_generated",
        "claim_boundary": "deterministic review bytecode image, not an ISA-validated firmware binary or observed hardware execution",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report = "\n".join(
        [
            "# Target Execution Package",
            "",
            "All shared hybrid workload plans were lowered into deterministic target commands, aligned SRAM offsets, register writes, and a reproducible 64-bit review bytecode image.",
            "",
            f"- models: `{len(compiled['models'])}`",
            f"- operators: `{compiled['operator_count']}`",
            f"- runtime commands: `{compiled['command_count']}`",
            f"- register writes: `{compiled['register_write_count']}`",
            f"- estimated schedule: `{compiled['estimated_cycles']}` cycles",
            "- review bytecode words: `{}`".format(len(bytecode)),
            "- hardware instruction-set binary: `not generated`",
            f"- physical converter: `{PHYSICAL_GATE}`",
            "",
            "Analog rows receive tile IDs, DAC/ADC settings, calibration profiles, fallback IDs, and SRAM buffers. Digital rows receive explicit digital-support commands. Each command also has a deterministic review encoding and aligned SRAM offsets. Cycle values remain planning assumptions, not measurements.",
            "",
            "This output is a target bytecode handoff, not an ISA-validated firmware binary, a board trace, or silicon evidence.",
            "",
        ]
    )
    (OUT / "compiled_target_execution_package.json").write_text(json.dumps(compiled, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "runtime_commands.json").write_text(json.dumps({"schema_version": "aimc_runtime_commands.v1", "commands": commands}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "register_writes.json").write_text(json.dumps({"schema_version": "aimc_register_writes.v1", "registers": registers}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "target_execution_trace.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "target_bytecode.json").write_text(json.dumps(bytecode_image, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "compiled_target_execution_package.md").write_text(report, encoding="utf-8")
    print(f"compiled_package,{compiled['package_id']}")
    print(f"models,{len(compiled['models'])}")
    print(f"operators,{compiled['operator_count']}")
    print(f"commands,{compiled['command_count']}")
    print(f"register_writes,{compiled['register_write_count']}")
    print(f"estimated_cycles,{compiled['estimated_cycles']}")
    print(f"review_bytecode_words,{len(bytecode)}")
    print("hardware_binary,not_generated")
    print(f"physical_converter_gate,{PHYSICAL_GATE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
