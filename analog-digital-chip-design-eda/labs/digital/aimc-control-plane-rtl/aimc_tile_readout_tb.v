`timescale 1ns/1ps

module aimc_tile_readout_tb;
    reg clk = 0;
    reg rst_n = 0;
    reg sample_valid = 0;
    reg tile_enabled = 1;
    reg [11:0] adc_code = 12'd0;
    reg signed [8:0] zero_code = 9'sd128;
    reg signed [8:0] gain_q6 = 9'sd64;
    reg signed [15:0] bias = 16'sd0;
    reg [9:0] residual_abs = 10'd0;
    reg [9:0] residual_budget = 10'd20;
    reg [15:0] calibration_age = 16'd0;
    wire signed [15:0] corrected_value;
    wire output_valid;
    wire fallback;
    wire [3:0] reason;

    aimc_tile_readout dut (
        .clk(clk),
        .rst_n(rst_n),
        .sample_valid(sample_valid),
        .tile_enabled(tile_enabled),
        .adc_code(adc_code),
        .zero_code(zero_code),
        .gain_q6(gain_q6),
        .bias(bias),
        .residual_abs(residual_abs),
        .residual_budget(residual_budget),
        .calibration_age(calibration_age),
        .corrected_value(corrected_value),
        .output_valid(output_valid),
        .fallback(fallback),
        .reason(reason)
    );

    always #5 clk = ~clk;

    task run_sample;
        input [160*8:1] name;
        input in_tile_enabled;
        input [11:0] in_adc_code;
        input signed [8:0] in_zero_code;
        input signed [8:0] in_gain_q6;
        input signed [15:0] in_bias;
        input [9:0] in_residual_abs;
        input [15:0] in_calibration_age;
        input signed [15:0] expected_value;
        input expected_valid;
        input expected_fallback;
        input [3:0] expected_reason;
        begin
            @(negedge clk);
            tile_enabled = in_tile_enabled;
            adc_code = in_adc_code;
            zero_code = in_zero_code;
            gain_q6 = in_gain_q6;
            bias = in_bias;
            residual_abs = in_residual_abs;
            calibration_age = in_calibration_age;
            sample_valid = 1'b1;
            @(negedge clk);
            sample_valid = 1'b0;
            #1;
            $display("%0s,value=%0d,valid=%0d,fallback=%0d,reason=%0d",
                name, corrected_value, output_valid, fallback, reason);
            if (corrected_value !== expected_value ||
                output_valid !== expected_valid ||
                fallback !== expected_fallback ||
                reason !== expected_reason) begin
                $display("FAIL %0s expected value=%0d valid=%0d fallback=%0d reason=%0d",
                    name, expected_value, expected_valid, expected_fallback, expected_reason);
                $finish;
            end
        end
    endtask

    initial begin
        $dumpfile("aimc_tile_readout.vcd");
        $dumpvars(0, aimc_tile_readout_tb);

        repeat (2) @(negedge clk);
        rst_n = 1'b1;

        run_sample("centered_adc_with_unit_gain", 1'b1, 12'd160, 9'sd128, 9'sd64, 16'sd0, 10'd3, 16'd32, 16'sd32, 1'b1, 1'b0, 4'd0);
        run_sample("gain_and_bias_correction", 1'b1, 12'd160, 9'sd128, 9'sd96, -16'sd5, 10'd3, 16'd32, 16'sd43, 1'b1, 1'b0, 4'd0);
        run_sample("disabled_tile_fallback", 1'b0, 12'd160, 9'sd128, 9'sd64, 16'sd0, 10'd3, 16'd32, 16'sd32, 1'b0, 1'b1, 4'd1);
        run_sample("residual_fallback", 1'b1, 12'd160, 9'sd128, 9'sd64, 16'sd0, 10'd40, 16'd32, 16'sd32, 1'b0, 1'b1, 4'd2);
        run_sample("stale_calibration_fallback", 1'b1, 12'd160, 9'sd128, 9'sd64, 16'sd0, 10'd3, 16'd2048, 16'sd32, 1'b0, 1'b1, 4'd3);
        run_sample("high_saturation_fallback", 1'b1, 12'd4095, 9'sd0, 9'sd64, 16'sd0, 10'd3, 16'd32, 16'sd2047, 1'b0, 1'b1, 4'd4);
        run_sample("low_saturation_fallback", 1'b1, 12'd0, 9'sd255, 9'sd64, -16'sd2000, 10'd3, 16'd32, -16'sd2048, 1'b0, 1'b1, 4'd5);

        $display("PASS aimc_tile_readout_tb");
        $finish;
    end
endmodule
