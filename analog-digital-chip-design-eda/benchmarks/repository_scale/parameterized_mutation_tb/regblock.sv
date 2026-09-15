module tb;
  logic clk = 0, rst = 1, wr_en = 0; logic [1:0] addr = 0; logic [7:0] wdata = 0; logic [7:0] reg0;
  regblock dut(.clk, .rst, .wr_en, .addr, .wdata, .reg0);
  always #5 clk = ~clk;
  task tick; begin #10; end endtask
  initial begin
    tick; rst = 0; addr = 2'd1; wdata = 8'hAA; wr_en = 1; tick;
    if (reg0 !== 8'h00) $display("FAIL nonzero-address");
    addr = 2'd0; wdata = 8'hAA; tick; if (reg0 !== 8'hAA) $display("FAIL address-zero");
    addr = 2'd1; wdata = 8'h55; tick; if (reg0 !== 8'hAA) $display("FAIL nonzero-overwrite");
    $display("PASS"); $finish;
  end
endmodule
