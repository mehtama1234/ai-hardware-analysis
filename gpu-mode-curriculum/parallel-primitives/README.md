# Parallel primitives: executable references and analytical scenarios

The original `parallel_primitives/analyzer.py` models six scenarios from supplied
timings and resource assumptions. Its passing design checks are not numerical
tests or device measurements. The separate [reference module](parallel_primitives/reference.py)
now executes integer exclusive scan, stable stream compaction, histogram and
stable unsigned-32-bit radix sorting on CPU.

## Exclusive scan

For `[3,1,4,2]`, an exclusive sum is `[0,3,4,8]`: each output sums only earlier
inputs. The implementation pads to a power of two, reduces a binary tree upward,
replaces the root total with zero, then propagates prefix totals downward.
The left child receives the parent's prefix; the right child receives that
prefix plus the old left subtree total. Reading the left total before overwriting
it is essential. Empty inputs produce an empty result; padding never appears in
the logical output.

For padded length `p`, each sweep visits `p-1` internal nodes, with logarithmic
tree depth. The Python loops execute those nodes serially: the tree structure
does not itself make this a parallel CPU or GPU implementation.

Background: Guy Blelloch's [Prefix Sums and Their Applications](https://www.cs.cmu.edu/afs/cs.cmu.edu/project/scandal/public/papers/CMU-CS-90-190.html)
introduces prefix sums as a parallel-algorithm building block and discusses their
implementation and applications. Local correctness is established by our tests,
not by citing that report.

## Stable compaction

Scan predicate bits into output ranks, then scatter each kept element to its rank.
For flags `[True,False,True,True]`, ranks are `[0,1,1,2]`; kept elements go to
positions 0, 1 and 2. Their original relative order is retained, including duplicate
keys. The final rank plus the last predicate yields the output length.

```bash
python3 -m unittest discover -s gpu-mode-curriculum/parallel-primitives/tests -v
```

Seven tests passed: sequential scan oracle, exact large integers, stable compaction
against filtering, histogram counts, radix permutation/stability, and invalid inputs. Cases include empty/singleton inputs,
power-of-two boundaries, negative values, all/none/alternating/random predicates,
and duplicate keys carrying unique positions. Inputs are not modified.

Python integers do not overflow. Future fixed-width device implementations must
declare overflow behavior and test it separately. Block synchronization, multi-block
scan carries, scratch allocation, accelerator kernels and profiler measurements
remain open. These tests are registered in the aggregate advanced checkpoint;
both their test source and reference implementation are included in its freshness
snapshot. Passing them establishes CPU reference correctness, not GPU execution.

## Histogram and stable radix sorting

`histogram` counts integer bin indices and rejects values outside the declared
range. `radix_sort_indices` composes four byte-wise counting passes: histogram
the selected byte, exclusive-scan counts into bucket offsets, then scatter in
the previous pass's order. That stable scatter preserves lower-byte ordering
while successively sorting more significant bytes.

The result is a permutation of original indices, not only sorted key values.
Tests compare the entire permutation with Python's stable sort, exposing lost
elements and duplicate-key reordering. Inputs include all-equal keys, sorted and
reversed data, byte-boundary values, the largest uint32 value, random full-width
keys, and repeated high-byte keys. Negative or oversized keys are rejected rather
than silently truncated. This is a serial algorithmic reference, not GPU sorting
throughput or native fixed-width arithmetic evidence.
