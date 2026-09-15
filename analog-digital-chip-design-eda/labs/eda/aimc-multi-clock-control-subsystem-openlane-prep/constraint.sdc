create_clock -name core_clock -period 10.000 [get_ports core_clk]
create_clock -name maintenance_clock -period 20.000 [get_ports maintenance_clk]
set_clock_groups -asynchronous -group [get_clocks core_clock] -group [get_clocks maintenance_clock]
