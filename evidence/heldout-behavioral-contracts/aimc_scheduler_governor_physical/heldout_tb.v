`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst_n = 0;
    reg sample_valid = 0, analog_candidate = 0;
    reg [7:0] requested_tile_id = 8'd2;
    reg [1:0] tile0_health_action = 0, tile1_health_action = 0, tile2_health_action = 0, tile3_health_action = 0;
    reg [3:0] tile_busy = 0;
    reg [1:0] maintenance_budget = 0;
    reg [7:0] residual_q8 = 0;
    reg [3:0] drift_age = 0;
    reg [7:0] sensitivity_q8 = 0, cumulative_error_q8 = 0;
    wire [1:0] final_decision, selected_tile;
    wire [3:0] final_reason;
    wire [7:0] next_cumulative_error_q8;

    aimc_scheduler_governor_physical dut (.*);
    always #5 clk = ~clk;

    initial begin
        $dumpfile("trace.vcd");
        $dumpvars(0, dut);
        repeat (2) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        sample_valid = 1;
        analog_candidate = 1;
        repeat (3) @(posedge clk);
        #1;
        if (final_decision !== 2'd1 || selected_tile !== 2'd2 || final_reason !== 4'd9) begin
            $display("FAIL physical scheduler decision=%0d tile=%0d reason=%0d", final_decision, selected_tile, final_reason);
        end else begin
            $display("PASS heldout physical scheduler contract");
        end
        $finish;
    end
endmodule
