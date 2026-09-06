* Extracted regenerative latch starter structural transient.
* Uses exact Magic-extracted connectivity and parasitic capacitors with a
* bounded level-1 MOS model; this is not a Sky130 model signoff run.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
* NGSPICE file created from sky130_regenerative_latch_starter.ext - technology: sky130A

.subckt sky130_regenerative_latch_starter out_p out_n sense_p sense_n tail
M0 out_p out_n tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M1 out_n sense_n tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M2 out_n out_p tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
M3 out_p sense_p tail VSUBS LATCH_NMOS ad=3.36 pd=8 as=3.12 ps=7.6 w=1.2 l=0.6
C0 out_n out_p 0.74418f
C1 tail out_n 1.79756f
C2 sense_n out_p 0.00703f
C3 tail sense_n 0.1962f
C4 tail out_p 1.89733f
C5 out_p sense_p 0.04035f
C6 tail sense_p 0.18959f
C7 out_n sense_n 0.04664f
C8 tail VSUBS 19.18203f
C9 out_n VSUBS 7.10014f
C10 out_p VSUBS 0.98136f
.ends


.options method=gear maxord=1 trtol=7 reltol=1e-4 abstol=1e-12 gmin=1e-9
VDD vdd 0 1.8
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 0.905 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 0.895 0.50n 20p 20p 20n 40n)
RLP vdd out_p 20k
RLN vdd out_n 20k
CLP out_p 0 5f
CLN out_n 0 5f
XU out_p out_n sense_p sense_n 0 sky130_regenerative_latch_starter
    .ic v(out_p)=0.905 v(out_n)=0.895
.tran 20p 4n uic
.measure tran out_p_initial FIND v(out_p) AT=0.80n
.measure tran out_n_initial FIND v(out_n) AT=0.80n
.measure tran out_p_final FIND v(out_p) AT=3.00n
.measure tran out_n_final FIND v(out_n) AT=3.00n
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.measure tran output_diff_initial PARAM='out_p_initial-out_n_initial'
.control
run
.endc
.end
