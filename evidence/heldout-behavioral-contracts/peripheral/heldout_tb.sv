`timescale 1ns/1ps
module heldout_tb;
    logic clk = 0, rst = 1, valid = 0, write = 0;
    logic [1:0] addr = 0;
    logic [7:0] wdata = 0;
    logic ready;
    logic [7:0] control;
    peripheral dut(.*);
    always #5 clk = ~clk;
    initial begin
        $dumpfile("trace.vcd"); $dumpvars(0, dut);
        #1;
        if (ready !== 0) $display("FAIL reset ready=%b", ready);
        else $display("PASS heldout peripheral reset visibility contract");
        rst = 0; valid = 1; write = 1; wdata = 8'ha5;
        @(posedge clk); #1;
        if (control !== 8'ha5) $display("FAIL CSR write control=%h", control);
        else $display("PASS heldout peripheral reset and CSR write contract");
        $finish;
    end
endmodule
