/*
 * Copyright (c) 2024 Tahir Bangash
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// 8-bit Counter with Asynchronous Reset, Synchronous Load, and Tri-state Output
// Adapted for TinyTapeout interface
module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Input pin assignments for 8-bit counter
    wire reset = ~rst_n;           // Convert active-low reset to active-high
    wire load = ui_in[0];          // Load enable signal
    wire output_enable = ui_in[1]; // Output enable for tri-state
    wire [7:0] load_value = uio_in; // 8-bit load value from bidirectional pins
    
    // Internal counter register
    reg [7:0] counter;
    
    // Counter logic with asynchronous reset and synchronous load
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            // Asynchronous reset - highest priority
            counter <= 8'h00;
        end else if (load) begin
            // Synchronous load - second priority
            counter <= load_value;
        end else begin
            // Normal increment operation
            counter <= counter + 1'b1;
        end
    end
    
    // Output assignments
    assign uo_out = output_enable ? counter : 8'hzz;  // Tri-state counter output
    assign uio_out = 8'h00;  // Bidirectional outputs not used (input only for load_value)
    assign uio_oe = 8'h00;   // All bidirectional pins set as inputs
    
    // List unused inputs to prevent warnings
    wire _unused = &{ena, ui_in[7:2], 1'b0};

endmodule
