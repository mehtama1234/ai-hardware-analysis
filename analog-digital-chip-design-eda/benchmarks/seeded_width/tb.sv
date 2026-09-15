module tb;
  logic rst=1; logic [7:0] data=0; logic [3:0] low;
  width_adapter dut(.rst,.data,.low);
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    #1 if (low !== 4'b0000) begin $display("FAIL cycle=0 signal=low expected=0 actual=%0d",low); $finish(1); end
    rst=0; data=8'hA5;
    #1 if (low !== 4'h5) begin $display("FAIL cycle=1 signal=low expected=5 actual=%0d",low); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
