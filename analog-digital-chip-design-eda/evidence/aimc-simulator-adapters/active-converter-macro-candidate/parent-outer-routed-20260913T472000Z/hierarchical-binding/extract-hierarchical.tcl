drc on
path search +/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-converter-macro-candidate/parent-outer-routed-20260913T472000Z
load aimc_converter_macro_active_candidate -force
select top cell
drc check
drc count
extract all
ext2spice hierarchy on
ext2spice subcircuit on
ext2spice subcircuit top on
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o hierarchical.spice
quit -noprompt
