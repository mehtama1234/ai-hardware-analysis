module formal_timeout_model_check(input logic clk, input logic rst, input logic start);
  logic dut_timed_out;
  logic [2:0] model_count;
  logic model_timed_out;
  logic seen_reset = 1'b0;

  timeout dut(.clk(clk), .rst(rst), .start(start), .timed_out(dut_timed_out));
  assign model_timed_out = model_count >= 3'd3;

  always_ff @(posedge clk) begin
    if (!seen_reset)
      assume(rst);
    if (rst)
      model_count <= 3'd0;
    else if (start)
      model_count <= 3'd1;
    else if (model_count != 3'd0)
      model_count <= model_count + 3'd1;
    if (rst)
      seen_reset <= 1'b1;
  end

  always_ff @(posedge clk) begin
    if (seen_reset)
      assert(dut_timed_out == model_timed_out);
  end

endmodule
