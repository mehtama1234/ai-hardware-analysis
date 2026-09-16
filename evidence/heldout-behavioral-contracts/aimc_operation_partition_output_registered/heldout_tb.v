`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst_n = 0;
    reg [3:0] op_class = 4'd1;
    reg resident_weights = 1;
    reg [7:0] estimated_state_error = 0, state_error_budget = 8'd100;
    reg [7:0] attention_flip_rate = 0, attention_flip_budget = 8'd15;
    reg [7:0] token_flip_rate = 0, token_flip_budget = 8'd15;
    reg [15:0] calibration_age = 0;
    reg [7:0] weak_tiles = 0;
    wire [1:0] placement;
    wire [3:0] reason;

    aimc_operation_partition_output_registered dut (.*);
    always #5 clk = ~clk;

    initial begin
        $dumpfile("trace.vcd");
        $dumpvars(0, dut);
        repeat (2) @(negedge clk);
        rst_n = 1;
        @(posedge clk);
        #1;
        if (placement !== 2'd1 || reason !== 4'd1) begin
            $display("FAIL registered QKV placement=%0d reason=%0d", placement, reason);
        end else begin
            $display("PASS heldout registered fixed-weight contract");
        end
        $finish;
    end
endmodule
