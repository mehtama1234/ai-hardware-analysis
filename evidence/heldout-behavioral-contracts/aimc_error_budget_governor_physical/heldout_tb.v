`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst_n = 1, sample_valid = 0, analog_candidate = 0;
    reg [7:0] residual_q8 = 0, sensitivity_q8 = 0, cumulative_error_q8 = 0;
    reg [3:0] drift_age = 0;
    wire [1:0] service_decision, tile_action;
    wire [3:0] reason;
    wire [7:0] next_cumulative_error_q8;
    aimc_error_budget_governor_physical dut(.*);
    always #5 clk = ~clk;
    initial begin
        $dumpfile("trace.vcd"); $dumpvars(0, dut);
        #1 rst_n = 0; #1;
        if (service_decision !== 0 || tile_action !== 0 || reason !== 0 || next_cumulative_error_q8 !== 0)
            $display("FAIL reset outputs");
        else $display("PASS heldout error-budget physical reset contract");
        $finish;
    end
endmodule
