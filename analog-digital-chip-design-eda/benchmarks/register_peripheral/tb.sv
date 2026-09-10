module tb;
  logic clk=0, rst=1, valid=0, write=0; logic [1:0] addr=0; logic [7:0] wdata=0;
  logic ready; logic [7:0] control;
  peripheral dut(.clk,.rst,.valid,.write,.addr,.wdata,.ready,.control);
  always #5 clk = ~clk;
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    #2 if (ready !== 1'b0) begin $display("FAIL cycle=0 signal=ready expected=0 actual=%0d",ready); $finish(1); end
    #10 rst=0; addr=2'd1; wdata=8'h5a; valid=1; write=1; #10;
    if (control !== 8'h00) begin $display("FAIL cycle=1 signal=control expected=0 actual=%0d",control); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
