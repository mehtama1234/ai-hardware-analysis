"""Explicit learning dependencies and original cross-topic practice."""

PREREQUISITES = {
    's1': [],
    'dependencies-and-pipelines': ['s1'],
    's2': ['s1'],
    's3': ['s1', 'dependencies-and-pipelines'],
    's4': ['s3'],
    's5': ['s2', 's3'],
    's6': ['dependencies-and-pipelines', 's2', 's3'],
    'queues-and-batching': ['s1', 'dependencies-and-pipelines'],
    's7': ['dependencies-and-pipelines', 's3'],
    'physical-design': ['s1', 's3', 's4'],
    's8': ['s2', 's7'],
    's9': ['s3', 'queues-and-batching', 's8'],
    's10': ['s1', 's3', 's6', 'queues-and-batching', 's8'],
    'durable-update': ['s7', 's8'],
    'training-workflow': ['dependencies-and-pipelines', 's2', 's7'],
    'scientific-workflow': ['dependencies-and-pipelines', 's2', 's3', 's7'],
}

CHECKPOINTS = [
    {
        'id': 'checkpoint-bottleneck',
        'title': '1. Choose between a faster operation and a shorter path',
        'setup': 'An invented service has sequential stages: 6 ms waiting, 8 ms reading, 4 ms computing, and 2 ms delivering. A costs nothing to prepare and halves computing time. B skips the read and computation on a valid cache hit, but always adds a 1-ms lookup. Half the requests hit. Assume the waiting and delivery times remain fixed, misses run the original read and computation, and neither change affects output quality.',
        'question': 'Calculate the baseline, A, and B’s hit and miss times. Which has the lowest mean? Which has the most requests meeting a 19-ms deadline? What missing evidence would you ask for before predicting behavior under a burst?',
        'answer': 'Baseline is 20 ms. A takes 18 ms. B takes 9 ms on a hit and 21 ms on a miss, averaging 15 ms with equal counts. B wins on mean delay, but A meets the 19-ms deadline for every request under these assumptions; B meets it for only half, and the baseline for none. Before predicting burst behavior, inspect the arrival trace, shared-resource contention, cache hit pattern and validity, and how either change affects the queue. Fixed waiting was an assumption, not a measured consequence. Combining A with B requires a fresh calculation: misses would take 19 ms, hits 9, and the mean 14 if all other assumptions held.',
        'review': [('s1', 'Elapsed time'), ('s3', 'Valid reuse'), ('queues-and-batching', 'Delay distributions')],
    },
    {
        'id': 'checkpoint-accepted-result',
        'title': '2. Compare time to the accepted result',
        'setup': 'An invented solver has 2 seconds of setup, takes 100 iterations at 20 ms each, and spends 1 second checking and saving its accepted answer. A lower-precision version needs 160 iterations at 10 ms each and has the same other costs. Both pass the same justified accuracy test. A third version returns in 2 seconds but fails that test.',
        'question': 'Which valid version finishes sooner? What is the largest whole iteration count at which the lower-precision version is strictly faster? If conversion adds 0.6 seconds, what changes? Explain why the third version is not the winner.',
        'answer': 'The baseline takes 2 + 100 × 0.020 + 1 = 5 seconds. The lower-precision version takes 4.6 seconds, a saving of 0.4 seconds, not a twofold whole-job improvement. With no extra conversion, it is strictly faster at at most 199 iterations; 200 ties. With 0.6 seconds of conversion and 160 iterations, it takes 5.2 seconds and loses. Its strict-win limit is then 139 iterations; 140 ties. The third version fails the required result, so its time belongs in a failed-run report, not an equal-quality speed ranking. Check the accuracy rule’s adequacy separately from these timing calculations.',
        'review': [('s2', 'Representation error'), ('training-workflow', 'Time to quality'), ('scientific-workflow', 'Acceptance rules')],
    },
    {
        'id': 'checkpoint-evidence',
        'title': '3. Match a claim to the evidence that would support it',
        'setup': 'Three fictional reports say: “Our model preserves exclusive write permission”; “our device operation is twice as fast on the tested inputs”; and “our service has a lower average delay on the supplied request trace.” A proposal combines all three and claims a correct, twice-as-fast service that never misses a deadline.',
        'question': 'Identify three unsupported steps in that conclusion. Describe the next check that could test each one. Then decide whether more repetitions of the same timing benchmark would fill all three gaps.',
        'answer': 'First, a model property is not automatically an implementation guarantee: inspect the modeled assumptions, omitted behavior, and evidence connecting the implementation to the model. Also check whether exclusive permission is the full correctness promise; it is not the same as correct data or eventual progress. Second, a faster device operation need not halve total service time: measure the complete path, including unchanged work, preparation, movement, and interference in the combined configuration. Third, a lower average does not bound the slowest requests: examine deadline misses and the load and failure conditions under which the deadline promise is intended. More runs can improve estimates for that benchmark population, but cannot supply a missing correctness argument or justify behavior outside its conditions. A finite trace with no misses does not prove that misses are impossible.',
        'review': [('s8', 'Correctness claims'), ('paper-cxl-coherence-2025', 'Proof boundaries'), ('paper-flashinfer-2025', 'Operation and service measurements'), ('paper-blitzscale-2025', 'Changing capacity')],
    },
]
