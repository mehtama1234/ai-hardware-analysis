"""Focused OSDI walkthrough of reliable communication between replicated services."""

PDF = 'https://www.usenix.org/system/files/osdi25-frank.pdf'

PICSOU = {
    'id': 'picsou-2025',
    'route': 'osdi-2025',
    'title': 'Picsou: prove which messages reached the other replicated service',
    'identity': 'Reginald Frank, Micah Murray, Chawinphat Tankuranand, and colleagues · Picsou: Enabling Replicated State Machines to Communicate Efficiently · OSDI 2025',
    'scope': 'A focused walkthrough of the paper’s cross-cluster communication guarantee, QUACK acknowledgments, failure response, and selected evaluation results. The paper reports author-run measurements; this course does not reproduce them. Sequence diagrams and arithmetic examples here are teaching models, not executions of Picsou.',
    'lessons': [('s4', 'Routes and message paths'), ('s7', 'Coordination under failure'), ('s8', 'Correctness promises'), ('s10', 'End-to-end completion')],
    'blocks': [
        {
            'title': 'Two correct services still need a safe handoff',
            'paragraphs': [
                'A replicated service stores copies of its state on several machines. The copies use a consensus protocol to agree on the order of accepted changes. This protects one service’s internal state, but it does not by itself define how a second, independently replicated service receives a change. A message might be sent twice, lost on one path, or received by one server that then fails. The two groups also might use different consensus protocols.',
                'Picsou names the cross-group operation Cross-Cluster Consistent Broadcast, or C3B. Its core delivery promise is precise: when one replicated state machine sends a message to another, at least one correct replica in the receiving group eventually receives it. C3B also has an integrity rule: the receiving group should deliver a message only if the sending group transmitted it. “One correct replica receives it” is a delivery guarantee. It is not the stronger claim that every receiving replica has committed the change, that the receiving service has applied it, or that its clients may already read it. C3B also does not, by itself, promise an order across separate messages.',
                'Keeping those events separate helps diagnose failures. If a sender promises destination commitment but reports success as soon as it has evidence of receipt, it may report completion too early. If an application only needs reliable delivery into the destination group, waiting until clients can read the update may add unnecessary delay. The right completion point depends on the promise the application makes.',
            ],
        },
        {
            'title': 'A cumulative group acknowledgment identifies a safe prefix',
            'paragraphs': [
                'A sender needs evidence about more than the last network send it attempted. Picsou’s QUACK is a cumulative quorum acknowledgment. A quorum is the sufficient set of group members required by the protocol’s failure assumptions. Here the acknowledgment says messages through a numbered point have been reliably received by at least one correct member of the destination group. Cumulative means one acknowledgment summarizes an ordered prefix, rather than carrying a separate receipt for every earlier message.',
                'Use an invented sequence m1, m2, m3. Suppose the destination group confirms a safe prefix through m1, but the next message m2 is lost. A later repeated QUACK for prefix 1 signals that progress stopped at that point; the sender treats m2 as possibly lost and retransmits it. The sequence illustrates the paper’s signal, not the complete protocol or the exact behavior of every replica. In particular, a sender should not conclude that m2 was committed just because it issued a send, or that m3 is safe to expose merely because it arrived at one machine.',
                'This resembles cumulative acknowledgments in TCP, but the guarantee has to fit replicated groups and Byzantine behavior. In the paper’s failure-free case, each message is sent once with constant metadata overhead. When a failure is suspected, the protocol uses quorum evidence to target resends instead of letting one faulty participant provoke arbitrary retransmissions. The protocol therefore ties its evidence to the recipient group; a local network-send completion is not treated as proof of remote receipt.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, introduction and QUACK definition'), (PDF + '#page=4', 'Conference paper, C3B protocol overview')],
        },
        {
            'title': 'Reliability is only meaningful under named failure assumptions',
            'paragraphs': [
                'A guarantee needs a failure model: which machines may stop, which may lie, and what eventual communication the proof requires. Picsou supports replicated services using crash-fault-tolerant or Byzantine-fault-tolerant consensus, and its paper defines C3B under a unified UpRight model. The paper assumes messages are eventually delivered and that the receiving group can verify whether a transaction was committed by the sender group. Those assumptions are part of the promise, not optional fine print.',
                'For an invented handoff, suppose change 17 sets a stored count from four to five. The sender commits it, the receiving group verifies the sender’s proof, and a correct destination replica receives it. C3B’s delivery condition is now satisfied. If the destination has not yet committed and applied change 17, a client read can still return four. Even after commitment, a read from a copy that has not applied the update may return four if the service permits such reads. To promise five, the application needs a read rule that waits for or selects state containing change 17. This timeline illustrates the additional application requirement; it is not an execution of Picsou.',
                'The design also needs an application rule for which changes to transmit. The paper notes that an RSM need not forward every committed message; for example, groups may share only changes to selected objects. That filtering rule determines which state is supposed to cross the boundary. Reliable transport cannot compensate for a wrong selection rule or for an application that assumes stronger destination behavior than the protocol provides.',
            ],
            'sources': [(PDF + '#page=3', 'Conference paper, system and failure model'), (PDF + '#page=4', 'Conference paper, invoking Picsou and transmitting messages')],
        },
        {
            'title': 'Keep the speedup attached to the experiment',
            'paragraphs': [
                'The authors evaluate Picsou on up to 45 Google Cloud nodes and compare it with named alternatives, including traditional all-to-all broadcast and Kafka. They report up to 24× better performance than prior solutions in microbenchmarks and applications. That maximum is not one universal end-to-end speedup: the paper reports different results by node count, message size, consensus protocol, workload, and failure condition.',
                'Two narrower results show why the boundary matters. When consensus is not the bottleneck, the paper reports 3.2× over traditional all-to-all broadcast for a four-node network and up to 24× for a 19-node network. For its Etcd disaster-recovery and data-reconciliation applications, it reports 2× performance over Kafka; the paper also calls out a known high-latency Kafka consumer issue affecting that comparison. Its blockchain workloads have a different tradeoff, including latency that grows with network size.',
                'These measurements support the claim that a purpose-built group protocol can reduce communication cost in the tested conditions. They do not establish behavior under arbitrary network partitions, every deployed consensus protocol, or a different application’s definition of completion. To compare systems for a real handoff, measure delivery, destination commit, and client-visible completion separately, and keep message size, failure rate, network, and required guarantee fixed.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, abstract and headline results'), (PDF + '#page=10', 'Conference paper, microbenchmark and application evaluation')],
        },
    ],
    'exercise': {
        'question': 'A source service commits update U. The sender gets a QUACK establishing a safe destination-received prefix through U. The destination has not yet committed U in its own log. Can the sender claim that destination clients will read U? Name one fact established and one still missing.',
        'answer': 'It can claim only the delivery fact covered by C3B: at least one correct destination replica has reliably received U under the stated assumptions. It cannot infer that the destination group has committed U or that a client read is required to expose U. The destination’s own commit and read-consistency rule are still missing. In a real system, the sender may report “delivered” at this point only if its interface says delivered; a promise of applied or readable state requires additional evidence.',
    },
}
