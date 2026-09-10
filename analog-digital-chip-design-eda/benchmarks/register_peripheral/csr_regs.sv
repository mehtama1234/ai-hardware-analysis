module csr_regs(input logic clk, input logic rst, input logic wr_en,
                input logic [1:0] addr, input logic [7:0] wdata,
                output logic [7:0] control);
  always_ff @(posedge clk) begin
    if (rst) control <= 8'h00;
    else if (wr_en) control <= wdata; // SEEDED_BUG: decode addr zero before write
  end
endmodule
