drc on
path search +/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-converter-macro-candidate/two-single-preamp-parent-wired-20260913T501000Z
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
