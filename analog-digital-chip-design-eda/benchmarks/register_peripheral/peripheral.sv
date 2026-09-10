module peripheral(input logic clk, input logic rst, input logic valid,
                  input logic write, input logic [1:0] addr,
                  input logic [7:0] wdata, output logic ready,
                  output logic [7:0] control);
  assign ready = !rst;
  csr_regs regs(.clk, .rst, .wr_en(valid && write), .addr, .wdata, .control);
endmodule
