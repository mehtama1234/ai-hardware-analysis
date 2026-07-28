# The Deep Read: One Constraint, Ten Answers

**Corpus: 1,769 papers across ten venues (MLSys, ISCA, MICRO, HPCA, ASPLOS, DAC, ISSCC, Hot Chips, SC, VLSID), 2025.**

---

## The One Constraint: Moving Data, Not Thinking

A computer chip does two jobs, and only two. It does arithmetic—adding and multiplying numbers—and it moves numbers between the place they are stored and the place the arithmetic happens. That is the whole machine. Everything a chip has ever done is some arrangement of those two jobs: fetch the numbers, combine them, put the answer back.

For most of computing history, the arithmetic was the expensive part, so engineers poured effort into faster arithmetic. They succeeded so completely that they inverted the problem. A modern chip can multiply two numbers in a sliver of a billionth of a second, at almost no energy cost. But before it can multiply them, those two numbers have to physically arrive from memory, traveling as electrical charge down metal wires. That trip is slow and expensive—often a hundred times more expensive in time and energy than the multiplication it feeds. The arithmetic became nearly free. The fetching did not.

Picture a brilliant accountant who can add any column of figures instantly, but whose ledgers sit in a warehouse across town, delivered one page at a time by a single courier. The accountant is never the bottleneck. The courier is. This is the one fact underneath every paper in this collection: **modern computers are limited by moving data, not by doing arithmetic.**

Artificial intelligence arrived and drove this problem from serious to dominant. A large language model is an enormous pile of learned numbers called weights—hundreds of billions of them. To produce even a single word of output, the chip must read essentially every one of those weights out of memory, pass each through a quick multiply-and-add, and move on. The arithmetic per weight is trivial. The hauling is not. Multiply billions of weights by the cost of dragging each one down the wire, and the machine's speed is set almost entirely by how many weights per second it can pull through the memory doorway.

There is a second twist that makes AI uniquely punishing. As a language model reads a conversation, it does not re-read every earlier word for each new word it writes. Instead, when each word first goes by, the model computes a small summary and stores it. This growing pile of summaries is the model's running notes—the KV cache in jargon. The notes let a chatbot hold a long thread in its head. They are also a second enormous thing that must live in the chip's fast memory and be hauled past the arithmetic units to generate each word. As the conversation grows, the notes grow, and every new word gets slower to produce because there are more pages to drag.

Put those together and you have the constraint the whole field bends around. The models are too big to fit in fast memory, so their weights must be streamed constantly. Their running notes grow without bound and must be streamed too. Split the work across many chips to go faster, and now numbers must cross even-slower wires between chips. At every level—inside one chip, between neighbors, across a data center—the arithmetic units are starving and the supply lines are the constraint.

---

## Ten Answers to One Question

If the enemy is data movement, there are only a handful of fundamental moves: move less data, move it a shorter distance, or move the arithmetic to where the data already sits. The ten themes are ten communities making these moves at different layers of the machine.

**T0: Compression and Honest Evaluation** — making data smaller before it travels, and getting the arithmetic of comparison right so we know whether we actually improved.

**T1: Attention and the KV-Cache** — keeping the notebook of what was said in fast memory, packed efficiently, and read without hauling every page.

**T2: Quantization and Low-Precision** — shrinking each number so less travels down the wire, trading precision against throughput.

**T3: Memory Hierarchy and Near-Data Processing** — moving arithmetic into memory itself so data never has to leave.

**T4: Interconnect and Collectives** — hiding communication cost between chips underneath computation, or redesigning the wires themselves.

**T5: Sparsity and Mixture-of-Experts** — skipping work that does not matter—the zeros, the sleeping experts, the near-repeats—so it never moves at all.

**T6: Compilation and Hardware Generation** — rearranging arithmetic so fewer numbers make the trip, and letting machines design chips automatically.

**T7: Security and Reliability** — protecting data and results while they move, against attackers and against the physics that silently corrupts.

**T8: Cryptographic and Quantum Acceleration** — specialized machines built from first principles for workloads utterly unlike ordinary AI.

**T9: Serving Schedules and Energy** — keeping the system fair and efficient as millions of users share one machine, and accounting for the true cost of electricity.

---

## T0: Compression, Measurement, and Honest Evaluation

This theme is the drawer of important things that don't fit elsewhere—and when laid out, they turn out to be different faces of the same root problem.

The most direct move is to make data smaller. Scientific instruments produce rivers of numbers too large for storage and cables to keep up with. A specialized compressor tuned to the internal structure of floating-point numbers can pack data to a third its original size and unpack it at hundreds of gigabytes per second. The machine must consume the data at the rate it arrives or compression helps nothing. So the whole apparatus is baked into the datapath where numbers travel. The tradeoff is that the compressor is specialized: it wins on one format and nowhere else.

A quieter thread runs through this: honest measurement. When you test a machine on many jobs, each gives its own speedup number. To summarize, you must average them—and the average the field has used for decades is mathematically wrong. It can rank a slower machine above a faster one. Getting the average right is not nitpicking. Real architectural conclusions rest on these numbers.

Deeper still is environmental accounting. A chip's true cost is not just electricity burned while running; it is pollution baked into manufacturing—mining, fabrication, shipping. If you optimize only for running cost, you appear to win by building a bigger, dirtier chip whose environmental debt you ignored. A design that places memory closer to compute improves both running efficiency and environmental score.

What ties this together is a shift in what counts as progress. For a long time, faster meant faster arithmetic. This section argues that faster usually means less data travels, less is stored, less is compressed. And you can only claim victory if you measure the right thing.

---

## T1: Attention and the KV-Cache

To write each new word, a language model must haul its entire growing notebook of running notes past the arithmetic units, doing tiny math on huge data.

The most basic move is keeping the notes rather than recomputing them, and reusing them wherever conversations overlap. If a thousand users begin with the same long instruction, the model would naively compute and store that identical notebook a thousand times. Prefix caching stores the shared opening once and lets everyone borrow it—organized as a tree where the shared trunk lives once and branches diverge per user.

The notebook must be laid out in limited fast memory. Early systems reserved a fixed slab per conversation sized for worst case, wasting most of it. The field learned to break the notebook into small pages handed out on demand, the way operating systems manage memory. That change alone unlocked serving far more users per chip.

The other half is the arithmetic of attention itself. A naive computation builds a giant weight table, writes it to slow memory, reads it back—pure waste. The breakthrough routine the field now uses never materializes the table: it processes in small tiles that fit in on-chip scratch, carrying just enough running totals to stitch them. On top sit the honest-tradeoff moves: store notes in coarser numbers—four digits instead of sixteen, a quarter the data—or skip pages that barely matter, since in long passages most earlier words contribute little to the next. Both trade accuracy for large cuts in data moved. A recurring finding is that these savings shrink or vanish once measured inside a real serving stack rather than a clean benchmark.

**Connects to:** T3 (computing attention in-memory for long contexts), T2 (shrinking the notebook with quantization), T5 (skipping unimportant pages via sparse attention), T4 (splitting prefill and decode across the network).

---

## T2: Quantization and Low-Precision Arithmetic

Every weight and note is stored in some number of bits. More bits means more warehouse space and more wire congestion on every trip.

The single most powerful move is making numbers smaller. A value in four bits instead of sixteen is a quarter the size and a quarter the data to move—and for many models barely dents output quality. The workhorse move is re-expressing numbers that lived in 16 or 32 bits using just 4 or 8: pick a small ladder of evenly-spaced values and snap each original to its nearest rung. Almost every serving system now quantizes weights to 4 bits and activations to 8.

The difficulty is that smaller numbers are cruder numbers. With four bits you have sixteen buckets. Most weights cluster near zero and round cleanly, but a few freakishly large outliers carry disproportionate importance and degrade badly when crushed. The field's ingenuity is almost entirely about paying the speed savings without the accuracy tax: spend more bits only on rare outliers and crush the ordinary bulk; give each small group of numbers its own ladder tuned to its spread; or let the number format itself adapt per group.

Vector quantization compresses whole little groups together by matching them to entries in a shared codebook, reaching below one bit per weight—at the cost of awkward, cache-thrashing lookups that only pay off with careful hardware. A subtle trap haunts all of it: you can shrink numbers and get no faster, because the chip pays back all savings just unpacking small numbers into forms its rigid arithmetic understands. One paper found unpacking devouring ninety-five percent of instructions. So a large share of work is rebuilding hardware to consume small numbers natively.

**Connects to:** T3 (fitting shrunken data through memory), T6 (compilers choosing quantization per-layer), T1 (shrinking the KV-cache).

---

## T3: Memory Hierarchy and Near-Data Processing

The machine spends most of its time not doing arithmetic but hauling numbers. This reshapes everything about where data lives and how it moves.

The oldest answer is the cache: a small, fast pocket sitting right next to the math, holding data most likely needed soon. When right, the needed data is already there. When wrong, expensive warehouse trips happen. The whole art is making fewer wrong guesses. Some approaches track how "hot" each piece of data is—frequently reused or rarely used—and protect hot data specially. Others use the compiler to analyze code ahead of time and leave hints about what the program will need.

Pre-fetching predicts which numbers the program will want next and sends for them in advance, so they arrive before being needed. The engine watches the stream of requests, spots patterns, and races ahead. The danger is a wrong guess: fetching data never used wastes the bandwidth you were trying to conserve.

A deeper rethink inverts the traditional arrangement entirely. If hauling data to the processor is the whole expense, why not place small arithmetic units inside memory chips themselves? Then numbers can be multiplied or added without the long trip out to the main processor. There is a spectrum. At one end, tiny compute units sit next to memory banks; at the other, memory cells themselves do arithmetic as a side effect of how they are read. Both keep data still.

Processing-in-memory shines when workloads drown in simple, regular, data-heavy operations—genome alignment, sifting huge database tables, or the KV-cache lookup itself. It requires careful co-design of memory layout and compute granularity. A whole sub-field is devoted to compilers and mapping tools that figure out how to lay programs across this hybrid substrate.

For the largest machines, a new plumbing standard called CXL lets you bolt extra memory pools onto a machine at slightly slower than on-chip memory. The question becomes: which pages deserve the fast local pool, which can be exiled to roomier CXL? The answers range from tracking both long-term and momentary page popularity, to learned agents tuning migration, to simply measuring accesses so the system stops mistaking warm data for hot.

The broad win is that the field has conquered easy, regular cases. For programs marching predictably through memory, caches and prefetchers hide the commute so well the memory wall barely shows. The hard core remains: irregular, scattered, pointer-chasing accesses of graphs and sparse math, address-translation taxes, and above all the sheer volume of data modern AI must haul. For these, no clean general answer exists.

**Connects to:** T1 (caching the KV-cache, computing attention in-memory), T2 (fitting shrunken data), T4 (memory hierarchy as a network design problem), T5 (irregular sparsity requires clever data layout).

---

## T4: Interconnect and Collectives

When many chips work together they hit a new, painful wall: they must tell each other what they found, and that talking is even slower than fetching from local memory.

The crude fact is compute scales beautifully and communication does not. Double the chips and get double the arithmetic. But the amount of talking grows faster, and the wires do not magically get fatter. So as you add chips, a larger fraction is spent with expensive chips idle, waiting for messages.

The single most important idea is deceptively simple: never let a chip sit idle waiting to talk. Arrange things so that while messages travel, the chip computes the next piece. Communication happens in the background underneath arithmetic. This is called overlap, and it is the closest thing this theme has to a universal goal.

Making overlap automatic is hard. Writing overlapped code by hand is notoriously error-prone. The field invests heavily in tools and abstractions that let programmers express overlapping compute-and-send code without manually juggling calculation and messaging.

The next lever is to reduce data traveling in the first place. The cheapest message never sent. Eliminate redundancy—when the same information is shipped multiple times, fuse those sends. Compress and selectively send—if important updates from one step to the next are mostly the same few, ship only those and reuse the pattern, cutting wire data by nearly ninety percent. Smart routing—when requested data sits on a passing module, grab it from there instead of the distant source.

Match the message pattern to the physical layout of wires. Chips are wired in fixed shapes—grids, rings, trees. When the pattern of who-talks-to-whom mismatch the layout, messages take long detours, collide, and waste pipes. The solution is redesigning communication so it flows naturally along actual wires.

Before optimizing any message, decide how to cut work into chip-sized pieces, because that choice largely determines cross-chip traffic. A bad cut drowns the cluster in communication. Natural ways to cut—hand each chip different data slices, or give each a pipeline stage, or split bookkeeping—can be combined into truly good plans.

For the largest workloads, do work inside the network itself instead of only at endpoints. Many chips sending numbers that need adding can add them up as they pass through switches in the middle, so only the final sum emerges. Making the network itself do arithmetic slashes data reaching any destination.

The field won the first battle on well-behaved, predictable workloads. The community now knows how to hide most communication underneath computation and shape heavy repeating traffic to not collide. But when the pattern of who-talks-to-whom depends on input and changes every step—recommendation and graph workloads—clean overlap tricks break down and progress remains piecemeal.

**Connects to:** T1 (distributing attention across chips), T5 (routing sparse operations across the network), T9 (energy of communication).

---

## T5: Sparsity and Mixture-of-Experts

A huge fraction of numbers these AI models work with are zero, or so close they might as well be. Multiplying by zero gives zero; adding zero changes nothing. Every zero fetched from memory, hauled across the chip, multiplied, and added is pure wasted effort—real energy, real time, zero effect.

The entire theme is one idea: if most work does not matter because it involves zeros or near-zeros or exact repeats, can we skip that work entirely and skip the data movement it requires?

The reason this is hard comes from a mismatch between where zeros scatter and how chips like to work. Chips are fastest doing the same operation on big, dense, regularly-shaped blocks of numbers marching in lockstep. But zeros scatter irregularly like holes in Swiss cheese. To skip a zero you first find it, track where survivors are, then feed them to arithmetic without leaving units idle. The bookkeeping to track "which numbers are non-zero and where" can cost more time than you saved by skipping zeros.

One branch goes down to individual bits: break numbers into thin slices and skip any slice that is all zeros, jointly for both model knowledge and incoming data.

Another branch forces zeros into tidy, predictable patterns. Instead of letting models zero wherever they want, insist on rules like "in every group of four numbers, exactly two must be zero." This structured sparsity lets chips march through at full speed with almost no bookkeeping. The trouble is forcing zeros into rigid patterns throws away accuracy because numbers you are forced to delete are not always least important.

A stubborn, unintuitive fact: sometimes it is faster to do wasteful dense computation, zeros and all, than to pay bookkeeping costs of being clever about zeros. A chip's dense math units are so heavily optimized that overhead of tracking scattered survivors can more than eat up savings. So some systems decide, per region, whether this region is sparse enough that skipping pays off, or whether to just run fast dense math here.

Modern large language models are increasingly Mixture-of-Experts: rather than one giant network processing every word, the model splits into many specialist sub-networks, and a lightweight router decides which few experts each word visits. The rest stay asleep. The model can hold enormous knowledge while only running a small slice per word. This coarse sparsity creates distinctive problems. The total pile of experts is far too big for a chip's fast memory, so sleeping experts live in slower, distant memory and get fetched only when a word wakes them. The whole apparatus becomes a data-movement and prediction problem: guess which experts you need soon enough to start fetching, arrange them in memory for efficient bursts, and keep arithmetic units fed while fetching.

Some work does not matter not because it is zero but because it is nearly identical to something already computed, or because no one notices if dropped. Diffusion models refine a guess over hundreds of small steps; from one step to the next most barely moves—reuse the earlier result wherever change would be tiny, avoiding most arithmetic. Graphics rendering renders the center in full detail and periphery cheaply because human eyes see sharply only in the small central spot. Reusing an old result or dropping "barely noticeable" detail is a bet the error stays invisible. These papers spend effort proving the bet is safe.

The deepest open problem is that wins are mostly one-off and specialized. The sparsity pattern for one model does not generalize to another. A chip tuned to one workload's sparsity pays dearly with different ones, which is why so much recent effort targets reconfigurable chips and learned runtime decisions rather than fixed designs.

**Connects to:** T2 (quantization interacts with sparsity), T3 (irregular sparsity requires clever data layout), T6 (compilers detecting and scheduling sparsity).

---

## T6: Compilation and Hardware Generation

Between a person's wish and a computer's execution sits a translator. A person writes what they want a machine to figure out as basically a wish. A compiler turns that wish into exact, ordered, machine-level steps a specific chip can actually perform.

The fundamental move is to rearrange operations so that it touches memory as little as possible. Two workhorse tricks are fusion—gluing back-to-back operations together so an intermediate result stays on the fast bench instead of being shipped to memory and immediately shipped back—and reuse—arranging work so once a number is on the bench, every operation needing it happens before it leaves.

The key difficulty is knowing what is safe to fuse or reuse. If operation B secretly depends on A, you cannot reorder them. The subtle insight is that the granularity at which you track dependencies matters enormously: too fine-grained and bookkeeping is so tangled you see no opportunities; too coarse and you miss real ones. Some approaches track dependencies at tile-sized block level, a middle grain that simultaneously untangles bookkeeping and exposes hidden chances to run things in parallel.

For any real computation there are astronomically many valid plans—different orders, different tile sizes, different work assignments. Usually no formula hands you the best one, because "best" depends on messy physical details of a specific chip. So a large branch simply searches: generate many candidate plans, estimate how each performs, keep promising ones, refine, repeat. The catch is actually running each candidate is far too slow with millions of candidates, so the field builds a cost model—a fast predictor guessing how well a plan runs without running it. This cost model is the whole ballgame.

Some approaches split the difference with a draft-then-check scheme: cheap rough analysis throws out obviously bad candidates, and only survivors get expensive accurate prediction. The predictor itself is increasingly a learned model rather than hand-written formula. One striking idea uses a language model as predictor and cleverly predicts performance one digit at a time so it can estimate computations far larger than anything it was trained on.

Classic compilers do all thinking ahead of time, once, and produce a fixed plan. But modern AI often changes: a model's workload depends on how long your prompt is, a model over a network depends on that specific input's shape. A plan optimized for one shape can be badly wrong for another. So newer clusters push decision-making later—sometimes all the way to runtime—while still preparing as much as possible in advance.

The most literal reading of hardware-generation is that the compiler's output is not a plan for running software on an existing chip—it is the design of a new chip itself. Designing chips by hand is extraordinarily slow and error-prone. The dream is to describe computation once, at a human level, and have a machine derive the actual hardware.

**Connects to:** T2 (choosing quantization per-layer), T3 (optimizing memory access), T1 (generating efficient attention kernels).

---

## T7: Security and Reliability

A computer chip is a slab of silicon with billions of microscopic switches carved into it, and thin metal wires connecting them. We have spent seventy years making switches smaller, faster, more numerous, and quietly convinced ourselves of something not actually true: that the machine always gives the right answer.

It usually does. But "usually" is terrifying once you run millions of chips day and night for years, because at scale even a one-in-a-billion mistake happens constantly, and nobody rings a bell when it does.

The chip does not know it is wrong. When a microscopic switch has a tiny manufacturing flaw, wears out a little, or gets nudged by heat or a stray particle, arithmetic can come out subtly wrong while every light stays green. The chip reports success. It hands you a number off by a bit, and your program keeps going as if nothing happened. Engineers call this a silent data corruption—silent because there is no crash, no error message, no smoke, just a wrong answer flowing downstream into everything you compute next.

Correctness is mostly a property of the data-moving machinery, not of arithmetic. The add itself is simple. What is fiendishly hard is guaranteeing that when two chips both want the same data, they agree on its current value; that a number written just before power loss actually survived; that one machine's work does not leak secretly into another's.

To go fast, modern chips cheat: they guess. When a chip reaches a fork, rather than wait to learn which way to go, it picks a direction and starts running, ready to throw work away if wrong. This guessing is where most chip speed comes from, but it makes the chip's true behavior fantastically more complicated than do-this-then-do-that.

One approach is to stop trying to prevent every error and instead become very good at noticing when one has happened. Even a silent wrong answer usually leaves ripples. A program fed corrupted data tends sooner or later to crash, write nonsensical log entries, dump memory, or fail visibly. If you watch millions of machines over years and notice that one particular physical chip sits behind a suspiciously large share of failures, you can point a finger at the silicon itself without needing special test circuitry built in.

The opposite philosophy refuses to rely on catching errors later and instead proves with the full rigor of mathematics that a design cannot misbehave in the first place. Formal verification translates hardware or software into precise logical statements, then has a machine grind through every possible case to show that some desired property always holds. When it works it is the strongest assurance there is. The cost is brutal effort and limited reach: proofs historically could only handle small, tidy designs because cases to check explode as designs grow.

A gentler, more targeted flavor of proof appears when you want to change a design to make it faster or smaller and need to be certain you did not accidentally change what it does. Compilers and hardware tools constantly rewrite things, replacing circuits with cleverer equivalents. The approach verifies each rewrite rule once, proving before and after are truly equivalent, so it can then be applied freely with confidence.

At large scale, some component failing is not a possibility to guard against but a certainty to plan around. The approach accepts parts will die and focuses on keeping the overall system correct and available. The core mechanism is redundancy and graceful retreat: keep enough spare copy or slack that when something fails the system carries on or steps down gently instead of collapsing.

**Connects to:** T3 (coherence and memory-system correctness), T4 (failures in large distributed systems), T9 (cost of redundancy).

---

## T8: Cryptographic and Quantum Acceleration

These themes sit at the extreme: workloads so different from ordinary AI that they demand their own silicon, built from first principles.

Cryptographic proof generation (zero-knowledge proofs, fully homomorphic encryption) requires that data remain encrypted even while processed. A single secret number must balloon into thousands of encrypted numbers so operations happen without revealing the secret. This means the data-movement ratio is catastrophic. Every operation touches an enormous amount of data, and the machine cannot move that much fast enough. The only answer is to build a fixed-function chip whose circuits are laid out to match the specific computation, keeping intermediate results flowing directly from one unit to the next instead of being shuttled to memory.

Quantum computing inverts the usual problem. Memory is the constraint, but not because it is distant. A qubit is so fragile it forgets what it holds in a fraction of a second and is corrupted by the faintest disturbance. A quantum machine must spend the overwhelming majority of effort not on the calculation you care about but on continuously detecting and repairing errors before they spread. This is error correction, and it imposes a brutal real-time deadline: repair must complete within under a microsecond, cycle after cycle, or errors outrun fixing.

That deadline turns quantum computing into a hardware-design problem aimed at supporting a strange new machine. The field has built ordinary fast electronics whose only job is keeping the fragile quantum part alive: error-decoding engines meeting sub-microsecond deadlines, branch-prediction techniques borrowed from classical processors to speculatively guess quantum measurement outcomes, low-cost detectors for when qubits slip into forbidden states, and control architectures coordinating many controllers with almost no synchronization overhead.

---

## T9: Serving Schedules and Energy

When millions of people chat with a model, electricity and hardware bills are overwhelmingly spent on one loop: haul the notebook of what was said, weigh the past, emit one word, repeat. A serving system halving the data per word roughly halves the enterprise's cost.

In the naive approach, a model is set up to be fast and then asked to work for thousands of users. But users make different requests at different times with different deadlines—a user might tolerate three seconds for a long question, but only half a second for a simple query. The machine must decide what to compute when so every user gets an answer within their deadline and the chip stays busy rather than idle.

The approach is phase-aware: recognize that producing each word involves different operations with different resource hungers. The initial heavy reading of a prompt is arithmetic-bound—keep multiplying units busy. But producing each subsequent word is data-bound—mostly waiting on the notebook. These are opposite appetites. Running them on the same chip means each interferes with the other. Some systems disaggregate them, dedicating one chip pool to heavy initial reads and another to word-by-word generation, sized and tuned for different needs.

The other axis is energy. Most papers report throughput or latency. A smaller but growing cluster reports Joules—true computing cost, accounting for electricity burned. Some systems use the prefill/decode split as a knob to manage energy and temperature across a data center, dialing chip speed to the phase being run. Others make GPU energy attribution a research topic, breaking down exactly which machine parts consume the most power so architectural and scheduling decisions can target real hot spots.

**Connects to:** T1 (optimizing the prefill/decode split), T3 (memory bandwidth dominates energy), T4 (communication cost in Joules).

---

## Where It All Points

What do 1,769 papers tell us about the future? That the field has internalized the core lesson across every layer.

**What is solved:** The field knows how to restructure attention and the KV-cache to fit the target datapath. Shrinking to 4-bit weights and 8-bit activations is routine. Caches and prefetchers hide memory latency for well-behaved workloads. Mixture-of-Experts offloading has matured to running trillion-parameter models. Processing-in-memory shines in its niche. Secure speculation defenses offer provable safety at genuinely low average cost. Formal verification has reached genuine commercial artifacts, exposing real bugs in industry standards. The field has a rich menu of partial answers, each excellent in its niche.

**What is being solved:** The community has largely settled that the bottleneck is data movement, not arithmetic. Co-design—reshaping both algorithm and hardware together—is now universal practice. Compilation tools that automatically search for efficient plans and adapt to unseen hardware are maturing. Serving systems balancing throughput, latency, and energy under realistic SLOs are deployed at scale. Reproducibility and artifact evaluation are becoming first-class research artifacts, particularly at supercomputing scale.

**What remains genuinely open:** No one has a way to get proof-grade certainty at fleet-grade scale and cost. Silent corruptions are still only partially characterized; the field learns how often they strike but not fully why, or how to stop them cheaply. When the pattern of who-talks-to-whom depends on input and changes every step, clean overlap tricks break down. Pushing quantization below 4-bit while maintaining accuracy is delicate. The most promising frontier—computing inside or beside memory and storage—delivers spectacular wins in narrow, hand-tuned demonstrations, but remains far from a drop-in solution because memory chips have brutally tight room for logic.

The deepest unsolved question is not how to build a fast machine for a known problem. It is how to keep pace when problems themselves keep changing underneath the silicon. Each advance in model architecture shifts the balance and reopens questions that looked closed. The root problem—that computers are limited by moving data—is not going away. It is being managed, layer by layer, one clever overlap at a time.

---

## Summary

This corpus of nearly 1,800 papers across ten venues describes a field unified by one physical constraint: fetching numbers is far more expensive than using them. The bottleneck is universal; solutions differ only in what layer they reshape. Software compilers hide latency through careful scheduling. Silicon architects build specialized datapaths and memory systems. Circuit designers measure and optimize per-chip power. Operating systems and serving schedulers allocate fairly. The same problem appears at every scale: moving data costs time and energy, so every advance reduces data movement or moves computation to where data lives. The field knows this, acts on it consistently, and measures whether claimed improvements survive when the full stack runs together. That maturity is what 1,769 papers collectively demonstrate.
