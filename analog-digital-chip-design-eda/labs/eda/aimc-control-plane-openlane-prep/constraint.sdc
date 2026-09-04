create_clock -name clk -period 10.000 [get_ports clk]
set_input_delay 1.000 -clock clk [all_inputs]
set_output_delay 1.000 -clock clk [all_outputs]
set_false_path -from [get_ports rst_n]
