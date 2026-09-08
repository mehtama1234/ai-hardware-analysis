# Vectorized RL simulation

This lab isolates one hardware-relevant part of GPU reinforcement learning: a
large batch of independent grid-world state transitions. The PyTorch path keeps
all environment state and reward computation in tensors; a small scalar oracle
checks the transition semantics before timing the vectorized rollout. It also
executes a deterministic goal-directed policy with terminal detection and reset
accounting, and compares those episode semantics against the scalar oracle.

It is deliberately not an Isaac Gym replacement and does not claim physics,
policy quality, or simulator throughput beyond the recorded configuration.
`run_vectorized_simulation.py --device cuda` records an unavailable result when
CUDA is absent rather than silently measuring CPU work as GPU evidence.

```bash
python rl-gpu-simulation/run_vectorized_simulation.py --device cpu
python rl-gpu-simulation/run_vectorized_simulation.py --device cuda
python -m unittest discover -s rl-gpu-simulation/tests -v
python rl-gpu-simulation/run_policy_quality.py --device cuda
```
