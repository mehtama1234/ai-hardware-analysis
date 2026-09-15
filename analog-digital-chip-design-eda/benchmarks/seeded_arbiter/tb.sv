module tb;
  logic rst=1; logic [1:0] req=0; logic [1:0] grant;
  arbiter dut(.rst,.req,.grant);
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    #1 if (grant !== 2'b00) begin $display("FAIL cycle=0 signal=grant expected=0 actual=%0d",grant); $finish(1); end
    rst=0; req=2'b10;
    #1 if (grant !== 2'b10) begin $display("FAIL cycle=1 signal=grant expected=2 actual=%0d",grant); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
