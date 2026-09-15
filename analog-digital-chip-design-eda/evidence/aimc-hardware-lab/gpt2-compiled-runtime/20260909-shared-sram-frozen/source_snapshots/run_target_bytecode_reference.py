#!/usr/bin/env python3
"""Decode and execute the review bytecode in a deterministic reference model.

This is a software interpreter for the review encoding. It checks that every
word decodes to the command that produced it and that the schedule is ordered.
It is intentionally not presented as firmware or hardware execution.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "evidence" / "aimc-hybrid-compiler-runtime"
OUT_JSON = PACKAGE / "target_bytecode_reference_execution.json"
OUT_MD = PACKAGE / "target_bytecode_reference_execution.md"

OPCODES = {
    0x01: "LOAD_ACTIVATION",
    0x02: "SET_DAC",
    0x03: "RUN_ANALOG_TILE",
    0x04: "READ_ADC",
    0x05: "APPLY_CALIBRATION",
    0x06: "STORE_PARTIAL_SUM",
    0x07: "RUN_DIGITAL_SUPPORT",
}
SRAM_ALIGNMENT_BYTES = 64


def decode(word: str) -> dict[str, int | str | None]:
    value = int(word, 16)
    opcode = (value >> 56) & 0xFF
    model_index = (value >> 48) & 0xFF
    operator_index = (value >> 32) & 0xFFFF
    tile_id = (value >> 24) & 0xFF
    duration = (value >> 16) & 0xFF
    activation_offset_units = value & 0xFFFF
    return {
        "opcode": opcode,
        "command": OPCODES.get(opcode),
        "model_index": model_index,
        "operator_index": operator_index,
        "tile_id": tile_id or None,
        "estimated_cycles": duration,
        "activation_offset_bytes": activation_offset_units * SRAM_ALIGNMENT_BYTES,
    }


def main(package: Path = PACKAGE) -> int:
    PACKAGE = package
    OUT_JSON = package / "target_bytecode_reference_execution.json"
    OUT_MD = package / "target_bytecode_reference_execution.md"
    bytecode = json.loads((PACKAGE / "target_bytecode.json").read_text(encoding="utf-8"))
    commands = json.loads((PACKAGE / "runtime_commands.json").read_text(encoding="utf-8"))["commands"]
    words = bytecode["words"]
    errors: list[str] = []
    decoded_trace: list[dict[str, object]] = []
    cycle = 0
    for expected_sequence, (command, encoded) in enumerate(zip(commands, words), 1):
        word = encoded.get("word", "")
        try:
            decoded = decode(word)
        except (TypeError, ValueError):
            errors.append(f"sequence {expected_sequence}: invalid word {word!r}")
            continue
        expected = {
            "opcode": command["opcode"],
            "command": command["command"],
            "model_index": command["model_index"],
            "operator_index": command["operator_index"],
            "tile_id": command["tile_id"],
            "estimated_cycles": command["estimated_cycles"],
            "activation_offset_bytes": command["activation_offset_bytes"],
        }
        for key, value in expected.items():
            if decoded.get(key) != value:
                errors.append(
                    f"sequence {expected_sequence}: {key} decoded as {decoded.get(key)!r}, expected {value!r}"
                )
        if encoded.get("sequence") != expected_sequence or command.get("sequence") != expected_sequence:
            errors.append(f"sequence {expected_sequence}: sequence numbering is not contiguous")
        if command.get("start_cycle") != cycle:
            errors.append(
                f"sequence {expected_sequence}: start cycle {command.get('start_cycle')} does not follow {cycle}"
            )
        if decoded["command"] is None or decoded["estimated_cycles"] == 0:
            errors.append(f"sequence {expected_sequence}: unknown opcode or zero duration")
        decoded_trace.append({
            "sequence": expected_sequence,
            "command": decoded["command"],
            "model_index": decoded["model_index"],
            "operator_index": decoded["operator_index"],
            "tile_id": decoded["tile_id"],
            "start_cycle": cycle,
            "estimated_cycles": decoded["estimated_cycles"],
            "activation_offset_bytes": decoded["activation_offset_bytes"],
            "source_operator_id": command.get("operator_id"),
        })
        cycle += int(decoded["estimated_cycles"])
    if len(commands) != len(words) or len(words) != bytecode.get("word_count"):
        errors.append("command, word, and declared word counts do not match")
    result = {
        "schema_version": "aimc_target_bytecode_reference_execution.v1",
        "status": "reference_interpreter_pass" if not errors else "reference_interpreter_failed",
        "measured": True,
        "execution_kind": "deterministic_software_reference_interpreter",
        "command_count": len(commands),
        "word_count": len(words),
        "word_width_bits": bytecode.get("word_width_bits"),
        "decoded_command_count": len(decoded_trace),
        "total_planning_cycles": cycle,
        "errors": errors,
        "trace": decoded_trace,
        "claim_boundary": "software decode and schedule check only; not ISA validation, firmware execution, board runtime, or silicon evidence",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "\n".join([
            "# Target Bytecode Reference Execution",
            "",
            f"- status: `{result['status']}`",
            f"- words decoded: `{result['word_count']}`",
            f"- decoded commands: `{result['decoded_command_count']}`",
            f"- total planning cycles: `{result['total_planning_cycles']}`",
            f"- errors: `{len(errors)}`",
            "",
            "This is a deterministic software interpreter for the review bytecode. It verifies encoding, command identity, SRAM offset decoding, sequence order, and planning-cycle continuity. It is not firmware and does not prove hardware execution.",
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
            "",
        ]),
        encoding="utf-8",
    )
    print(f"status,{result['status']}")
    print(f"words,{result['word_count']}")
    print(f"commands,{result['decoded_command_count']}")
    print(f"cycles,{result['total_planning_cycles']}")
    if errors:
        for error in errors:
            print(f"error,{error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
