* Extracted capacitive-isolation frontend port-mapping diagnostic.

.include "/home/mehtama1/git-repo/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-ngspice.includes"
.include "/home/mehtama1/git-repo/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_capacitive_isolation_frontend_extracted.spice"
.param vdd=1.8
.param vinp=0.900076485293
.param vinn=0.899923514707
VDD vdd 0 {vdd}
VSS vss 0 0
VBIAS vcm 0 0.9
VCLK clk 0 PULSE(0 {vdd} 1.00n 20p 20p 5n 10n)
VSP sp 0 PULSE(0 {vinp} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {vinn} 0.05n 20p 20p 20n 40n)
XFRONT vss vdd sn gp clk gn sp sky130_capacitive_isolation_frontend
RBIASP gp vcm 100G
RBIASN gn vcm 100G
.tran 2p 3n
.measure tran sp_before_v FIND v(sp) AT=0.90n
.measure tran sn_before_v FIND v(sn) AT=0.90n
.measure tran sp_after_v FIND v(sp) AT=2.60n
.measure tran sn_after_v FIND v(sn) AT=2.60n
.measure tran gp_before_v FIND v(gp) AT=0.90n
.measure tran gn_before_v FIND v(gn) AT=0.90n
.measure tran gp_after_v FIND v(gp) AT=2.60n
.measure tran gn_after_v FIND v(gn) AT=2.60n
.measure tran gp_after_v FIND v(gp) AT=2.60n
.measure tran gn_after_v FIND v(gn) AT=2.60n
.control
run
.endc
.end
