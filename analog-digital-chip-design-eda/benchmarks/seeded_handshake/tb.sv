module tb;
  logic rst=1; logic ready;
  handshake dut(.rst,.ready);
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    #1 if (ready !== 1'b0) begin $display("FAIL cycle=0 signal=ready expected=0 actual=%0d",ready); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
