module tb;
  logic rst=1; logic [1:0] sel=0; logic [3:0] decode;
  decoder dut(.rst,.sel,.decode);
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    #1 if (decode !== 4'b0000) begin $display("FAIL cycle=0 signal=decode expected=0 actual=%0d",decode); $finish(1); end
    rst=0; sel=2'd2;
    #1 if (decode !== 4'b0100) begin $display("FAIL cycle=1 signal=decode expected=4 actual=%0d",decode); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
