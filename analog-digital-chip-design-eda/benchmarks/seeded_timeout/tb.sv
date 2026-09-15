module tb;
  logic clk=0, rst=1, start=0, timed_out;
  timeout dut(.clk,.rst,.start,.timed_out);
  always #1 clk = ~clk;
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    repeat (1) @(posedge clk); rst=0; start=1;
    @(posedge clk); #0.1 start=0;
    @(posedge clk); #0.1 if (timed_out !== 1'b1) begin $display("FAIL cycle=2 signal=timed_out expected=1 actual=%0d",timed_out); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
