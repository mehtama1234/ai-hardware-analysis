`timescale 1ns/1ps

module openroad_aes_tb;
  logic clk, rst, ld;
  logic [127:0] key, text_in;
  wire done;
  wire [127:0] text_out;

  aes_cipher_top dut(.clk(clk), .rst(rst), .ld(ld), .done(done),
                     .key(key), .text_in(text_in), .text_out(text_out));
  always #5 clk = ~clk;

  initial begin
    clk = 0; rst = 0; ld = 0;
    key = 128'h000102030405060708090a0b0c0d0e0f;
    text_in = 128'h00112233445566778899aabbccddeeff;
    repeat (2) @(posedge clk);
    rst = 1;
    @(negedge clk);
    ld = 1;
    @(negedge clk);
    ld = 0;
    wait (done);
    #1;
    if (text_out !== 128'h69c4e0d86a7b0430d8cdb78070b4c55a) begin
      $display("FAIL aes ciphertext=%h", text_out);
      $finish(1);
    end
    $display("PASS aes known-answer");
    $finish(0);
  end
endmodule
