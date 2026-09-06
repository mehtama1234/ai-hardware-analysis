* Flat extracted latch plus physical PMOS precharge structural transient.
* Exact extracted topology and parasitic capacitors; bounded level-1 models.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model PRECHARGE_PMOS pmos level=1 kp=100u vto=-0.55 lambda=0.02
* NGSPICE file created from sky130_latch_precharge_wide_input_medium_feedback_flat.ext - technology: sky130A

.subckt sky130_latch_precharge_wide_input_medium_feedback_flat out_p out_n sense_p
+ sense_n tail reset vdd
M0 out_n out_p tail VSUBS LATCH_NMOS ad=3.24 pd=7.8 as=3 ps=7.4 w=1.2 l=0.8
M1 out_p sense_p tail VSUBS LATCH_NMOS ad=16.8 pd=17.6 as=15.6 ps=17.2 w=6 l=0.6
M2 out_n sense_n tail VSUBS LATCH_NMOS ad=16.8 pd=17.6 as=15.6 ps=17.2 w=6 l=0.6
M3 out_n reset vdd vdd PRECHARGE_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M4 out_p out_n tail VSUBS LATCH_NMOS ad=3.24 pd=7.8 as=3 ps=7.4 w=1.2 l=0.8
M5 out_p reset vdd vdd PRECHARGE_PMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
C0 out_p sense_p 0.05301f
C1 tail out_n 2.03185f
C2 reset out_n 0.05967f
C3 out_p out_n 1.42023f
C4 out_n sense_n 0.06074f
C5 vdd out_n 0.07263f
C6 vdd out_n 0.70572f
C7 out_p tail 2.14101f
C8 out_p reset 0.07615f
C9 tail sense_n 0.19827f
C10 vdd reset 0.20878f
C11 out_p sense_n 0.00703f
C12 vdd out_p 0.28588f
C13 vdd reset 4.03573f
C14 out_p vdd 0.76428f
C15 sense_p tail 0.19338f
C16 vdd vdd 1.53672f
C17 vdd VSUBS 0.90789f
C18 out_p VSUBS 11.74542f
C19 tail VSUBS 25.78658f
C20 vdd VSUBS 30f
.ends


.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
VDD vdd 0 1.8
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 0.905 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 0.895 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 0.20n 20p 20p 0.80n 20n)
XU out_p out_n sense_p sense_n 0 reset vdd sky130_latch_precharge_wide_input_medium_feedback_flat
.ic v(out_p)=1.8 v(out_n)=1.8
.tran 20p 4n uic
.measure tran out_p_released FIND v(out_p) AT=1.20n
.measure tran out_n_released FIND v(out_n) AT=1.20n
.measure tran out_p_final FIND v(out_p) AT=3.00n
.measure tran out_n_final FIND v(out_n) AT=3.00n
.measure tran output_diff_released PARAM='out_p_released-out_n_released'
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.control
run
.endc
.end
