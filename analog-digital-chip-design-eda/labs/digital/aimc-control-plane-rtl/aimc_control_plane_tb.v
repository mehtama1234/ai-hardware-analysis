`timescale 1ns/1ps

module aimc_control_plane_tb;
    reg clk = 0;
    reg rst_n = 0;
    reg phase_decode = 0;
    reg [3:0] batch_size = 1;
    reg [15:0] active_context = 2048;
    reg resident_weights = 1;
    reg [7:0] healthy_tiles = 128;
    reg [7:0] weak_tiles = 2;
    reg [15:0] calibration_age = 128;
    reg [7:0] estimated_error = 8'd45;
    reg [7:0] error_budget = 8'd100;
    wire [1:0] path;
    wire [2:0] reason;

    aimc_control_plane dut (
        .clk(clk),
        .rst_n(rst_n),
        .phase_decode(phase_decode),
        .batch_size(batch_size),
        .active_context(active_context),
        .resident_weights(resident_weights),
        .healthy_tiles(healthy_tiles),
        .weak_tiles(weak_tiles),
        .calibration_age(calibration_age),
        .estimated_error(estimated_error),
        .error_budget(error_budget),
        .path(path),
        .reason(reason)
    );

    always #5 clk = ~clk;

    task run_case;
        input [160*8:1] name;
        input in_phase_decode;
        input [3:0] in_batch_size;
        input [15:0] in_active_context;
        input in_resident_weights;
        input [7:0] in_healthy_tiles;
        input [7:0] in_weak_tiles;
        input [15:0] in_calibration_age;
        input [7:0] in_estimated_error;
        input [7:0] in_error_budget;
        input [1:0] expected_path;
        input [2:0] expected_reason;
        begin
            phase_decode = in_phase_decode;
            batch_size = in_batch_size;
            active_context = in_active_context;
            resident_weights = in_resident_weights;
            healthy_tiles = in_healthy_tiles;
            weak_tiles = in_weak_tiles;
            calibration_age = in_calibration_age;
            estimated_error = in_estimated_error;
            error_budget = in_error_budget;
            @(posedge clk);
            #1;
            $display("%0s,path=%0d,reason=%0d,expected_path=%0d,expected_reason=%0d",
                name, path, reason, expected_path, expected_reason);
            if (path !== expected_path || reason !== expected_reason) begin
                $display("FAIL %0s", name);
                $finish;
            end
        end
    endtask

    initial begin
        $dumpfile("aimc_control_plane.vcd");
        $dumpvars(0, aimc_control_plane_tb);
        #12 rst_n = 1;

        run_case("prompt_batch", 1'b0, 4'd2, 16'd2048, 1'b1, 8'd128, 8'd2, 16'd128, 8'd45, 8'd100, 2'd1, 3'd0);
        run_case("batched_decode", 1'b1, 4'd8, 16'd2048, 1'b1, 8'd128, 8'd1, 16'd128, 8'd35, 8'd100, 2'd2, 3'd6);
        run_case("long_context_decode", 1'b1, 4'd1, 16'd16384, 1'b1, 8'd128, 8'd2, 16'd128, 8'd85, 8'd100, 2'd0, 3'd5);
        run_case("stale_weak_tiles", 1'b0, 4'd2, 16'd2048, 1'b1, 8'd96, 8'd8, 16'd2048, 8'd80, 8'd100, 2'd0, 3'd4);
        run_case("error_too_high", 1'b0, 4'd2, 16'd2048, 1'b1, 8'd128, 8'd1, 16'd128, 8'd130, 8'd100, 2'd0, 3'd3);
        run_case("missing_weights", 1'b0, 4'd1, 16'd1024, 1'b0, 8'd128, 8'd2, 16'd128, 8'd45, 8'd100, 2'd0, 3'd1);

        $display("PASS aimc_control_plane_tb");
        $finish;
    end
endmodule
