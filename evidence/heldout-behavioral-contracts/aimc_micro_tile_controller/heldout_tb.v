`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst_n = 0;
    reg sample_valid = 0;
    reg [3:0] op_class = 4'd1;
    reg resident_weights = 1;
    reg [7:0] tile_id = 8'd3;
    reg tile_enabled = 0;
    reg [11:0] adc_code = 12'd160;
    reg signed [8:0] zero_code = 9'sd128, gain_q6 = 9'sd64;
    reg signed [15:0] bias = 0;
    reg [7:0] estimated_state_error = 0, state_error_budget = 8'd100;
    reg [7:0] attention_flip_rate = 0, attention_flip_budget = 8'd15;
    reg [7:0] token_flip_rate = 0, token_flip_budget = 8'd15;
    reg [9:0] residual_abs = 0, residual_budget = 10'd20;
    reg [15:0] calibration_age = 0;
    reg [7:0] weak_tiles = 0;
    reg calibration_done = 0, probe_request = 0, probe_passed = 0, probe_failed = 0;
    wire signed [15:0] corrected_value;
    wire [1:0] execution_path, tile_health_action;
    wire [3:0] reason;
    wire [7:0] last_fallback_tile_id;
    wire [15:0] fallback_count, accepted_count, residual_fallback_count, stale_fallback_count;

    aimc_micro_tile_controller dut (.*);
    always #5 clk = ~clk;

    initial begin
        $dumpfile("trace.vcd");
        $dumpvars(0, dut);
        repeat (2) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        sample_valid = 1;
        repeat (3) @(posedge clk);
        #1;
        if (execution_path !== 2'd0 || reason !== 4'd9 || fallback_count !== 16'd1) begin
            $display("FAIL disabled tile fallback path=%0d reason=%0d fallback_count=%0d", execution_path, reason, fallback_count);
        end else begin
            $display("PASS heldout disabled tile fallback contract");
        end
        $finish;
    end
endmodule
