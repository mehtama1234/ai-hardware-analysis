module timeout_reset_property(input logic clk, input logic rst, input logic start);
  logic q;
  logic [1:0] reset_cycles = 2'd0;
  timeout dut(.clk(clk), .rst(rst), .start(start), .timed_out(q));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst && reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
    if (reset_cycles >= 2 && rst) assert(!q);
  end
endmodule

module timeout_start_property(input logic clk, input logic rst, input logic start);
  logic q;
  logic [1:0] reset_cycles = 2'd0;
  timeout dut(.clk(clk), .rst(rst), .start(start), .timed_out(q));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst && reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
    if (reset_cycles >= 2 && !rst && start) assert(!q);
  end
endmodule

module timeout_boundary_property(input logic clk, input logic rst, input logic start);
  logic q;
  logic [2:0] model_count;
  logic [1:0] reset_cycles = 2'd0;
  timeout dut(.clk(clk), .rst(rst), .start(start), .timed_out(q));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst) begin
      if (reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
      model_count <= 3'd0;
    end else if (start)
      model_count <= 3'd1;
    else if (model_count != 3'd0)
      model_count <= model_count + 3'd1;
    if (reset_cycles >= 2 && !rst && !start && model_count == 3'd3)
      assert(q);
  end
endmodule

module timeout_not_early_property(input logic clk, input logic rst, input logic start);
  logic q;
  logic [2:0] model_count;
  logic [1:0] reset_cycles = 2'd0;
  timeout dut(.clk(clk), .rst(rst), .start(start), .timed_out(q));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst) begin
      if (reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
      model_count <= 3'd0;
    end else if (start)
      model_count <= 3'd1;
    else if (model_count != 3'd0)
      model_count <= model_count + 3'd1;
    if (reset_cycles >= 2 && !rst && !start && model_count < 3'd3)
      assert(!q);
  end
endmodule
