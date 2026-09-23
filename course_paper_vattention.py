"""Focused ASPLOS walkthrough of virtual memory for dynamic KV-cache serving."""

PDF = 'https://doi.org/10.1145/3669940.3707256'

VATTENTION = {
    'id': 'vattention-2025',
    'route': 'asplos-2025',
    'title': 'vAttention: separate a simple address layout from physical allocation',
    'identity': 'Ramya Prabhu and colleagues · vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention · ASPLOS 2025',
    'scope': 'A focused walkthrough of KV-cache growth, fragmentation, virtual-versus-physical memory, kernel compatibility, and the reported serving evaluation. The local author-hosted primary text was inspected. Results are author-reported and have not been independently reproduced here. The address and timing examples are original teaching models.',
    'lessons': [('s3', 'Memory hierarchy'), ('s6', 'Execution plans'), ('queues-and-batching', 'Serving under load'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'The KV cache grows one step at a time, but its final size is unknown',
            'paragraphs': [
                'During generation, a model reuses the key and value vectors from earlier tokens. This saved state is the KV cache. Every new token adds more state, but the system usually does not know the final number of generated tokens when a request arrives. Reserving the maximum possible space wastes memory; allocating only what is needed requires a way to grow the cache while other requests are using the GPU.',
                'The waste is not only unused bytes. If each request reserves a large private region, those holes reduce the number of requests that fit in memory, which reduces batch size and can reduce throughput. A useful memory design therefore has to answer two separate questions: where should the program think the cache is, and which physical memory pages currently back it?',
                'Original model: four requests each reserve 10 units, but their actual caches need 2, 4, 6, and 8 units. Static reservation consumes 40 units while only 20 hold data, so half the reserved space is unused. If the system can grow each cache in 2-unit pieces, it needs 20 units plus at most the current partially filled pieces. The exact saving depends on the allocation unit and request lifetimes; “dynamic allocation” alone does not specify it.',
            ],
            'sources': [(PDF, 'vAttention paper, sections 1 and 2: KV-cache growth, fragmentation, and dynamic allocation')],
        },
        {
            'title': 'Paged storage solves one problem by changing another layout',
            'paragraphs': [
                'PagedAttention allocates physical memory in blocks as a request grows. That avoids reserving the maximum cache size, but the blocks may not be adjacent in the virtual address space. The attention kernel then needs a table that maps logical cache positions to blocks and must follow that mapping while reading keys and values.',
                'This creates a boundary between memory management and computation. A highly optimized attention kernel normally expects a contiguous tensor and regular addresses. A paged kernel has extra lookups, branches, indexing state, and sometimes padding in the CPU-created block table. New attention optimizations also need a second implementation that understands the paging layout. The cost is not just a few instructions; it is ongoing work at the interface between the allocator and every consumer.',
                'Original address example: a logical cache has four 2-unit blocks. A contiguous consumer reads addresses 0–7 in order. A fragmented allocation may map those blocks to physical locations 20–21, 4–5, 40–41, and 10–11. The data are still present, but the consumer needs four mappings and loses the simple address pattern. If a mapping lookup costs 1 unit per block and the actual arithmetic costs 2 units, the lookup adds 4 units to 8 units of arithmetic. The ratio changes when the kernel is dominated by memory waits or much larger arithmetic.',
            ],
            'sources': [(PDF, 'vAttention paper, section 3: rewritten attention kernels, mapping redundancy, and runtime overhead')],
        },
        {
            'title': 'vAttention separates virtual contiguity from physical commitment',
            'paragraphs': [
                'vAttention reserves a large contiguous virtual address range for the KV cache, but delays assigning physical pages until the cache needs them. The GPU kernel therefore sees the regular contiguous layout it was designed for, while the physical allocator avoids committing the full maximum size up front. This is the central design move: virtual address space is the stable view used by code; physical memory is the scarce resource assigned over time.',
                'The paper uses CUDA virtual-memory facilities and adds workload-specific policies. Decode grows predictably by one token per iteration, so the system can know whether another page will be needed for the next iteration. It can allocate ahead of time, overlap allocation with computation, and defer reclamation. Those policies address the cost of page operations, but they also create state: a completed request’s physical pages may remain available for reuse, and page size affects internal waste.',
                'Original break-even model: a paged kernel saves 12 units of physical-memory waste but adds 5 units of mapping and indexing work per request. A virtually contiguous design spends 2 units reserving and managing pages but removes the 5-unit kernel cost. If physical capacity is the limiting resource, the first design may admit more requests; if the kernel is the limiting resource, the second may finish each request faster. The right choice depends on which resource controls the accepted service rate.',
            ],
            'sources': [(PDF, 'vAttention paper, sections 4 and 5: workload observations, virtual/physical separation, and allocation policies')],
        },
        {
            'title': 'The result depends on which phase and boundary you measure',
            'paragraphs': [
                'The paper evaluates prefill kernels, decode throughput, offline end-to-end throughput, and online request latency. It reports that vAttention’s contiguous kernels can improve prefill results where paging adds visible computation and address-handling overhead. In decode, the paper reports parity with the best paged FlashAttention-2 path in its tested cases because decode is more memory-bound and can hide some extra computation. A mechanism can therefore matter strongly in one phase and weakly in another.',
                'For its stated models and systems, the paper reports up to 1.99×, 1.58×, and 1.53× over vLLM for decode throughput on Yi-6B, Llama-3-8B, and Yi-34B, and offline end-to-end gains of up to 1.18×, 1.15×, and 1.13× over FlashAttention-2 paged kernels. It also reports selected median online latency reductions of up to 42%, 28%, and 29%. These are separate boundaries with different baselines, models, request traces, and load conditions; they must not be merged into one universal speedup.',
                'The evidence is bounded to the paper’s A100/H100 systems, software versions, model choices, context lengths, batch sizes, and request rates. CUDA virtual-memory behavior, page size, kernel libraries, and serving policies may differ elsewhere. This walkthrough has not reproduced the implementation or the reported measurements. Its address and timing examples are original teaching models, not vAttention measurements.',
            ],
            'sources': [(PDF, 'vAttention paper, sections 6 and 7: methodology, kernel results, decode, offline, and online evaluation')],
        },
    ],
    'exercise': {
        'question': 'A service has 100 units of physical memory. Four requests need 18, 22, 26, and 30 units, but a static allocator reserves 30 units for each. How many requests fit under static reservation? If a dynamic allocator uses the actual sizes, how much space remains? Then name one cost that could still make the dynamic design slower.',
        'answer': 'Static reservation fits 3 requests because 3 × 30 = 90 while 4 × 30 = 120. Dynamic allocation uses 18 + 22 + 26 + 30 = 96 units and fits all four, leaving 4 units. The dynamic design can still be slower if it adds page allocation, mapping, synchronization, page faults, reclamation, or kernel work; capacity improvement and per-request latency are different claims. These are original teaching calculations, not vAttention measurements.',
    },
}
