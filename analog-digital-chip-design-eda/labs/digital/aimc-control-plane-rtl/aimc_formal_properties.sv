module aimc_scheduler_no_sample;
  reg sample_valid, analog_candidate;
  reg [7:0] requested_tile_id;
  reg [1:0] tile0_health_action, tile1_health_action, tile2_health_action, tile3_health_action;
  reg [3:0] tile_busy;
  reg [1:0] maintenance_budget;
  wire [1:0] decision, selected_tile;
  wire [3:0] reason;
  aimc_tile_service_scheduler dut(.sample_valid(sample_valid),.analog_candidate(analog_candidate),.requested_tile_id(requested_tile_id),.tile0_health_action(tile0_health_action),.tile1_health_action(tile1_health_action),.tile2_health_action(tile2_health_action),.tile3_health_action(tile3_health_action),.tile_busy(tile_busy),.maintenance_budget(maintenance_budget),.service_decision(decision),.selected_tile(selected_tile),.reason(reason));
  always @* begin
    if (!sample_valid) begin
      assert(decision == 2'd0);
      assert(reason == 4'd0);
    end
  end
endmodule

module aimc_scheduler_no_candidate;
  reg sample_valid, analog_candidate;
  reg [7:0] requested_tile_id;
  reg [1:0] tile0_health_action, tile1_health_action, tile2_health_action, tile3_health_action;
  reg [3:0] tile_busy;
  reg [1:0] maintenance_budget;
  wire [1:0] decision, selected_tile;
  wire [3:0] reason;
  aimc_tile_service_scheduler dut(.sample_valid(sample_valid),.analog_candidate(analog_candidate),.requested_tile_id(requested_tile_id),.tile0_health_action(tile0_health_action),.tile1_health_action(tile1_health_action),.tile2_health_action(tile2_health_action),.tile3_health_action(tile3_health_action),.tile_busy(tile_busy),.maintenance_budget(maintenance_budget),.service_decision(decision),.selected_tile(selected_tile),.reason(reason));
  always @* begin
    if (sample_valid && !analog_candidate) begin
      assert(decision == 2'd0);
      assert(reason == 4'd1);
    end
  end
endmodule

module aimc_scheduler_nominal;
  reg sample_valid, analog_candidate;
  reg [7:0] requested_tile_id;
  reg [1:0] tile0_health_action, tile1_health_action, tile2_health_action, tile3_health_action;
  reg [3:0] tile_busy;
  reg [1:0] maintenance_budget;
  wire [1:0] decision, selected_tile;
  wire [3:0] reason;
  aimc_tile_service_scheduler dut(.sample_valid(sample_valid),.analog_candidate(analog_candidate),.requested_tile_id(requested_tile_id),.tile0_health_action(tile0_health_action),.tile1_health_action(tile1_health_action),.tile2_health_action(tile2_health_action),.tile3_health_action(tile3_health_action),.tile_busy(tile_busy),.maintenance_budget(maintenance_budget),.service_decision(decision),.selected_tile(selected_tile),.reason(reason));
  always @* begin
    if (sample_valid && analog_candidate && requested_tile_id[1:0] == 2'd0 && tile0_health_action == 2'd0 && tile_busy[0] == 1'b0) begin
      assert(decision == 2'd1);
      assert(selected_tile == 2'd0);
      assert(reason == 4'd2);
    end
  end
endmodule

module aimc_governor_no_sample;
  reg sample_valid, analog_candidate;
  reg [7:0] residual_q8, sensitivity_q8, cumulative_error_q8;
  reg [3:0] drift_age;
  wire [1:0] decision, tile_action;
  wire [3:0] reason;
  wire [7:0] next_cumulative_error_q8;
  aimc_error_budget_governor dut(.sample_valid(sample_valid),.analog_candidate(analog_candidate),.residual_q8(residual_q8),.drift_age(drift_age),.sensitivity_q8(sensitivity_q8),.cumulative_error_q8(cumulative_error_q8),.service_decision(decision),.tile_action(tile_action),.reason(reason),.next_cumulative_error_q8(next_cumulative_error_q8));
  always @* begin
    if (!sample_valid) begin
      assert(decision == 2'd0);
      assert(reason == 4'd0);
      assert(next_cumulative_error_q8 == cumulative_error_q8);
    end
  end
endmodule

module aimc_governor_high_residual;
  reg sample_valid, analog_candidate;
  reg [7:0] residual_q8, sensitivity_q8, cumulative_error_q8;
  reg [3:0] drift_age;
  wire [1:0] decision, tile_action;
  wire [3:0] reason;
  wire [7:0] next_cumulative_error_q8;
  aimc_error_budget_governor dut(.sample_valid(sample_valid),.analog_candidate(analog_candidate),.residual_q8(residual_q8),.drift_age(drift_age),.sensitivity_q8(sensitivity_q8),.cumulative_error_q8(cumulative_error_q8),.service_decision(decision),.tile_action(tile_action),.reason(reason),.next_cumulative_error_q8(next_cumulative_error_q8));
  always @* begin
    if (sample_valid && analog_candidate && residual_q8 > 8'd46) begin
      assert(decision == 2'd0);
      assert(tile_action == 2'd2);
      assert(reason == 4'd2);
    end
  end
endmodule

module aimc_governor_nominal;
  reg sample_valid, analog_candidate;
  reg [7:0] residual_q8, sensitivity_q8, cumulative_error_q8;
  reg [3:0] drift_age;
  wire [1:0] decision, tile_action;
  wire [3:0] reason;
  wire [7:0] next_cumulative_error_q8;
  aimc_error_budget_governor dut(.sample_valid(sample_valid),.analog_candidate(analog_candidate),.residual_q8(residual_q8),.drift_age(drift_age),.sensitivity_q8(sensitivity_q8),.cumulative_error_q8(cumulative_error_q8),.service_decision(decision),.tile_action(tile_action),.reason(reason),.next_cumulative_error_q8(next_cumulative_error_q8));
  always @* begin
    if (sample_valid && analog_candidate && residual_q8 == 8'd0 && drift_age == 4'd0 && sensitivity_q8 == 8'd0 && cumulative_error_q8 == 8'd0) begin
      assert(decision == 2'd1);
      assert(tile_action == 2'd0);
      assert(reason == 4'd6);
      assert(next_cumulative_error_q8 == 8'd0);
    end
  end
endmodule
