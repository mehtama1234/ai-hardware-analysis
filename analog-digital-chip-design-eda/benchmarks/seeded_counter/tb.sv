module tb;
  logic clk = 0, rst = 1, enable = 0;
  logic [3:0] counter_q;
  counter dut(.clk, .rst, .enable, .counter_q);
  always #5 clk = ~clk;
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0, tb);
    #12 rst = 0;
    #8; // first rising edge after reset release, enable remains low
    if (counter_q !== 4'd0) begin
      $display("FAIL cycle=1 signal=counter_q expected=0 actual=%0d", counter_q);
      $finish(1);
    end
    $display("PASS"); $finish(0);
  end
endmodule
