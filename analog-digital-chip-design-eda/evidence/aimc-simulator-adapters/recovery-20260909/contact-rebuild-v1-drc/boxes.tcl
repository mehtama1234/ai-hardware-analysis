drc on
load aimc_converter_macro_active_candidate -force
select top cell
flatten aimc_converter_macro_active_candidate_flat
load aimc_converter_macro_active_candidate_flat -force
select top cell
drc check
drc catchup
foreach {why boxes} [drc listall why] {puts "DRC_BOXES	$why	$boxes"}
puts DRC_AUDIT_COMPLETE
quit -noprompt
