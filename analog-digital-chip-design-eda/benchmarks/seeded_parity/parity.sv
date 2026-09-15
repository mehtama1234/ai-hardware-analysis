module parity(input logic rst, input logic [3:0] data, output logic even);
  // SEEDED_BUG: even parity result is inverted
  assign even = rst ? 1'b0 : ^data;
endmodule
