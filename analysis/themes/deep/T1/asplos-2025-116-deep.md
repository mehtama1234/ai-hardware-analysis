# Coach: Exploiting Temporal Patterns for All-Resource Oversubscription in Cloud Platforms

**Venue:** ASPLOS · **Theme:** System Scheduling

## What It Does

Cloud platforms remain significantly underutilized across all resource types (CPU, memory, network, storage) because existing oversubscription approaches target only a single resource (typically CPU), causing the oversubscribed bottleneck to shift to other resources and leaving overall utilization low. Memory oversubscription is especially difficult because memory is non-fungible — physical pages cannot be quickly reassigned between VMs.

Characterization of over 1 million Azure VMs shows that VMs lasting more than one day consume 96% of resource-hours, many exhibit predictable complementary temporal utilization patterns (daily peaks and valleys), and holistic multi-resource oversubscription can enable ~26% more VMs per server.

Coach introduces CoachVM, a general-purpose VM type that partitions each resource into a guaranteed portion (always allocated, PA-backed for memory) and an oversubscribed portion (allocated on demand from a shared pool, VA-backed for memory using zNUMA to deprioritize cold pages via guest NUMA policy). A prediction model (random forest regressor) predicts per-VM resource utilization in time windows (e.g., 3x8-hour daily windows) using VM configuration, weekday, subscription history, and customer-specific features, computing per-resource oversubscription rates per time window. The cluster scheduler uses these per-time-window predictions to colocate VMs with complementary temporal patterns, maximizing multiplexing savings. A per-server oversubscription agent monitors resource utilization and applies reactive mitigations (local resource reassignment) or proactive mitigations (VM migration) to prevent SLO violations when contention occurs.

## The Key Experiment

- **speedup:** None
- **energy or tops w:** None
- **area:** None
- **ppa:** None
- **accuracy:** None
- **other:** ~26% more VMs hosted per server with minimal performance degradation; 4x6hr time windows save ~15% memory and ~20% CPU vs single-lifetime-max allocation

**Compared against:** no oversubscription; CPU-only oversubscription; CPU+memory oversubscription (non-temporal); Harvest VMs

**Hardware:** CPU · **Workloads:** database; HPC

## Why This Approach

Holistic all-resource oversubscription of cloud VMs using temporal utilization pattern prediction to colocate complementary workloads, with a PA/VA memory partition (zNUMA) that enables transparent memory oversubscription for unmodified guest VMs.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Characterization of resource utilization patterns across 1M+ Azure VMs revealing complementary temporal patterns, stranding, and multi-resource bottleneck shifts from CPU-only oversubscription..

## What It Leaves Open

- Memory oversubscription effectiveness depends on the availability of complementary temporal patterns which may not exist for all workload mixes
- the approach does not handle GPU or NVMe SSD without hardware ATS/PRI support.

**Tags:** cloud-resource-management, oversubscription, memory-oversubscription, temporal-patterns, vm-scheduling, azure
