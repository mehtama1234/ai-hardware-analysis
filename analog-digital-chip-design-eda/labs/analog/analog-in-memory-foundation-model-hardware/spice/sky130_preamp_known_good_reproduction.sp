* Sky130 preamp known-good reproduction.
* This reproduces the passing comparator input-stage deck shape.
* It is not extracted layout, not a latch, and not accepted converter evidence.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param vinp=0.900033500000
.param vinn=0.899966500000
.param rd=100k
.param itail=20u

VDD vdd 0 {vdd}
VINP inp 0 {vinp}
VINN inn 0 {vinn}
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
