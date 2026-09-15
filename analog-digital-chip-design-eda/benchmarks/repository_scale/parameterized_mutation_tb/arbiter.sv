module tb;
  logic rst = 1; logic [1:0] req = 0; logic [1:0] grant;
  arbiter dut(.rst, .req, .grant);
  initial begin
    #1 if (grant !== 2'b00) $display("FAIL reset");
    rst = 0; req = 2'b10; #1 if (grant !== 2'b10) $display("FAIL requester1");
    req = 2'b01; #1 if (grant !== 2'b01) $display("FAIL requester0");
    req = 2'b00; #1 if (grant !== 2'b00) $display("FAIL idle");
    $display("PASS"); $finish;
  end
endmodule
