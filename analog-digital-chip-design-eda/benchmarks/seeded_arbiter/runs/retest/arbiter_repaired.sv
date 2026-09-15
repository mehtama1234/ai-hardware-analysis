module arbiter(input logic rst, input logic [1:0] req, output logic [1:0] grant);
  logic grant_a, grant_b;
  // SEEDED_BUG: requester 1 is never granted
  assign grant = rst ? 2'b00 : req; // repaired one-hot request mapping
  assign grant_a = grant[0];
  assign grant_b = grant[1];
endmodule
