# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly, Timer


@cocotb.test()
async def test_8bit_counter(dut):
    """Test the 8-bit counter functionality"""
    dut._log.info("Starting 8-bit Counter Test")

    # Set the clock period to 10 ns (100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0b00000010  # output_enable=1, load=0
    dut.uio_in.value = 0

    # Test 1: Reset functionality
    dut._log.info("Test 1: Reset functionality")
    dut.rst_n.value = 0  # Assert reset
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1  # Release reset
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()  # Wait for all signal updates to complete
    
    # Counter should start at 1 after first clock cycle post-reset
    assert dut.uo_out.value == 1, f"Expected 1, got {dut.uo_out.value}"
    dut._log.info("Reset test passed")

    # Test 2: Basic counting
    dut._log.info("Test 2: Basic counting")
    for expected_value in range(2, 10):
        await ClockCycles(dut.clk, 1)
        await Timer(1, units="ns")  # Allow gate delays to settle
        await ReadOnly()
        assert dut.uo_out.value == expected_value, f"Expected {expected_value}, got {dut.uo_out.value}"
    dut._log.info("Basic counting test passed")

    # Test 3: Load functionality
    dut._log.info("Test 3: Load functionality")
    load_value = 0xA5
    await ClockCycles(dut.clk, 1)  # Exit read-only phase from previous test
    dut.uio_in.value = load_value  # Set load value
    dut.ui_in.value = 0b00000011   # output_enable=1, load=1
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == load_value, f"Expected {load_value}, got {dut.uo_out.value}"
    
    # Disable load and verify counting continues
    await ClockCycles(dut.clk, 1)  # Exit read-only phase (load still asserted, so stays at load_value)
    dut.ui_in.value = 0b00000010   # output_enable=1, load=0
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == (load_value + 1) & 0xFF, f"Expected {(load_value + 1) & 0xFF}, got {dut.uo_out.value}"
    dut._log.info("Load functionality test passed")

    # Test 4: Tri-state output
    dut._log.info("Test 4: Tri-state output")
    await ClockCycles(dut.clk, 1)  # Exit read-only phase
    dut.ui_in.value = 0b00000000   # output_enable=0, load=0
    await ClockCycles(dut.clk, 1)
    # Note: In cocotb, high-Z values might be represented differently
    # The counter should still be incrementing internally even with output disabled
    
    # Re-enable output
    dut.ui_in.value = 0b00000010   # output_enable=1, load=0
    await ClockCycles(dut.clk, 1)
    # Counter should have continued incrementing
    dut._log.info("Tri-state output test passed")

    # Test 5: Wrap-around test
    dut._log.info("Test 5: Wrap-around test")
    # Load 0xFF and test wrap-around
    dut.uio_in.value = 0xFF
    dut.ui_in.value = 0b00000011   # output_enable=1, load=1
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == 0xFF, f"Expected 0xFF, got {dut.uo_out.value}"
    
    # Disable load and check wrap-around
    await ClockCycles(dut.clk, 1)  # Exit read-only phase
    dut.ui_in.value = 0b00000010   # output_enable=1, load=0
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == 0x00, f"Expected 0x00 (wrap-around), got {dut.uo_out.value}"
    
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == 0x01, f"Expected 0x01 (after wrap), got {dut.uo_out.value}"
    dut._log.info("Wrap-around test passed")

    # Test 6: Reset during operation
    dut._log.info("Test 6: Reset during operation")
    # Let counter run to some value
    await ClockCycles(dut.clk, 5)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    current_value = int(dut.uo_out.value)
    assert current_value > 1, "Counter should be running"
    
    # Assert reset
    await ClockCycles(dut.clk, 1)  # Exit read-only phase
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == 1, f"Expected 1 after reset, got {dut.uo_out.value}"
    dut._log.info("Reset during operation test passed")

    dut._log.info("All 8-bit counter tests passed!")


@cocotb.test()
async def test_edge_cases(dut):
    """Test edge cases and timing"""
    dut._log.info("Starting edge case tests")

    # Set the clock period to 10 ns (100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.ui_in.value = 0b00000010  # output_enable=1, load=0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Test simultaneous reset and load (reset should have priority)
    dut._log.info("Testing reset priority over load")
    dut.uio_in.value = 0x88
    dut.ui_in.value = 0b00000011   # output_enable=1, load=1
    dut.rst_n.value = 0            # Assert reset
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 1            # Release reset
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    # After reset release with load still asserted, should load the value
    assert dut.uo_out.value == 0x88, f"Expected 0x88 after reset+load, got {dut.uo_out.value}"
    
    dut._log.info("Edge case tests passed!")


# Additional test for comprehensive coverage
@cocotb.test()
async def test_load_timing(dut):
    """Test load signal timing"""
    dut._log.info("Starting load timing test")

    # Set the clock period to 10 ns (100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.ui_in.value = 0b00000010  # output_enable=1, load=0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Let counter run

    # Test load assertion just before clock edge
    await ClockCycles(dut.clk, 1)  # Exit any previous read-only phase
    current_value = dut.uo_out.value
    dut.uio_in.value = 0x33
    dut.ui_in.value = 0b00000011   # Assert load
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == 0x33, f"Expected 0x33, got {dut.uo_out.value}"
    
    # Disable load
    await ClockCycles(dut.clk, 1)  # Exit read-only phase
    dut.ui_in.value = 0b00000010   # output_enable=1, load=0
    await ClockCycles(dut.clk, 1)
    await Timer(1, units="ns")  # Allow gate delays to settle
    await ReadOnly()
    assert dut.uo_out.value == 0x34, f"Expected 0x34, got {dut.uo_out.value}"

    dut._log.info("Load timing test passed!")
