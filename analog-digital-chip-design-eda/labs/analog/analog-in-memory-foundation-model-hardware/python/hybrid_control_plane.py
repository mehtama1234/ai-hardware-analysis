#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    name: str
    phase: str
    tokens: int
    batch: int
    active_context: int
    latency_budget: float
    error_budget: float
    resident_weights: bool


@dataclass(frozen=True)
class TilePool:
    healthy_tiles: int
    weak_tiles: int
    calibration_age: int
    adc_bits: int = 6
    dac_bits: int = 6


@dataclass(frozen=True)
class Machine:
    hidden: int = 4096
    layers: int = 32
    bytes_per_value: int = 2
    analog_mac: float = 1.0
    digital_mac: float = 12.0
    boundary_per_token: float = 1_250_000.0
    memory_byte: float = 0.08
    correction_per_token: float = 180_000.0
    calibration_unit: float = 14_000_000.0


def projection_macs(request: Request, machine: Machine) -> int:
    h = machine.hidden
    per_layer = (h * 3 * h) + (h * h) + (h * 4 * h) + (4 * h * h)
    return request.tokens * request.batch * machine.layers * per_layer


def cache_energy(request: Request, machine: Machine) -> float:
    if request.phase == "prefill":
        cache_reads = request.tokens * request.batch * machine.layers * machine.hidden
    else:
        cache_reads = request.active_context * request.tokens * request.batch * machine.layers * machine.hidden
    return cache_reads * machine.bytes_per_value * machine.memory_byte


def converter_cost(request: Request, pool: TilePool, machine: Machine) -> float:
    bit_factor = 2 ** max(0, pool.adc_bits - 4) + 0.35 * (2 ** max(0, pool.dac_bits - 4))
    return request.tokens * request.batch * machine.boundary_per_token * bit_factor


def calibration_cost(pool: TilePool, machine: Machine) -> float:
    if pool.calibration_age < 512:
        return 0.0
    age_factor = min(4.0, pool.calibration_age / 512.0)
    weak_factor = 1.0 + 0.25 * pool.weak_tiles
    return machine.calibration_unit * age_factor * weak_factor


def estimate_state_error(request: Request, pool: TilePool) -> float:
    converter = 0.18 / max(1, 2 ** (pool.adc_bits - 3))
    calibration = 0.012 * min(6.0, pool.calibration_age / 256.0)
    weak_tile = 0.006 * pool.weak_tiles
    context = 0.000004 * request.active_context if request.phase == "decode" else 0.006
    batch_relief = -0.015 if request.batch >= 4 else 0.0
    return max(0.0, converter + calibration + weak_tile + context + batch_relief)


def choose_path(request: Request, pool: TilePool, machine: Machine) -> dict[str, float | str]:
    macs = projection_macs(request, machine)
    cache = cache_energy(request, machine)
    analog_projection = macs * machine.analog_mac
    digital_projection = macs * machine.digital_mac
    boundary = converter_cost(request, pool, machine)
    correction = request.tokens * request.batch * machine.correction_per_token
    calibration = calibration_cost(pool, machine)
    analog_total = analog_projection + boundary + correction + calibration + cache
    digital_total = digital_projection + cache
    state_error = estimate_state_error(request, pool)
    latency_pressure = analog_total / max(1.0, request.latency_budget)
    cost_ratio = analog_total / max(1.0, digital_total)

    decision = "analog"
    reason = "resident weights, healthy tiles, and enough dense work"
    if not request.resident_weights:
        decision = "digital"
        reason = "weights are not resident in analog tiles"
    elif pool.healthy_tiles < 64:
        decision = "digital"
        reason = "not enough healthy tiles for the projection set"
    elif state_error > request.error_budget:
        decision = "digital"
        reason = "estimated state error exceeds the request budget"
    elif request.phase == "decode" and request.batch < 4 and request.active_context >= 8192:
        decision = "digital"
        reason = "cache movement dominates single-request long-context decode"
    elif cost_ratio > 0.65:
        decision = "digital"
        reason = "analog path does not beat digital by enough margin"
    elif request.phase == "decode" and request.batch >= 4:
        decision = "analog_batched_decode"
        reason = "batch reuse amortizes the converter boundary"
    elif latency_pressure > 1.0:
        decision = "digital"
        reason = "analog schedule misses the phase latency budget"

    return {
        "request": request.name,
        "phase": request.phase,
        "tokens": request.tokens,
        "batch": request.batch,
        "context": request.active_context,
        "healthy_tiles": pool.healthy_tiles,
        "weak_tiles": pool.weak_tiles,
        "calibration_age": pool.calibration_age,
        "cache_share": cache / max(1.0, analog_total),
        "boundary_share": boundary / max(1.0, analog_total),
        "cost_ratio": cost_ratio,
        "state_error": state_error,
        "decision": decision,
        "reason": reason,
    }


def main() -> None:
    machine = Machine()
    scenarios = [
        (Request("prompt_batch", "prefill", 2048, 2, 2048, 5.0e13, 0.11, True), TilePool(healthy_tiles=128, weak_tiles=2, calibration_age=128)),
        (Request("interactive_decode", "decode", 1, 1, 2048, 1.0e12, 0.10, True), TilePool(healthy_tiles=128, weak_tiles=2, calibration_age=128)),
        (Request("long_context_decode", "decode", 1, 1, 16384, 1.0e12, 0.10, True), TilePool(healthy_tiles=128, weak_tiles=2, calibration_age=128)),
        (Request("batched_decode", "decode", 1, 8, 2048, 7.5e12, 0.10, True), TilePool(healthy_tiles=128, weak_tiles=1, calibration_age=128)),
        (Request("stale_tiles_prefill", "prefill", 2048, 2, 2048, 5.0e13, 0.11, True), TilePool(healthy_tiles=96, weak_tiles=8, calibration_age=2048)),
        (Request("cold_weight_request", "prefill", 1024, 1, 1024, 3.5e13, 0.11, False), TilePool(healthy_tiles=128, weak_tiles=2, calibration_age=128)),
    ]

    print("hybrid_control_plane")
    print("relative units,not process calibrated")
    print()
    print("request,phase,tokens,batch,context,healthy_tiles,weak_tiles,calibration_age,cache_share,boundary_share,cost_ratio,state_error,decision,reason")
    for request, pool in scenarios:
        row = choose_path(request, pool, machine)
        print(
            f"{row['request']},{row['phase']},{row['tokens']},{row['batch']},{row['context']},"
            f"{row['healthy_tiles']},{row['weak_tiles']},{row['calibration_age']},"
            f"{row['cache_share']:.4f},{row['boundary_share']:.4f},{row['cost_ratio']:.4f},"
            f"{row['state_error']:.4f},{row['decision']},{row['reason']}"
        )


if __name__ == "__main__":
    main()
