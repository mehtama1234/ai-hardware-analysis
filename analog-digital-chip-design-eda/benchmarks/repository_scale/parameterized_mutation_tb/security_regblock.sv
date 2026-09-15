module tb;
  logic clk = 0, rst = 1, wr_en = 0; logic [1:0] addr = 0; logic [7:0] wdata = 0; logic [7:0] reg0;
  regblock dut(.clk, .rst, .wr_en, .addr, .wdata, .reg0);
  always #5 clk = ~clk;
  task tick; begin #10; end endtask
  initial begin
    tick; if (reg0 !== 8'h00) $display("FAIL reset");
    rst = 0; addr = 2'd1; wdata = 8'hAA; wr_en = 1; tick;
    if (reg0 !== 8'h00) $display("FAIL unauthorized-address-one");
    addr = 2'd0; wdata = 8'hAA; tick;
    if (reg0 !== 8'hAA) $display("FAIL authorized-address-zero");
    wr_en = 0; wdata = 8'h55; tick;
    if (reg0 !== 8'hAA) $display("FAIL write-enable-bypass");
    wr_en = 1; addr = 2'd2; wdata = 8'hCC; tick;
    if (reg0 !== 8'hAA) $display("FAIL unauthorized-address-two");
    rst = 1; tick; if (reg0 !== 8'h00) $display("FAIL reset-state");
    $display("PASS"); $finish;
  end
endmodule
