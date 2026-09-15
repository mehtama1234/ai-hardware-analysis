// Solver-backed bounded properties for the stateful micro-tile controller.
// This harness intentionally excludes the multi-clock wrapper: CDC evidence
// remains a separate simulation-backed campaign until a multi-clock formal
// model and assumptions are established.
module aimc_micro_tile_controller_formal;
  reg clk;
  reg rst_n;
  reg sample_valid;
  reg [3:0] op_class;
  reg resident_weights;
  reg [7:0] tile_id;
  reg tile_enabled;
  reg [11:0] adc_code;
  reg signed [8:0] zero_code, gain_q6;
  reg signed [15:0] bias;
  reg [7:0] estimated_state_error, state_error_budget;
  reg [7:0] attention_flip_rate, attention_flip_budget;
  reg [7:0] token_flip_rate, token_flip_budget;
  reg [9:0] residual_abs, residual_budget;
  reg [15:0] calibration_age;
  reg [7:0] weak_tiles;
  reg calibration_done, probe_request, probe_passed, probe_failed;
  wire signed [15:0] corrected_value;
  wire [1:0] execution_path;
  wire [3:0] reason;
  wire [7:0] last_fallback_tile_id;
  wire [15:0] fallback_count, accepted_count;
  wire [15:0] residual_fallback_count, stale_fallback_count;
  wire [1:0] tile_health_action;

  aimc_micro_tile_controller dut(
    .clk(clk), .rst_n(rst_n), .sample_valid(sample_valid), .op_class(op_class),
    .resident_weights(resident_weights), .tile_id(tile_id),
    .tile_enabled(tile_enabled), .adc_code(adc_code), .zero_code(zero_code),
    .gain_q6(gain_q6), .bias(bias),
    .estimated_state_error(estimated_state_error),
    .state_error_budget(state_error_budget),
    .attention_flip_rate(attention_flip_rate),
    .attention_flip_budget(attention_flip_budget),
    .token_flip_rate(token_flip_rate), .token_flip_budget(token_flip_budget),
    .residual_abs(residual_abs), .residual_budget(residual_budget),
    .calibration_age(calibration_age), .weak_tiles(weak_tiles),
    .calibration_done(calibration_done), .probe_request(probe_request),
    .probe_passed(probe_passed), .probe_failed(probe_failed),
    .corrected_value(corrected_value), .execution_path(execution_path),
    .reason(reason), .last_fallback_tile_id(last_fallback_tile_id),
    .fallback_count(fallback_count), .accepted_count(accepted_count),
    .residual_fallback_count(residual_fallback_count),
    .stale_fallback_count(stale_fallback_count),
    .tile_health_action(tile_health_action)
  );

  // All inputs are unconstrained after the reset state. The assertions are
  // therefore checked for every legal input sequence in the bounded window.
  always @(posedge clk) begin
    if (!rst_n) begin
      assert(execution_path == 2'd0);
      assert(fallback_count == 16'd0);
      assert(accepted_count == 16'd0);
      assert(residual_fallback_count == 16'd0);
      assert(stale_fallback_count == 16'd0);
      assert(tile_health_action == 2'd0);
    end
    if (rst_n && $past(rst_n)) begin
      assert(fallback_count >= $past(fallback_count));
      assert(accepted_count >= $past(accepted_count));
      assert(residual_fallback_count >= $past(residual_fallback_count));
      assert(stale_fallback_count >= $past(stale_fallback_count));
      assert(fallback_count - $past(fallback_count) <= 16'd1);
      assert(accepted_count - $past(accepted_count) <= 16'd1);
      assert(residual_fallback_count - $past(residual_fallback_count) <= 16'd1);
      assert(stale_fallback_count - $past(stale_fallback_count) <= 16'd1);
    end
    if (rst_n && execution_path == 2'd1)
      assert(reason == 4'd1);
    if (rst_n && execution_path == 2'd2)
      assert(reason == 4'd2);

    // Saturated accounting must never wrap around.
    if (rst_n && $past(rst_n) && $past(fallback_count) == 16'hffff)
      assert(fallback_count == 16'hffff);
    if (rst_n && $past(rst_n) && $past(accepted_count) == 16'hffff)
      assert(accepted_count == 16'hffff);
    if (rst_n && $past(rst_n) && $past(residual_fallback_count) == 16'hffff)
      assert(residual_fallback_count == 16'hffff);
    if (rst_n && $past(rst_n) && $past(stale_fallback_count) == 16'hffff)
      assert(stale_fallback_count == 16'hffff);
  end
endmodule
