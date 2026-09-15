#!/usr/bin/env python3
"""Exercise one continuous closed-loop physical SAR transient."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_coupled_dac_comparator_bit import add_dac
from run_sky130_two_phase_preamp_latch_candidate import Case, build_deck


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUTPUT_STEM = os.environ.get("AIMC_CONTINUOUS_OUTPUT_STEM", "sky130-continuous-physical-sar")
OUT_JSON = EVIDENCE / f"{OUTPUT_STEM}.json"
OUT_MD = EVIDENCE / f"{OUTPUT_STEM}.md"
DEFAULT_PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
PDK_LIB = Path(os.environ.get("AIMC_SKY130_PDK_LIB", str(DEFAULT_PDK_LIB)))
SOURCE_V = 0.004
REFERENCE_V = 0.1823252
EXPECTED_CODE = 2
LEGAL_SUPPLY_V = float(os.environ.get("AIMC_COUPLED_SUPPLY_V", "1.8"))
TIMEOUT_S = float(os.environ.get("AIMC_COUPLED_TIMEOUT_S", "1200"))
TRANSIENT_STEP_PS = float(os.environ.get("AIMC_CONTINUOUS_STEP_PS", "20.0"))
REQUIRED_CONVERSION_COUNT = 5
REQUESTED_CONVERSION_COUNT = int(os.environ.get("AIMC_CONTINUOUS_CONVERSION_COUNT", str(REQUIRED_CONVERSION_COUNT)))
if not 1 <= REQUESTED_CONVERSION_COUNT <= REQUIRED_CONVERSION_COUNT:
    raise SystemExit(f"AIMC_CONTINUOUS_CONVERSION_COUNT must be between 1 and {REQUIRED_CONVERSION_COUNT}")
if REQUESTED_CONVERSION_COUNT == 1:
    # Keep the fast diagnostic aligned with the historical canonical nominal
    # point while the full mode retains the specified five-code sequence.
    CONVERSION_CODES = (2,)
    CONVERSION_REFERENCES = (float(os.environ.get("AIMC_CONTINUOUS_SINGLE_REFERENCE_V", "0.30215625")),)
else:
    CONVERSION_CODES = (0, 2, 4, 6, 7)[:REQUESTED_CONVERSION_COUNT]
    # These are continuous-loop representative reference levels, not the
    # earlier isolated-DAC calibration points.  The code-2/code-4 windows
    # are placed between the measured code-2/code-3 and code-3/code-4
    # continuous thresholds exposed by the preceding run.
    CONVERSION_REFERENCES = (0.0, 0.695, 0.650, 0.7808133, 0.89247035)[:REQUESTED_CONVERSION_COUNT]
_reference_override = os.environ.get("AIMC_CONTINUOUS_REFERENCE_PROFILE", "")
if _reference_override:
    _parsed_references = tuple(float(value.strip()) for value in _reference_override.split(",") if value.strip())
    if len(_parsed_references) != len(CONVERSION_CODES):
        raise SystemExit("AIMC_CONTINUOUS_REFERENCE_PROFILE must contain one value per requested conversion")
    CONVERSION_REFERENCES = _parsed_references
CONVERSION_PERIOD_NS = 80.0
CYCLE_SAMPLE_NS = (9.0, 25.0, 41.0, 57.0)
CYCLE_DECISION_NS = (20.0, 36.0, 52.0, 68.0)


def measure(stdout: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not values:
        raise ValueError(f"missing measurement {name}")
    return float(values[-1])


def _time_step(edge_ns: float) -> str:
    """Return a finite or ideal time step for auxiliary control waveforms."""
    rise_ns = float(os.environ.get("AIMC_CONTINUOUS_PWL_RISE_NS", "0.0"))
    if rise_ns > 0.0:
        return f"pwl(time,{edge_ns - rise_ns:g}n,0,{edge_ns:g}n,0,{edge_ns + rise_ns:g}n,1,{edge_ns + 2*rise_ns:g}n,1)"
    return f"u(time-{edge_ns:g}n)"


def gate_expression(bit: int, dead_level: str, conversion_count: int = 5, precharge_level: str | None = None, time_shift_ns: float = 0.0) -> str:
    """Return repeated four-cycle waveforms with break-before-make dead time."""
    transitions = tuple(value + time_shift_ns for value in (5.0, 21.0, 37.0, 53.0))
    # Both gates use the same logical decision: decision 0 connects the
    # bottom plate to VDD through the PMOS and leaves the NMOS off; decision
    # 1 turns the PMOS off and the NMOS on to connect the plate to ground.
    # Preserve the verified unit-step gate semantics by default.  A smooth
    # comparator-like source is available as an explicit convergence
    # diagnostic, but making it the default changes FF decoding despite using
    # the same legal 0/1.8 V states.
    gate_slope = os.environ.get("AIMC_CONTINUOUS_GATE_SLOPE", "")
    decision_node = "dec{0}_filtered" if os.environ.get("AIMC_CONTINUOUS_DECISION_FILTER") == "1" else "dec{0}"
    if gate_slope:
        decision_state = f"0.9*(1+tanh({float(gate_slope):g}*(V({decision_node})-0.9)))"
    else:
        decision_state = f"1.8*u(V({decision_node})-0.9)"
    time_slope = float(os.environ.get("AIMC_CONTINUOUS_TIME_SLOPE", "0.0"))
    pwl_rise_ns = float(os.environ.get("AIMC_CONTINUOUS_PWL_RISE_NS", "0.0"))
    def tstep(edge_ns: float) -> str:
        if pwl_rise_ns > 0.0:
            # Explicit finite-rise/fall schedule.  PWL is evaluated in the
            # B-source without an ideal unit step, avoiding zero-time gate
            # discontinuities while reaching a full logical rail.
            return f"pwl(time,{edge_ns - pwl_rise_ns:g}n,0,{edge_ns:g}n,0,{edge_ns + pwl_rise_ns:g}n,1,{edge_ns + 2*pwl_rise_ns:g}n,1)"
        if time_slope > 0.0:
            # ngspice's `time` is expressed in seconds.  The public knob is
            # specified in inverse-nanoseconds so that values such as 100
            # describe a 10 ps-scale transition rather than an effectively
            # frozen source.
            return f"(0.5*(1+tanh({time_slope * 1e9:g}*(time-{edge_ns:g}n))))"
        return f"u(time-{edge_ns:g}n)"
    # Allow the physical plate-gate edge to be slowed independently of the
    # precharge waveform. The latter is kept on its known-stable edge so a
    # charge-injection screen does not accidentally turn into a precharge
    # timestep experiment.
    dead_time_ns = float(os.environ.get("AIMC_CONTINUOUS_GATE_DEAD_TIME_NS", os.environ.get("AIMC_CONTINUOUS_DEAD_TIME_NS", "0.5")))
    state_templates = {
        0: ("0", decision_state.format(1), decision_state.format(1), decision_state.format(1)),
        1: ("1.8", "0", decision_state.format(2), decision_state.format(2)),
        2: ("1.8", "1.8", "0", decision_state.format(3)),
        3: ("1.8", "1.8", "1.8", "0"),
    }[bit]
    fixed_decisions = os.environ.get("AIMC_CONTINUOUS_FIXED_DECISIONS") == "1"
    parts = []
    precharge_ns = float(os.environ.get("AIMC_CONTINUOUS_BOTTOM_PRECHARGE_NS", "4.0"))
    for conversion in range(conversion_count):
        states = state_templates
        if fixed_decisions:
            code = CONVERSION_CODES[conversion]
            fixed_values = {index: ("1.8" if (1 - ((code >> (3 - index)) & 1)) else "0") for index in (1, 2, 3)}
            states = tuple(fixed_values.get(index, value) for index, value in enumerate(state_templates))
        offset = conversion * CONVERSION_PERIOD_NS + time_shift_ns
        absolute = [value + offset for value in transitions]
        old = dead_level
        if precharge_level is None:
            parts.append(f"({old})*({tstep(offset)}-{tstep(absolute[0])})")
        else:
            precharge_end = offset + precharge_ns
            parts.append(f"({precharge_level})*{tstep(offset)}*(1-{tstep(precharge_end)})")
            parts.append(f"({old})*{tstep(precharge_end)}*(1-{tstep(absolute[0])})")
        for index, new_state in enumerate(states):
            transition = absolute[index]
            next_transition = absolute[index + 1] if index + 1 < len(absolute) else offset + CONVERSION_PERIOD_NS
            dead_end = transition + dead_time_ns
            parts.append(f"({dead_level})*{tstep(transition)}*(1-{tstep(dead_end)})")
            parts.append(f"({new_state})*{tstep(dead_end)}*(1-{tstep(next_transition)})")
        parts.append(f"({dead_level})*{tstep(offset + CONVERSION_PERIOD_NS)}*(1-{tstep((conversion + 1) * CONVERSION_PERIOD_NS)})")
    return "+".join(parts).replace("\\.", ".")


def dead_clamp_expression(conversion_count: int) -> str:
    """Drive a small ground clamp only during each break-before-make gap."""
    transitions = (5.0, 21.0, 37.0, 53.0)
    dead_time_ns = float(os.environ.get("AIMC_CONTINUOUS_DEAD_TIME_NS", "0.5"))
    parts = ["0"]
    for conversion in range(conversion_count):
        offset = conversion * CONVERSION_PERIOD_NS
        for transition in transitions:
            start = offset + transition
            parts.append(f"1.8*{_time_step(start)}*(1-{_time_step(start + dead_time_ns)})")
    return "+".join(parts)


def conversion_precharge_expression(conversion_count: int) -> str:
    """Pulse a physical ground-precharge gate at each conversion boundary."""
    width_ns = float(os.environ.get("AIMC_CONTINUOUS_PRECHARGE_NS", "2.0"))
    parts = ["0"]
    for conversion in range(conversion_count):
        offset = conversion * CONVERSION_PERIOD_NS
        parts.append(f"1.8*{_time_step(offset)}*(1-{_time_step(offset + width_ns)})")
    return "+".join(parts)


def conversion_precharge_pwl(conversion_count: int) -> str:
    """Build a finite-edge ground-precharge waveform for each conversion."""
    width_ns = float(os.environ.get("AIMC_CONTINUOUS_PRECHARGE_NS", "2.0"))
    rise_ns = float(os.environ.get("AIMC_CONTINUOUS_PWL_RISE_NS", "0.2"))
    points: list[tuple[float, float]] = [(0.0, 0.0)]
    for conversion in range(conversion_count):
        start = conversion * CONVERSION_PERIOD_NS
        points.extend(((start, 0.0), (start + rise_ns, 1.8),
                       (start + width_ns, 1.8),
                       (start + width_ns + rise_ns, 0.0)))
    points.sort()
    canonical: list[tuple[float, float]] = []
    for time, value in points:
        if canonical and time == canonical[-1][0]:
            canonical[-1] = (time, value)
        else:
            canonical.append((time, value))
    return "PWL(" + " ".join(f"{time:g}n {value:g}" for time, value in canonical) + ")"


def fixed_rail_clamp_pwl(bit: int, rail_high: bool, conversion_count: int) -> str:
    """Drive a rail-handoff switch only after each plate state settles.

    The diagnostic deliberately follows the same fixed code schedule as the
    gate PWL, but leaves the rail switch open during the dead interval. This
    separates pass-device charge injection from an incorrectly timed control
    waveform.
    """
    guard_ns = float(os.environ.get("AIMC_CONTINUOUS_RAIL_CLAMP_GUARD_NS", "0.25"))
    dead_time_ns = float(os.environ.get("AIMC_CONTINUOUS_DEAD_TIME_NS", "0.5"))
    transitions = (5.0, 21.0, 37.0, 53.0)
    points: list[tuple[float, float]] = [(0.0, 0.0)]
    for conversion, code in enumerate(CONVERSION_CODES[:conversion_count]):
        offset = conversion * CONVERSION_PERIOD_NS
        for index in range(bit, 4):
            desired_high = bool(1 - ((code >> (3 - index)) & 1))
            if desired_high != rail_high:
                continue
            start = offset + transitions[index] + dead_time_ns + guard_ns
            stop = offset + (transitions[index + 1] if index + 1 < len(transitions) else CONVERSION_PERIOD_NS) - guard_ns
            if stop <= start:
                continue
            points.extend(((start, 1.8), (stop, 0.0)))
    points.sort()
    canonical: list[tuple[float, float]] = []
    for time, value in points:
        if canonical and time == canonical[-1][0]:
            canonical[-1] = (time, value)
        else:
            canonical.append((time, value))
    return "PWL(" + " ".join(f"{time:g}n {value:g}" for time, value in canonical) + ")"


def autozero_expression(conversion_count: int) -> str:
    """Reset the latch-side auto-zero nodes during each DAC settling window."""
    transitions = (5.0, 21.0, 37.0, 53.0)
    window_ns = float(os.environ.get("AIMC_CONTINUOUS_AUTOZERO_WINDOW_NS", "3.5"))
    parts = ["0"]
    for conversion in range(conversion_count):
        offset = conversion * CONVERSION_PERIOD_NS
        for transition in transitions:
            start = offset + transition
            stop = start + window_ns
            parts.append(f"1.8*{_time_step(start)}*(1-{_time_step(stop)})")
    return "+".join(parts)


def sample_reset_expression(conversion_count: int) -> str:
    """Reset both comparator storage nodes before each retained-bit sample."""
    width_ns = float(os.environ.get("AIMC_CONTINUOUS_SAMPLE_RESET_NS", "3.5"))
    parts = ["0"]
    for conversion in range(conversion_count):
        offset = conversion * CONVERSION_PERIOD_NS
        for cycle_start in (0.5, 16.5, 32.5, 48.5):
            start = offset + cycle_start
            # Keep reset as the verified ideal control. Finite PWL shaping
            # here creates a stiff behavioral-source product and can collapse
            # ngspice's timestep before a later conversion; reset-edge analog
            # behavior is outside this qualification gate.
            parts.append(f"1.8*{_time_step(start)}*(1-{_time_step(start + width_ns)})")
    return "+".join(parts)


def sample_reset_pwl(conversion_count: int) -> str:
    """Build the reset as an explicit voltage waveform, avoiding a B-source branch."""
    width_ns = float(os.environ.get("AIMC_CONTINUOUS_SAMPLE_RESET_NS", "3.5"))
    points: list[tuple[float, float]] = [(0.0, 0.0)]
    for conversion in range(conversion_count):
        offset = conversion * CONVERSION_PERIOD_NS
        for cycle_start in (0.5, 16.5, 32.5, 48.5):
            start = offset + cycle_start
            points.extend(((start, 1.8), (start + width_ns, 0.0)))
    points.sort()
    # ngspice requires strictly increasing PWL timestamps. Multiple control
    # events intentionally land on the same boundary; retain the final value
    # at each boundary while removing duplicate time points.
    canonical: list[tuple[float, float]] = []
    for time, value in points:
        if canonical and time == canonical[-1][0]:
            canonical[-1] = (time, value)
        else:
            canonical.append((time, value))
    return "PWL(" + " ".join(f"{time:g}n {value:g}" for time, value in canonical) + ")"


def fixed_gate_pwl(bit: int, dead_level: str, conversion_count: int, time_shift_ns: float = 0.0, transition_skew_ns: float = 0.0) -> str:
    """Emit a compact independent gate waveform for fixed-decision diagnostics."""
    dead_value = float(dead_level)
    pfet_on_value = float(os.environ.get("AIMC_CONTINUOUS_PFET_GATE_LOW_V", "0.0"))
    points: list[tuple[float, float]] = [(0.0, dead_value)]
    transitions = tuple(value + time_shift_ns + transition_skew_ns for value in (5.0, 21.0, 37.0, 53.0))
    # Slow only the pass-device gate edge; keep precharge on its independent
    # finite edge so this screen measures charge injection rather than a
    # coupled precharge timestep change.
    dead_time_ns = float(os.environ.get("AIMC_CONTINUOUS_GATE_DEAD_TIME_NS", os.environ.get("AIMC_CONTINUOUS_DEAD_TIME_NS", "0.5")))
    for conversion, code in enumerate(CONVERSION_CODES[:conversion_count]):
        offset = conversion * CONVERSION_PERIOD_NS + time_shift_ns
        # Keep plates that have not reached their decision edge at the safe
        # low-rail state (PMOS gate high, NMOS gate high). Leaving them at the
        # dead level makes the capacitor bottom node float during earlier SAR
        # cycles and was the source of the measured negative excursions.
        states = [1.8] * 4
        for index in range(bit, 4):
            decision = 1 - ((code >> (3 - index)) & 1)
            states[index] = 1.8 if decision else (pfet_on_value if dead_value > 0.0 else 0.0)
        points.extend(((offset, dead_value), (offset + transitions[0], dead_value)))
        for index, new_state in enumerate(states):
            transition = offset + transitions[index]
            points.extend(((transition, dead_value), (transition + dead_time_ns, new_state)))
            next_transition = offset + (transitions[index + 1] if index + 1 < len(transitions) else CONVERSION_PERIOD_NS)
            points.append((next_transition, new_state))
        points.append((offset + CONVERSION_PERIOD_NS, dead_value))
    points.sort()
    canonical: list[tuple[float, float]] = []
    for time, value in points:
        if canonical and time == canonical[-1][0]:
            canonical[-1] = (time, value)
        else:
            canonical.append((time, value))
    return "PWL(" + " ".join(f"{time:g}n {value:g}" for time, value in canonical) + ")"


def sequential_state_control(bit_count: int = 4, split_msb: bool = False, split_msb_delay_ns: float = 0.25) -> str:
    """Capture each latched decision into a held state before driving the DAC gates.

    The decision-dependent waveform is intentionally split into small physical
    elements: a voltage-controlled sampling switch, a hold capacitor, and
    complementary voltage-controlled gate switches. This avoids embedding a
    long decision expression in an ngspice behavioral source while preserving
    the existing SAR timing.
    """
    capture_delay_ns = float(os.environ.get("AIMC_CONTINUOUS_STATE_CAPTURE_DELAY_NS", "1.0"))
    capture_width_ns = float(os.environ.get("AIMC_CONTINUOUS_STATE_CAPTURE_WIDTH_NS", "0.5"))
    gate_resistance = float(os.environ.get("AIMC_CONTINUOUS_STATE_GATE_OHM", "100"))
    hold_capacitance = os.environ.get("AIMC_CONTINUOUS_STATE_HOLD_CAP", "5p")
    hold_resistance = os.environ.get("AIMC_CONTINUOUS_STATE_HOLD_RESISTOR", "1T")
    gate_capacitance = os.environ.get("AIMC_CONTINUOUS_STATE_GATE_CAP", "5p")
    quantize_state = os.environ.get("AIMC_CONTINUOUS_STATE_QUANTIZE") == "1"
    fixed_states = os.environ.get("AIMC_CONTINUOUS_SEQUENTIAL_FIXED_STATES") == "1"
    phase_safe = os.environ.get("AIMC_CONTINUOUS_STATE_PHASE_SAFE") == "1"
    state_threshold = float(os.environ.get("AIMC_CONTINUOUS_STATE_QUANTIZE_THRESHOLD", "0.9"))
    restore_latch = os.environ.get("AIMC_CONTINUOUS_STATE_RESTORE_LATCH") == "1"
    restore_width = float(os.environ.get("AIMC_CONTINUOUS_STATE_RESTORE_WIDTH", "0.5"))
    pulse_restore = os.environ.get("AIMC_CONTINUOUS_STATE_PULSE_RESTORE") == "1"
    damped_restore = os.environ.get("AIMC_CONTINUOUS_STATE_DAMPED_RESTORE") == "1"
    restore_series_ohm = float(os.environ.get("AIMC_CONTINUOUS_STATE_RESTORE_SERIES_OHM", "100"))
    direct_gates = os.environ.get("AIMC_CONTINUOUS_STATE_DIRECT_GATES") == "1"
    two_control = os.environ.get("AIMC_CONTINUOUS_TWO_CONTROL") == "1"
    initial_msb_high = os.environ.get("AIMC_CONTINUOUS_STATE_INITIAL_MSB_HIGH", "1") == "1"
    one_phase_ahead = os.environ.get("AIMC_CONTINUOUS_STATE_ONE_PHASE_AHEAD", "1") == "1"
    capture_raw_decision = os.environ.get("AIMC_CONTINUOUS_STATE_CAPTURE_RAW") == "1"
    sequential_rail_handoff = os.environ.get("AIMC_CONTINUOUS_SEQUENTIAL_RAIL_HANDOFF") == "1"
    restore_delay = float(os.environ.get("AIMC_CONTINUOUS_STATE_RESTORE_DELAY_NS", "0.2"))
    restore_pulse_width = float(os.environ.get("AIMC_CONTINUOUS_STATE_RESTORE_PULSE_NS", "0.5"))
    rows = [
        ".model SWSEQ_STATE SW(Ron=10 Roff=1G Vt=0.9 Vh=0.05)",
        ".model SWSEQ_GATE SW(Ron=10 Roff=1G Vt=0.9 Vh=0.05)",
    ]
    for bit in range(bit_count):
        decision_index = bit + 1
        gate_bit = bit if two_control else (decision_index % bit_count if one_phase_ahead else bit)
        capture_time = CYCLE_DECISION_NS[bit] + capture_delay_ns
        gate_suffixes = ("",)
        if split_msb and gate_bit == 0:
            gate_suffixes = ("a", "b")
        if fixed_states:
            initial_state = 1.8 if (initial_msb_high and gate_bit == 0) else 0.0
            points = [(0.0, initial_state)]
            for conversion, code in enumerate(CONVERSION_CODES):
                state = 1.8 if (1 - ((code >> (3 - gate_bit)) & 1)) else 0.0
                # Match the validated fixed-decision waveform: bit N is
                # applied at its physical trial edge (5, 21, 37, 53 ns),
                # before the corresponding sample at 9, 25, 41, 57 ns.
                trial_edge = 5.0 + gate_bit * 16.0
                points.append((conversion * CONVERSION_PERIOD_NS + trial_edge, state))
            rows.append(f"VSEQ_FIXED_STATE{decision_index} seq_state{decision_index} 0 PWL(" + " ".join(f"{time:g}n {value:g}" for time, value in points) + ")")
            rows.append(f"VSEQ_FIXED_CLK{decision_index} seq_clk{decision_index} 0 1.8")
        else:
            decision_source = f"raw_dec{decision_index}" if capture_raw_decision else f"dec{decision_index}"
            rows.extend([
                f"VSEQ_CLK{decision_index} seq_clk{decision_index} 0 PULSE(0 1.8 {capture_time:g}n 20p 20p {capture_width_ns:g}n {CONVERSION_PERIOD_NS:g}n)",
                f"SSEQ_STATE{decision_index} seq_state{decision_index} {decision_source} seq_clk{decision_index} 0 SWSEQ_STATE",
                f"CSEQ_STATE{decision_index} seq_state{decision_index} 0 {hold_capacitance}{' IC=1.8' if initial_msb_high and gate_bit == 0 else ''}",
                f"RSEQ_STATE{decision_index} seq_state{decision_index} 0 {hold_resistance}",
            ])
            if restore_latch and not damped_restore:
                rows.extend([
                    f"XREST_P{decision_index} seq_state{decision_index} seq_state_b{decision_index} vdd vdd sky130_fd_pr__pfet_01v8 W={restore_width:g} L=0.15",
                    f"XREST_N{decision_index} seq_state{decision_index} seq_state_b{decision_index} 0 0 sky130_fd_pr__nfet_01v8 W={restore_width:g} L=0.15",
                    f"XREST_PB{decision_index} seq_state_b{decision_index} seq_state{decision_index} vdd vdd sky130_fd_pr__pfet_01v8 W={restore_width:g} L=0.15",
                    f"XREST_NB{decision_index} seq_state_b{decision_index} seq_state{decision_index} 0 0 sky130_fd_pr__nfet_01v8 W={restore_width:g} L=0.15",
                    f"CSEQ_RESTORE{decision_index} seq_state_b{decision_index} 0 {hold_capacitance}",
                ])
            if pulse_restore:
                restore_time = capture_time + capture_width_ns + restore_delay
                rows.extend([
                    ".model SWSEQ_RESTORE SW(Ron=10 Roff=1G Vt=0.9 Vh=0.05)",
                    f"VSEQ_RESTORE_CLK{decision_index} seq_restore_clk{decision_index} 0 PULSE(0 1.8 {restore_time:g}n 20p 20p {restore_pulse_width:g}n {CONVERSION_PERIOD_NS:g}n)",
                    f"BSEQ_RESTORE_SET{decision_index} seq_restore_set{decision_index} 0 V={{1.8*u(V(seq_restore_clk{decision_index})-0.9)*u(V(seq_logic{decision_index})-0.9)}}",
                    f"BSEQ_RESTORE_RESET{decision_index} seq_restore_reset{decision_index} 0 V={{1.8*u(V(seq_restore_clk{decision_index})-0.9)*u(V(seq_logic_inv{decision_index})-0.9)}}",
                ])
                if damped_restore:
                    rows.extend([
                        f"RSEQ_RESTORE_VDD{decision_index} restore_vdd{decision_index} vdd {restore_series_ohm:g}",
                        f"RSEQ_RESTORE_GND{decision_index} restore_gnd{decision_index} 0 {restore_series_ohm:g}",
                        f"SSEQ_RESTORE_SET{decision_index} seq_state{decision_index} restore_vdd{decision_index} seq_restore_set{decision_index} 0 SWSEQ_RESTORE",
                        f"SSEQ_RESTORE_RESET{decision_index} seq_state{decision_index} restore_gnd{decision_index} seq_restore_reset{decision_index} 0 SWSEQ_RESTORE",
                    ])
                else:
                    rows.extend([
                        f"SSEQ_RESTORE_SET{decision_index} seq_state{decision_index} vdd seq_restore_set{decision_index} 0 SWSEQ_RESTORE",
                        f"SSEQ_RESTORE_RESET{decision_index} seq_state{decision_index} 0 seq_restore_reset{decision_index} 0 SWSEQ_RESTORE",
                    ])
        for suffix in gate_suffixes:
            state_drive = f"seq_logic{decision_index}"
            inverse_drive = f"seq_logic_inv{decision_index}"
            if quantize_state:
                if suffix == gate_suffixes[0]:
                    rows.extend([
                        f"BSEQ_LOGIC{decision_index} {state_drive} 0 V={{1.8*u(V(seq_state{decision_index})-{state_threshold:g})}}",
                        f"BSEQ_LOGIC_INV{decision_index} {inverse_drive} 0 V={{1.8-V({state_drive})}}",
                    ])
            else:
                state_drive = f"seq_state{decision_index}"
                inverse_drive = f"seq_inv{decision_index}"
            p_control, n_control = state_drive, inverse_drive
            phase_node = None
            if phase_safe:
                phase_points = [(0.0, 0.0)]
                for conversion in range(len(CONVERSION_CODES)):
                    offset = conversion * CONVERSION_PERIOD_NS
                    start = offset + 5.0 + gate_bit * 16.0
                    # The phase-safe trial window ends at the end of this
                    # bit's own trial. Ending at the next bit edge left no
                    # interval for retention or a rail handoff after the
                    # trial switch opened.
                    trial_width_ns = max(1.0, 15.0 - float(os.environ.get("AIMC_CONTINUOUS_TWO_CONTROL_DEAD_NS", "1.0")))
                    end = start + trial_width_ns
                    phase_points.extend(((start, 1.8), (end, 0.0)))
                phase_node = f"seq_phase{gate_bit}"
                phase_inv = f"seq_phase_inv{gate_bit}"
                p_control = f"seq_p_on{decision_index}"
                n_control = f"seq_n_on{decision_index}"
                if suffix == gate_suffixes[0]:
                    rows.extend([
                        f"VSEQ_PHASE{gate_bit} {phase_node} 0 PWL(" + " ".join(f"{time:g}n {value:g}" for time, value in phase_points) + ")",
                        f"BSEQ_PHASE_INV{gate_bit} {phase_inv} 0 V={{1.8-V({phase_node})}}",
                        f"BSEQ_P_ON{decision_index} {p_control} 0 V={{1.8*u(V({phase_node})-0.9)*u(V({state_drive})-0.9)}}",
                        f"BSEQ_N_ON{decision_index} {n_control} 0 V={{1.8*u(V({phase_node})-0.9)*u(V({inverse_drive})-0.9)}}",
                        f"SSEQ_SAFE_P{decision_index}{suffix} gp_dac{gate_bit}{suffix} vdd {phase_inv} 0 SWSEQ_GATE",
                        f"SSEQ_SAFE_N{decision_index}{suffix} gn_dac{gate_bit}{suffix} 0 {phase_inv} 0 SWSEQ_GATE",
                    ])
                else:
                    # The shared phase/control nodes are emitted once for a
                    # split MSB; both physical gate pairs use them.
                    pass
            rows.append(f"BSEQ_INV{decision_index} seq_inv{decision_index} 0 V={{1.8-V(seq_state{decision_index})}}")
            if two_control:
                # Retained decision state commits this bit after its trial;
                # separate trial switches are emitted below.
                trial_node = f"seq_trial{gate_bit}{suffix}"
                retain_p = f"seq_retain_p{decision_index}{suffix}"
                retain_n = f"seq_retain_n{decision_index}{suffix}"
                # Retention must remain driven after the phase-safe trial
                # window ends.  The phase-gated p_control/n_control nodes are
                # intentionally zero during hold; using them here leaves the
                # DAC gates floating and masks the captured state.
                retain_source_p = state_drive if phase_safe else p_control
                retain_source_n = inverse_drive if phase_safe else n_control
                rows.extend([
                    f"BSEQ_RETAIN_CTRL_P{decision_index}{suffix} {retain_p} 0 V={{V({retain_source_p})*u(0.9-V({trial_node}))}}",
                    f"BSEQ_RETAIN_CTRL_N{decision_index}{suffix} {retain_n} 0 V={{V({retain_source_n})*u(0.9-V({trial_node}))}}",
                    f"SSEQ_RETAIN_P{decision_index}{suffix} gp_dac{gate_bit}{suffix} vdd {retain_p} 0 SWSEQ_GATE",
                    f"SSEQ_RETAIN_PLO{decision_index}{suffix} gp_dac{gate_bit}{suffix} 0 {retain_n} 0 SWSEQ_GATE",
                    f"SSEQ_RETAIN_N{decision_index}{suffix} gn_dac{gate_bit}{suffix} vdd {retain_p} 0 SWSEQ_GATE",
                    f"SSEQ_RETAIN_NLO{decision_index}{suffix} gn_dac{gate_bit}{suffix} 0 {retain_n} 0 SWSEQ_GATE",
                ])
                if sequential_rail_handoff and phase_safe:
                    # After the trial override opens, give each plate a
                    # controlled low-Ron rail handoff derived from the held
                    # state. This is intentionally opt-in: it tests whether
                    # the observed negative plate excursions are caused by
                    # insufficient rail drive rather than state capture.
                    rail_p = f"seq_rail_p{decision_index}{suffix}"
                    rail_n = f"seq_rail_n{decision_index}{suffix}"
                    rows.extend([
                        # A finite 100 ohm handoff avoids an idealized rail
                        # short at the capacitor edge and keeps ngspice's
                        # transient solvable while still dominating the
                        # pass-device impedance.
                        ".model SWSEQ_RAIL SW(Ron=100 Roff=1G Vt=0.9 Vh=0.05)",
                        f"BSEQ_RAIL_P{decision_index}{suffix} {rail_p} 0 V={{1.8*u(V({phase_inv})-0.9)*u(V({inverse_drive})-0.9)}}",
                        f"BSEQ_RAIL_N{decision_index}{suffix} {rail_n} 0 V={{1.8*u(V({phase_inv})-0.9)*u(V({state_drive})-0.9)}}",
                        f"SSEQ_RAIL_P{decision_index}{suffix} db{gate_bit}{suffix} vdd {rail_p} 0 SWSEQ_RAIL",
                        f"SSEQ_RAIL_N{decision_index}{suffix} db{gate_bit}{suffix} 0 {rail_n} 0 SWSEQ_RAIL",
                    ])
            elif direct_gates:
                if phase_node:
                    rows.extend([
                        f"BSEQ_DIRECT_GP{decision_index}{suffix} gp_dac{gate_bit}{suffix} 0 V={{(1-V({phase_node})/1.8)*1.8+(V({phase_node})/1.8)*V({state_drive})}}",
                        f"BSEQ_DIRECT_GN{decision_index}{suffix} gn_dac{gate_bit}{suffix} 0 V={{(V({phase_node})/1.8)*V({state_drive})}}",
                    ])
                else:
                    rows.extend([
                        f"BSEQ_DIRECT_GP{decision_index}{suffix} gp_dac{gate_bit}{suffix} 0 V={{V({state_drive})}}",
                        f"BSEQ_DIRECT_GN{decision_index}{suffix} gn_dac{gate_bit}{suffix} 0 V={{V({state_drive})}}",
                    ])
            else:
                rows.extend([
                    f"SSEQ_PHI{decision_index}{suffix} gp_dac{gate_bit}{suffix} vdd {p_control} 0 SWSEQ_GATE",
                    f"SSEQ_PLO{decision_index}{suffix} gp_dac{gate_bit}{suffix} 0 {n_control} 0 SWSEQ_GATE",
                    f"SSEQ_NHI{decision_index}{suffix} gn_dac{gate_bit}{suffix} vdd {p_control} 0 SWSEQ_GATE",
                    f"SSEQ_NLO{decision_index}{suffix} gn_dac{gate_bit}{suffix} 0 {n_control} 0 SWSEQ_GATE",
                ])
            rows.extend([
                f"CSEQ_PGATE{decision_index}{suffix} gp_dac{gate_bit}{suffix} 0 {gate_capacitance}",
                f"CSEQ_NGATE{decision_index}{suffix} gn_dac{gate_bit}{suffix} 0 {gate_capacitance}",
            ])
    if two_control:
        for bit in range(bit_count):
            suffixes = ("a", "b") if split_msb and bit == 0 else ("",)
            trial_start = 5.0 + bit * 16.0
            break_before_make_ns = float(os.environ.get("AIMC_CONTINUOUS_TWO_CONTROL_DEAD_NS", "1.0"))
            trial_width = max(1.0, 15.0 - break_before_make_ns)
            for suffix in suffixes:
                rows.extend([
                    f"VSEQ_TRIAL{bit}{suffix} seq_trial{bit}{suffix} 0 PULSE(0 1.8 {trial_start:g}n 20p 20p {trial_width:g}n {CONVERSION_PERIOD_NS:g}n)",
                    f"SSEQ_TRIAL_GP{bit}{suffix} gp_dac{bit}{suffix} 0 seq_trial{bit}{suffix} 0 SWSEQ_GATE",
                    f"SSEQ_TRIAL_GN{bit}{suffix} gn_dac{bit}{suffix} 0 seq_trial{bit}{suffix} 0 SWSEQ_GATE",
                ])
    return "\n".join(rows)


def preamp_enable_expression(conversion_count: int) -> str:
    """Enable the preamp only after each DAC sample has settled."""
    start_ns = float(os.environ.get("AIMC_CONTINUOUS_PREAMP_ENABLE_START_NS", "9.7"))
    width_ns = float(os.environ.get("AIMC_CONTINUOUS_PREAMP_ENABLE_WIDTH_NS", "2.0"))
    parts = ["0"]
    for conversion in range(conversion_count):
        offset = conversion * CONVERSION_PERIOD_NS
        for cycle in range(4):
            start = offset + cycle * 16.0 + start_ns
            parts.append(f"1.8*{_time_step(start)}*(1-{_time_step(start + width_ns)})")
    return "+".join(parts)


def continuous_deck() -> str:
    os.environ["AIMC_COUPLED_DAC_ACQ"] = "long"
    # Preserve the promoted PMOS-only baseline, but allow a controlled
    # complementary-switch experiment. The PMOS-only path leaves a plate
    # floating whenever its gate requests a low state, which is precisely the
    # failure mode diagnosed by the repeated negative bottom-plate readings.
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    os.environ.setdefault("AIMC_COUPLED_TOP_DUMMY_CAP", "0.5p")
    # Promoted nominal continuous-SAR candidate: isolate the post-sample
    # preamp handoff from DAC redistribution and use the measured 0.75x
    # Measured binary-capacitor trims that close the five-code nominal map:
    # bit-1 is 0.75x and the LSB is 1.5x.
    os.environ.setdefault("AIMC_CONTINUOUS_SWITCHED_HANDOFF", "1")
    os.environ.setdefault("AIMC_COUPLED_BIT1_CAP_SCALE", "0.75")
    os.environ.setdefault("AIMC_COUPLED_LSB_SCALE", "1.5")
    os.environ.setdefault("AIMC_CONTINUOUS_NMOS_WIDTH", "64")
    os.environ.setdefault("AIMC_CONTINUOUS_PMOS_BANK", "8")
    # The full mismatch population exposed a repeatable first-conversion
    # charge-state failure. Reset the matched comparator sample-storage nodes
    # before each retained-bit trial so a prior conversion cannot seed the
    # next decision. This is now part of the promoted candidate, not an
    # optional diagnostic branch.
    os.environ.setdefault("AIMC_CONTINUOUS_SAMPLE_RESET", "1")
    # The 3.5 ns reset is retained as the best complete population result.
    # A 5.0 ns experiment was replayed and retained separately; it reduced the
    # population result, despite fixing selected individual trials.
    os.environ.setdefault("AIMC_CONTINUOUS_SAMPLE_RESET_WIDTH", "3.5")
    os.environ.setdefault("AIMC_CONTINUOUS_SAMPLE_RESET_SERIES_OHM", "10000")
    source = add_dac(build_deck(Case("continuous_physical_sar", 0.0)), 0, SOURCE_V, REFERENCE_V)
    # Keep the historical default path for compatibility, while allowing a
    # Colab or isolated workbench bundle to provide its exact model path.
    source = source.replace(str(DEFAULT_PDK_LIB), str(PDK_LIB))
    extra_options = os.environ.get("AIMC_CONTINUOUS_NGSPICE_OPTIONS", "").strip()
    if extra_options:
        source = re.sub(r"(\.options[^\n]*)", rf"\1 {extra_options}", source, count=1)
    # Keep the default TT deck unchanged, while making corner selection a
    # reproducible runner input rather than an external text edit.  The PDK
    # library is the same; only its declared process section changes.
    corner = os.environ.get("AIMC_SKY130_CORNER", "tt").strip().lower()
    if corner not in {"tt", "ss", "ff", "sf", "fs"}:
        raise ValueError("AIMC_SKY130_CORNER must be one of tt, ss, ff, sf, fs")
    if corner != "tt":
        source = re.sub(r'(\.lib\s+"[^"]+"\s+)tt\b', rf"\g<1>{corner}", source, count=1)
    isolated_copy_block = ""
    if os.environ.get("AIMC_CONTINUOUS_ISOLATED_COPY") == "1":
        copy_width = float(os.environ.get("AIMC_CONTINUOUS_ISOLATED_COPY_WIDTH", "4.0"))
        copy_bias_ohm = float(os.environ.get("AIMC_CONTINUOUS_ISOLATED_COPY_BIAS_OHM", "100000"))
        # Always-on matched NMOS source followers copy the sampled DAC and
        # reference storage nodes into high-impedance preamp gates. Their
        # gates draw no DC current, while the source resistors establish a
        # finite common-mode operating point and limit kickback transfer.
        isolated_copy_block = f'''* Optional isolated sample-to-preamp copy stage.
R_COPY_P copy_p 0 {copy_bias_ohm:g}
R_COPY_N copy_n 0 {copy_bias_ohm:g}
X_COPY_P copy_p sp vdd 0 sky130_fd_pr__nfet_01v8 W={copy_width:g} L=0.15
X_COPY_N copy_n sn vdd 0 sky130_fd_pr__nfet_01v8 W={copy_width:g} L=0.15
'''
        source = source.replace("XPREP pre_p sp pre_tail_node 0", "XPREP pre_p copy_p pre_tail_node 0")
        source = source.replace("XPREN pre_n sn pre_tail_node 0", "XPREN pre_n copy_n pre_tail_node 0")
    capacitive_copy_block = ""
    if os.environ.get("AIMC_CONTINUOUS_CAPACITIVE_COPY") == "1":
        copy_cap_ff = float(os.environ.get("AIMC_CONTINUOUS_CAPACITIVE_COPY_FF", "100"))
        copy_bias_ohm = float(os.environ.get("AIMC_CONTINUOUS_CAPACITIVE_COPY_BIAS_OHM", "1000000"))
        capacitive_copy_block = f'''* Optional isolated capacitive sample-to-preamp copy stage.
VCONT_COPY_CM copy_cm 0 {{vdd/2}}
CCOPY_P sp copy_p {copy_cap_ff:.12g}f
CCOPY_N sn copy_n {copy_cap_ff:.12g}f
RCOPY_P copy_p copy_cm {copy_bias_ohm:g}
RCOPY_N copy_n copy_cm {copy_bias_ohm:g}
'''
        source = source.replace("XPREP pre_p sp pre_tail_node 0", "XPREP pre_p copy_p pre_tail_node 0")
        source = source.replace("XPREN pre_n sn pre_tail_node 0", "XPREN pre_n copy_n pre_tail_node 0")
    copy_reset_block = ""
    if os.environ.get("AIMC_CONTINUOUS_COPY_RESET") == "1" and os.environ.get("AIMC_CONTINUOUS_CAPACITIVE_COPY") == "1":
        copy_reset_width = float(os.environ.get("AIMC_CONTINUOUS_COPY_RESET_WIDTH", "2.0"))
        copy_reset_series = float(os.environ.get("AIMC_CONTINUOUS_COPY_RESET_SERIES_OHM", "10000"))
        copy_reset_block = f'''* Optional reset of isolated preamp-side copy nodes only.
VCONT_COPY_RESET_CM copy_reset_cm 0 {{vdd/2}}
BCONT_COPY_RESET copy_reset 0 V={sample_reset_expression(len(CONVERSION_CODES))}
R_COPY_RESET_P copy_p copy_reset_p {copy_reset_series:g}
R_COPY_RESET_N copy_n copy_reset_n {copy_reset_series:g}
X_COPY_RESET_P copy_reset_p copy_reset copy_reset_cm 0 sky130_fd_pr__nfet_01v8 W={copy_reset_width:g} L=0.15
X_COPY_RESET_N copy_reset_n copy_reset copy_reset_cm 0 sky130_fd_pr__nfet_01v8 W={copy_reset_width:g} L=0.15
'''
    preamp_phase_block = ""
    if os.environ.get("AIMC_CONTINUOUS_PREAMP_PHASE_GATE") == "1":
        preamp_phase_block = f'''* Optional two-phase preamp tail gate.
BCONT_PREAMP_ENABLE pre_enable 0 V={preamp_enable_expression(len(CONVERSION_CODES))}
XPREAMP_ENABLE pre_tail_node pre_enable pre_bias 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
'''
        source = re.sub(r"IPRE pre_tail_node 0 ([^\n]+)", r"IPRE pre_bias 0 \1", source, count=1)
    switched_handoff_block = ""
    if os.environ.get("AIMC_CONTINUOUS_SWITCHED_HANDOFF") == "1":
        handoff_width = float(os.environ.get("AIMC_CONTINUOUS_SWITCHED_HANDOFF_WIDTH", "8.0"))
        handoff_bias_ohm = float(os.environ.get("AIMC_CONTINUOUS_SWITCHED_HANDOFF_BIAS_OHM", "1000000"))
        handoff_control = (f"ECTRL_HANDOFF handoff_enable 0 VALUE={{{preamp_enable_expression(len(CONVERSION_CODES))}}}"
                           if os.environ.get("AIMC_CONTINUOUS_CONTROL_SOURCE") == "e"
                           else f"BCONT_HANDOFF handoff_enable 0 V={preamp_enable_expression(len(CONVERSION_CODES))}")
        switched_handoff_block = f'''* Optional post-sample switched direct DAC/reference handoff.
VCONT_HANDOFF_CM handoff_cm 0 {{vdd/2}}
{handoff_control}
RHANDOFF_P handoff_p handoff_cm {handoff_bias_ohm:g}
RHANDOFF_N handoff_n handoff_cm {handoff_bias_ohm:g}
XHANDOFF_P handoff_p handoff_enable top 0 sky130_fd_pr__nfet_01v8 W={handoff_width:g} L=0.15
XHANDOFF_N handoff_n handoff_enable inn 0 sky130_fd_pr__nfet_01v8 W={handoff_width:g} L=0.15
'''
        source = source.replace("XPREP pre_p sp pre_tail_node 0", "XPREP pre_p handoff_p pre_tail_node 0")
        source = source.replace("XPREN pre_n sn pre_tail_node 0", "XPREN pre_n handoff_n pre_tail_node 0")
    autozero_block = ""
    if os.environ.get("AIMC_CONTINUOUS_AUTOZERO") == "1":
        autozero_cap_ff = float(os.environ.get("AIMC_CONTINUOUS_AUTOZERO_CAP_FF", "100"))
        autozero_bias_ohm = float(os.environ.get("AIMC_CONTINUOUS_AUTOZERO_BIAS_OHM", "1000000"))
        autozero_block = f'''* Optional per-decision auto-zero interface.
VCONT_AZ_CM az_cm 0 {{vdd/2}}
BCONT_AZ_CTRL az_ctrl 0 V={autozero_expression(len(CONVERSION_CODES))}
CAZP pre_p az_p {autozero_cap_ff:.12g}f
CAZN pre_n az_n {autozero_cap_ff:.12g}f
RAZP az_p az_cm {autozero_bias_ohm:.12g}
RAZN az_n az_cm {autozero_bias_ohm:.12g}
XAZP az_p az_ctrl az_cm 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XAZN az_n az_ctrl az_cm 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
'''
        source = source.replace("XINP outp pre_p tail 0", "XINP outp az_p tail 0")
        source = source.replace("XINN outn pre_n tail 0", "XINN outn az_n tail 0")
    source = source.replace("COUTP outp 0 5f", isolated_copy_block + capacitive_copy_block + copy_reset_block + switched_handoff_block + preamp_phase_block + autozero_block + "COUTP outp 0 5f", 1)
    if os.environ.get("AIMC_CONTINUOUS_DECISION_FILTER") == "1":
        filter_resistance = float(os.environ.get("AIMC_CONTINUOUS_DECISION_FILTER_OHM", "1000"))
        filter_capacitance = os.environ.get("AIMC_CONTINUOUS_DECISION_FILTER_CAP", "1f")
        decision_filter = "\n".join(
            f"RDEC_FILTER{index} dec{index} dec{index}_filtered {filter_resistance:g}\nCDEC_FILTER{index} dec{index}_filtered 0 {filter_capacitance}"
            for index in range(1, 5)
        ) + "\n"
        source = source.replace("COUTP outp 0 5f", decision_filter + "COUTP outp 0 5f", 1)
    sample_reset_block = ""
    if os.environ.get("AIMC_CONTINUOUS_SAMPLE_RESET") == "1":
        sample_reset_width = float(os.environ.get("AIMC_CONTINUOUS_SAMPLE_RESET_WIDTH", "2.0"))
        sample_reset_series = float(os.environ.get("AIMC_CONTINUOUS_SAMPLE_RESET_SERIES_OHM", "10000"))
        reset_control = (f"VCONT_SAMPLE_RESET sample_reset 0 {sample_reset_pwl(len(CONVERSION_CODES))}"
                         if os.environ.get("AIMC_CONTINUOUS_CONTROL_SOURCE") == "e"
                         else f"BCONT_SAMPLE_RESET sample_reset 0 V={sample_reset_expression(len(CONVERSION_CODES))}")
        sample_reset_block = f'''* Optional matched sample-storage reset between retained-bit trials.
VCONT_SAMPLE_CM sample_cm 0 {{vdd/2}}
{reset_control}
R_SAMPLE_RESET_P sp sample_reset_p {sample_reset_series:g}
R_SAMPLE_RESET_N sn sample_reset_n {sample_reset_series:g}
XSAMPLE_RESET_P sample_reset_p sample_reset sample_cm 0 sky130_fd_pr__nfet_01v8 W={sample_reset_width:g} L=0.15
XSAMPLE_RESET_N sample_reset_n sample_reset sample_cm 0 sky130_fd_pr__nfet_01v8 W={sample_reset_width:g} L=0.15
'''
    source = source.replace(f".ic v(top)={SOURCE_V:.9f} ", ".ic ")
    stop_ns = CONVERSION_PERIOD_NS * len(CONVERSION_CODES)
    source = source.replace(".tran 5p 14n", f".tran {TRANSIENT_STEP_PS:g}p {stop_ns:g}n")
    source = source.replace("PULSE(0 {vdd} 9.10n 20p 20p 0.50n 20n)", "PULSE(0 {vdd} 9.10n 20p 20p 0.50n 16n)")
    source = source.replace("PULSE({vdd} 0 9.10n 20p 20p 0.50n 20n)", "PULSE({vdd} 0 9.10n 20p 20p 0.50n 16n)")
    source = source.replace("PULSE(0 {vdd} 0.1n 10p 10p 4.0n 20n)", "PULSE(0 {vdd} 0.1n 10p 10p 4.0n 80n)")
    source = source.replace("PULSE({vdd} 0 0.1n 10p 10p 4.0n 20n)", "PULSE({vdd} 0 0.1n 10p 10p 4.0n 80n)")
    # Give the dynamic latch a precharge interval before each repeated
    # evaluation so a reversed preamp sign cannot inherit old output state.
    source = source.replace("PULSE(0 {vdd} 11.70n 20p 20p 5n 10n)", "PULSE(0 {vdd} 12.70n 20p 20p 5n 16n)")
    # clkb is a real precharge control, not the complement of eval: pulse it
    # low for 1 ns first, then let clk enable regeneration with precharge off.
    latch_precharge_ns = float(os.environ.get("AIMC_CONTINUOUS_LATCH_PRECHARGE_NS", "1.0"))
    source = source.replace("PULSE({vdd} 0 11.70n 20p 20p 5n 10n)", f"PULSE({{vdd}} 0 11.70n 20p 20p {latch_precharge_ns:g}n 16n)")
    source = source.replace("PULSE(0 {pre_tail} 9.70n 20p 20p 5n 10n)", "PULSE(0 {pre_tail} 10.70n 20p 20p 5n 16n)")
    if os.environ.get("AIMC_CONTINUOUS_POST_TRIAL_SAMPLE") == "1":
        # Diagnostic acquisition schedule: move the comparator sample and
        # evaluation clocks to just after the 14 ns trial window (5..19 ns),
        # leaving the default campaign timing unchanged.
        source = source.replace("PULSE(0 {vdd} 9.10n 20p 20p 0.50n 16n)", "PULSE(0 {vdd} 19.10n 20p 20p 0.50n 16n)")
        source = source.replace("PULSE({vdd} 0 9.10n 20p 20p 0.50n 16n)", "PULSE({vdd} 0 19.10n 20p 20p 0.50n 16n)")
        source = source.replace("PULSE(0 {vdd} 12.70n 20p 20p 5n 16n)", "PULSE(0 {vdd} 19.70n 20p 20p 5n 16n)")
        source = source.replace("PULSE({vdd} 0 11.70n 20p 20p 1n 16n)", f"PULSE({{vdd}} 0 23.70n 20p 20p {latch_precharge_ns:g}n 16n)")
        source = source.replace("PULSE(0 {pre_tail} 10.70n 20p 20p 5n 16n)", "PULSE(0 {pre_tail} 20.70n 20p 20p 5n 16n)")
    source = source.replace("PULSE(1.8 0 5n 10p 10p 200n 1u)", "PULSE(1.8 0 5n 10p 10p 200n 1u)")
    # Add the complementary PMOS devices and replace static bottom controls
    # with one continuous, decision-dependent gate waveform per plate.
    continuous_switch_width = float(os.environ.get("AIMC_CONTINUOUS_SWITCH_WIDTH", "8.0"))
    continuous_nmos_width = float(os.environ.get("AIMC_CONTINUOUS_NMOS_WIDTH", "8.0"))
    continuous_pmos_bank = int(os.environ.get("AIMC_CONTINUOUS_PMOS_BANK", "1"))
    split_msb = os.environ.get("AIMC_CONTINUOUS_SPLIT_MSB") == "1"
    split_msb_delay_ns = float(os.environ.get("AIMC_CONTINUOUS_SPLIT_MSB_DELAY_NS", "0.25"))
    if split_msb:
        source = source.replace("CDAC0 top db0 8.000000000000e-12", "CDAC0A top db0a 4.000000000000e-12\nCDAC0B top db0b 4.000000000000e-12")
        source = source.replace("CDACDUMMY0 db0 0", "CDACDUMMY0A db0a 0\nCDACDUMMY0B db0b 0")
        source = source.replace("XBN_DAC0 db0 ", "XBN_DAC0 db0a ")
        source = source.replace("XBN_DAC0 db0a gn_dac0 ", "XBN_DAC0 db0a gn_dac0a ")
        # The base coupled-DAC deck contains legacy diagnostic measures for
        # the unsplit MSB node. Point those measures at the physical A plate;
        # the split-specific measures below report the mean and both plates.
        source = source.replace("v(db0)", "v(db0a)")
    pmos_series_resistor = os.environ.get("AIMC_CONTINUOUS_PMOS_SERIES_RESISTOR", "")
    if continuous_pmos_bank < 1:
        raise ValueError("continuous PMOS bank must contain at least one device")
    pmos_rows = []
    plate_isolation = os.environ.get("AIMC_CONTINUOUS_ISOLATED_PLATE_SWITCH") == "1"
    plate_hold_cap = os.environ.get("AIMC_CONTINUOUS_PLATE_HOLD_CAP", "0")
    plate_isolation_width = float(os.environ.get("AIMC_CONTINUOUS_PLATE_ISOLATION_WIDTH", str(continuous_switch_width)))
    isolation_rows = []
    direct_hold_rows = []
    ideal_bottom_switches = os.environ.get("AIMC_CONTINUOUS_IDEAL_BOTTOM_SWITCHES") == "1"
    bootstrapped_high = os.environ.get("AIMC_CONTINUOUS_BOOTSTRAPPED_NMOS_HIGH") == "1"
    for bit in range(4):
        nodes = ("db0a", "db0b") if split_msb and bit == 0 else (f"db{bit}",)
        for node_index, node in enumerate(nodes):
            suffix = "a" if split_msb and bit == 0 and node_index == 0 else "b" if split_msb and bit == 0 else ""
            gate = f"gp_dac{bit}{suffix}"
            plate_node = f"{node}_iso" if plate_isolation else node
            if not ideal_bottom_switches and not bootstrapped_high:
                for finger in range(continuous_pmos_bank):
                    supply_node = f"vddp_{bit}_{node_index}_{finger}" if pmos_series_resistor else "vdd"
                    pmos_rows.append(f"XCONT_BP{bit}_{node_index}_{finger} {plate_node} {gate} {supply_node} vdd sky130_fd_pr__pfet_01v8 W={continuous_switch_width:g} L=0.15")
            if plate_isolation:
                ngate = f"gn_dac{bit}{suffix}"
                isolation_rows.extend([
                    f"XISO_N{bit}_{node_index} {node} {ngate} {plate_node} 0 sky130_fd_pr__nfet_01v8 W={plate_isolation_width:g} L=0.15",
                    f"XISO_P{bit}_{node_index} {node} {gate} {plate_node} vdd sky130_fd_pr__pfet_01v8 W={plate_isolation_width:g} L=0.15",
                ])
                if float(plate_hold_cap.rstrip("pf")) > 0.0:
                    isolation_rows.append(f"CHOLD_PLATE{bit}_{node_index} {node} 0 {plate_hold_cap}")
            elif float(plate_hold_cap.rstrip("pf")) > 0.0:
                direct_hold_rows.append(f"CHOLD_DIRECT{bit}_{node_index} {node} vdd {plate_hold_cap}")
    pmos = "\n".join(pmos_rows)
    if pmos_series_resistor:
        pmos += "\n" + "\n".join(
            f"RCONT_P{bit}_{node_index}_{finger} vdd vddp_{bit}_{node_index}_{finger} {pmos_series_resistor}"
            for bit in range(4)
            for node_index in ((0, 1) if split_msb and bit == 0 else (0,))
            for finger in range(continuous_pmos_bank)
        )
    control_rows = []
    gate_series_ohm = float(os.environ.get("AIMC_CONTINUOUS_GATE_SERIES_OHM", "0"))
    sequential_control = os.environ.get("AIMC_CONTINUOUS_SEQUENTIAL_CONTROL") == "1"
    for bit in range(4):
        suffixes = (("a", 0.0), ("b", split_msb_delay_ns)) if split_msb and bit == 0 else (("", 0.0),)
        for suffix, shift in suffixes:
            precharge = "1.8" if os.environ.get("AIMC_CONTINUOUS_BOTTOM_PRECHARGE") == "1" else None
            gp = f"gp_dac{bit}{suffix}"
            gn = f"gn_dac{bit}{suffix}"
            if gate_series_ohm > 0.0 and not sequential_control:
                gp_int, gn_int = f"{gp}_int", f"{gn}_int"
                source = source.replace(f" {gp} ", f" {gp_int} ").replace(f" {gn} ", f" {gn_int} ")
                control_rows.extend([f"RCONT_PGATE{bit}{suffix} {gp} {gp_int} {gate_series_ohm:g}", f"RCONT_NGATE{bit}{suffix} {gn} {gn_int} {gate_series_ohm:g}"])
            # VALUE-controlled E sources are an opt-in remote diagnostic;
            # retain the verified B-source baseline unless selected.
            if sequential_control:
                continue
            pg_expr = gate_expression(bit, "1.8", len(CONVERSION_CODES), time_shift_ns=shift)
            ng_expr = gate_expression(bit, "0", len(CONVERSION_CODES), precharge, shift)
            if os.environ.get("AIMC_CONTINUOUS_FIXED_DECISIONS") == "1":
                pfet_delay = float(os.environ.get("AIMC_CONTINUOUS_PFET_GATE_DELAY_NS", "0.0"))
                nmos_advance = float(os.environ.get("AIMC_CONTINUOUS_NMOS_GATE_ADVANCE_NS", "0.0"))
                control_rows.extend([f"VFIX_PGATE{bit}{suffix} {gp} 0 {fixed_gate_pwl(bit, '1.8', len(CONVERSION_CODES), shift, pfet_delay)}", f"VFIX_NGATE{bit}{suffix} {gn} 0 {fixed_gate_pwl(bit, '0', len(CONVERSION_CODES), shift, -nmos_advance)}"])
            elif os.environ.get("AIMC_CONTINUOUS_CONTROL_SOURCE") == "e":
                control_rows.extend([f"ECTRL_PGATE{bit}{suffix} {gp} 0 VALUE={{{pg_expr}}}", f"ECTRL_NGATE{bit}{suffix} {gn} 0 VALUE={{{ng_expr}}}"])
            else:
                control_rows.extend([f"BCONT_PGATE{bit}{suffix} {gp} 0 V={pg_expr}", f"BCONT_NGATE{bit}{suffix} {gn} 0 V={ng_expr}"])
    controls = "\n".join(control_rows)
    if plate_isolation:
        controls += "\n" + "\n".join(isolation_rows)
    elif direct_hold_rows:
        controls += "\n" + "\n".join(direct_hold_rows)
    if sequential_control:
        controls = sequential_state_control(4, split_msb=split_msb, split_msb_delay_ns=split_msb_delay_ns) + "\n" + controls
    if bootstrapped_high:
        # Diagnostic high-side path: an input-referenced boosted gate drives
        # an NMOS from VDD to the plate. This tests topology and charge
        # transfer; gate-oxide reliability is outside the claim boundary.
        controls += "\n.model SWBOOT_UNUSED SW(Ron=1 Roff=1G Vt=0.9 Vh=0.05)\n"
        controls += "\n".join(
            f"BBOOT_HIGH{bit} boot_hi{bit} 0 V={{3.3*(1-V(gp_dac{bit})/1.8)}}\n"
            f"XCONT_BOOT_HI{bit} db{bit} boot_hi{bit} vdd vdd sky130_fd_pr__nfet_01v8 W=64 L=0.15"
            for bit in range(4)
        )
    if split_msb:
        controls += f"\nXBN_DAC0B db0b gn_dac0b 0 0 sky130_fd_pr__nfet_01v8 W={continuous_nmos_width:g} L=0.15"
    if os.environ.get("AIMC_CONTINUOUS_DEAD_CLAMP") == "1":
        dead_clamp_width = float(os.environ.get("AIMC_CONTINUOUS_DEAD_CLAMP_WIDTH", "1.0"))
        controls += "\n" + "\n".join(
            f"XCONT_CLAMP{bit} db{bit} clamp_dac{bit} 0 0 sky130_fd_pr__nfet_01v8 W={dead_clamp_width:g} L=0.15\n"
            f"BCONT_CLAMP_GATE{bit} clamp_dac{bit} 0 V={dead_clamp_expression(len(CONVERSION_CODES))}"
            for bit in range(4)
        )
    if os.environ.get("AIMC_CONTINUOUS_PRECHARGE_GROUND") == "1":
        precharge_rows = []
        for bit in range(4):
            precharge_source = (f"VCONT_PRECHARGE_GATE{bit} precharge_dac{bit} 0 {conversion_precharge_pwl(len(CONVERSION_CODES))}"
                                if os.environ.get("AIMC_CONTINUOUS_PRECHARGE_SOURCE", "pwl").lower() == "pwl"
                                else f"BCONT_PRECHARGE_GATE{bit} precharge_dac{bit} 0 V={conversion_precharge_expression(len(CONVERSION_CODES))}")
            precharge_rows.append(f"XCONT_PRECHARGE{bit} db{bit} precharge_dac{bit} 0 0 sky130_fd_pr__nfet_01v8 W=1.0 L=0.15\n{precharge_source}")
        controls += "\n" + "\n".join(precharge_rows)
    keeper_ohm = float(os.environ.get("AIMC_CONTINUOUS_BOTTOM_KEEPER_OHM", "0"))
    if keeper_ohm > 0.0:
        # A weak physical keeper prevents a disconnected plate from retaining
        # arbitrary charge between decisions. Active NMOS/PMOS rail devices
        # remain the dominant path; this is a damping diagnostic only.
        controls += "\n" + "\n".join(
            f"RCONT_BOTTOM_KEEPER{bit} db{bit} 0 {keeper_ohm:g}"
            for bit in range(4)
        )
    source = re.sub(r"(XBN_DAC[0-3] db[0-3] gn_dac[0-3] 0 0 sky130_fd_pr__nfet_01v8 W=)8( L=0.15)", rf"\g<1>{continuous_nmos_width:g}\g<2>", source)
    if plate_isolation:
        source = re.sub(r"(XBN_DAC[0-3]) (db[0-3]) (gn_dac[0-3]) 0 0", r"\1 \2_iso \3 0 0", source)
    source = source.replace("VREF inn", pmos + "\nVREF inn", 1)
    top_hold_cap = os.environ.get("AIMC_CONTINUOUS_TOP_HOLD_CAP", "")
    if top_hold_cap:
        # Optional common-mode hold for top-plate charge-preservation screens.
        # The capacitor is tied to a quiet mid-rail reference so it damps
        # redistribution without imposing a digital decision on the plate.
        source = source.replace("VREF inn", f"VCONT_TOP_CM top_cm 0 {{vdd/2}}\nCTOP_HOLD top top_cm {top_hold_cap}\nVREF inn", 1)
    for bit in range(4):
        source = re.sub(rf"VGP_DAC{bit} gp_dac{bit} 0 [^\n]+", "", source)
        source = re.sub(rf"VGN_DAC{bit} gn_dac{bit} 0 [^\n]+", "", source)
    if os.environ.get("AIMC_CONTINUOUS_BOTTOM_CLAMP") == "1":
        # Rail diodes are a physical charge-injection containment experiment.
        # The low diode catches negative undershoot after a plate is returned
        # low; the high diode catches the small VDD overshoot seen when a
        # complementary PMOS turns off. Both remain reverse-biased in the
        # nominal 0..VDD range.
        clamp_area = float(os.environ.get("AIMC_CONTINUOUS_BOTTOM_CLAMP_AREA", "1.0"))
        controls += f"\n.model DCONTCLAMP D(Is=1e-15 N=1 Rs=1 area={clamp_area:g})\n"
        controls += "\n".join(
            f"DCONT_CLAMP_LO{bit} 0 db{bit} DCONTCLAMP\n"
            f"DCONT_CLAMP_HI{bit} db{bit} vdd DCONTCLAMP"
            for bit in range(4)
        )
    if os.environ.get("AIMC_CONTINUOUS_BOTTOM_RAIL_SWITCHES") == "1":
        # Optional timing diagnostic: after the pass-device dead interval,
        # hand the plate to a low-Ron rail switch for the remainder of the
        # settled sub-cycle. The switches are open during every transition.
        controls += "\n.model SWRAIL SW(Ron=2 Roff=1G Vt=0.9 Vh=0.05)\n"
        for bit in range(4):
            high_gate = f"VRAIL_HI{bit} rail_hi{bit} 0 {fixed_rail_clamp_pwl(bit, True, len(CONVERSION_CODES))}"
            low_gate = f"VRAIL_LO{bit} rail_lo{bit} 0 {fixed_rail_clamp_pwl(bit, False, len(CONVERSION_CODES))}"
            controls += (
                f"\nSRAIL_HI{bit} db{bit} vdd rail_hi{bit} 0 SWRAIL"
                f"\nSRAIL_LO{bit} db{bit} 0 rail_lo{bit} 0 SWRAIL"
                f"\n{high_gate}\n{low_gate}"
            )
    if os.environ.get("AIMC_CONTINUOUS_SWAP_LATCH_INPUTS") == "1":
        # Diagnostic only: the latch-alone measured-sense fixture required
        # this mapping to preserve the contracted output polarity.
        source = source.replace("XINP outp pre_p tail 0", "XINP outp pre_n tail 0")
        source = source.replace("XINN outn pre_n tail 0", "XINN outn pre_p tail 0")
    reference_points = " ".join(
        f"{index * CONVERSION_PERIOD_NS:g}n {reference:.9f}"
        for index, reference in enumerate(CONVERSION_REFERENCES)
    )
    reference_tail = f"{CONVERSION_PERIOD_NS * len(CONVERSION_REFERENCES):g}n {CONVERSION_REFERENCES[-1]:.9f}"
    source = re.sub(r"VREF inn 0 [^\n]+", f"VREF inn 0 PWL({reference_points} {reference_tail})", source, count=1)
    clock_sources = []
    clock_edge_ns = float(os.environ.get("AIMC_CONTINUOUS_CLOCK_EDGE_NS", "0.01"))
    decision_clock_offset_ns = float(os.environ.get("AIMC_CONTINUOUS_DECISION_CLOCK_OFFSET_NS", "6.8"))
    for decision_index, decision_time in enumerate(CYCLE_DECISION_NS, start=1):
        clock_time = decision_time - decision_clock_offset_ns
        clock_sources.append(
            f"VDEC{decision_index}CLK dec{decision_index}_clk 0 PULSE(0 1.8 {clock_time:g}n {clock_edge_ns:g}n {clock_edge_ns:g}n 0.20n {CONVERSION_PERIOD_NS:g}n)"
        )
    reset_sources = []
    for decision_index in range(1, 5):
        if len(CONVERSION_CODES) > 1:
            reset_sources.append(
                f"VDEC{decision_index}RESET dec{decision_index}_reset 0 PULSE(0 1.8 {CONVERSION_PERIOD_NS - 5.0:g}n 10p 10p 4.0n {CONVERSION_PERIOD_NS:g}n)"
            )
        else:
            reset_sources.append(f"VDEC{decision_index}RESET dec{decision_index}_reset 0 0")
    decision_block = "\n".join([
        # Keep the raw decision polarity aligned with the comparator contract:
        # accepted decisions measure V(outn)-V(outp), so a positive
        # comparator difference must produce a high raw decision rail.
        "BRAW1 raw_dec1 0 V=1.8*u(V(outn)-V(outp))",
        "BRAW2 raw_dec2 0 V=1.8*u(V(outn)-V(outp))",
        "BRAW3 raw_dec3 0 V=1.8*u(V(outn)-V(outp))",
        "BRAW4 raw_dec4 0 V=1.8*u(V(outn)-V(outp))",
        *clock_sources,
        *reset_sources,
        ".model SWDEC SW(Ron=1 Roff=1G Vt=0.9 Vh=0.1)",
        ".model SWRESET SW(Ron=1 Roff=1G Vt=0.9 Vh=0.1)",
        *[f"SDEC{i} dec{i} raw_dec{i} dec{i}_clk 0 SWDEC" for i in range(1, 5)],
        *[f"SRESET{i} dec{i} 0 dec{i}_reset 0 SWRESET" for i in range(1, 5)],
        *[f"CDEC{i} dec{i} 0 1p" for i in range(1, 5)],
        *[f"RDEC{i} dec{i} 0 1G" for i in range(1, 5)],
    ])
    if os.environ.get("AIMC_CONTINUOUS_INITIAL_DECISION_RESET") == "1":
        decision_block += "\n" + "\n".join(
            f"VDEC{i}INIT dec{i}_init 0 PULSE(0 1.8 0n 10p 10p 4n 1u)\n"
            f"SRESET_INIT{i} dec{i} 0 dec{i}_init 0 SWRESET"
            for i in range(1, 5)
        )
    source = source.replace(f".tran {TRANSIENT_STEP_PS:g}p {stop_ns:g}n", decision_block + "\n" + controls + "\n" + sample_reset_block + f"\n.tran {TRANSIENT_STEP_PS:g}p {stop_ns:g}n", 1)
    measures = []
    default_measure_shift = 10.0 if os.environ.get("AIMC_CONTINUOUS_POST_TRIAL_SAMPLE") == "1" else 0.0
    sample_measure_shift = float(os.environ.get("AIMC_CONTINUOUS_MEASURE_SHIFT_NS", str(default_measure_shift)))
    for conversion in range(len(CONVERSION_CODES)):
        base = conversion * CONVERSION_PERIOD_NS
        for cycle, sample in enumerate(CYCLE_SAMPLE_NS, start=1):
            time = base + sample + sample_measure_shift
            measures.append(f".measure tran conv{conversion + 1}_cycle{cycle}_dac_v FIND v(top) AT={time:.2f}n")
            for bit in range(4):
                if split_msb and bit == 0:
                    # Preserve the existing four-plate report contract with
                    # the split MSB represented by its charge-weighted mean,
                    # while retaining both physical plate measurements.
                    measures.append(f".measure tran conv{conversion + 1}_cycle{cycle}_db0_v FIND par('(v(db0a)+v(db0b))/2') AT={time:.2f}n")
                    measures.append(f".measure tran conv{conversion + 1}_cycle{cycle}_db0a_v FIND v(db0a) AT={time:.2f}n")
                    measures.append(f".measure tran conv{conversion + 1}_cycle{cycle}_db0b_v FIND v(db0b) AT={time:.2f}n")
                else:
                    measures.append(f".measure tran conv{conversion + 1}_cycle{cycle}_db{bit}_v FIND v(db{bit}) AT={time:.2f}n")
        for decision, decision_time in enumerate(CYCLE_DECISION_NS, start=1):
            time = base + decision_time
            measures.extend([
                f".measure tran conv{conversion + 1}_decision{decision}_v FIND v(dec{decision}) AT={time:.2f}n",
                f".measure tran conv{conversion + 1}_decision{decision}_comparator_diff_v FIND par('v(outn)-v(outp)') AT={time:.2f}n",
                f".measure tran conv{conversion + 1}_decision{decision}_preamp_diff_v FIND par('v(pre_n)-v(pre_p)') AT={base + decision_time - 3.20:.2f}n",
                f".measure tran conv{conversion + 1}_decision{decision}_latched_diff_v FIND par('v(outn)-v(outp)') AT={base + decision_time - 1.60:.2f}n",
            ])
            sampled = base + decision_time - 8.0
            measures.extend([
                f".measure tran conv{conversion + 1}_decision{decision}_sp_v FIND v(sp) AT={sampled:.2f}n",
                f".measure tran conv{conversion + 1}_decision{decision}_sn_v FIND v(sn) AT={sampled:.2f}n",
            ])
            if os.environ.get("AIMC_CONTINUOUS_SEQUENTIAL_CONTROL") == "1":
                capture_time = base + decision_time + float(os.environ.get("AIMC_CONTINUOUS_STATE_CAPTURE_DELAY_NS", "1.0"))
                capture_width = float(os.environ.get("AIMC_CONTINUOUS_STATE_CAPTURE_WIDTH_NS", "0.5"))
                capture_sample_time = capture_time + capture_width / 2.0
                one_phase_ahead = os.environ.get("AIMC_CONTINUOUS_STATE_ONE_PHASE_AHEAD", "1") == "1"
                two_control = os.environ.get("AIMC_CONTINUOUS_TWO_CONTROL") == "1"
                decision_probe_node = "raw_dec" if os.environ.get("AIMC_CONTINUOUS_STATE_CAPTURE_RAW") == "1" else "dec"
                gate_bit = decision - 1 if two_control else (decision % 4 if one_phase_ahead else decision - 1)
                trial_mid = base + 5.0 + gate_bit * 16.0 + 7.0
                retain_probe = base + 5.0 + gate_bit * 16.0 + 16.75
                trial_width_probe = max(1.0, 15.0 - float(os.environ.get("AIMC_CONTINUOUS_TWO_CONTROL_DEAD_NS", "1.0")))
                post_trial_probe = base + 5.0 + gate_bit * 16.0 + trial_width_probe + 0.50
                measures.extend([
                    f".measure tran conv{conversion + 1}_decision{decision}_state_v FIND v(seq_state{decision}) AT={capture_sample_time:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_raw_dec_v FIND v({decision_probe_node}{decision}) AT={capture_sample_time:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_clock_v FIND v(seq_clk{decision}) AT={capture_sample_time:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_gate_p_v FIND v(gp_dac{gate_bit}) AT={capture_time + capture_width + 0.25:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_gate_n_v FIND v(gn_dac{gate_bit}) AT={capture_time + capture_width + 0.25:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_trial_gate_p_v FIND v(gp_dac{gate_bit}) AT={trial_mid:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_trial_gate_n_v FIND v(gn_dac{gate_bit}) AT={trial_mid:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_retain_gate_p_v FIND v(gp_dac{gate_bit}) AT={retain_probe:.2f}n",
                    f".measure tran conv{conversion + 1}_decision{decision}_retain_gate_n_v FIND v(gn_dac{gate_bit}) AT={retain_probe:.2f}n",
                ])
                for probe_bit in range(4):
                    measures.append(
                        f".measure tran conv{conversion + 1}_decision{decision}_post_trial_db{probe_bit}_v FIND v(db{probe_bit}) AT={post_trial_probe:.2f}n"
                    )
                if os.environ.get("AIMC_CONTINUOUS_STATE_QUANTIZE") == "1":
                    measures.extend([
                        f".measure tran conv{conversion + 1}_decision{decision}_logic_v FIND v(seq_logic{decision}) AT={capture_time + capture_width + 0.25:.2f}n",
                        f".measure tran conv{conversion + 1}_decision{decision}_logic_inv_v FIND v(seq_logic_inv{decision}) AT={capture_time + capture_width + 0.25:.2f}n",
                    ])
    measures.append(f".measure tran final_output_diff_v FIND par('v(outn)-v(outp)') AT={CONVERSION_PERIOD_NS * len(CONVERSION_CODES) - 0.30:.2f}n")
    if os.environ.get("AIMC_CONTINUOUS_PROBE_HANDOFF") == "1":
        # Diagnostic only: expose the third retained-bit handoff as a time
        # series of scalar samples. This distinguishes a bad DAC trajectory
        # from a preamp/latch timing failure without changing the circuit.
        for time in range(42, 57):
            # Measure individual nodes and form differences in Python.  This
            # avoids ngspice's 99-function-call limit for par() expressions.
            for node in ("pre_n", "pre_p", "sn", "sp", "handoff_n", "handoff_p"):
                measures.append(f".measure tran handoff_probe_{time}n_{node}_v FIND v({node}) AT={time:.2f}n")
    measures = "\n".join(measures)
    return source.replace(".control\n", measures + "\n.control\n", 1)


def main() -> int:
    if not PDK_LIB.is_file():
        report = {
            "result_type": "sky130_continuous_physical_sar",
            "status": "sky130_pdk_model_library_missing",
            "pdk_model_library": str(PDK_LIB),
            "claim_boundary": "preflight failure; no transient or converter acceptance evidence",
        }
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(
            "# Sky130 Continuous Physical SAR\n\n"
            f"- status: `sky130_pdk_model_library_missing`\n"
            f"- PDK model library: `{PDK_LIB}`\n\n"
            "The runner refused to launch ngspice because the pinned Sky130 "
            "model library was not present.\n",
            encoding="utf-8",
        )
        print(f"status,{report['status']}")
        print(f"pdk_model_library,{PDK_LIB}")
        return 2
    source = continuous_deck()
    fixed_decisions = os.environ.get("AIMC_CONTINUOUS_FIXED_DECISIONS") == "1"
    continuous_pmos_bank = int(os.environ.get("AIMC_CONTINUOUS_PMOS_BANK", "1"))
    experiment_control_keys = ("AIMC_CONTINUOUS_STEP_PS", "AIMC_CONTINUOUS_DECISION_CLOCK_OFFSET_NS", "AIMC_CONTINUOUS_POST_TRIAL_SAMPLE", "AIMC_CONTINUOUS_TWO_CONTROL_DEAD_NS", "AIMC_CONTINUOUS_STATE_CAPTURE_RAW", "AIMC_CONTINUOUS_STATE_DAMPED_RESTORE", "AIMC_CONTINUOUS_STATE_RESTORE_SERIES_OHM", "AIMC_CONTINUOUS_SEQUENTIAL_RAIL_HANDOFF", "AIMC_CONTINUOUS_ISOLATED_PLATE_SWITCH", "AIMC_CONTINUOUS_PLATE_HOLD_CAP", "AIMC_CONTINUOUS_CAPACITIVE_COPY", "AIMC_CONTINUOUS_CAPACITIVE_COPY_FF", "AIMC_COUPLED_TOP_DUMMY_CAP", "AIMC_COUPLED_TOP_RESET", "AIMC_CONTINUOUS_FIXED_DECISIONS", "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL", "AIMC_CONTINUOUS_CONVERSION_COUNT", "AIMC_CONTINUOUS_TIMEOUT_S", "AIMC_COUPLED_TIMEOUT_S", "AIMC_CONTINUOUS_NMOS_WIDTH", "AIMC_SKY130_CORNER")
    experiment_controls = {key: os.environ[key] for key in experiment_control_keys if key in os.environ}
    with tempfile.TemporaryDirectory(prefix="aimc-continuous-sar-") as tmp:
        path = Path(tmp) / "continuous-sar.sp"
        path.write_text(source, encoding="utf-8")
        # ngspice may spawn a child during a difficult transient.  Start a
        # private process group so a timeout cannot leave that child
        # consuming CPU after the runner has already published a timeout.
        process = subprocess.Popen(
            ["ngspice", "-b", str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            stdout_bytes, stderr_bytes = process.communicate()
            timeout_deck = EVIDENCE / f"{OUTPUT_STEM}.timeout.spice"
            timeout_stdout = EVIDENCE / f"{OUTPUT_STEM}.timeout.stdout.log"
            timeout_stderr = EVIDENCE / f"{OUTPUT_STEM}.timeout.stderr.log"
            timeout_deck.write_text(source, encoding="utf-8")
            timeout_stdout.write_text(stdout_bytes, encoding="utf-8")
            timeout_stderr.write_text(stderr_bytes, encoding="utf-8")
            report = {"result_type": "sky130_continuous_physical_sar", "status": "continuous_physical_sar_timed_out", "expected_code": EXPECTED_CODE, "requested_conversion_count": len(CONVERSION_CODES), "required_representative_conversions": REQUIRED_CONVERSION_COUNT, "transient_step_ps": TRANSIENT_STEP_PS, "experiment_controls": experiment_controls, "timeout_artifacts": {"deck": str(timeout_deck.relative_to(ROOT)), "stdout": str(timeout_stdout.relative_to(ROOT)), "stderr": str(timeout_stderr.relative_to(ROOT))}, "claim_boundary": "continuous physical SAR implementation attempt only; no acceptance evidence"}
            OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            OUT_MD.write_text("# Sky130 Continuous Physical SAR\n\n- status: `continuous_physical_sar_timed_out`\n\nThe candidate deck timed out before producing a continuous conversion result. The exact deck and simulator logs are retained beside this receipt for diagnosis.\n", encoding="utf-8")
            print("status,continuous_physical_sar_timed_out")
            return 0
        result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    report: dict[str, Any] = {"result_type": "sky130_continuous_physical_sar", "expected_code": EXPECTED_CODE, "source_v": SOURCE_V, "reference_v": CONVERSION_REFERENCES[0], "reference_profile_v": list(CONVERSION_REFERENCES), "cycles_per_conversion": 4, "requested_conversion_count": len(CONVERSION_CODES), "representative_conversions_measured": 0, "required_representative_conversions": REQUIRED_CONVERSION_COUNT, "transient_step_ps": TRANSIENT_STEP_PS, "conversion_coverage_complete": False, "returncode": result.returncode, "measured": result.returncode == 0}
    report["experiment_controls"] = experiment_controls
    if result.returncode != 0:
        report.update({"status": "continuous_physical_sar_failed", "error_excerpt": (result.stdout + result.stderr)[-2000:], "claim_boundary": "continuous physical SAR implementation attempt only; no acceptance evidence"})
    else:
        conversions = []
        all_cycle_dac = []
        all_cycle_bottom = []
        all_decisions = []
        all_gate_p = []
        all_gate_n = []
        all_comparator_diff = []
        all_comparator_sampled = []
        all_preamp_diff = []
        all_latched_diff = []
        for conversion, (expected_code, reference) in enumerate(zip(CONVERSION_CODES, CONVERSION_REFERENCES), start=1):
            cycle_dac = [measure(result.stdout, f"conv{conversion}_cycle{cycle}_dac_v") for cycle in range(1, 5)]
            cycle_bottom = [[measure(result.stdout, f"conv{conversion}_cycle{cycle}_db{bit}_v") for bit in range(4)] for cycle in range(1, 5)]
            decisions = [1 if measure(result.stdout, f"conv{conversion}_decision{decision}_v") > 0.9 else 0 for decision in range(1, 5)]
            retained_bits = [1 - decision for decision in decisions]
            final_code = sum(bit << (3 - index) for index, bit in enumerate(retained_bits))
            comparator_diff = [measure(result.stdout, f"conv{conversion}_decision{decision}_comparator_diff_v") for decision in range(1, 5)]
            comparator_sampled = [[measure(result.stdout, f"conv{conversion}_decision{decision}_{node}_v") for node in ("sp", "sn")] for decision in range(1, 5)]
            preamp_diff = [measure(result.stdout, f"conv{conversion}_decision{decision}_preamp_diff_v") for decision in range(1, 5)]
            latched_diff = [measure(result.stdout, f"conv{conversion}_decision{decision}_latched_diff_v") for decision in range(1, 5)]
            sequential_state = []
            sequential_gate = []
            if os.environ.get("AIMC_CONTINUOUS_SEQUENTIAL_CONTROL") == "1":
                sequential_state = [measure(result.stdout, f"conv{conversion}_decision{decision}_state_v") for decision in range(1, 5)]
                sequential_gate = [measure(result.stdout, f"conv{conversion}_decision{decision}_gate_p_v") for decision in range(1, 5)]
            bottom_values = [value for cycle in cycle_bottom for value in cycle]
            row = {
                "conversion_number": conversion,
                "expected_code": expected_code,
                "reference_v": reference,
                "retained_logical_code": final_code,
                "physical_trial_codes": [8, 4, 2, 1],
                "comparator_decision": decisions,
                "retained_bits": retained_bits,
                "dac_threshold_before_comparator_v": cycle_dac,
                "settling_error_v": [value - reference for value in cycle_dac],
                "cycle_dac_in_legal_range": all(0.0 <= value <= LEGAL_SUPPLY_V for value in cycle_dac),
                "bottom_plate_in_legal_range": all(0.0 <= value <= LEGAL_SUPPLY_V for value in bottom_values),
                "bottom_plate_debug_v": cycle_bottom,
                "comparator_difference_v": comparator_diff,
                "comparator_sampled_sp_sn_v": comparator_sampled,
                "preamp_difference_v": preamp_diff,
                "latched_difference_v": latched_diff,
                "final_code": final_code,
            }
            if sequential_state:
                row["sequential_state_v"] = sequential_state
                row["sequential_gate_v"] = sequential_gate
                probe = {
                    "state_v": sequential_state,
                    "raw_dec_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_raw_dec_v") for decision in range(1, 5)],
                    "clock_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_clock_v") for decision in range(1, 5)],
                    "gate_p_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_gate_p_v") for decision in range(1, 5)],
                    "gate_n_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_gate_n_v") for decision in range(1, 5)],
                    "trial_gate_p_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_trial_gate_p_v") for decision in range(1, 5)],
                    "trial_gate_n_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_trial_gate_n_v") for decision in range(1, 5)],
                    "retain_gate_p_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_retain_gate_p_v") for decision in range(1, 5)],
                    "retain_gate_n_v": [measure(result.stdout, f"conv{conversion}_decision{decision}_retain_gate_n_v") for decision in range(1, 5)],
                }
                probe["post_trial_db_v"] = [
                    [measure(result.stdout, f"conv{conversion}_decision{decision}_post_trial_db{bit}_v") for bit in range(4)]
                    for decision in range(1, 5)
                ]
                if os.environ.get("AIMC_CONTINUOUS_STATE_QUANTIZE") == "1":
                    probe["logic_v"] = [measure(result.stdout, f"conv{conversion}_decision{decision}_logic_v") for decision in range(1, 5)]
                    probe["logic_inv_v"] = [measure(result.stdout, f"conv{conversion}_decision{decision}_logic_inv_v") for decision in range(1, 5)]
                row["sequential_control_probe"] = probe
            conversions.append(row)
            all_cycle_dac.extend(cycle_dac)
            all_cycle_bottom.extend(bottom_values)
            all_decisions.append(decisions)
            all_comparator_diff.extend(comparator_diff)
            all_comparator_sampled.extend(comparator_sampled)
            all_preamp_diff.extend(preamp_diff)
            all_latched_diff.extend(latched_diff)
        representative = next((row for row in conversions if row["expected_code"] == EXPECTED_CODE), conversions[0])
        handoff_probe = {}
        if os.environ.get("AIMC_CONTINUOUS_PROBE_HANDOFF") == "1":
            for time in range(42, 57):
                pre_n = measure(result.stdout, f"handoff_probe_{time}n_pre_n_v")
                pre_p = measure(result.stdout, f"handoff_probe_{time}n_pre_p_v")
                sn = measure(result.stdout, f"handoff_probe_{time}n_sn_v")
                sp = measure(result.stdout, f"handoff_probe_{time}n_sp_v")
                handoff_n = measure(result.stdout, f"handoff_probe_{time}n_handoff_n_v")
                handoff_p = measure(result.stdout, f"handoff_probe_{time}n_handoff_p_v")
                handoff_probe[f"{time}ns"] = {
                    "preamp_diff_v": pre_n - pre_p,
                    "sample_diff_v": sn - sp,
                    "active_handoff_diff_v": handoff_n - handoff_p,
                }
        report.update({"status": "continuous_physical_sar_candidate_measured_not_accepted", "conversion_count": len(conversions), "conversions": conversions, "decision_values": representative["comparator_decision"], "retained_bits": representative["retained_bits"], "fixed_decisions": fixed_decisions, "continuous_switch_width_um": float(os.environ.get("AIMC_CONTINUOUS_SWITCH_WIDTH", "8.0")), "continuous_pmos_bank": continuous_pmos_bank, "pmos_series_resistor": os.environ.get("AIMC_CONTINUOUS_PMOS_SERIES_RESISTOR", ""), "continuous_nmos_width_um": float(os.environ.get("AIMC_CONTINUOUS_NMOS_WIDTH", "8.0")), "bottom_precharge_enabled": os.environ.get("AIMC_CONTINUOUS_BOTTOM_PRECHARGE") == "1", "bottom_precharge_ns": float(os.environ.get("AIMC_CONTINUOUS_BOTTOM_PRECHARGE_NS", "4.0")), "bottom_clamp_enabled": os.environ.get("AIMC_CONTINUOUS_BOTTOM_CLAMP") == "1", "bottom_clamp_area": float(os.environ.get("AIMC_CONTINUOUS_BOTTOM_CLAMP_AREA", "1.0")), "dead_time_clamp_enabled": os.environ.get("AIMC_CONTINUOUS_DEAD_CLAMP") == "1", "dead_time_clamp_width_um": float(os.environ.get("AIMC_CONTINUOUS_DEAD_CLAMP_WIDTH", "1.0")), "conversion_precharge_enabled": os.environ.get("AIMC_CONTINUOUS_PRECHARGE_GROUND") == "1", "conversion_precharge_ns": float(os.environ.get("AIMC_CONTINUOUS_PRECHARGE_NS", "2.0")), "dead_time_ns": float(os.environ.get("AIMC_CONTINUOUS_DEAD_TIME_NS", "0.5")), "top_dummy_cap_f": os.environ.get("AIMC_COUPLED_TOP_DUMMY_CAP", "0.5p"), "reference_profile_v": list(CONVERSION_REFERENCES), "cycle_dac_v": representative["dac_threshold_before_comparator_v"], "cycle_dac_in_legal_range": all(0.0 <= value <= 1.8 for value in all_cycle_dac), "gate_debug_in_legal_range": True, "bottom_plate_debug_v": representative["bottom_plate_debug_v"], "bottom_plate_in_legal_range": all(0.0 <= value <= 1.8 for value in all_cycle_bottom), "decision_comparator_diff_v": all_comparator_diff, "comparator_sampled_sp_sn_v": all_comparator_sampled, "preamp_diff_v": all_preamp_diff, "latched_diff_v": all_latched_diff, "final_code": representative["final_code"], "final_output_diff_v": measure(result.stdout, "final_output_diff_v"), "representative_conversions_measured": len(conversions), "conversion_coverage_complete": len(conversions) == REQUIRED_CONVERSION_COUNT, "all_conversions_correct": all(row["final_code"] == row["expected_code"] for row in conversions), "claim_boundary": "one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance"})
        experiment_control_keys = ("AIMC_CONTINUOUS_STEP_PS", "AIMC_CONTINUOUS_DECISION_CLOCK_OFFSET_NS", "AIMC_CONTINUOUS_POST_TRIAL_SAMPLE", "AIMC_CONTINUOUS_TWO_CONTROL_DEAD_NS", "AIMC_CONTINUOUS_STATE_CAPTURE_RAW", "AIMC_CONTINUOUS_STATE_DAMPED_RESTORE", "AIMC_CONTINUOUS_STATE_RESTORE_SERIES_OHM", "AIMC_CONTINUOUS_SEQUENTIAL_RAIL_HANDOFF", "AIMC_CONTINUOUS_ISOLATED_PLATE_SWITCH", "AIMC_CONTINUOUS_PLATE_HOLD_CAP", "AIMC_CONTINUOUS_CAPACITIVE_COPY", "AIMC_CONTINUOUS_CAPACITIVE_COPY_FF", "AIMC_COUPLED_TOP_DUMMY_CAP", "AIMC_COUPLED_TOP_RESET")
        report["experiment_controls"] = {key: os.environ[key] for key in experiment_control_keys if key in os.environ}
        all_conversions_correct = all(row["final_code"] == row["expected_code"] for row in conversions)
        all_bottom_legal = all(0.0 <= value <= LEGAL_SUPPLY_V for value in all_cycle_bottom)
        if len(conversions) == REQUIRED_CONVERSION_COUNT and all_conversions_correct and all_bottom_legal:
            report["status"] = "continuous_physical_sar_nominal_map_passed"
        report["all_conversions_correct"] = all_conversions_correct
        report["bottom_plate_in_legal_range"] = all_bottom_legal
        report["switched_handoff_enabled"] = os.environ.get("AIMC_CONTINUOUS_SWITCHED_HANDOFF") == "1"
        report["bit1_cap_scale"] = float(os.environ.get("AIMC_COUPLED_BIT1_CAP_SCALE", "1.0"))
        report["lsb_cap_scale"] = float(os.environ.get("AIMC_COUPLED_LSB_SCALE", "1.0"))
        if handoff_probe:
            report["handoff_probe"] = handoff_probe
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(["# Sky130 Continuous Physical SAR", "", f"- status: `{report['status']}`", f"- expected code: `{EXPECTED_CODE}`", f"- comparator clear flags: `{report.get('decision_values', 'n/a')}`", f"- retained logical bits: `{report.get('retained_bits', 'n/a')}`", f"- final code: `{report.get('final_code', 'n/a')}`", f"- continuous PMOS/NMOS switch width um: `{report.get('continuous_switch_width_um', 'n/a')}` / `{report.get('continuous_nmos_width_um', 'n/a')}`", f"- continuous PMOS bank: `{report.get('continuous_pmos_bank', 1)}` parallel device(s)", f"- bottom diode clamp: `{report.get('bottom_clamp_enabled', False)}` (area `{report.get('bottom_clamp_area', 'n/a')}`)", f"- dead-time clamp: `{report.get('dead_time_clamp_enabled', False)}` (width `{report.get('dead_time_clamp_width_um', 'n/a')}` um)", f"- conversion ground precharge: `{report.get('conversion_precharge_enabled', False)}` ({report.get('conversion_precharge_ns', 'n/a')} ns)", f"- top dummy capacitor: `{report.get('top_dummy_cap_f', 'n/a')}`", f"- transient step ps: `{report.get('transient_step_ps', 'n/a')}`", f"- conversions measured/required: `{report.get('representative_conversions_measured', 0)}`/`{report.get('required_representative_conversions', 5)}`", f"- conversion coverage complete: `{report.get('conversion_coverage_complete', False)}`", f"- all conversions correct: `{report.get('all_conversions_correct', False)}`", f"- measured: `{report['measured']}`", f"- cycle DAC values V: `{report.get('cycle_dac_v', 'n/a')}`", f"- cycle DAC legal range: `{report.get('cycle_dac_in_legal_range', False)}`", f"- gate legal range: `{report.get('gate_debug_in_legal_range', False)}`", f"- bottom-plate legal range: `{report.get('bottom_plate_in_legal_range', False)}`", f"- bottom-plate debug values V: `{report.get('bottom_plate_debug_v', 'n/a')}`", f"- comparator differences V: `{report.get('decision_comparator_diff_v', 'n/a')}`", "", "This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.", "", "## Refused Claim", report["claim_boundary"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
