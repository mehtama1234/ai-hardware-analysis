create_clock -name clk -period 1.000 [get_ports clk]
set_input_delay 0.100 -clock clk [remove_from_collection [all_inputs] [get_ports clk]]
set_output_delay 0.100 -clock clk [all_outputs]
set_clock_uncertainty 0.050 [get_clocks clk]
