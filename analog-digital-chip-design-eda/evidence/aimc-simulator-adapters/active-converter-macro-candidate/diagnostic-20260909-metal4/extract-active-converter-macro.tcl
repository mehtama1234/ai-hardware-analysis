drc on
path search +/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-converter-macro-candidate/diagnostic-20260909-metal4 +/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells
load aimc_converter_macro_active_candidate -force
flatten -tree
select top cell
drc check
drc count
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o aimc_converter_macro_active_candidate_extracted.spice
quit -noprompt
