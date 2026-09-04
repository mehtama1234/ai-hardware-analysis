module aimc_micro_tile_controller (
    input wire clk,
    input wire rst_n,
    input wire sample_valid,
    input wire [3:0] op_class,
    input wire resident_weights,
    input wire [7:0] tile_id,
    input wire tile_enabled,
    input wire [11:0] adc_code,
    input wire signed [8:0] zero_code,
    input wire signed [8:0] gain_q6,
    input wire signed [15:0] bias,
    input wire [7:0] estimated_state_error,
    input wire [7:0] state_error_budget,
    input wire [7:0] attention_flip_rate,
    input wire [7:0] attention_flip_budget,
    input wire [7:0] token_flip_rate,
    input wire [7:0] token_flip_budget,
    input wire [9:0] residual_abs,
    input wire [9:0] residual_budget,
    input wire [15:0] calibration_age,
    input wire [7:0] weak_tiles,
    input wire calibration_done,
    input wire probe_request,
    input wire probe_passed,
    input wire probe_failed,
    output wire signed [15:0] corrected_value,
    output reg [1:0] execution_path,
    output reg [3:0] reason,
    output reg [7:0] last_fallback_tile_id,
    output reg [15:0] fallback_count,
    output reg [15:0] accepted_count,
    output reg [15:0] residual_fallback_count,
    output reg [15:0] stale_fallback_count,
    output reg [1:0] tile_health_action
);
    localparam PLACE_DIGITAL = 2'd0;
    localparam PLACE_ANALOG = 2'd1;
    localparam PLACE_HYBRID = 2'd2;

    localparam EXEC_DIGITAL = 2'd0;
    localparam EXEC_ANALOG_ACCEPTED = 2'd1;
    localparam EXEC_HYBRID_REVIEW = 2'd2;

    localparam REASON_PARTITION_DIGITAL = 4'd0;
    localparam REASON_ANALOG_ACCEPTED = 4'd1;
    localparam REASON_HYBRID_REVIEW = 4'd2;
    localparam REASON_TILE_READOUT_FALLBACK = 4'd8;
    localparam READOUT_REASON_RESIDUAL_HIGH = 4'd2;
    localparam READOUT_REASON_CALIBRATION_STALE = 4'd3;
    localparam TILE_SERVE = 2'd0;
    localparam TILE_RECALIBRATE = 2'd1;
    localparam TILE_DISABLE = 2'd2;
    localparam TILE_PROBE = 2'd3;

    wire [1:0] placement;
    wire [3:0] partition_reason;
    wire readout_valid;
    wire readout_fallback;
    wire [3:0] readout_reason;
    reg analog_read_pending;
    reg [7:0] pending_tile_id;

    aimc_operation_partition partition (
        .op_class(op_class),
        .resident_weights(resident_weights),
        .estimated_state_error(estimated_state_error),
        .state_error_budget(state_error_budget),
        .attention_flip_rate(attention_flip_rate),
        .attention_flip_budget(attention_flip_budget),
        .token_flip_rate(token_flip_rate),
        .token_flip_budget(token_flip_budget),
        .calibration_age(calibration_age),
        .weak_tiles(weak_tiles),
        .placement(placement),
        .reason(partition_reason)
    );

    aimc_tile_readout readout (
        .clk(clk),
        .rst_n(rst_n),
        .sample_valid(sample_valid && (placement == PLACE_ANALOG)),
        .tile_enabled(tile_enabled),
        .adc_code(adc_code),
        .zero_code(zero_code),
        .gain_q6(gain_q6),
        .bias(bias),
        .residual_abs(residual_abs),
        .residual_budget(residual_budget),
        .calibration_age(calibration_age),
        .corrected_value(corrected_value),
        .output_valid(readout_valid),
        .fallback(readout_fallback),
        .reason(readout_reason)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            execution_path <= EXEC_DIGITAL;
            reason <= REASON_PARTITION_DIGITAL;
            analog_read_pending <= 1'b0;
            pending_tile_id <= 8'd0;
            last_fallback_tile_id <= 8'd0;
            fallback_count <= 16'd0;
            accepted_count <= 16'd0;
            residual_fallback_count <= 16'd0;
            stale_fallback_count <= 16'd0;
            tile_health_action <= TILE_SERVE;
        end else if (tile_health_action == TILE_DISABLE && probe_request) begin
            tile_health_action <= TILE_PROBE;
        end else if (tile_health_action == TILE_PROBE && probe_passed) begin
            tile_health_action <= TILE_SERVE;
        end else if (tile_health_action == TILE_PROBE && probe_failed) begin
            tile_health_action <= TILE_DISABLE;
        end else if (tile_health_action == TILE_RECALIBRATE && calibration_done) begin
            tile_health_action <= TILE_SERVE;
        end else if (analog_read_pending) begin
            analog_read_pending <= 1'b0;
            if (readout_fallback) begin
                execution_path <= EXEC_DIGITAL;
                reason <= REASON_TILE_READOUT_FALLBACK | readout_reason;
                last_fallback_tile_id <= pending_tile_id;
                if (fallback_count != 16'hffff) begin
                    fallback_count <= fallback_count + 16'd1;
                end
                if (readout_reason == READOUT_REASON_RESIDUAL_HIGH && residual_fallback_count != 16'hffff) begin
                    residual_fallback_count <= residual_fallback_count + 16'd1;
                    if (residual_fallback_count >= 16'd1) begin
                        tile_health_action <= TILE_DISABLE;
                    end
                end
                if (readout_reason == READOUT_REASON_CALIBRATION_STALE && stale_fallback_count != 16'hffff) begin
                    stale_fallback_count <= stale_fallback_count + 16'd1;
                    if (tile_health_action != TILE_DISABLE) begin
                        tile_health_action <= TILE_RECALIBRATE;
                    end
                end
            end else if (readout_valid) begin
                execution_path <= EXEC_ANALOG_ACCEPTED;
                reason <= REASON_ANALOG_ACCEPTED;
                if (accepted_count != 16'hffff) begin
                    accepted_count <= accepted_count + 16'd1;
                end
            end else begin
                execution_path <= EXEC_DIGITAL;
                reason <= REASON_TILE_READOUT_FALLBACK;
            end
        end else if (sample_valid) begin
            if (placement == PLACE_DIGITAL) begin
                execution_path <= EXEC_DIGITAL;
                reason <= partition_reason;
            end else if (placement == PLACE_HYBRID) begin
                execution_path <= EXEC_HYBRID_REVIEW;
                reason <= REASON_HYBRID_REVIEW;
            end else begin
                analog_read_pending <= 1'b1;
                pending_tile_id <= tile_id;
            end
        end
    end
endmodule
