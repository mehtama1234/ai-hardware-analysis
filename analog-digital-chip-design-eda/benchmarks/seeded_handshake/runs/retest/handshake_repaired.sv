module handshake(input logic rst, output logic ready);
  assign ready = !rst; // repaired reset gating
endmodule
