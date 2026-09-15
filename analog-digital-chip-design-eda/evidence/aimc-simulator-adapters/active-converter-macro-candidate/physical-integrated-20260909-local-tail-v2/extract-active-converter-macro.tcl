drc on
path search +/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-converter-macro-candidate/physical-integrated-20260909-local-tail-v2 +/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells
load aimc_converter_macro_active_candidate -force
select top cell
flatten aimc_converter_macro_active_candidate_flat
load aimc_converter_macro_active_candidate_flat -force
select top cell
drc check
drc count
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o aimc_converter_macro_active_candidate_extracted.spice
quit -noprompt
