module counter_reset_property(input logic clk, input logic rst, input logic enable);
  logic [3:0] q;
  logic [1:0] reset_cycles = 2'd0;
  counter dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(q));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst && reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
    if (reset_cycles >= 2 && rst) assert(q == 4'd0);
  end
endmodule

module counter_hold_property(input logic clk, input logic rst, input logic enable);
  logic [3:0] q, model_q;
  logic [1:0] reset_cycles = 2'd0;
  counter dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(q));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst) begin
      if (reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
      model_q <= 4'd0;
    end else if (enable)
      model_q <= model_q + 4'd1;
    if (reset_cycles >= 2 && !rst && !enable) assert(q == model_q);
  end
endmodule

module counter_enable_property(input logic clk, input logic rst, input logic enable);
  logic [3:0] q, model_q;
  logic [1:0] reset_cycles = 2'd0;
  counter dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(q));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst) begin
      if (reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
      model_q <= 4'd0;
    end else if (enable)
      model_q <= model_q + 4'd1;
    if (reset_cycles >= 2 && !rst && enable) assert(q == model_q);
  end
endmodule
