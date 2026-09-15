module csr_reset_property(input logic clk, input logic rst, input logic wr_en, input logic [1:0] addr, input logic [7:0] wdata);
  logic [7:0] control;
  logic [1:0] reset_cycles = 2'd0;
  csr_regs dut(.clk(clk), .rst(rst), .wr_en(wr_en), .addr(addr), .wdata(wdata), .control(control));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst && reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
    if (reset_cycles >= 2 && rst) assert(control == 8'h00);
  end
endmodule

module csr_nonzero_address_property(input logic clk, input logic rst, input logic wr_en, input logic [1:0] addr, input logic [7:0] wdata);
  logic [7:0] control, model_control;
  logic [1:0] reset_cycles = 2'd0;
  csr_regs dut(.clk(clk), .rst(rst), .wr_en(wr_en), .addr(addr), .wdata(wdata), .control(control));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst) begin
      if (reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
      model_control <= 8'h00;
    end else if (wr_en && addr == 2'd0)
      model_control <= wdata;
    if (reset_cycles >= 2 && !rst && wr_en && addr != 2'd0)
      assert(control == model_control);
  end
endmodule

module csr_zero_address_write_property(input logic clk, input logic rst, input logic wr_en, input logic [1:0] addr, input logic [7:0] wdata);
  logic [7:0] control, model_control;
  logic [1:0] reset_cycles = 2'd0;
  csr_regs dut(.clk(clk), .rst(rst), .wr_en(wr_en), .addr(addr), .wdata(wdata), .control(control));
  always_ff @(posedge clk) begin
    if (reset_cycles < 2) assume(rst);
    if (rst) begin
      if (reset_cycles < 2) reset_cycles <= reset_cycles + 2'd1;
      model_control <= 8'h00;
    end else if (wr_en && addr == 2'd0)
      model_control <= wdata;
    if (reset_cycles >= 2 && !rst && wr_en && addr == 2'd0)
      assert(control == model_control);
  end
endmodule
