module tb;
  logic rst=1; logic signed [3:0] a=0,b=0; logic signed [5:0] sum;
  signed_add dut(.rst,.a,.b,.sum);
  initial begin
    $dumpfile("waveform.vcd"); $dumpvars(0,tb);
    #1 if (sum !== 5'sd0) begin $display("FAIL cycle=0 signal=sum expected=0 actual=%0d",sum); $finish(1); end
    rst=0; a=-1; b=-1;
    #1 if (sum !== -2) begin $display("FAIL cycle=1 signal=sum expected=-2 actual=%0d",sum); $finish(1); end
    $display("PASS"); $finish(0);
  end
endmodule
