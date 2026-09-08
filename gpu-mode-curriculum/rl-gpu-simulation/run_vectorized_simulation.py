#!/usr/bin/env python3
"""Deterministic vectorized grid-world rollout with an explicit scalar oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "rl-gpu-simulation/reports/vectorized-simulation.json"
GRID = 31
ACTION_COUNT = 4


def scalar_rollout(starts, goals, actions, grid=GRID):
    positions = [list(map(int, point)) for point in starts]
    rewards = []
    for action_row in actions:
        row_rewards = []
        for index, action in enumerate(action_row):
            y, x = positions[index]
            action = int(action)
            if action == 0:
                y -= 1
            elif action == 1:
                y += 1
            elif action == 2:
                x -= 1
            elif action == 3:
                x += 1
            y = min(max(y, 0), grid - 1)
            x = min(max(x, 0), grid - 1)
            positions[index] = [y, x]
            row_rewards.append(10.0 if positions[index] == list(map(int, goals[index])) else -1.0)
        rewards.append(row_rewards)
    return positions, rewards


def vectorized_rollout(starts, goals, actions, grid=GRID):
    positions = starts.clone()
    y_delta = torch.tensor((-1, 1, 0, 0), device=actions.device, dtype=torch.int64)
    x_delta = torch.tensor((0, 0, -1, 1), device=actions.device, dtype=torch.int64)
    rewards = []
    for action_row in actions.unbind(0):
        positions = positions + torch.stack((y_delta[action_row], x_delta[action_row]), dim=1)
        positions = positions.clamp(0, grid - 1)
        rewards.append(torch.where((positions == goals).all(dim=1), 10.0, -1.0))
    return positions, torch.stack(rewards, dim=0)


def scalar_policy_episode(starts, goals, steps, grid=GRID):
    """Reference goal-directed policy with terminal reset semantics."""
    initial = [list(map(int, point)) for point in starts]
    positions = [point[:] for point in initial]
    goal_points = [list(map(int, point)) for point in goals]
    rewards, dones, reset_count = [], [], 0
    for _ in range(steps):
        row_rewards, row_dones = [], []
        for index, (position, goal) in enumerate(zip(positions, goal_points)):
            y, x = position
            gy, gx = goal
            action = 1 if y < gy else 0 if y > gy else 3 if x < gx else 2 if x > gx else 0
            if action == 0:
                y -= 1
            elif action == 1:
                y += 1
            elif action == 2:
                x -= 1
            else:
                x += 1
            position[:] = [min(max(y, 0), grid - 1), min(max(x, 0), grid - 1)]
            done = position == goal
            row_dones.append(done)
            row_rewards.append(10.0 if done else -1.0)
            if done:
                positions[index] = initial[index][:]
                reset_count += 1
        rewards.append(row_rewards)
        dones.append(row_dones)
    return positions, torch.tensor(rewards), torch.tensor(dones), reset_count


def vectorized_policy_episode(starts, goals, steps, grid=GRID):
    positions = starts.clone()
    initial = starts.clone()
    y_delta = torch.tensor((-1, 1, 0, 0), device=starts.device, dtype=torch.int64)
    x_delta = torch.tensor((0, 0, -1, 1), device=starts.device, dtype=torch.int64)
    reset_count = 0
    rewards, dones = [], []
    for _ in range(steps):
        y, x = positions[:, 0], positions[:, 1]
        gy, gx = goals[:, 0], goals[:, 1]
        actions = torch.where(y < gy, 1, torch.where(y > gy, 0, torch.where(x < gx, 3, torch.where(x > gx, 2, 0))))
        positions = positions + torch.stack((y_delta[actions], x_delta[actions]), dim=1)
        positions = positions.clamp(0, grid - 1)
        done = (positions == goals).all(dim=1)
        rewards.append(torch.where(done, 10.0, -1.0))
        dones.append(done)
        reset_count += int(done.sum().item())
        positions = torch.where(done[:, None], initial, positions)
    return positions, torch.stack(rewards), torch.stack(dones), reset_count


def source_hashes():
    return {str(path.relative_to(ROOT.parent.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [Path(__file__)]}


def timed_rollout(starts, goals, actions, device, repeats):
    if device.type == "cuda":
        torch.cuda.synchronize(device)
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        samples = []
        for _ in range(repeats):
            start.record()
            vectorized_rollout(starts, goals, actions)
            end.record()
            end.synchronize()
            samples.append(start.elapsed_time(end) / 1000.0)
        return samples, "cuda-event", "explicit CUDA-event synchronization"
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        vectorized_rollout(starts, goals, actions)
        samples.append(time.perf_counter() - started)
    return samples, "host-wall-clock", "CPU synchronous call"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--envs", type=int, default=4096)
    parser.add_argument("--steps", type=int, default=128)
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args(argv)
    requested = torch.device(args.device)
    report = {
        "experiment": "vectorized_gridworld_rollout",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requested_device": args.device,
        "env_count": args.envs,
        "steps": args.steps,
        "repeats": args.repeats,
        "grid_size": GRID,
        "action_count": ACTION_COUNT,
        "measured": False,
        "gpu_execution_accepted": False,
        "source_sha256": source_hashes(),
        "python": sys.version,
        "platform": platform.platform(),
    }
    if args.envs < 1 or args.steps < 1 or args.repeats < 1:
        raise SystemExit("envs, steps, and repeats must be positive")
    if requested.type == "cuda" and not torch.cuda.is_available():
        report.update({"status": "unavailable", "reason": "cuda-runtime", "scope": "requested CUDA; no device available"})
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        print(json.dumps(report, indent=2))
        return 2
    device = requested
    generator = torch.Generator(device="cpu").manual_seed(20260907)
    starts_cpu = torch.randint(0, GRID, (args.envs, 2), generator=generator, dtype=torch.int64)
    goals_cpu = torch.randint(0, GRID, (args.envs, 2), generator=generator, dtype=torch.int64)
    actions_cpu = torch.randint(0, ACTION_COUNT, (args.steps, args.envs), generator=generator, dtype=torch.int64)
    oracle_n = min(args.envs, 17)
    oracle_positions, oracle_rewards = scalar_rollout(starts_cpu[:oracle_n].tolist(), goals_cpu[:oracle_n].tolist(), actions_cpu[:, :oracle_n].tolist())
    starts, goals, actions = starts_cpu.to(device), goals_cpu.to(device), actions_cpu.to(device)
    result_positions, result_rewards = vectorized_rollout(starts[:oracle_n], goals[:oracle_n], actions[:, :oracle_n])
    position_match = result_positions.cpu().tolist() == oracle_positions
    reward_match = result_rewards.cpu().tolist() == oracle_rewards
    policy_oracle = scalar_policy_episode(starts_cpu[:oracle_n].tolist(), goals_cpu[:oracle_n].tolist(), args.steps)
    policy_result = vectorized_policy_episode(starts[:oracle_n], goals[:oracle_n], args.steps)
    policy_position_match = policy_result[0].cpu().tolist() == policy_oracle[0]
    policy_reward_match = policy_result[1].cpu().tolist() == policy_oracle[1].tolist()
    policy_done_match = policy_result[2].cpu().tolist() == policy_oracle[2].tolist()
    policy_reset_match = policy_result[3] == policy_oracle[3]
    samples, timing_scope, synchronization = timed_rollout(starts, goals, actions, device, args.repeats)
    report.update({
        "status": "passed" if position_match and reward_match else "failed",
        "device": str(device),
        "device_name": torch.cuda.get_device_name(device) if device.type == "cuda" else "cpu",
        "torch_version": torch.__version__,
        "position_match": position_match,
        "reward_match": reward_match,
        "policy_position_match": policy_position_match,
        "policy_reward_match": policy_reward_match,
        "policy_termination_match": policy_done_match,
        "policy_reset_match": policy_reset_match,
        "policy_episode_resets": policy_result[3],
        "oracle_envs": oracle_n,
        "samples_seconds": samples,
        "median_seconds": sorted(samples)[len(samples) // 2],
        "steps_per_second": args.steps * args.envs / (sorted(samples)[len(samples) // 2] or 1e-12),
        "timing_scope": timing_scope,
        "synchronization": synchronization,
        "measured": True,
        "gpu_execution_accepted": device.type == "cuda" and position_match and reward_match and policy_position_match and policy_reward_match and policy_done_match and policy_reset_match,
        "scope": "vectorized deterministic grid-world transitions and goal-directed policy; no physics or policy-quality claim",
    })
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
