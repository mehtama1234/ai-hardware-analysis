# OpenLane's base constraints provide the standard I/O and core-clock model.
source $::env(SCRIPTS_DIR)/base.sdc

# The maintenance domain is sampled before the two-flop synchronizer.
create_clock -name maintenance_clk -period 20.000 [get_ports maintenance_clk]
set_clock_uncertainty 0.250 [get_clocks maintenance_clk]
set_clock_groups -asynchronous \
    -group [get_clocks core_clk] \
    -group [get_clocks maintenance_clk]
set_false_path -from [get_ports rst_n]
