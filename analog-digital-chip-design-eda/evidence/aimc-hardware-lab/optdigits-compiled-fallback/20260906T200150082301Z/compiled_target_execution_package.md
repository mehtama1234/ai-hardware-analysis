# Target Execution Package

All shared hybrid workload plans were lowered into deterministic target commands, aligned SRAM offsets, register writes, and a reproducible 64-bit review bytecode image.

- models: `1`
- operators: `5`
- runtime commands: `5`
- register writes: `0`
- estimated schedule: `15` cycles
- review bytecode words: `5`
- hardware instruction-set binary: `not generated`
- physical converter: `blocked_extracted_latch_polarity_voltage`

Analog rows receive tile IDs, DAC/ADC settings, calibration profiles, fallback IDs, and SRAM buffers. Digital rows receive explicit digital-support commands. Each command also has a deterministic review encoding and aligned SRAM offsets. Cycle values remain planning assumptions, not measurements.

This output is a target bytecode handoff, not an ISA-validated firmware binary, a board trace, or silicon evidence.
