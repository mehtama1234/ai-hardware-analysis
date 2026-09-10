module tb;
  logic clk = 0, rst = 1, wr_en = 0; logic [1:0] addr = 0; logic [7:0] wdata = 0; logic [7:0] reg0;
  regblock dut(.clk, .rst, .wr_en, .addr, .wdata, .reg0);
  always #5 clk = ~clk;
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0, tb);
    #12 rst = 0; addr = 2'd1; wdata = 8'hAA; wr_en = 1; #10;
    if (reg0 !== 8'h00) begin
      $display("FAIL cycle=1 signal=reg0 expected=0 actual=%0d", reg0);
      $finish(1);
    end
    $display("PASS"); $finish(0);
  end
endmodule
