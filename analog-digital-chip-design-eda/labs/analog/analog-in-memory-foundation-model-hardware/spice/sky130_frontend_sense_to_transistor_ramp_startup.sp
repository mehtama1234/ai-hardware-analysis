* Frontend-sense to Sky130 transistor ramp-startup handoff.
* Inputs ramp from common-mode to the measured extracted-frontend sense voltage.
* This does not include the extracted frontend transient, latch, SAR, or accepted converter evidence.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param rd=100k
.param itail=20u
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {vdd}
VINP inp 0 PWL(0 0.9 100p 0.9 700p 0.900033500000 2n 0.900033500000)
VINN inn 0 PWL(0 0.9 100p 0.9 700p 0.899966500000 2n 0.899966500000)
RDP vdd outp {rd}
RDN vdd outn {rd}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
ITAIL tail 0 {itail}
COUTP outp 0 2f
COUTN outn 0 2f

.ic v(outp)=0.8 v(outn)=0.8 v(tail)=0.231
.tran 100p 2n uic
.measure tran outp_end_v FIND v(outp) AT=2n
.measure tran outn_end_v FIND v(outn) AT=2n
.measure tran tail_end_v FIND v(tail) AT=2n
.control
set noaskquit
run
.endc
.end
