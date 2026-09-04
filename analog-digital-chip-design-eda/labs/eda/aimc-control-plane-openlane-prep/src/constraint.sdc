set_units -time ns
create_clock [get_ports clk] -name core_clock -period 10.000
set_input_delay 1.000 -clock core_clock [all_inputs]
set_output_delay 1.000 -clock core_clock [all_outputs]
set_false_path -from [get_ports rst_n]
