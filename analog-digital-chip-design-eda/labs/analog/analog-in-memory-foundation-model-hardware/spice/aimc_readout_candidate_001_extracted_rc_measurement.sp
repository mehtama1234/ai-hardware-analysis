* Same-candidate extracted-RC fixture for aimc_readout_candidate_001.
* This includes the assembled candidate netlist and measures charge movement on its extracted capacitances.
* It is not a transistor converter proof.

.global VSUBS
.include "/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice"

VDD vdd 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VREFP vrefp 0 1.2
VREFN vrefn 0 0.6
VROW row_src 0 PULSE(0 1.8 0.1n 20p 20p 5n 10n)
VSENSE sense_src 0 PULSE(0.9 0.92 0.25n 20p 20p 5n 10n)
VCLK clk_src 0 PULSE(0 1.8 0.2n 20p 20p 1n 2n)
RROW row_src row_drive 1000
RSENSE sense_src column_sense 2000
RCLK clk_src sample_clock 1000
RDIG digital_code_out 0 1000

XCAND vss vdd row_drive column_sense digital_code_out sample_clock vrefp vrefn aimc_readout_candidate_001

.tran 1p 2n
.measure tran row_final FIND v(row_drive) AT=1.5n
.measure tran sense_final FIND v(column_sense) AT=1.5n
.measure tran clock_peak MAX v(sample_clock) FROM=0.2n TO=1.2n
.measure tran digital_peak MAX v(digital_code_out) FROM=0.1n TO=2n
.measure tran row_90_when WHEN v(row_drive)=1.62 RISE=1
.measure tran row_99_when WHEN v(row_drive)=1.782 RISE=1
.measure tran sense_delta PARAM='abs(sense_final - 0.92)'
.control
run
.endc

.end
