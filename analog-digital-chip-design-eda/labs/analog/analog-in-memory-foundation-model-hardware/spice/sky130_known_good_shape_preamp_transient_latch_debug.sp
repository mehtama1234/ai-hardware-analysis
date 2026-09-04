* Sky130 known-good-shape preamp transient latch debug.
* Same simple OP-passing preamp shape, no latch attached.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param vinp=0.900076485293
.param vinn=0.899923514707
.param rd=100k
.param itail=20u
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {vdd}
VINP inp 0 PWL(0 0.9 100p 0.9 500p {vinp} 2n {vinp})
VINN inn 0 PWL(0 0.9 100p 0.9 500p {vinn} 2n {vinn})
RDP vdd outp {rd}
RDN vdd outn {rd}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
ITAIL tail 0 {itail}
COUTP outp 0 2f
COUTN outn 0 2f

.ic v(outp)=0.799296100000 v(outn)=0.800703700000 v(tail)=0.231080700000
.tran 20p 2n uic
.measure tran outp_1p2n_v FIND v(outp) AT=1.20n
.measure tran outn_1p2n_v FIND v(outn) AT=1.20n
.measure tran outp_1p6n_v FIND v(outp) AT=1.60n
.measure tran outn_1p6n_v FIND v(outn) AT=1.60n
.measure tran outp_2n_v FIND v(outp) AT=2.00n
.measure tran outn_2n_v FIND v(outn) AT=2.00n
.measure tran tail_2n_v FIND v(tail) AT=2.00n
.control
set noaskquit
run
.endc

.end
