module svm_harness;
  logic clk = 1'b0;
  logic rst = 1'b1;
  logic enable = 1'b0;
  logic [3:0] q;
  logic mismatch;
  counter dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(q));
  counter_svm check(.clk(clk), .rst(rst), .enable(enable), .actual(q), .mismatch(mismatch));
  always #5 clk = ~clk;
  always @(posedge clk) if (mismatch) $display("SVM_MISMATCH cycle=1 actual=%0d expected=%0d", q, 0);
  initial begin
    #12 rst = 1'b0;
    enable = 1'b1;
    #30 enable = 1'b0;
    #2;
    $display("SVM_CYCLES cycles=4");
    if (!mismatch) $display("SVM_PASS");
    $finish;
  end
endmodule
