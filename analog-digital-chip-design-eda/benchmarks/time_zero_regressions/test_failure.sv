module test_failure;
  initial begin
    $display("TIMEZERO_STIMULUS");
    $fatal(1, "TIMEZERO_TEST_FAILURE");
  end
endmodule
