module aimc_multi_clock_control_subsystem (
    input wire core_clk,
    input wire maintenance_clk,
    input wire rst_n,
    input wire maintenance_budget_async,
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
    input wire analog_candidate,
    input wire [7:0] requested_tile_id,
    input wire [1:0] tile1_health_action,
    input wire [1:0] tile2_health_action,
    input wire [1:0] tile3_health_action,
    input wire [3:0] tile_busy,
    input wire [3:0] drift_age,
    input wire [7:0] sensitivity_q8,
    input wire [7:0] cumulative_error_q8,
    output wire signed [15:0] corrected_value,
    output wire [1:0] execution_path,
    output wire [3:0] controller_reason,
    output wire [7:0] last_fallback_tile_id,
    output wire [15:0] fallback_count,
    output wire [15:0] accepted_count,
    output wire [15:0] residual_fallback_count,
    output wire [15:0] stale_fallback_count,
    output wire [1:0] tile0_health_action,
    output wire [1:0] final_decision,
    output wire [1:0] selected_tile,
    output wire [3:0] governor_reason,
    output wire [7:0] next_cumulative_error_q8,
    output wire maintenance_budget_core
);
    reg maintenance_budget_maintenance;
    reg maintenance_budget_sync1;
    reg maintenance_budget_sync2;
    reg sample_valid_core;
    reg [3:0] op_class_core;
    reg resident_weights_core, tile_enabled_core;
    reg [7:0] tile_id_core;
    reg [11:0] adc_code_core;
    reg signed [8:0] zero_code_core, gain_q6_core;
    reg signed [15:0] bias_core;
    reg [7:0] estimated_state_error_core, state_error_budget_core;
    reg [7:0] attention_flip_rate_core, attention_flip_budget_core;
    reg [7:0] token_flip_rate_core, token_flip_budget_core;
    reg [9:0] residual_abs_core, residual_budget_core;
    reg [15:0] calibration_age_core;
    reg [7:0] weak_tiles_core;
    reg calibration_done_core, probe_request_core, probe_passed_core, probe_failed_core;

    always @(posedge maintenance_clk or negedge rst_n) begin
        if (!rst_n) begin
            maintenance_budget_maintenance <= 1'b0;
        end else begin
            maintenance_budget_maintenance <= maintenance_budget_async;
        end
    end

    always @(posedge core_clk or negedge rst_n) begin
        if (!rst_n) begin
            maintenance_budget_sync1 <= 1'b0;
            maintenance_budget_sync2 <= 1'b0;
            sample_valid_core <= 1'b0;
            op_class_core <= 4'd0;
            resident_weights_core <= 1'b0;
            tile_enabled_core <= 1'b0;
            tile_id_core <= 8'd0;
            adc_code_core <= 12'd0;
            zero_code_core <= 9'sd0;
            gain_q6_core <= 9'sd0;
            bias_core <= 16'sd0;
            estimated_state_error_core <= 8'd0;
            state_error_budget_core <= 8'd0;
            attention_flip_rate_core <= 8'd0;
            attention_flip_budget_core <= 8'd0;
            token_flip_rate_core <= 8'd0;
            token_flip_budget_core <= 8'd0;
            residual_abs_core <= 10'd0;
            residual_budget_core <= 10'd0;
            calibration_age_core <= 16'd0;
            weak_tiles_core <= 8'd0;
            calibration_done_core <= 1'b0;
            probe_request_core <= 1'b0;
            probe_passed_core <= 1'b0;
            probe_failed_core <= 1'b0;
        end else begin
            maintenance_budget_sync1 <= maintenance_budget_maintenance;
            maintenance_budget_sync2 <= maintenance_budget_sync1;
            sample_valid_core <= sample_valid;
            op_class_core <= op_class;
            resident_weights_core <= resident_weights;
            tile_enabled_core <= tile_enabled;
            tile_id_core <= tile_id;
            adc_code_core <= adc_code;
            zero_code_core <= zero_code;
            gain_q6_core <= gain_q6;
            bias_core <= bias;
            estimated_state_error_core <= estimated_state_error;
            state_error_budget_core <= state_error_budget;
            attention_flip_rate_core <= attention_flip_rate;
            attention_flip_budget_core <= attention_flip_budget;
            token_flip_rate_core <= token_flip_rate;
            token_flip_budget_core <= token_flip_budget;
            residual_abs_core <= residual_abs;
            residual_budget_core <= residual_budget;
            calibration_age_core <= calibration_age;
            weak_tiles_core <= weak_tiles;
            calibration_done_core <= calibration_done;
            probe_request_core <= probe_request;
            probe_passed_core <= probe_passed;
            probe_failed_core <= probe_failed;
        end
    end

    assign maintenance_budget_core = maintenance_budget_sync2;

    aimc_micro_tile_controller tile_controller (
        .clk(core_clk),
        .rst_n(rst_n),
        .sample_valid(sample_valid_core),
        .op_class(op_class_core),
        .resident_weights(resident_weights_core),
        .tile_id(tile_id_core),
        .tile_enabled(tile_enabled_core),
        .adc_code(adc_code_core),
        .zero_code(zero_code_core),
        .gain_q6(gain_q6_core),
        .bias(bias_core),
        .estimated_state_error(estimated_state_error_core),
        .state_error_budget(state_error_budget_core),
        .attention_flip_rate(attention_flip_rate_core),
        .attention_flip_budget(attention_flip_budget_core),
        .token_flip_rate(token_flip_rate_core),
        .token_flip_budget(token_flip_budget_core),
        .residual_abs(residual_abs_core),
        .residual_budget(residual_budget_core),
        .calibration_age(calibration_age_core),
        .weak_tiles(weak_tiles_core),
        .calibration_done(calibration_done_core),
        .probe_request(probe_request_core),
        .probe_passed(probe_passed_core),
        .probe_failed(probe_failed_core),
        .corrected_value(corrected_value),
        .execution_path(execution_path),
        .reason(controller_reason),
        .last_fallback_tile_id(last_fallback_tile_id),
        .fallback_count(fallback_count),
        .accepted_count(accepted_count),
        .residual_fallback_count(residual_fallback_count),
        .stale_fallback_count(stale_fallback_count),
        .tile_health_action(tile0_health_action)
    );

    aimc_scheduler_governor scheduler_governor (
        .sample_valid(sample_valid),
        .analog_candidate(analog_candidate),
        .requested_tile_id(requested_tile_id),
        .tile0_health_action(tile0_health_action),
        .tile1_health_action(tile1_health_action),
        .tile2_health_action(tile2_health_action),
        .tile3_health_action(tile3_health_action),
        .tile_busy(tile_busy),
        .maintenance_budget({1'b0, maintenance_budget_core}),
        .residual_q8({6'd0, residual_abs[9:8]}),
        .drift_age(drift_age),
        .sensitivity_q8(sensitivity_q8),
        .cumulative_error_q8(cumulative_error_q8),
        .final_decision(final_decision),
        .selected_tile(selected_tile),
        .final_reason(governor_reason),
        .next_cumulative_error_q8(next_cumulative_error_q8)
    );
endmodule
