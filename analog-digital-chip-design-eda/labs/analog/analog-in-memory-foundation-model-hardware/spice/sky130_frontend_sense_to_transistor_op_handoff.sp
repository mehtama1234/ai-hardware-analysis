* Frontend-sense to Sky130 transistor OP handoff.
* This uses the measured extracted-frontend sense voltage as DC input to the real Sky130 input pair.
* It does not include the extracted frontend transient, latch, SAR loop, or accepted converter payload.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param rd=100k
.param itail=20u
.options reltol=1e-4 abstol=1e-14 vntol=1e-8 gmin=1e-12

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

.op
.control
op
.endc
.end
