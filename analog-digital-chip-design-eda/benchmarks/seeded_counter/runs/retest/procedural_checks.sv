// Generated procedural checker; 3 approved plans
module procedural_checks(input logic clk, input logic rst, input logic enable, input logic [3:0] counter_q);
  logic [3:0] previous_counter_q;
  logic previous_valid;
  initial begin previous_counter_q = '0; previous_valid = 1'b0; end
  always @(posedge clk) begin
    // requirement: REQ-COUNTER-RESET
    if (rst && counter_q !== 4'd0) $display("FAIL cycle=%0t signal=counter_q expected=0 actual=%0d", $time, counter_q);
    // requirement: REQ-COUNTER-ENABLE
    if (previous_valid && !rst && enable && counter_q !== previous_counter_q + 1'b1) $display("FAIL cycle=%0t signal=counter_q increment", $time);
    // requirement: REQ-COUNTER-HOLD
    if (previous_valid && !rst && !enable && counter_q !== previous_counter_q) $display("FAIL cycle=%0t signal=counter_q expected=%0d actual=%0d", $time, previous_counter_q, counter_q);
    previous_counter_q <= counter_q;
    previous_valid <= 1'b1;
  end
endmodule
