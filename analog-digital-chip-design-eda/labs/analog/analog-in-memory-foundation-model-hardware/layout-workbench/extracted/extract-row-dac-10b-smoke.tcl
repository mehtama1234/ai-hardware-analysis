drc off
path search +/home/mehtama1/git-repo/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells
load row_dac_10b -force
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o row_dac_10b_layout_smoke.spice
quit -noprompt
