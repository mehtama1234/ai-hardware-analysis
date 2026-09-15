module tb;
  logic rst=1; logic [3:0] data=0; logic even;
  parity dut(.rst,.data,.even);
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    #1 if (even !== 1'b0) begin $display("FAIL cycle=0 signal=even expected=0 actual=%0d",even); $finish(1); end
    rst=0; data=4'b0011;
    #1 if (even !== 1'b1) begin $display("FAIL cycle=1 signal=even expected=1 actual=%0d",even); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
