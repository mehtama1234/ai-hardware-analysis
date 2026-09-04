#!/usr/bin/env python3
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class TileProfile:
    tile_id: int
    base_accept_probability: float
    residual_pressure: float
    calibration_age: int


@dataclass
class TileTelemetry:
    attempts: int = 0
    accepted: int = 0
    fallback: int = 0
    residual_fallback: int = 0
    stale_fallback: int = 0


def classify(profile: TileProfile, telemetry: TileTelemetry) -> tuple[str, str]:
    if telemetry.attempts == 0:
        return "observe", "no_samples"

    accept_rate = telemetry.accepted / telemetry.attempts
    fallback_rate = telemetry.fallback / telemetry.attempts
    residual_rate = telemetry.residual_fallback / telemetry.attempts
    stale_rate = telemetry.stale_fallback / telemetry.attempts

    if profile.calibration_age >= 1024 or stale_rate > 0.10:
        return "recalibrate", "calibration_evidence_is_stale"
    if residual_rate > 0.25:
        return "disable", "residual_fallbacks_are_repeated"
    if fallback_rate > 0.30:
        return "recalibrate", "fallback_rate_is_high"
    if accept_rate >= 0.85:
        return "serve", "accepted_readouts_dominate"
    return "shadow", "not_enough_trust_for_primary_path"


def simulate_tile(profile: TileProfile, requests: int, seed: int) -> TileTelemetry:
    rng = random.Random(seed + profile.tile_id)
    telemetry = TileTelemetry()
    for request in range(requests):
        telemetry.attempts += 1
        stale_risk = 0.0
        if profile.calibration_age + request * 8 >= 1024:
            stale_risk = 0.18
        residual_risk = profile.residual_pressure + rng.uniform(-0.04, 0.04)
        accept_probability = max(0.0, min(1.0, profile.base_accept_probability - stale_risk - residual_risk))

        if rng.random() < accept_probability:
            telemetry.accepted += 1
        else:
            telemetry.fallback += 1
            if stale_risk > 0.0 and rng.random() < 0.55:
                telemetry.stale_fallback += 1
            else:
                telemetry.residual_fallback += 1
    return telemetry


def main() -> None:
    profiles = [
        TileProfile(11, 0.96, 0.03, 128),
        TileProfile(12, 0.90, 0.12, 256),
        TileProfile(13, 0.82, 0.28, 384),
        TileProfile(14, 0.93, 0.05, 1100),
        TileProfile(15, 0.76, 0.10, 512),
    ]
    requests = 64

    print("tile_telemetry_policy")
    print(f"requests_per_tile,{requests}")
    print()
    print("tile_id,attempts,accepted,fallback,accept_rate,residual_fallback,stale_fallback,action,reason")
    for profile in profiles:
        telemetry = simulate_tile(profile, requests, 15000)
        action, reason = classify(profile, telemetry)
        accept_rate = telemetry.accepted / telemetry.attempts
        print(
            f"{profile.tile_id},{telemetry.attempts},{telemetry.accepted},{telemetry.fallback},"
            f"{accept_rate:.3f},{telemetry.residual_fallback},{telemetry.stale_fallback},{action},{reason}"
        )

    print()
    print("interpretation")
    print("The RTL counters make tile behavior visible.")
    print("Runtime policy should compare accepted readouts with fallback reasons by tile.")
    print("A tile can be useful, need recalibration, move to shadow service, or be disabled.")


if __name__ == "__main__":
    main()
