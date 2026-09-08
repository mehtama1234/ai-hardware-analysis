#!/usr/bin/env python3
"""Train and evaluate a tiny goal-directed policy on the vectorized environment."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "rl-gpu-simulation/reports/policy-quality.json"
MODULE_PATH = ROOT / "rl-gpu-simulation/run_vectorized_simulation.py"
spec = importlib.util.spec_from_file_location("vectorized_simulation", MODULE_PATH)
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)


class GoalPolicy(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(4, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 4))

    def forward(self, positions, goals):
        scale = float(sim.GRID - 1)
        return self.net(torch.cat((positions, goals), dim=1).float() / scale)


def shortest_action(positions, goals):
    y, x = positions[:, 0], positions[:, 1]
    gy, gx = goals[:, 0], goals[:, 1]
    return torch.where(y < gy, 1, torch.where(y > gy, 0, torch.where(x < gx, 3, torch.where(x > gx, 2, 0))))


def evaluate(policy, starts, goals, steps):
    positions = starts.clone()
    reached = torch.zeros(starts.shape[0], dtype=torch.bool, device=starts.device)
    resets = 0
    with torch.no_grad():
        for _ in range(steps):
            actions = policy(positions, goals).argmax(dim=1)
            y_delta = torch.tensor((-1, 1, 0, 0), device=positions.device, dtype=torch.int64)
            x_delta = torch.tensor((0, 0, -1, 1), device=positions.device, dtype=torch.int64)
            positions = (positions + torch.stack((y_delta[actions], x_delta[actions]), dim=1)).clamp(0, sim.GRID - 1)
            done = (positions == goals).all(dim=1)
            reached |= done
            resets += int(done.sum().item())
            positions = torch.where(done[:, None], starts, positions)
    return reached, resets


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--train-samples", type=int, default=32768)
    parser.add_argument("--train-steps", type=int, default=300)
    parser.add_argument("--eval-envs", type=int, default=8192)
    parser.add_argument("--eval-steps", type=int, default=128)
    args = parser.parse_args(argv)
    requested = torch.device(args.device)
    report = {
        "experiment": "trained_goal_policy_quality",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requested_device": args.device,
        "train_samples": args.train_samples,
        "train_steps": args.train_steps,
        "eval_envs": args.eval_envs,
        "eval_steps": args.eval_steps,
        "grid_size": sim.GRID,
        "measured": False,
        "gpu_execution_accepted": False,
        "source_sha256": {
            str(path.relative_to(ROOT.parent.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), MODULE_PATH)
        },
        "python": sys.version,
        "platform": platform.platform(),
    }
    if min(args.train_samples, args.train_steps, args.eval_envs, args.eval_steps) < 1:
        raise SystemExit("all sizes must be positive")
    if requested.type == "cuda" and not torch.cuda.is_available():
        report.update({"status": "unavailable", "reason": "cuda-runtime", "scope": "requested CUDA; no device available"})
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 2
    device = requested
    generator = torch.Generator(device="cpu").manual_seed(20260908)
    train_positions = torch.randint(0, sim.GRID, (args.train_samples, 2), generator=generator, dtype=torch.int64)
    train_goals = torch.randint(0, sim.GRID, (args.train_samples, 2), generator=generator, dtype=torch.int64)
    starts_cpu = torch.randint(0, sim.GRID, (args.eval_envs, 2), generator=generator, dtype=torch.int64)
    goals_cpu = torch.randint(0, sim.GRID, (args.eval_envs, 2), generator=generator, dtype=torch.int64)
    train_positions, train_goals = train_positions.to(device), train_goals.to(device)
    starts, goals = starts_cpu.to(device), goals_cpu.to(device)
    policy = GoalPolicy().to(device)
    optimizer = torch.optim.Adam(policy.parameters(), lr=3e-3)
    labels = shortest_action(train_positions, train_goals)
    policy.train()
    train_start = time.perf_counter()
    for _ in range(args.train_steps):
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(policy(train_positions, train_goals), labels)
        loss.backward()
        optimizer.step()
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    train_seconds = time.perf_counter() - train_start
    policy.eval()
    with torch.no_grad():
        action_accuracy = (policy(train_positions, train_goals).argmax(dim=1) == labels).float().mean().item()
    reached, resets = evaluate(policy, starts, goals, args.eval_steps)
    success_rate = reached.float().mean().item()
    oracle_reached, oracle_resets = evaluate(lambda p, g: nn.functional.one_hot(shortest_action(p, g), num_classes=4).float(), starts, goals, args.eval_steps)
    oracle_success_rate = oracle_reached.float().mean().item()
    report.update({
        "status": "passed" if success_rate >= 0.95 and oracle_success_rate == 1.0 else "failed",
        "device": str(device),
        "device_name": torch.cuda.get_device_name(device) if device.type == "cuda" else "cpu",
        "torch_version": torch.__version__,
        "action_accuracy": action_accuracy,
        "success_rate": success_rate,
        "oracle_success_rate": oracle_success_rate,
        "policy_episode_resets": resets,
        "oracle_episode_resets": oracle_resets,
        "training_seconds": train_seconds,
        "measured": True,
        "gpu_execution_accepted": device.type == "cuda" and success_rate >= 0.95 and oracle_success_rate == 1.0,
        "scope": "supervised goal policy quality on deterministic grid-world; not RL optimization or physics quality",
    })
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
