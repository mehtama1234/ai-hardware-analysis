`timescale 1ns/1ps

module aimc_operation_partition_tb;
    reg [3:0] op_class = 0;
    reg resident_weights = 1;
    reg [7:0] estimated_state_error = 8'd60;
    reg [7:0] state_error_budget = 8'd100;
    reg [7:0] attention_flip_rate = 8'd5;
    reg [7:0] attention_flip_budget = 8'd15;
    reg [7:0] token_flip_rate = 8'd5;
    reg [7:0] token_flip_budget = 8'd15;
    reg [15:0] calibration_age = 16'd128;
    reg [7:0] weak_tiles = 8'd1;
    wire [1:0] placement;
    wire [3:0] reason;

    aimc_operation_partition dut (
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
        .reason(reason)
    );

    task run_case;
        input [160*8:1] name;
        input [3:0] in_op_class;
        input in_resident_weights;
        input [7:0] in_estimated_state_error;
        input [7:0] in_attention_flip_rate;
        input [7:0] in_token_flip_rate;
        input [15:0] in_calibration_age;
        input [7:0] in_weak_tiles;
        input [1:0] expected_placement;
        input [3:0] expected_reason;
        begin
            op_class = in_op_class;
            resident_weights = in_resident_weights;
            estimated_state_error = in_estimated_state_error;
            attention_flip_rate = in_attention_flip_rate;
            token_flip_rate = in_token_flip_rate;
            calibration_age = in_calibration_age;
            weak_tiles = in_weak_tiles;
            #1;
            $display("%0s,placement=%0d,reason=%0d,expected_placement=%0d,expected_reason=%0d",
                name, placement, reason, expected_placement, expected_reason);
            if (placement !== expected_placement || reason !== expected_reason) begin
                $display("FAIL %0s", name);
                $finish;
            end
        end
    endtask

    initial begin
        $dumpfile("aimc_operation_partition.vcd");
        $dumpvars(0, aimc_operation_partition_tb);

        run_case("embedding_is_digital", 4'd0, 1'b1, 8'd60, 8'd5, 8'd5, 16'd128, 8'd1, 2'd0, 4'd0);
        run_case("qkv_fixed_weight_analog", 4'd1, 1'b1, 8'd60, 8'd5, 8'd5, 16'd128, 8'd1, 2'd1, 4'd1);
        run_case("mlp_fixed_weight_analog", 4'd7, 1'b1, 8'd60, 8'd5, 8'd5, 16'd128, 8'd1, 2'd1, 4'd1);
        run_case("attention_score_hybrid", 4'd2, 1'b1, 8'd60, 8'd5, 8'd5, 16'd128, 8'd1, 2'd2, 4'd2);
        run_case("attention_selection_fallback", 4'd2, 1'b1, 8'd60, 8'd28, 8'd5, 16'd128, 8'd1, 2'd0, 4'd5);
        run_case("logits_hybrid", 4'd11, 1'b1, 8'd60, 8'd5, 8'd5, 16'd128, 8'd1, 2'd2, 4'd2);
        run_case("logits_token_fallback", 4'd11, 1'b1, 8'd60, 8'd5, 8'd22, 16'd128, 8'd1, 2'd0, 4'd6);
        run_case("kv_cache_is_digital", 4'd10, 1'b1, 8'd60, 8'd5, 8'd5, 16'd128, 8'd1, 2'd0, 4'd0);
        run_case("state_error_fallback", 4'd1, 1'b1, 8'd120, 8'd5, 8'd5, 16'd128, 8'd1, 2'd0, 4'd4);
        run_case("stale_weak_fallback", 4'd7, 1'b1, 8'd60, 8'd5, 8'd5, 16'd2048, 8'd8, 2'd0, 4'd7);
        run_case("missing_weights_fallback", 4'd1, 1'b0, 8'd60, 8'd5, 8'd5, 16'd128, 8'd1, 2'd0, 4'd3);

        $display("PASS aimc_operation_partition_tb");
        $finish;
    end
endmodule
