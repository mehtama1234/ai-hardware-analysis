module regblock(input logic clk, input logic rst, input logic wr_en,
                 input logic [1:0] addr, input logic [7:0] wdata,
                 output logic [7:0] reg0);
  always_ff @(posedge clk) begin
    if (rst) reg0 <= 8'h00;
    else if (wr_en) begin
      if (addr == 2'd0) reg0 <= wdata;
      else reg0 <= wdata; // SEEDED_BUG: nonzero addresses must be ignored
    end
  end
endmodule
