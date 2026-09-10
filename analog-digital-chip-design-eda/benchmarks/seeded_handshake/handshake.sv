module handshake(input logic rst, output logic ready);
  assign ready = 1'b1; // SEEDED_BUG: ready must be low during reset
endmodule
