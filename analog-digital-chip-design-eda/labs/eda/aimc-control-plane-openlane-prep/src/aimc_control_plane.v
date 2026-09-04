module aimc_control_plane (
    input wire clk,
    input wire rst_n,
    input wire phase_decode,
    input wire [3:0] batch_size,
    input wire [15:0] active_context,
    input wire resident_weights,
    input wire [7:0] healthy_tiles,
    input wire [7:0] weak_tiles,
    input wire [15:0] calibration_age,
    input wire [7:0] estimated_error,
    input wire [7:0] error_budget,
    output reg [1:0] path,
    output reg [2:0] reason
);
    localparam PATH_DIGITAL = 2'd0;
    localparam PATH_ANALOG = 2'd1;
    localparam PATH_ANALOG_BATCHED_DECODE = 2'd2;

    localparam REASON_OK_ANALOG = 3'd0;
    localparam REASON_MISSING_WEIGHTS = 3'd1;
    localparam REASON_TOO_FEW_TILES = 3'd2;
    localparam REASON_ERROR_HIGH = 3'd3;
    localparam REASON_STALE_CALIBRATION = 3'd4;
    localparam REASON_CACHE_DOMINATES = 3'd5;
    localparam REASON_BATCH_REUSE = 3'd6;

    wire batched_decode = phase_decode && (batch_size >= 4'd4);
    wire long_context_single_decode = phase_decode && (batch_size < 4'd4) && (active_context >= 16'd8192);
    wire stale_weak_tiles = (calibration_age >= 16'd1024) && (weak_tiles >= 8'd4);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            path <= PATH_DIGITAL;
            reason <= REASON_MISSING_WEIGHTS;
        end else if (!resident_weights) begin
            path <= PATH_DIGITAL;
            reason <= REASON_MISSING_WEIGHTS;
        end else if (healthy_tiles < 8'd64) begin
            path <= PATH_DIGITAL;
            reason <= REASON_TOO_FEW_TILES;
        end else if (estimated_error > error_budget) begin
            path <= PATH_DIGITAL;
            reason <= REASON_ERROR_HIGH;
        end else if (stale_weak_tiles) begin
            path <= PATH_DIGITAL;
            reason <= REASON_STALE_CALIBRATION;
        end else if (long_context_single_decode) begin
            path <= PATH_DIGITAL;
            reason <= REASON_CACHE_DOMINATES;
        end else if (batched_decode) begin
            path <= PATH_ANALOG_BATCHED_DECODE;
            reason <= REASON_BATCH_REUSE;
        end else begin
            path <= PATH_ANALOG;
            reason <= REASON_OK_ANALOG;
        end
    end
endmodule
