module aimc_operation_partition (
    input wire [3:0] op_class,
    input wire resident_weights,
    input wire [7:0] estimated_state_error,
    input wire [7:0] state_error_budget,
    input wire [7:0] attention_flip_rate,
    input wire [7:0] attention_flip_budget,
    input wire [7:0] token_flip_rate,
    input wire [7:0] token_flip_budget,
    input wire [15:0] calibration_age,
    input wire [7:0] weak_tiles,
    output reg [1:0] placement,
    output reg [3:0] reason
);
    localparam OP_EMBEDDING = 4'd0;
    localparam OP_QKV = 4'd1;
    localparam OP_ATTENTION_SCORE = 4'd2;
    localparam OP_MASK = 4'd3;
    localparam OP_SOFTMAX = 4'd4;
    localparam OP_VALUE_MIX = 4'd5;
    localparam OP_OUT_PROJ = 4'd6;
    localparam OP_MLP = 4'd7;
    localparam OP_RESIDUAL = 4'd8;
    localparam OP_NORM = 4'd9;
    localparam OP_KV_CACHE = 4'd10;
    localparam OP_LOGITS = 4'd11;
    localparam OP_SAMPLING = 4'd12;
    localparam OP_ADAPTER = 4'd13;

    localparam PLACE_DIGITAL = 2'd0;
    localparam PLACE_ANALOG = 2'd1;
    localparam PLACE_HYBRID = 2'd2;

    localparam REASON_DIGITAL_RULE = 4'd0;
    localparam REASON_FIXED_WEIGHT_ANALOG = 4'd1;
    localparam REASON_HYBRID_NEEDS_EVIDENCE = 4'd2;
    localparam REASON_MISSING_WEIGHTS = 4'd3;
    localparam REASON_STATE_ERROR_HIGH = 4'd4;
    localparam REASON_ATTENTION_SELECTION_HIGH = 4'd5;
    localparam REASON_TOKEN_CHOICE_HIGH = 4'd6;
    localparam REASON_STALE_WEAK_TILES = 4'd7;
    localparam REASON_UNKNOWN_OP = 4'd15;

    wire stale_weak_tiles = (calibration_age >= 16'd1024) && (weak_tiles >= 8'd4);
    wire fixed_weight_op = (op_class == OP_QKV) || (op_class == OP_OUT_PROJ) || (op_class == OP_MLP);
    wire hybrid_candidate = (op_class == OP_ATTENTION_SCORE) || (op_class == OP_VALUE_MIX) || (op_class == OP_LOGITS) || (op_class == OP_ADAPTER);
    wire digital_only = (op_class == OP_EMBEDDING) || (op_class == OP_MASK) || (op_class == OP_SOFTMAX) ||
        (op_class == OP_RESIDUAL) || (op_class == OP_NORM) || (op_class == OP_KV_CACHE) || (op_class == OP_SAMPLING);

    always @* begin
        placement = PLACE_DIGITAL;
        reason = REASON_UNKNOWN_OP;

        if (digital_only) begin
            placement = PLACE_DIGITAL;
            reason = REASON_DIGITAL_RULE;
        end else if (!resident_weights && (fixed_weight_op || hybrid_candidate)) begin
            placement = PLACE_DIGITAL;
            reason = REASON_MISSING_WEIGHTS;
        end else if (estimated_state_error > state_error_budget) begin
            placement = PLACE_DIGITAL;
            reason = REASON_STATE_ERROR_HIGH;
        end else if (stale_weak_tiles) begin
            placement = PLACE_DIGITAL;
            reason = REASON_STALE_WEAK_TILES;
        end else if ((op_class == OP_ATTENTION_SCORE || op_class == OP_VALUE_MIX) && (attention_flip_rate > attention_flip_budget)) begin
            placement = PLACE_DIGITAL;
            reason = REASON_ATTENTION_SELECTION_HIGH;
        end else if (op_class == OP_LOGITS && (token_flip_rate > token_flip_budget)) begin
            placement = PLACE_DIGITAL;
            reason = REASON_TOKEN_CHOICE_HIGH;
        end else if (fixed_weight_op) begin
            placement = PLACE_ANALOG;
            reason = REASON_FIXED_WEIGHT_ANALOG;
        end else if (hybrid_candidate) begin
            placement = PLACE_HYBRID;
            reason = REASON_HYBRID_NEEDS_EVIDENCE;
        end else begin
            placement = PLACE_DIGITAL;
            reason = REASON_UNKNOWN_OP;
        end
    end
endmodule
