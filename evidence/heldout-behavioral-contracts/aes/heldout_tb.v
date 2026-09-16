`timescale 1ns/1ps
module heldout_tb;
    reg clk = 0, rst = 0, ld = 0;
    reg [127:0] key = 128'h000102030405060708090a0b0c0d0e0f;
    reg [127:0] text_in = 128'h00112233445566778899aabbccddeeff;
    wire done;
    wire [127:0] text_out;
    reg saw_done = 0;

    aes_cipher_top dut (.clk(clk), .rst(rst), .ld(ld), .done(done), .key(key), .text_in(text_in), .text_out(text_out));
    always #5 clk = ~clk;

    initial begin
        $dumpfile("trace.vcd");
        $dumpvars(0, dut);
        #12 rst = 1;
        @(negedge clk) ld = 1;
        @(negedge clk) ld = 0;
        repeat (20) begin
            @(posedge clk);
            #2;
            if (done) begin
                saw_done = 1;
                if (text_out !== 128'h69c4e0d86a7b0430d8cdb78070b4c55a)
                    $display("FAIL AES known-answer text_out=%h", text_out);
                else
                    $display("PASS heldout AES known-answer contract");
                $finish;
            end
        end
        if (!saw_done) $display("FAIL AES done timeout");
        $finish;
    end
endmodule
