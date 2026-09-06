* Extracted RC transient fixture for the AIMC converter starter macro.
* This uses Magic-extracted capacitances, explicit driver/load resistors, and no transistor converter behavior.

.global VSUBS
.include "/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_layout_smoke.spice"

VDD vdd 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VSTEP src 0 PULSE(0 1.8 0.1n 20p 20p 5n 10n)
RDRV src row_drive 1000
RCOLUMN column_sense 0 2250
RDIG digital_code_out 0 1000
RCLK sample_clock 0 1000
XMAC vss vdd row_drive column_sense digital_code_out sample_clock aimc_converter_macro

.tran 1p 2n
.measure tran row_final FIND v(row_drive) AT=1.5n
.measure tran column_peak MAX v(column_sense) FROM=0.1n TO=2n
.measure tran digital_peak MAX v(digital_code_out) FROM=0.1n TO=2n
.measure tran row_90_when WHEN v(row_drive)=1.62 RISE=1
.measure tran row_99_when WHEN v(row_drive)=1.782 RISE=1
.control
run
.endc

.end
