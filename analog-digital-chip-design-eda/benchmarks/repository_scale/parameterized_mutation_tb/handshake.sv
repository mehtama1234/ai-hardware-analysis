module tb;
  logic rst = 1; logic ready;
  handshake dut(.rst, .ready);
  initial begin
    #1 if (ready !== 1'b0) $display("FAIL reset");
    rst = 0; #1 if (ready !== 1'b1) $display("FAIL active");
    $display("PASS"); $finish;
  end
endmodule
