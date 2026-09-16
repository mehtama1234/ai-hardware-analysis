`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst_n = 1, resident_weights = 0;
    reg [3:0] op_class = 0;
    reg [7:0] estimated_state_error = 0, state_error_budget = 0, attention_flip_rate = 0,
               attention_flip_budget = 0, token_flip_rate = 0, token_flip_budget = 0, weak_tiles = 0;
    reg [15:0] calibration_age = 0;
    wire [1:0] placement;
    wire [3:0] reason;
    aimc_operation_partition_physical dut(.*);
    always #5 clk = ~clk;
    initial begin
        $dumpfile("trace.vcd"); $dumpvars(0, dut);
        #1 rst_n = 0; #1;
        if (placement !== 0 || reason !== 0) $display("FAIL reset outputs");
        else $display("PASS heldout operation-partition physical reset contract");
        $finish;
    end
endmodule
