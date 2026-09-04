drc off
path search +/home/mehtama1/git-repo/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells
load aimc_converter_macro -force
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o aimc_converter_macro_layout_smoke.spice
quit -noprompt
