* Frontend-sense to Sky130 transistor short transient.
* Starts from the measured OP point and runs only a short local transient.
* This is not the full extracted frontend transient, latch, SAR, or accepted converter evidence.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param rd=100k
.param itail=20u
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {vdd}
VINP inp 0 0.900033500000
VINN inn 0 0.899966500000
RDP vdd outp {rd}
RDN vdd outn {rd}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
ITAIL tail 0 {itail}
COUTP outp 0 2f
COUTN outn 0 2f

.ic v(outp)=0.799691600000 v(outn)=0.800308200000 v(tail)=0.231080700000
.tran 100p 500p uic
.measure tran outp_end_v FIND v(outp) AT=500p
.measure tran outn_end_v FIND v(outn) AT=500p
.measure tran tail_end_v FIND v(tail) AT=500p
.control
set noaskquit
run
.endc
.end
