# MoE Routing And All-To-All

## First Question

A mixture-of-experts layer sends each token to a small number of experts. If many tokens choose the same expert, some devices overload while others wait. This lane asks how routing balance, capacity drops, and all-to-all payload affect the step.

## What The Code Does

- `moe-routing-all-to-all/moe_routing_all_to_all/simulator.py computes routing outcomes.`
- `distributed-collectives/distributed_collectives/analyzer.py supplies the communication context.`
- `hardware-capacity-planning/hardware_capacity_planning/planner.py connects the result to hardware choice.`

## What The Measurement Proves

The measurement proves each scenario records load balance, dropped tokens, payload size, communication time, and the bottleneck label.

## What It Does Not Prove

It does not prove a real MoE model was trained. It proves the routing failure modes are made measurable.

## Read Next

- `site/moe-routing-all-to-all.html`
- `site/hardware-capacity.html`
