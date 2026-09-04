* Sky130 differential dummy-cancellation candidate mismatch sweep.
* The fixed 0.50x dummy candidate is perturbed by scaling one differential side.

.lib "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.param vdd=1.8
.param lmin=0.15
.param wn_p=1.96
.param wp_p=3.92
.param dwn_p=0.98
.param dwp_p=1.96
.param wn_n=2.0
.param wp_n=4.0
.param dwn_n=1.0
.param dwp_n=2.0
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

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={wn_p} L={lmin}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={wp_p} L={lmin}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={wn_n} L={lmin}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={wp_n} L={lmin}
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={dwn_p} L={lmin}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={dwp_p} L={lmin}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={dwn_n} L={lmin}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={dwp_n} L={lmin}

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
