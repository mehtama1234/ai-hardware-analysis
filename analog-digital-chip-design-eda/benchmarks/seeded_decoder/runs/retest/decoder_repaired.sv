module decoder(input logic rst, input logic [1:0] sel, output logic [3:0] decode);
  // SEEDED_BUG: opcode 2 is missing
  always_comb begin
    decode = 4'b0000;
    if (!rst) begin
      case (sel)
        2'd0: decode = 4'b0001;
        2'd1: decode = 4'b0010;
        2'd2: decode = 4'b0100;
        2'd3: decode = 4'b1000;
        default: decode = 4'b0000;
      endcase
    end
  end
endmodule
