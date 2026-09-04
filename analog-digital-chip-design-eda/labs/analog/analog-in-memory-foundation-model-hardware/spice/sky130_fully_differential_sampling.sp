* Sky130 fully differential sampling fixture.
* Two matched transmission gates sample opposite sides of a differential voltage.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param csample=0.2p
.param cload=0.05p
.param vinp=1.0
.param vinn=0.8

VDD vdd 0 {vdd}
VSS vss 0 0
VINP inp 0 PULSE(0 {vinp} 0.1n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {vinn} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {vdd} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({vdd} 0 0.2n 20p 20p 7n 20n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={wn} L={lmin}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={wp} L={lmin}

CSP sp 0 {csample}
CSN sn 0 {csample}
CLP sp 0 {cload}
CLN sn 0 {cload}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

.tran 2p 10n
.measure tran acquired_p_v FIND v(sp) AT=6.8n
.measure tran acquired_n_v FIND v(sn) AT=6.8n
.measure tran held_p_v FIND v(sp) AT=8.5n
.measure tran held_n_v FIND v(sn) AT=8.5n
.measure tran input_p_v FIND v(inp) AT=6.8n
.measure tran input_n_v FIND v(inn) AT=6.8n
.control
run
.endc

.end
