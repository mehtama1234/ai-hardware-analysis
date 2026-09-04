#!/usr/bin/env python3
from __future__ import annotations


def row_voltages(vin: float, cell_resistance: float, segment_resistance: float, cells: int) -> list[float]:
    voltages = [vin for _ in range(cells)]
    for _ in range(4000):
        old = voltages[:]
        for i in range(cells):
            conductance_sum = 1.0 / cell_resistance
            current_sum = 0.0
            if i == 0:
                conductance_sum += 1.0 / segment_resistance
                current_sum += vin / segment_resistance
            else:
                conductance_sum += 1.0 / segment_resistance
                current_sum += voltages[i - 1] / segment_resistance
            if i < cells - 1:
                conductance_sum += 1.0 / segment_resistance
                current_sum += voltages[i + 1] / segment_resistance
            voltages[i] = current_sum / conductance_sum
        if max(abs(a - b) for a, b in zip(old, voltages)) < 1e-12:
            break
    return voltages


def main() -> None:
    vin = 0.8
    cell_resistance = 10_000.0
    ideal_current_per_cell = vin / cell_resistance

    print("row_wire_drop_sweep")
    print("cells,rseg_ohm,far_voltage,total_current_uA,ideal_current_uA,current_loss_percent")
    for cells in [4, 8, 16, 32, 64, 128]:
        for rseg in [5.0, 25.0, 100.0, 500.0]:
            voltages = row_voltages(vin, cell_resistance, rseg, cells)
            total_current = sum(v / cell_resistance for v in voltages)
            ideal_current = cells * ideal_current_per_cell
            loss = 100.0 * (ideal_current - total_current) / ideal_current
            print(
                f"{cells},{rseg:.1f},{voltages[-1]:.6f},"
                f"{total_current * 1e6:.3f},{ideal_current * 1e6:.3f},{loss:.3f}"
            )

    print("\nInterpretation")
    print("Cells farther from the driver see lower voltage when row resistance grows.")
    print("Large arrays improve reuse but increase the physical error the calibration must cover.")


if __name__ == "__main__":
    main()
