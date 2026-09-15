module formal_model_check(input logic clk, input logic rst, input logic enable);
  logic [3:0] dut_q;
  logic [3:0] model_q;

  counter dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(dut_q));

  logic seen_reset = 1'b0;

  always_ff @(posedge clk) begin
    if (!seen_reset)
      assume(rst);
    if (rst)
      model_q <= 4'd0;
    else if (enable)
      model_q <= model_q + 4'd1;
    if (rst)
      seen_reset <= 1'b1;
  end

  always_ff @(posedge clk) begin
    if (seen_reset)
      assert(dut_q == model_q);
  end

endmodule
