# A. Delegato: Locality-Aware Atomic Memory Operations on Chiplets

**Venue:** MICRO · **Subtheme:** Coherence & Chiplet Interconnect

## What It Does

Delegato addresses a performance cliff in chiplet-based multi-core systems: atomic memory operations (AMOs) — fine-grained synchronization primitives like compare-and-swap used in parallel workloads — become orders of magnitude slower when cache lines are split across chiplets. In monolithic designs, an AMO executes locally at the cache line's current owner (a few cycles). In dual-chiplet systems like NVIDIA Grace (two 16-core chiplets connected via 50ns NVLink interposer), every AMO that misses locally must either: (1) fetch the cache line to the requester's chiplet, execute it, and writeback (ping-pong traffic), or (2) send the RMW operation to a centralized directory ALU (adds directory latency). Delegato introduces two new coherence transactions: **Delegated AMOs** forward the RMW operation via a new SnpAMO snoop to the cache-line owner, which executes the operation locally and returns the result without transferring the line; **Migrating AMOs** transfer ownership of the cache line to the requester using an AtomicLoad request. The directory tracks cache-line state and chiplet location, then chooses between five static policies (All-Central, All-Migrate, Present-Central, Pinned-Owner, Unowned-Central) and a Chiplet-Aware policy. On top of these, **Delegato** adds a one-bit reuse_bit that the L2 cache piggybacks in every SnpAMO response back to the directory. This bit signals whether the cache line was used again by the same requester; the directory's Predictor Table uses this feedback to transition between policies over time, learning which AMO strategy minimizes round-trip latency for each cache line.

Data flow: Requester on Chiplet A issues AMO → directory checks reuse_bit history → if "pinned" pattern detected, issues SnpAMO to Chiplet B owner → owner executes RMW in-place, returns result → Chiplet A receives result directly without fetching the line. This eliminates the inter-chiplet cache-line transfer.

## The Key Result

On graph analytics and HPC benchmarks, Delegato achieves 1.13× speedup over DynAMO (state-of-the-art AMO predictor) and 1.07× speedup over All-Centralized AMOs, evaluated on 20+ benchmarks in gem5 with 32 out-of-order cores (dual 16-core chiplets) and AMBA 5 CHI protocol. Delegated AMOs reduce critical-path inter-chiplet messages from 4 to 2 in pathological worst-case scenarios. The atomic ALU extension requires only 2894 µm² at 7nm (0.11% of a Neoverse V1 core tile).

## Why This Approach

Chiplet scaling is now mandatory for large core counts (post-2020 CPUs and GPUs are all chiplet-based), but interposer latency (50ns for NVLink, 30-40ns for advanced interposers) makes traditional AMO execution strategies fail. Near AMOs (cache-line fetch) incur 2× interposer crossings (fetch + writeback). Centralized AMOs require directory involvement and ALU cycles, serializing all AMOs through a bottleneck. Delegato's insight is that fine-grained locality patterns exist: if a cache line is frequently accessed by one chiplet, it should stay pinned there and let remote AMOs delegate. The reuse_bit piggybacking mechanism captures this pattern at near-zero overhead (one bit in an existing snoop response) and lets the directory adapt per cache line. This beats static policies because different cache lines have different AMO access patterns. The alternative — increasing interposer bandwidth or accepting higher latency — scales poorly; Delegato exploits locality instead.

## What It Leaves Open

- Delegated transactions currently assume single-owner scenarios; multi-sharer cases (multiple chiplets with cached copies) defer to centralized fallback, losing the delegation benefit.
- Performance gains are modest (1.07x-1.13x geomean), reflecting the narrow optimization window — only a fraction of workload time is spent in AMO-heavy phases; further gains would require algorithmic changes at the application level.
- The reuse_bit Predictor Table has a fixed size and replacement policy; no analysis of misprediction rates on workloads with many unique cache lines or thrashing patterns.
- Evaluation limited to two chiplets; scalability to 4+ chiplets and how directory predictor state explosion affects performance is unexplored.
- No comparison with hardware transactional memory (HTM) or other alternatives to fine-grained AMOs on chiplet systems; assumes AMO-based workloads are unavoidable.
