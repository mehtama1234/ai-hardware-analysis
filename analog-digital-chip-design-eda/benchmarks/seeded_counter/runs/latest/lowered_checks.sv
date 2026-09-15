// Generated explicit SVA lowering; unsupported properties are not executable.
module lowered_checks(input logic clk, input logic rst, input logic enable, input logic [3:0] counter_q, input logic b1);
  logic [3:0] previous_counter_q;
  logic previous_valid;
  initial begin previous_counter_q = '0; previous_valid = 1'b0; end
  // requirement: REQ-COUNTER-RESET status=supported
  always @(posedge clk) begin
    if (rst && counter_q !== '0) $error("REQ-COUNTER-RESET: reset invariant violated");
  end
  // requirement: REQ-COUNTER-ENABLE status=supported
  always @(posedge clk) begin
    if (previous_valid && !(rst) && enable && counter_q !== previous_counter_q + 1'b1) $error("REQ-COUNTER-ENABLE: increment violated");
    previous_counter_q <= counter_q;
    previous_valid <= 1'b1;
  end
  // requirement: REQ-COUNTER-HOLD status=supported
  always @(posedge clk) begin
    if (previous_valid && !(rst) && !enable && counter_q !== previous_counter_q) $error("REQ-COUNTER-HOLD: hold violated");
    previous_counter_q <= counter_q;
    previous_valid <= 1'b1;
  end
endmodule
