drc off
load aimc_magic_smoke_wire -force
box 0 0 200 40
paint metal1
label smoke_node center metal1
port make
save aimc_magic_smoke_wire
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o aimc_magic_smoke_wire.spice
quit -noprompt
