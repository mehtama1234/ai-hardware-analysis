"""Permission-model teaching example alongside a bounded ASPLOS paper discussion."""
PDF = 'https://johnwickerson.github.io/papers/cxl_cache_ASPLOS25.pdf'

CXL = {
    'id': 'cxl-coherence-2025',
    'route': 'asplos-2025',
    'title': 'Formalising CXL Cache Coherence: who is allowed to use a copy?',
    'identity': 'Chengsong Tan, Alastair F. Donaldson, and John Wickerson · Formalising CXL Cache Coherence · ASPLOS 2025, volume 2',
    'scope': 'Focused on what a permission proof establishes. Sections 5.2, 6, and 8 of the author-hosted paper were inspected, alongside the local source notes. The authors’ proof has not been rerun. The three-device example below is an original, deliberately smaller protocol—not the paper’s CXL model and not an extension of its proof.',
    'lessons': [('s3', 'Cached data'), ('s7', 'Messages and coordination'), ('s8', 'Specifications and correctness')],
    'blocks': [
        {
            'title': 'The problem is permission, not just copying bytes',
            'paragraphs': [
                'Keeping a nearby copy saves a trip to memory. But if another device may change the value, the nearby copy needs a rule governing when it may be used. A cache can physically contain bytes while no longer being permitted to return them. Separate those two facts: presence is a storage fact; permission is a protocol fact.',
                'Consider one location shared by devices A, B, and C. Permit several readers at once, or one writer with no other readers or writers. The writer may also read its own copy. This rule is often called single-writer, multiple-reader permission. It prevents conflicting access rights. On its own it does not prove that the writer received the right bytes, that an update survives a crash, or that every waiting request will eventually finish.',
            ],
        },
        {
            'title': 'What the paper establishes',
            'paragraphs': [
                'The authors formalise CXL.cache in Isabelle and prove a single-writer, multiple-reader property of their model. Section 6 uses a stronger condition that is true in the starting state and remains true after every allowed step; that kind of preserved condition is called an invariant. Section 5.2 demonstrates a coherence violation after relaxing a message-ordering restriction. Section 8 limits the model to two devices and one location, excludes some messages, and assumes perfect tracking in certain rules. The proof does not show that the system cannot get stuck, or that every waiting request eventually completes.',
            ],
            'sources': [(PDF + '#page=8', 'Paper sections 5.2 and 6 — restriction test and permission property'), (PDF + '#page=11', 'Paper section 8 — assumptions and limitations')],
        },
        {
            'title': 'A message sent is not a permission removed',
            'paragraphs': [
                'In our separate teaching protocol, all three devices initially have read permission and nobody has write permission. A asks to become the writer. A coordinator sends requests telling B and C to stop using their copies. Each recipient removes its read permission before sending an acknowledgement. The coordinator may grant A write permission only after receiving both acknowledgements. No new readers or other upgrades are allowed during this one operation.',
                'Now remove the waiting rule. The coordinator sends both requests, then grants A write permission immediately. Before either message arrives, B and C still have read permission. The forbidden overlap already exists; no particular incorrect data value is needed to demonstrate it. Saying “the invalidation was sent” confuses an intended future action with an action already completed at another device.',
                'Waiting for one acknowledgement is also insufficient with three initial readers. B may revoke its copy and acknowledge quickly while C’s message is delayed. Granting then leaves A as writer and C as reader. A two-device teaching case cannot expose this particular missing-second-acknowledgement bug because it has only one other reader. That is a reason to inspect model size, not a claim that a two-device proof has no value.',
            ],
        },
        {
            'title': 'Write down enough state to explain every step',
            'paragraphs': [
                'Track the reader set, the writer if any, outstanding revoke messages, acknowledgements on their way back, and the readers whose acknowledgements are still awaited. These are different sets. After B revokes, it is no longer a reader, but its acknowledgement can still be in transit and the coordinator can still be waiting for it. Collapsing those stages into one instantaneous operation would hide a real ordering question.',
                'A state is one complete assignment of those facts. A transition is one allowed event: begin the upgrade, deliver one revoke, deliver one acknowledgement, or grant the writer. A rule must specify both its guard—the condition allowing it—and the state it changes. For this example, the grant guard is that no acknowledgements remain outstanding. Delays select which event happens next; they do not make a sent message count as delivered.',
                'The desired property says: whenever A is the writer, neither B nor C is a reader. To explain why the rules preserve it, use an additional fact: every other device that still has read permission must be in the awaited set. Starting the upgrade records both readers. Delivering a revoke only removes a reader. Delivering its acknowledgement removes it from the awaited set only after revocation. Granting with that set empty therefore cannot leave another reader. The connection between permissions and pending messages is doing essential work in this argument.',
            ],
        },
        {
            'title': 'Testing, exhaustive exploration, and proof answer different questions',
            'paragraphs': [
                'Running one message schedule can demonstrate that particular execution, or reveal a bug. Exhaustively exploring every reachable state of this finite example covers every permitted ordering for its one upgrade. The accompanying checker does that and also checks two intentionally broken grant rules. It stores visited states rather than enumerating every possible duration of a delay; elapsed time does not affect this example’s permission rule.',
                'That exhaustive result remains about these states and transitions. It omits repeated upgrades, crashes, corrupted messages, new readers, and actual data values. A proof for a more general model can instead establish a property through a base case and preservation under every allowed transition. Both approaches still require a faithful model and an appropriate property. Neither turns an omitted hardware behavior into a checked one.',
                'Safety also differs from progress. If C never processes its revoke request, the correct teaching protocol never grants A permission. It remains safe while A waits forever. A claim that A eventually obtains permission needs additional assumptions about delivery and scheduling, and a separate argument. Likewise, exclusive write permission says nothing by itself about ordering accesses to two different locations.',
            ],
            'sources': [('scripts/check_course_permissions.py', 'Optional: inspect the teaching-model checker; run with Python 3 from the repository')],
        },
        {
            'title': 'Carry the distinction into the performance papers',
            'paragraphs': [
                'The earlier walkthroughs ask whether splitting work or moving it to another worker reduces delay. This example adds another question: which states and messages make that movement legal? A buffer that still exists is not necessarily safe to reuse; a model layer that is loaded is not necessarily the version a request requires. These are connections between teaching concepts, not claims that the CXL proof applies to FlashInfer or BlitzScale.',
                'When a paper says verified, finish the sentence: which property, of which model, under which assumptions, checked by which method? Then ask what connects that model to the implementation. A throughput measurement and a permission proof can both be valuable without either substituting for the other.',
            ],
            'sources': [('#paper-flashinfer-2025', 'Compare: dividing attention work'), ('#paper-blitzscale-2025', 'Compare: work on a partly loaded worker')],
        },
    ],
    'exercise': {
        'question': 'B has revoked and its acknowledgement has arrived. C still has read permission, but its revoke request is in transit. May A be granted write permission? If C instead revoked but its acknowledgement is still in transit, is granting allowed by this protocol? Explain why actual safety at one instant and permission to take a protocol step are different questions.',
        'answer': 'The first grant violates the stated permission property because C remains a reader. In the second state, granting would not create that particular overlap, but the protocol still forbids it: the coordinator has not received the evidence its guard requires. Following the guard makes the decision depend on available information instead of assuming knowledge of a remote action. Neither state tells us how long the remaining message will take.',
    },
}
