# Target Execution Package

All shared hybrid workload plans were lowered into deterministic target commands, aligned SRAM offsets, register writes, and a reproducible 64-bit review bytecode image.

- models: `1`
- operators: `1`
- runtime commands: `1`
- register writes: `0`
- estimated schedule: `3` cycles
- review bytecode words: `1`
- hardware instruction-set binary: `not generated`
- physical converter: `unqualified_calibrated_range_hardware`

Analog rows receive tile IDs, DAC/ADC settings, calibration profiles, fallback IDs, and SRAM buffers. Digital rows receive explicit digital-support commands. Each command also has a deterministic review encoding and aligned SRAM offsets. Cycle values remain planning assumptions, not measurements.

This output is a target bytecode handoff, not an ISA-validated firmware binary, a board trace, or silicon evidence.
