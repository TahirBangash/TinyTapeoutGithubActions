`default_nettype none
`timescale 1ns / 1ps

/* Testbench for 8-bit Counter with TinyTapeout interface
   This testbench instantiates the module and provides convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  // Dump the signals to a VCD file. You can view it with gtkwave or surfer.
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;
`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  // Convenient signal names for 8-bit counter interface
  wire load = ui_in[0];
  wire output_enable = ui_in[1];
  wire [7:0] load_value = uio_in;
  wire [7:0] counter_out = uo_out;

  // 8-bit Counter module instantiation
  tt_um_example user_project (

      // Include power ports for the Gate Level test:
`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif

      .ui_in  (ui_in),    // Dedicated inputs: [1]=output_enable, [0]=load
      .uo_out (uo_out),   // Dedicated outputs: 8-bit counter output
      .uio_in (uio_in),   // IOs: Input path - 8-bit load value
      .uio_out(uio_out),  // IOs: Output path - unused
      .uio_oe (uio_oe),   // IOs: Enable path - all inputs
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset (active low)
  );

  // Initialize signals for simulation
  // Cocotb will drive these, but they need initial values to avoid X states
  initial begin
    clk = 0;
    rst_n = 0;
    ena = 0;
    ui_in = 0;
    uio_in = 0;
  end

endmodule
