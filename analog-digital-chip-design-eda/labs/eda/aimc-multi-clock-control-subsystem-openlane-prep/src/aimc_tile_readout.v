module aimc_tile_readout (
    input wire clk,
    input wire rst_n,
    input wire sample_valid,
    input wire tile_enabled,
    input wire [11:0] adc_code,
    input wire signed [8:0] zero_code,
    input wire signed [8:0] gain_q6,
    input wire signed [15:0] bias,
    input wire [9:0] residual_abs,
    input wire [9:0] residual_budget,
    input wire [15:0] calibration_age,
    output reg signed [15:0] corrected_value,
    output reg output_valid,
    output reg fallback,
    output reg [3:0] reason
);
    localparam REASON_OK = 4'd0;
    localparam REASON_TILE_DISABLED = 4'd1;
    localparam REASON_RESIDUAL_HIGH = 4'd2;
    localparam REASON_CALIBRATION_STALE = 4'd3;
    localparam REASON_SATURATED_HIGH = 4'd4;
    localparam REASON_SATURATED_LOW = 4'd5;

    localparam [15:0] MAX_CALIBRATION_AGE = 16'd1024;

    wire signed [15:0] centered_adc = $signed({4'b0000, adc_code}) - {{7{zero_code[8]}}, zero_code};
    wire signed [25:0] scaled = centered_adc * gain_q6;
    wire signed [25:0] corrected_wide = $signed(scaled >>> 6) + {{10{bias[15]}}, bias};

    wire saturated_high = corrected_wide > 26'sd2047;
    wire saturated_low = corrected_wide < -26'sd2048;
    wire residual_high = residual_abs > residual_budget;
    wire calibration_stale = calibration_age >= MAX_CALIBRATION_AGE;
    wire should_fallback = (!tile_enabled) || residual_high || calibration_stale || saturated_high || saturated_low;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            corrected_value <= 16'sd0;
            output_valid <= 1'b0;
            fallback <= 1'b0;
            reason <= REASON_OK;
        end else begin
            output_valid <= 1'b0;
            fallback <= 1'b0;
            reason <= REASON_OK;

            if (sample_valid) begin
                output_valid <= !should_fallback;
                fallback <= should_fallback;

                if (saturated_high) begin
                    corrected_value <= 16'sd2047;
                    reason <= REASON_SATURATED_HIGH;
                end else if (saturated_low) begin
                    corrected_value <= -16'sd2048;
                    reason <= REASON_SATURATED_LOW;
                end else begin
                    corrected_value <= corrected_wide[15:0];
                    if (!tile_enabled) begin
                        reason <= REASON_TILE_DISABLED;
                    end else if (residual_high) begin
                        reason <= REASON_RESIDUAL_HIGH;
                    end else if (calibration_stale) begin
                        reason <= REASON_CALIBRATION_STALE;
                    end else begin
                        reason <= REASON_OK;
                    end
                end
            end
        end
    end
endmodule
