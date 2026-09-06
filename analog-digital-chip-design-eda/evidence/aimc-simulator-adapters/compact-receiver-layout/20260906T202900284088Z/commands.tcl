load compact_receiver -force
box position 0um 0um
box size 0um 0um
sky130::sky130_fd_pr__nfet_01v8_draw [sky130::sky130_fd_pr__nfet_01v8_defaults]
box position 0um 5um
box size 0um 0um
sky130::sky130_fd_pr__pfet_01v8_draw [sky130::sky130_fd_pr__pfet_01v8_defaults]
save compact_receiver
select top cell
drc on
drc catchup
drc count
extract all
ext2spice lvs
ext2spice hierarchy off
ext2spice subcircuit on
ext2spice subcircuit top on
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o extracted.spice
quit -noprompt
