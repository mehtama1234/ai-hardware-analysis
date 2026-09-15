module tb;
  reg clk = 0, reset = 1, req_val = 0, resp_rdy = 1;
  reg [31:0] req_msg = 0;
  wire req_rdy, resp_val;
  wire [15:0] resp_msg;
  gcd dut(.clk(clk), .req_msg(req_msg), .req_rdy(req_rdy), .req_val(req_val),
          .reset(reset), .resp_msg(resp_msg), .resp_rdy(resp_rdy), .resp_val(resp_val));
  always #5 clk = ~clk;
  initial begin
    $dumpfile("gcd.vcd"); $dumpvars(0, tb);
    #12 reset = 0;
    run_case(16'd48, 16'd18, 16'd6);
    run_case(16'd1071, 16'd462, 16'd21);
    run_case(16'd0, 16'd7, 16'd7);
    $display("PASS"); $finish(0);
  end
  task automatic run_case(input [15:0] a, input [15:0] b, input [15:0] expected);
    begin
      @(posedge clk); #1 req_msg = {a, b}; req_val = 1;
      wait(req_rdy); @(posedge clk); #1 req_val = 0;
      wait(resp_val); #1;
      if (resp_msg !== expected) begin
        $display("FAIL expected=%0d actual=%0d", expected, resp_msg); $finish(1);
      end
      @(posedge clk); #1;
    end
  endtask
  initial begin
    #1000; $display("FAIL timeout"); $finish(1);
  end
endmodule
