module width_adapter(input logic rst, input logic [7:0] data, output logic [3:0] low);
  // SEEDED_BUG: adapter exposes the wrong nibble
  assign low = rst ? 4'b0000 : data[7:4];
endmodule
