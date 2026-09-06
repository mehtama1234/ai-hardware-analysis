* Extracted latch/precharge/tail/active-load structural transient.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model LOAD_PMOS pmos level=1 kp=100u vto=-0.55 lambda=0.02
.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
* NGSPICE file created from sky130_latch_precharge_wide_input_weak_feedback_tail_active_load_flat.ext - technology: sky130A

.subckt sky130_latch_precharge_wide_input_weak_feedback_tail_active_load_flat out_p
+ out_n sense_p sense_n tail reset vdd vss eval
M0 out_p out_n tail VSUBS LATCH_NMOS ad=3 pd=7.4 as=2.76 ps=7 w=1.2 l=1.2
M1 out_n out_p vdd_active vdd_active LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M2 out_p sense_p tail VSUBS LATCH_NMOS ad=16.8 pd=17.6 as=15.6 ps=17.2 w=6 l=0.6
M3 out_n sense_n tail VSUBS LATCH_NMOS ad=16.8 pd=17.6 as=15.6 ps=17.2 w=6 l=0.6
M4 out_n out_p tail VSUBS LATCH_NMOS ad=3 pd=7.4 as=2.76 ps=7 w=1.2 l=1.2
M5 out_n reset vdd w_12400_300# LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M6 tail eval vss VSUBS LATCH_NMOS ad=16.8 pd=17.6 as=15.6 ps=17.2 w=6 l=0.6
M7 out_p out_n vdd_active vdd_active LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M8 out_p reset vdd w_12400_300# LOAD_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
C0 tail sense_n 0.19827f
C1 out_n w_12400_300# 0.70572f
C2 vss eval 0.04634f
C3 out_p vdd_active 4.31746f
C4 out_p tail 3.65794f
C5 vss out_p 0.1661f
C6 vdd w_12400_300# 1.53672f
C7 eval out_n 0.02298f
C8 out_p w_12400_300# 0.76428f
C9 out_n sense_n 0.06074f
C10 vdd out_n 0.07263f
C11 out_p sense_p 0.05301f
C12 out_p out_n 1.99225f
C13 reset w_12400_300# 4.03573f
C14 eval out_p 0.04062f
C15 out_n reset 0.05967f
C16 vss tail 0.19272f
C17 out_p sense_n 0.00703f
C18 vdd out_p 0.28588f
C19 tail sense_p 0.19338f
C20 out_n vdd_active 5.52673f
C21 out_n tail 2.60214f
C22 vdd reset 0.20878f
C23 out_p reset 0.07615f
C24 eval tail 0.09415f
C25 vss out_n 0.06009f
C26 vdd VSUBS 0.90789f
C27 tail VSUBS 18.87666f
C28 vss VSUBS 0.75002f
C29 out_p VSUBS 6.5951f
C30 w_12400_300# VSUBS 30f
C31 vdd_active VSUBS 64.1063f
.ends


VDD vdd 0 1.8
VDD_ACTIVE vdd_active 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 0.65 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 1.15 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 2.00n 20p 20p 18n 20n)
VEVAL eval 0 PULSE(0 1.8 2.10n 20p 20p 7n 20n)
XU out_p out_n sense_p sense_n tail reset vdd vss eval sky130_latch_precharge_wide_input_weak_feedback_tail_active_load_flat
.ic v(out_p)=1.85 v(out_n)=1.75
.tran 20p 10n uic
.measure tran out_p_released FIND v(out_p) AT=2.20n
.measure tran out_n_released FIND v(out_n) AT=2.20n
.measure tran out_p_final FIND v(out_p) AT=8.00n
.measure tran out_n_final FIND v(out_n) AT=8.00n
.measure tran out_p_eval FIND v(out_p) AT=4n
.measure tran out_n_eval FIND v(out_n) AT=4n
.measure tran output_diff_released PARAM='out_p_released-out_n_released'
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.measure tran output_diff_eval PARAM='out_p_eval-out_n_eval'
.control
run
.endc
.end
