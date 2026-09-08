"""Exact integer CPU references; tree structure mirrors parallel scan work.

Python integers do not overflow. A fixed-width GPU implementation must define
its overflow policy separately. These loops are not device kernels.
"""


def exclusive_scan(values):
    """Blelloch up-sweep/down-sweep, padded to a power of two."""
    data = list(values)
    if any(type(x) is not int for x in data):
        raise ValueError("scan requires integers, excluding booleans")
    count = len(data)
    if count == 0:
        return []
    size = 1 << (count - 1).bit_length()
    tree = data + [0] * (size - count)
    stride = 1
    while stride < size:
        for end in range(2 * stride - 1, size, 2 * stride):
            tree[end] += tree[end - stride]
        stride *= 2
    tree[-1] = 0  # Exclusive scan's identity replaces the total at the root.
    stride = size // 2
    while stride:
        for end in range(2 * stride - 1, size, 2 * stride):
            left = tree[end - stride]
            tree[end - stride] = tree[end]
            tree[end] += left
        stride //= 2
    return tree[:count]


def stable_compact(values, keep):
    """Stable scatter using exclusive predicate ranks, without atomic ordering."""
    data, flags = list(values), list(keep)
    if len(data) != len(flags) or any(type(flag) is not bool for flag in flags):
        raise ValueError("one boolean predicate per element is required")
    ranks = exclusive_scan([int(flag) for flag in flags])
    count = ranks[-1] + int(flags[-1]) if flags else 0
    output = [None] * count
    for index, flag in enumerate(flags):
        if flag:
            output[ranks[index]] = data[index]
    return output


def histogram(values, bins):
    """Exact counts for integer bin indices in [0, bins)."""
    if type(bins) is not int or bins < 1:
        raise ValueError("bins must be a positive integer")
    counts = [0] * bins
    for value in values:
        if type(value) is not int or not 0 <= value < bins:
            raise ValueError("histogram value outside integer bin range")
        counts[value] += 1
    return counts


def radix_sort_indices(keys):
    """Stable uint32 LSD radix sort returning original indices.

    Four byte-wise histogram/scan/scatter passes. No built-in sorting is used.
    Returning indices makes permutation preservation and duplicate-key stability
    observable independently of sorted key values.
    """
    data = list(keys)
    if any(type(key) is not int or not 0 <= key < 2**32 for key in data):
        raise ValueError("keys must be unsigned 32-bit integers")
    order = list(range(len(data)))
    for shift in (0, 8, 16, 24):
        digits = [(data[index] >> shift) & 255 for index in order]
        offsets = exclusive_scan(histogram(digits, 256))
        updated = [None] * len(order)
        for index, digit in zip(order, digits):
            updated[offsets[digit]] = index
            offsets[digit] += 1
        order = updated
    return order
