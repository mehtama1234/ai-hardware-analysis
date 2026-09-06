* Dynamic offset cancellation by capacitive charge transfer.
.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param cal_p=0.207958500000
.param cal_n=0.201625200000
.param target_p=0.207985200000
.param target_n=0.200754900000
VDD vdd 0 {vdd}
* Calibration is held until 2.00 ns; target output arrives before evaluation.
VOP out_p 0 PWL(0 {cal_p} 1.90n {cal_p} 2.20n {target_p} 6n {target_p})
VON out_n 0 PWL(0 {cal_n} 1.90n {cal_n} 2.20n {target_n} 6n {target_n})
VBIAS gate_bias 0 0.9
CCP out_p gate_p 5f
CCN out_n gate_n 5f
RGP gate_p gate_bias 100G
RGN gate_n gate_bias 100G
VCLK clk 0 PULSE(0 {vdd} 2.40n 20p 20p 3n 10n)
VCLKB clkb 0 PULSE({vdd} 0 2.40n 20p 20p 3n 10n)
* Dynamic latch; input gates are isolated from the source during regeneration.
XPREP vdd clkb lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPREN vdd clkb lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLP lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLN lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRP lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRN lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINP lat_p gate_p tail 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XINN lat_n gate_n tail 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.ic v(gate_p)=0.9 v(gate_n)=0.9 v(lat_p)=1.8 v(lat_n)=1.8
.tran 2p 6n
.measure tran gate_p_cal_v FIND v(gate_p) AT=1.80n
.measure tran gate_n_cal_v FIND v(gate_n) AT=1.80n
.measure tran gate_p_eval_v FIND v(gate_p) AT=2.35n
.measure tran gate_n_eval_v FIND v(gate_n) AT=2.35n
.measure tran lat_p_final_v FIND v(lat_p) AT=5.60n
.measure tran lat_n_final_v FIND v(lat_n) AT=5.60n
.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'
.control
set noaskquit
run
.endc
.end
