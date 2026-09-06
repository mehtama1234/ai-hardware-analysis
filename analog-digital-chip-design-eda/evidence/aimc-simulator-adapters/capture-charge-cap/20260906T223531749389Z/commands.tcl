load capture_charge_cap -force
box position 0um 0um
box size 0um 0um
sky130::sky130_fd_pr__cap_mim_m3_1_draw [sky130::sky130_fd_pr__cap_mim_m3_1_defaults]
save capture_charge_cap
drc on
drc catchup
drc count
drc listall why
extract all
ext2spice lvs
ext2spice hierarchy off
ext2spice subcircuit on
ext2spice subcircuit top on
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o extracted.spice
quit -noprompt
