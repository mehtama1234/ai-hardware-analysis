# ProtoRAIL: A Risk-cognizant Imitation Agent for Adaptive vCPU Oversubscription In the Cloud

**Venue:** MLSYS 2025 · **Theme:** vCPU / System Scheduling

## What It Does

Cloud vCPU oversubscription policies must jointly minimize overloading risk (hot nodes) and maximize utilization (stranded resource recovery), but demand patterns vary dynamically across VM types and time, making static heuristic policies either too conservative (waste capacity) or too aggressive (cause overload).

Online RL cannot safely train on live cloud infrastructure and struggles to converge with two competing objectives (COGS benefit vs overloading risk). Supervised learning is unaware of environment interactions. Imitation learning from offline telemetry is feasible, but noisy data leads to sub-optimal policies. Prototypical IL exploits approximate symmetries in usage patterns across VM/service types, and active feedback from domain experts can de-risk policies without requiring online interaction.

ProtoRAIL has three components: (1) Prototypical Imitation Learning - a trajectory encoder (LSTM or Transformer) maps CPU usage trajectories to embeddings; K prototype embeddings represent equivalence classes of usage patterns; policy is a linear layer over similarities to prototypes. Loss has four terms: Lrep (representativeness: L2 distance to nearest prototype), Ldiv (diversity: repel close prototypes), Lint (interpretability: anchor each prototype to a real trajectory), and LIMloss (imitation learning via behavior cloning or adversarial IL). (2) Active Knowledge-in-the-Loop (KITL) - identifies uncertain prototypes (high cluster entropy) and risky predictions (predicted oversubscription rate below actual usage) via a query framework; solicits feedback from domain experts (or LLMs) as up/down votes on prototypes and actions, plus merge/split operations on prototype clusters; feedback is applied via advice potential gates (exponential scaling of loss components) to steer training without explicit prior design. (3) Query scheduling - minimizes feedback budget by only querying at uncertain or risky stages.

## The Key Experiment

- **hot node rate:** 0% hot node rate (vs 0.89-1.47% for baselines including Coop-MARL, GAIL, BC, DDPG)
- **remain core benefit:** 8161 remain cores vs 7938 for best baseline (Dagger with 20 human steps)
- **deployment utilization:** 9.4% vCPU utilization improvement on Microsoft internal cloud
- **deployment hot nodes:** 0% hot node rate on 300 deployed clusters
- **kitl query budget:** <=10 total feedback queries to reach stable performance
- **benefit risk ratio:** BRR 31.34 vs 18.95 for heuristics and 7.79 for manual

**Compared against:** Grid-search heuristic; Moving average heuristic; Behavior Cloning (BC); GAIL; Dagger (20 steps); DDPG; LSTM (ScroogeVM); Cooperative Multi-Agent RL

**Hardware:** cloud-cpu; datacenter · **Workloads:** cloud-vms; cpu-oversubscription; resource-scheduling

## Why This Approach

Prototypical imitation learning for sequential decision-making with explicit interpretable pattern classes; active knowledge-in-the-loop with prototype-level feedback (merge/split/vote) to de-risk policies with minimal expert queries.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Prototypical imitation learning framework for oversubscription ratio prediction using usage trajectory equivalence classes.

## What It Leaves Open

- Prototype count K must be tuned; wrong K causes redundant or missing coverage of usage patterns
- Active KITL requires human experts with domain knowledge; LLMs are inferior (87% vs 98% clustering accuracy)
- Bootstrap period needed before alpha tuning and KITL convergence
- Airline ticket overbooking shows performance degradation due to COVID-19 distribution shift

**Tags:** cloud-oversubscription, vCPU, imitation-learning, prototypical, active-learning, KITL, resource-management
