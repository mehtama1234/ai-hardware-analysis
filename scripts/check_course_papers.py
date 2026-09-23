#!/usr/bin/env python3
"""Check original walkthrough arithmetic; does not reproduce paper results."""
from fractions import Fraction as F
from collections import Counter
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from course_papers import PAPERS


def main():
    # Every walkthrough must tell readers what source was inspected and what
    # was not reproduced. This is a boundary check, not proof the paper summary
    # is accurate; that still requires reading the cited source.
    assert len(PAPERS) == 58, f'Expected 58 conference walkthroughs, found {len(PAPERS)}'
    boundary = re.compile(
        r'\bnot\b.{0,70}\b(?:reproduc\w*|rerun|implementation)\b|'
        r'\bno\b.{0,70}\b(?:reproduc\w*|hardware)\b', re.I | re.S)
    for paper in PAPERS:
        assert len(paper['scope']) >= 150, f"Scope is too thin: {paper['id']}"
        assert boundary.search(paper['scope']), f"Missing reproduction/evidence boundary: {paper['id']}"
        cited = [source for block in paper['blocks'] for source in block.get('sources', [])]
        assert cited, f"No source citations in walkthrough: {paper['id']}"
        assert all(label.strip() for _, label in cited), f"Unlabeled source in walkthrough: {paper['id']}"
    print('All 58 walkthroughs identify their reading scope, source citations, and a non-reproduction boundary; this does not verify the source interpretation.')
    daris = next(paper for paper in PAPERS if paper['id'] == 'daris-2025')
    daris_text = ' '.join(p for block in daris['blocks'] for p in block['paragraphs'])
    assert daris['route'] == 'dac-2025'
    assert all(term in daris_text for term in ('oversubscription', 'staging', 'Maximum Recent Execution Time', '15% over batching', 'hard deadline'))
    assert (2/5)*10 == 4 and (3/5)*10 == 6
    print('DARIS walkthrough: capacity limits, staged priority, proportional virtual deadlines, and soft-evidence boundaries passed; results not reproduced.')
    camdn = next(paper for paper in PAPERS if paper['id'] == 'camdn-2025')
    camdn_text = ' '.join(p for block in camdn['blocks'] for p in block['paragraphs'])
    assert camdn['route'] == 'dac-2025'
    assert all(term in camdn_text for term in ('cache contention', 'NPU-controlled', 'mapping candidates', 'dynamic cache allocation', 'not a measurement from a fabricated CaMDN chip'))
    assert (0.5 + 4) == 4.5
    print('CaMDN walkthrough: reuse distance, explicit cache ownership, candidate mappings, fallback allocation, and evidence boundaries passed; results not reproduced.')
    tropical = next(paper for paper in PAPERS if paper['id'] == 'tropical-2025')
    tropical_text = ' '.join(p for block in tropical['blocks'] for p in block['paragraphs'])
    assert tropical['route'] == 'dac-2025'
    assert all(term in tropical_text for term in ('TTFT', 'TPOT', 'slack', 'SLO-aware multiplexing', 'joint'))
    assert (5-3) == 2 and 1.5 + 0.25 + 0.25 == 2
    print('Tropical walkthrough: phase-specific latency, queue/interference tradeoff, slack budgeting, joint SLO attainment, and evidence boundaries passed; results not reproduced.')
    versaslot = next(paper for paper in PAPERS if paper['id'] == 'versaslot-2025')
    versaslot_text = ' '.join(p for block in versaslot['blocks'] for p in block['paragraphs'])
    assert versaslot['route'] == 'dac-2025'
    assert all(term in versaslot_text for term in ('partial reconfiguration', 'Big slot', 'Little slots', 'dual-core scheduling', 'live migration'))
    assert 4 + 5 == 9 and 4 + 5 + 4 == 13
    print('VersaSlot walkthrough: reconfiguration contention, heterogeneous slots, dependency-safe overlap, migration break-even, and evidence boundaries passed; results not reproduced.')
    dips = next(paper for paper in PAPERS if paper['id'] == 'di-ps-2026')
    assert dips['route'] == 'nsdi-2026'
    assert '1.27–4.67×' in ' '.join(p for block in dips['blocks'] for p in block['paragraphs'])
    assert '1.00–1.60×' in ' '.join(p for block in dips['blocks'] for p in block['paragraphs'])
    assert 'not interchangeable measurements' in ' '.join(p for block in dips['blocks'] for p in block['paragraphs'])
    assert 'not a numerical claim about Di-PS' in dips['exercise']['answer']
    assert 7-3 == 4
    print('Di-PS walkthrough: synchronous wait arithmetic, separate baselines, and production overhead denominators passed; paper results not reproduced.')
    oaken = next(paper for paper in PAPERS if paper['id'] == 'oaken-2025')
    oaken_text = ' '.join(p for block in oaken['blocks'] for p in block['paragraphs'])
    assert oaken['route'] == 'isca-2025'
    assert '1.79× over vLLM and 1.58× over QServe' in oaken_text
    assert '0.87% below the original FP16 baseline' in oaken_text
    assert 'not a measurement from fabricated Oaken silicon' in oaken_text
    assert (23-8)*1000 == 15000
    print('Oaken walkthrough: sparse-record arithmetic, distinct accuracy/throughput baselines, and simulation-versus-silicon evidence passed; results not reproduced.')
    pimba = next(paper for paper in PAPERS if paper['id'] == 'pimba-2025')
    pimba_text = ' '.join(p for block in pimba['blocks'] for p in block['paragraphs'])
    assert pimba['route'] == 'micro-2025'
    assert '4.1× the generation throughput' in pimba_text and '2.1× that' in pimba_text
    assert 'timing-and-event simulator' in pimba_text and 'not measurements from a manufactured Pimba memory device' in pimba_text
    assert 'underutilization' in pimba_text and 'sub-batch interleaving' in pimba_text
    assert F(9, 10)*10 + 1 == 10
    assert F(1, 2)*(-4) + 3 == 1
    assert 10 + 2*1 == 12 and 11 + 2*(-1) == 9
    print('Pimba walkthrough: sequential state-update arithmetic, separate throughput/evidence boundaries, and utilization limit passed; results not reproduced.')

    original = [8, 2, 2, 2]
    pieces = [2] * 7
    workers = [0] * 4
    for piece in pieces:
        workers[workers.index(min(workers))] += piece
    assert sum(original) == sum(pieces)
    assert max(original) == 8 and max(workers) == 4
    assert F('0.5') + max(workers) + 1 == F('5.5')
    assert 1 + max(workers) + F('3.5') == F('8.5')
    sum_a, weight_a = 1 * 2 + 3 * 6, 1 + 3
    sum_b, weight_b = 2 * 10 + 4 * 4, 2 + 4
    assert F(sum_a, weight_a) == 5 and F(sum_b, weight_b) == 6
    assert F(sum_a + sum_b, weight_a + weight_b) == F('5.6')
    assert F(3 * 2 + 9 * 8, 2 + 8) == F('7.8')
    flashinfer = next(paper for paper in PAPERS if paper['id'] == 'flashinfer-2025')
    evaluation_text = ' '.join(
        paragraph for block in flashinfer['blocks']
        for paragraph in block['paragraphs']
    )
    assert all(anchor in evaluation_text for anchor in (
        '21.7 to 13.5 ms', '29.6 to 9.1 ms',
        '48.3 to 24.0 ms', '30.7 to 21.8 ms',
        '99th-percentile time to the first output below 200 ms',
        'not as a comparison at one fixed arrival rate',
    )), 'FlashInfer reported result anchors or load boundary changed'
    published_values = [(F('21.7'), F('13.5')), (F('29.6'), F('9.1')),
                        (F('48.3'), F('24.0')), (F('30.7'), F('21.8'))]
    reductions = [round(float(100 * (old - new) / old))
                  for old, new in published_values]
    assert reductions == [38, 69, 50, 29]
    print('FlashInfer walkthrough: teaching arithmetic and four source-checked median ITL comparisons passed; paper results not reproduced.')
    def pipeline(stages, count):
        available = [F(0)] * len(stages)
        completed = []
        for _ in range(count):
            ready = F(0)
            for index, duration in enumerate(stages):
                ready = max(ready, available[index]) + duration
                available[index] = ready
            completed.append(ready)
        return completed
    assert pipeline([4, 1, 4], 3) == [9, 13, 17]
    assert pipeline([8], 3) == [8, 16, 24]
    assert pipeline([4, 6, 4], 3) == [14, 20, 26]
    assert pipeline([4, 9, 4], 3) == [17, 26, 35]
    for startup in (3, 8):
        backlog = startup * (100 - 80)
        assert startup + F(backlog, 120 - 100) == 2 * startup
    partial_backlog = 3 * (100 - 80) + 5 * (100 - 90)
    assert partial_backlog == 110
    assert 8 + F(partial_backlog, 120 - 100) == F('13.5')
    blitzscale = next(paper for paper in PAPERS if paper['id'] == 'blitzscale-2025')
    blitzscale_text = ' '.join(
        paragraph for block in blitzscale['blocks']
        for paragraph in block['paragraphs']
    )
    assert all(anchor in blitzscale_text for anchor in (
        '72-billion-parameter model in cluster A',
        'mean time to first token 75.5% shorter than ServerlessLLM',
        '21.1% shorter than its always-host-cached variant',
        'time between later tokens as 7.4% and 5.1% shorter',
        'one-second windows',
        'not a 75.5% reduction in every request’s delay or in tail latency',
    )), 'BlitzScale reported result anchors or evaluation boundary changed'
    print('BlitzScale walkthrough: toy schedule arithmetic and source-checked latency results passed; paper results not reproduced.')
    qserve = next(paper for paper in PAPERS if paper['id'] == 'qserve-2025')
    qserve_text = ' '.join(
        paragraph for block in qserve['blocks']
        for paragraph in block['paragraphs']
    )
    assert all(anchor in qserve_text for anchor in (
        'W4A8KV4', '20–90% runtime overhead',
        'best-performing TensorRT-LLM configuration',
        '1.2× for Llama-3-8B on A100', '3.5× for Qwen1.5-72B on L40S',
        'not a promise that each request has lower delay',
        'not a proof that every task, prompt, or downstream use is unaffected',
    )), 'QServe source result, quality, or workload boundary changed'
    assert F(80 + 20) == 100
    assert F(40 + 65 + 20) == 125
    assert F(40 + 30 + 20) == 90
    assert max(40, 30) + 20 == 60
    print('QServe walkthrough: toy movement/conversion arithmetic and source-bounded throughput and quality claims passed; paper results not reproduced.')
    sola = next(paper for paper in PAPERS if paper['id'] == 'sola-2025')
    sola_text = ' '.join(
        paragraph for block in sola['blocks']
        for paragraph in block['paragraphs']
    )
    assert all(anchor in sola_text for anchor in (
        'Time-to-first-token (TTFT)', 'Time-per-output-token (TPOT)',
        'SOLA calls the share of requests meeting the configured latency limits SLO attainment',
        'The paper reports that, averaged over its tested settings',
        '1.08–1.27 times', '1.04–1.11 times', '0.40–0.45%',
        '4.6-request-per-second arrival rate',
        '65% with vLLM’s default strategy to 98% with SOLA',
        'not universal',
    )), 'SOLA scheduling objective, source results, or evaluation boundary changed'
    meets = lambda pairs: sum(1 for ttft, tpot in pairs if ttft <= 4 and tpot <= F('0.8'))
    initial_pairs = [(F('2.0'), F('1.0')), (F('3.5'), F('0.7')), (F('4.2'), F('0.6'))]
    adjusted_pairs = [(F('2.4'), F('0.75')), (F('3.8'), F('0.7')), (F('4.2'), F('0.6'))]
    assert meets(initial_pairs) == 1 and meets(adjusted_pairs) == 2
    print('SOLA walkthrough: dual-latency SLO example and source-bounded goodput, attainment, and overhead claims passed; paper results not reproduced.')
    milo = next(paper for paper in PAPERS if paper['id'] == 'milo-2025')
    milo_text = ' '.join(
        paragraph for block in milo['blocks']
        for paragraph in block['paragraphs']
    )
    assert milo['route'] == 'mlsys-2025'
    assert all(anchor in milo_text for anchor in (
        'Mixtral-8×7B perplexity from 3.42 in FP16 to 4.81',
        'W ≈ Q⁻¹(Wq) + UV', 'higher kurtosis',
        'three-iteration sliding average', 'twenty iterations',
        'INT3-by-FP16 matrix-multiplication kernel',
        'one NVIDIA A100 with 40 GB of VRAM',
        '0.102, 0.112, and 0.113 seconds',
        'not a general speedup for every MoE or GPU',
    )), 'MiLo quantization, kernel, evaluation, or evidence boundary changed'
    assert F(8, 16) == F(1, 2)
    assert 'not a MiLo measurement' in milo['exercise']['answer']
    print('MiLo walkthrough: quantization-quality tradeoff, low-rank correction, fused-kernel boundary, and A100 results passed; paper results not reproduced.')
    mirage = next(paper for paper in PAPERS if paper['id'] == 'mirage-2025')
    mirage_text = ' '.join(
        paragraph for block in mirage['blocks']
        for paragraph in block['paragraphs']
    )
    assert mirage['route'] == 'osdi-2025'
    assert all(anchor in mirage_text for anchor in (
        'hierarchical µGraph', 'abstract expressions to prune',
        'probability bound on accepting a non-equivalent candidate',
        'does not support some operators such as ReLU',
        '500 ms of search and compilation', '100 requests',
        'up to 3.3× improvement',
        'not a performance measurement',
    )), 'Mirage graph, verification, break-even, or evaluation boundary changed'
    assert 500 // (12 - 7) == 100
    assert 'not a Mirage measurement' in mirage['exercise']['answer']
    print('Mirage walkthrough: multi-level graph, equivalence boundary, preparation break-even, and GPU results passed; paper results not reproduced.')
    tigon = next(paper for paper in PAPERS if paper['id'] == 'tigon-2025')
    tigon_text = ' '.join(
        paragraph for block in tigon['blocks']
        for paragraph in block['paragraphs']
    )
    assert tigon['route'] == 'osdi-2025'
    assert all(anchor in tigon_text for anchor in (
        'cross-host active tuples, or CAT', '39,000 tuples or 7 MB',
        '214–394 ns versus 111–117 ns', '18–52 GB/s versus 218–246 GB/s',
        'fail-stop failures', 'eight virtual machines',
        'up to 2.5× higher throughput', 'up to 18.5× over an RDMA-based',
        'not a measurement from an eight-host physical CXL pod',
    )), 'Tigon CAT, memory boundary, emulation, or evaluation claims changed'
    assert 3 + 5*4 == 23 and 5*12 == 60
    assert 'original teaching model' in tigon['exercise']['answer']
    print('Tigon walkthrough: CAT placement, CXL cost limits, transaction boundary, and emulated-pod results passed; paper results not reproduced.')
    hydra = next(paper for paper in PAPERS if paper['id'] == 'hydraserve-2026')
    hydra_text = ' '.join(
        paragraph for block in hydra['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + hydra['exercise']['answer']
    assert hydra['route'] == 'nsdi-2026'
    assert all(anchor in hydra_text for anchor in (
        'Time-to-first-token (TTFT)', 'Time per output token (TPOT)',
        'pipeline workers', 'key–value cache', 'shared-link contention',
        '1.7×–4.7×', '1.43×–1.74×',
        'not HydraServe measurements',
    )), 'HydraServe cold-start stages, placement, or evaluation boundary changed'
    assert 100 / 20 == 5 and 25 / 20 == 1.25 and 1.25 + 0.4 + 1 == 2.65
    assert 'original teaching numbers' in hydra['exercise']['answer']
    print('HydraServe walkthrough: cold-start stages, overlap, placement, consolidation, and SLO results passed; paper results not reproduced.')
    dynamo = next(paper for paper in PAPERS if paper['id'] == 'dynamollm-2025')
    dynamo_text = ' '.join(
        paragraph for block in dynamo['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + dynamo['exercise']['answer']
    assert dynamo['route'] == 'hpca-2025'
    assert all(anchor in dynamo_text for anchor in (
        'Prefill processes the input prompt in parallel',
        'Decode produces output tokens one at a time',
        '52% lower energy',
        '38% lower operational carbon emissions',
        '61% lower customer cost',
        'above 98%',
        'hierarchically',
        'reconfiguration',
        'not a DynamoLLM measurement',
    )), 'DynamoLLM phase, profile, control, or evaluation boundary changed'
    assert 400 * 2 == 800 and 250 * 4 == 1000
    assert 'original teaching model' in dynamo['exercise']['answer']
    print('DynamoLLM walkthrough: phase-specific SLOs, energy accounting, reconfiguration, and cluster evidence passed; paper results not reproduced.')
    vq = next(paper for paper in PAPERS if paper['id'] == 'vq-llm-2025')
    vq_text = ' '.join(
        paragraph for block in vq['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + vq['exercise']['answer']
    assert vq['route'] == 'hpca-2025'
    assert all(anchor in vq_text for anchor in (
        'Vector quantization stores a short index',
        'thread-local registers',
        'bank conflicts',
        'codebook-centric dataflow',
        'hierarchical fusion',
        '46.13% latency reduction',
        'batch size is 16',
        'not a VQ-LLM measurement',
    )), 'VQ-LLM representation, placement, fusion, or evaluation boundary changed'
    assert 120 + 48 == 168 and 120 + 12 + 20 == 152 and 120 + 12 + 60 == 192
    assert 'original teaching model' in vq['exercise']['answer']
    print('VQ-LLM walkthrough: representation, codebook placement, traffic-aware fusion, and end-to-end evidence passed; paper results not reproduced.')
    exion = next(paper for paper in PAPERS if paper['id'] == 'exion-2025')
    exion_text = ' '.join(
        paragraph for block in exion['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + exion['exercise']['answer']
    assert exion['route'] == 'hpca-2025'
    assert all(anchor in exion_text for anchor in (
        'inter-iteration output sparsity',
        'intra-iteration output sparsity',
        'FFN-Reuse',
        'ConMerge',
        'cycle-level simulator',
        '3.2–379.3×',
        '45.1–3067.6×',
        'not EXION measurements',
    )), 'EXION sparsity, compaction, evaluation, or evidence boundary changed'
    assert 10 * 100 + 40 * 35 + 50 * 15 == 3150
    assert 'original teaching numbers' in exion['exercise']['answer']
    print('EXION walkthrough: safe reuse, sparse-output compaction, quality boundary, and simulator evidence passed; paper results not reproduced.')
    iris = next(paper for paper in PAPERS if paper['id'] == 'iris-2025')
    iris_text = ' '.join(
        paragraph for block in iris['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + iris['exercise']['answer']
    assert iris['route'] == 'hpca-2025'
    assert all(anchor in iris_text for anchor in (
        'edge density',
        'motion',
        'mixed-resolution tokenizer',
        'ORB-SLAM3',
        '22.8% lower average latency',
        '37.5% lower average latency',
        'software-only saliency',
        'not IRIS measurements',
    )), 'IRIS saliency, backend, task, or evidence boundary changed'
    assert 0.60 * 0.25 * 8 + 0.40 * 8 == 4.4 and 12 - 5 == 7
    assert 'original teaching numbers' in iris['exercise']['answer']
    print('IRIS walkthrough: saliency co-design, mixed-resolution consumers, task boundaries, and measured-versus-modeled evidence passed; paper results not reproduced.')
    choco = next(paper for paper in PAPERS if paper['id'] == 'choco-q-2025')
    choco_text = ' '.join(
        paragraph for block in choco['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + choco['exercise']['answer']
    assert choco['route'] == 'hpca-2025'
    assert all(anchor in choco_text for anchor in (
        'in-constraints rate',
        'success rate',
        'commute Hamiltonian',
        'Hamiltonian serialization',
        'equivalent decomposition',
        'Variable elimination',
        '235×',
        '4.69× end-to-end acceleration',
        'not Choco-Q measurements',
    )), 'Choco-Q correctness, compilation, evaluation, or evidence boundary changed'
    assert 98 / 100 == 0.98 and 20 / 100 == 0.2 and 2 * 520 == 1040
    assert 'original teaching calculations' in choco['exercise']['answer']
    print('Choco-Q walkthrough: legality versus optimality, hard constraints, circuit tradeoffs, and NISQ evidence passed; paper results not reproduced.')
    mve = next(paper for paper in PAPERS if paper['id'] == 'mve-2025')
    mve_text = ' '.join(
        paragraph for block in mve['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + mve['exercise']['answer']
    assert mve['route'] == 'hpca-2025'
    assert all(anchor in mve_text for anchor in (
        'multidimensional logical register',
        'multidimensional strided loads',
        'random-base loads',
        'dimension-level masks',
        'dirty cache lines',
        '44 data-parallel kernels',
        '2.9× performance improvement',
        '8.8× energy reduction',
        'not MVE measurements',
    )), 'MVE shape, movement, transition, or evidence boundary changed'
    assert 2 * 4 == 8 and 3 * 4 - 7 == 5 and 3 * 4 - 9 == 3
    assert 'original teaching numbers' in mve['exercise']['answer']
    print('MVE walkthrough: multidimensional ISA, movement and masks, cache transitions, and measured-versus-modeled evidence passed; paper results not reproduced.')
    teola = next(paper for paper in PAPERS if paper['id'] == 'teola-2025')
    teola_text = ' '.join(
        paragraph for block in teola['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + teola['exercise']['answer']
    assert teola['route'] == 'asplos-2025'
    assert all(anchor in teola_text for anchor in (
        'primitive operations',
        'dataflow graph',
        'graph optimizer',
        'topology-aware batching',
        '2.09× lower end-to-end latency',
        '1.3–3%',
        '3.1–6.2%',
        'not Teola measurements',
    )), 'Teola graph, scheduling, evaluation, or evidence boundary changed'
    assert max(20, 40) + 80 == 120
    assert 'original teaching calculations' in teola['exercise']['answer']
    print('Teola walkthrough: whole-application critical paths, graph optimization, topology-aware batching, and end-to-end evidence passed; paper results not reproduced.')
    ciphermatch = next(paper for paper in PAPERS if paper['id'] == 'ciphermatch-2025')
    ciphermatch_text = ' '.join(
        paragraph for block in ciphermatch['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + ciphermatch['exercise']['answer']
    assert ciphermatch['route'] == 'asplos-2025'
    assert all(anchor in ciphermatch_text for anchor in (
        'Homomorphic encryption',
        'homomorphic multiplication and rotation',
        'homomorphic addition',
        'inside NAND flash',
        'bit-serial adder',
        '20.7×–62.2×',
        '76.6×–216.0×',
        '250.1×–295.1×',
        'not CIPHERMATCH measurements',
    )), 'CIPHERMATCH representation, near-data, evaluation, or evidence boundary changed'
    assert 128 / 8 + 4 == 20 and 40 / 8 + 2 + 1 == 8
    assert 'original teaching model' in ciphermatch['exercise']['answer']
    print('CIPHERMATCH walkthrough: encrypted representation, addition-only matching, in-flash processing, and modeled-versus-measured evidence passed; paper results not reproduced.')
    vattention = next(paper for paper in PAPERS if paper['id'] == 'vattention-2025')
    vattention_text = ' '.join(
        paragraph for block in vattention['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + vattention['exercise']['answer']
    assert vattention['route'] == 'asplos-2025'
    assert all(anchor in vattention_text for anchor in (
        'KV cache',
        'physical memory',
        'virtual address space',
        'PagedAttention',
        'contiguous virtual address range',
        '1.99×, 1.58×, and 1.53×',
        '42%, 28%, and 29%',
        'not vAttention measurements',
    )), 'vAttention memory-layout, kernel, evaluation, or evidence boundary changed'
    assert 3 * 30 <= 100 and 4 * 30 > 100 and 18 + 22 + 26 + 30 == 96
    assert 'original teaching calculations' in vattention['exercise']['answer']
    print('vAttention walkthrough: KV-cache growth, virtual/physical separation, kernel compatibility, and phase-specific evidence passed; paper results not reproduced.')
    comet = next(paper for paper in PAPERS if paper['id'] == 'comet-2025')
    comet_text = ' '.join(
        paragraph for block in comet['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + comet['exercise']['answer']
    assert comet['route'] == 'asplos-2025'
    assert all(anchor in comet_text for anchor in (
        '4 bits',
        '8 bits',
        'outliers',
        'mixed-precision representation',
        'W4A4 and W4A8',
        'streaming multiprocessors',
        '2.88×',
        '2.02×',
        'not COMET measurements',
    )), 'COMET precision, layout, scheduling, evaluation, or evidence boundary changed'
    assert (80 * 4 + 20 * 8) / 8 == 60 and 100 * 8 / 8 == 100
    assert 'original teaching calculations' in comet['exercise']['answer']
    print('COMET walkthrough: outlier-aware precision, mixed-format layout, GPU scheduling, and quality-versus-throughput evidence passed; paper results not reproduced.')
    micro_blossom = next(paper for paper in PAPERS if paper['id'] == 'micro-blossom-2025')
    micro_blossom_text = ' '.join(
        paragraph for block in micro_blossom['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + micro_blossom['exercise']['answer']
    assert micro_blossom['route'] == 'asplos-2025'
    assert all(anchor in micro_blossom_text for anchor in (
        'exact',
        'CPU',
        'FPGA',
        'dual phase',
        'isolated conflicts',
        'stream decoder',
        '0.8 microseconds',
        '8× shorter',
        'not Micro Blossom measurements',
    )), 'Micro Blossom partition, interaction, stream, or evidence boundary changed'
    assert 100 / 50 + 900 / 50 == 20 and 100 / 50 + 2 + 900 / 300 + 2 == 9
    assert 'original teaching calculations' in micro_blossom['exercise']['answer']
    print('Micro Blossom walkthrough: exactness, CPU/FPGA partitioning, local conflict handling, stream decoding, and prototype evidence passed; paper results not reproduced.')
    pipellm = next(paper for paper in PAPERS if paper['id'] == 'pipellm-2025')
    pipellm_text = ' '.join(
        paragraph for block in pipellm['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + pipellm['exercise']['answer']
    assert pipellm['route'] == 'asplos-2025'
    assert all(anchor in pipellm_text for anchor in (
        'confidential GPU enclave',
        'initialization vector',
        'speculative encryption',
        'validation',
        'no-op padding',
        'decryption asynchronous',
        'below 19.6%',
        '5.2%–14.2%',
        'not PipeLLM measurements',
    )), 'PipeLLM pipeline, ordered-state, recovery, evaluation, or evidence boundary changed'
    assert 6 + 4 + 3 * max(6, 4) == 28 and 4 * (6 + 4) == 40
    assert 'original teaching calculations' in pipellm['exercise']['answer']
    print('PipeLLM walkthrough: confidential transfer, ordered-IV speculation, recovery, bandwidth, and end-to-end evidence passed; paper results not reproduced.')
    partir = next(paper for paper in PAPERS if paper['id'] == 'partir-2025')
    partir_text = ' '.join(
        paragraph for block in partir['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + partir['exercise']['answer']
    assert partir['route'] == 'asplos-2025'
    assert all(anchor in partir_text for anchor in (
        'intermediate representation',
        'tactics',
        'AllGather',
        'AllReduce',
        'ReduceScatter',
        'AllToAll',
        '58.5% versus 58.3%',
        '14% of overall XLA compilation time',
        'not PartIR measurements',
    )), 'PartIR representation, tactic, collective, evaluation, or evidence boundary changed'
    assert 4 + 5 + 3 == 12 and 7 + 3 == 10
    assert 'original teaching calculations' in partir['exercise']['answer']
    print('PartIR walkthrough: separate sharding intent, incremental rewrites, collective costs, and compiler/runtime evidence passed; paper results not reproduced.')
    tapas = next(paper for paper in PAPERS if paper['id'] == 'tapas-2025')
    tapas_text = ' '.join(
        paragraph for block in tapas['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + tapas['exercise']['answer']
    assert tapas['route'] == 'asplos-2025'
    assert all(anchor in tapas_text for anchor in (
        'temperature',
        'power',
        'prefill',
        'decode',
        'placement',
        'routing',
        'reconfiguration',
        '17%',
        '23%',
        '97% fewer thermal-throttling events',
        'not TAPAS measurements',
    )), 'TAPAS thermal, control, multi-tenant, evaluation, or evidence boundary changed'
    assert 70 + 20 <= 100 and 90 + 20 > 100 and 82 + 8 + 7 == 97
    assert 'original teaching calculations' in tapas['exercise']['answer']
    print('TAPAS walkthrough: phase-aware thermal/power control, placement, routing, reconfiguration, and cluster evidence passed; paper results not reproduced.')
    pccheck = next(paper for paper in PAPERS if paper['id'] == 'pccheck-2025')
    pccheck_text = ' '.join(
        paragraph for block in pccheck['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + pccheck['exercise']['answer']
    assert pccheck['route'] == 'asplos-2025'
    assert all(anchor in pccheck_text for anchor in (
        'goodput',
        'copy-on-write snapshots',
        'multiple checkpoints',
        'pipelined',
        'coherent',
        'A100-40GB',
        'every 10 training iterations',
        '3% training-throughput overhead',
        '2.86× higher goodput',
        'not PCcheck measurements',
    )), 'PCcheck interval, pipeline, consistency, evaluation, or evidence boundary changed'
    assert 3 * (6 + 8) == 42 and 6 + 8 + 2 * max(6, 8) == 30
    assert 'original teaching calculations' in pccheck['exercise']['answer']
    print('PCcheck walkthrough: checkpoint interval, concurrent persistence, consistency, goodput, and recovery evidence passed; paper results not reproduced.')
    cascade = next(paper for paper in PAPERS if paper['id'] == 'cascade-2025')
    cascade_text = ' '.join(
        paragraph for block in cascade['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + cascade['exercise']['answer']
    assert cascade['route'] == 'asplos-2025'
    assert all(anchor in cascade_text for anchor in (
        'temporal graph',
        'node memories',
        'topology-aware scheduler',
        'stabilized',
        'memory freshness',
        '1.3×–5.1×',
        '2.3× on average',
        '99.4% of the baseline',
        'not Cascade measurements',
    )), 'Cascade dependency, freshness, evaluation, or evidence boundary changed'
    assert 2 * 1 == 2 and 8 / 2 == 4
    assert 'original teaching calculations' in cascade['exercise']['answer']
    print('Cascade walkthrough: temporal dependencies, topology-aware batching, stabilized memories, accuracy, and evaluation evidence passed; paper results not reproduced.')
    mint = next(paper for paper in PAPERS if paper['id'] == 'mint-2025')
    mint_text = ' '.join(
        paragraph for block in mint['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + mint['exercise']['answer']
    assert mint['route'] == 'asplos-2025'
    assert all(anchor in mint_text for anchor in (
        'distributed trace',
        'common structure',
        'variable fields',
        'all-request trace collection',
        'agent that generates the trace',
        '2.7%',
        '4.2%',
        '0.21%',
        'not Mint measurements',
    )), 'Mint coverage, representation, overhead, evaluation, or evidence boundary changed'
    assert 100 + 1000 * 12 == 12100 and 110000 - 12100 == 97900
    assert 'original teaching calculations' in mint['exercise']['answer']
    print('Mint walkthrough: full trace coverage, common/variable representation, agent-side cost, query fidelity, and evidence boundaries passed; paper results not reproduced.')
    powermove = next(paper for paper in PAPERS if paper['id'] == 'powermove-2025')
    powermove_text = ' '.join(
        paragraph for block in powermove['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + powermove['exercise']['answer']
    assert powermove['route'] == 'asplos-2025'
    assert all(anchor in powermove_text for anchor in (
        'Neutral-atom quantum computers',
        'move qubits',
        'computation and storage zones',
        'Stage 1',
        'collective-move scheduler',
        'fidelity',
        '1.71×–3.46×',
        '213.55×',
        'not PowerMove measurements',
    )), 'PowerMove movement, scheduling, fidelity, evaluation, or evidence boundary changed'
    assert round(0.99 * 0.98 * 0.995, 3) == 0.965 and round(0.99 * 0.995 * 0.999, 3) == 0.984
    assert 'original teaching calculations' in powermove['exercise']['answer']
    print('PowerMove walkthrough: movement-aware compilation, zone scheduling, fidelity, and separate evaluation boundaries passed; paper results not reproduced.')
    pushtap = next(paper for paper in PAPERS if paper['id'] == 'pushtap-2025')
    pushtap_text = ' '.join(
        paragraph for block in pushtap['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + pushtap['exercise']['answer']
    assert pushtap['route'] == 'asplos-2025'
    assert all(anchor in pushtap_text for anchor in (
        'interleaved direction', 'processing unit inside one device accesses locally', 'same stored values',
        'rotates the column-to-device assignment', 'main data region', 'delta region',
        'snapshot', 'memory-controller support', '3.4×',
        'OLAP (online analytical processing)', '4.4×',
        'OLTP (online transaction processing)', 'throughput',
        'not measurements from this course',
    )), 'PUSHtap layout, update, controller, evaluation, or evidence boundary changed'
    assert 6*1 + 2*4 == 14 and 8 + 6*2 + 2*1 == 22
    assert 'original teaching calculations' in pushtap['exercise']['answer']
    print('PUSHtap walkthrough: dual access directions, balanced layout, snapshot visibility, controller coordination, and evidence boundaries passed; paper results not reproduced.')
    coserve = next(paper for paper in PAPERS if paper['id'] == 'coserve-2025')
    coserve_text = ' '.join(
        paragraph for block in coserve['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + coserve['exercise']['answer']
    assert coserve['route'] == 'asplos-2025'
    assert all(anchor in coserve_text for anchor in (
        'known before execution', 'Mixture-of-Experts', 'groups requests',
        'queue window', 'dependency information', 'offline probabilities',
        'CPU/GPU allocation', '4.5×–12× higher throughput',
        '93.87% reduction', 'not CoServe measurements',
    )), 'CoServe dependency, scheduling, eviction, evaluation, or evidence boundary changed'
    assert 5 + 1 + 1 + 5 + 1 == 13 and 5 + 1 + 5 + 1 + 5 + 1 == 18
    assert 'original teaching calculations' in coserve['exercise']['answer']
    print('CoServe walkthrough: predictable expert routes, grouping, eviction, profiling, service metrics, and evidence boundaries passed; paper results not reproduced.')
    dvfs = next(paper for paper in PAPERS if paper['id'] == 'fine-dvfs-2025')
    dvfs_text = ' '.join(
        paragraph for block in dvfs['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + dvfs['exercise']['answer']
    assert dvfs['route'] == 'asplos-2025'
    assert all(anchor in dvfs_text for anchor in (
        'operator the decision unit', 'performance-loss target',
        'power and timing behavior', 'average power is not the same thing as total energy',
        '11.29 seconds', '11.47 seconds', '2,823 J', '2,709 J',
        'not separately reported by the paper', 'not measurements from the fine-grained DVFS paper',
    )), 'Fine-grained DVFS operator, budget, energy, evaluation, or evidence boundary changed'
    assert (84 - 80) / 80 == 0.05 and 250 * 0.080 == 20 and 230 * 0.084 == 19.32
    assert 'original teaching calculations' in dvfs['exercise']['answer']
    print('Fine-grained DVFS walkthrough: operator budgets, power-versus-energy arithmetic, platform scope, and evidence boundaries passed; paper results not reproduced.')
    btrace = next(paper for paper in PAPERS if paper['id'] == 'btrace-2025')
    btrace_text = ' '.join(
        paragraph for block in btrace['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + btrace['exercise']['answer']
    assert btrace['route'] == 'asplos-2025'
    assert all(anchor in btrace_text for anchor in (
        'per-core buffers', 'global buffer', 'event completeness',
        'recording latency', 'zero loss', 'behavior during resize',
        '0.00% loss', '53 ns geometric-mean recording latency',
        '10.8 MB geometric-mean latest continuous fragment',
        'not BTrace measurements',
    )), 'BTrace buffer, completeness, resizing, evaluation, or evidence boundary changed'
    assert 10 + 8 + 8 + 10 == 36 and 40 - 36 == 4
    assert 'original teaching calculations' in btrace['exercise']['answer']
    print('BTrace walkthrough: shared buffer utilization, completeness/latency separation, resize safety, and evidence boundaries passed; paper results not reproduced.')
    picsou = next(paper for paper in PAPERS if paper['id'] == 'picsou-2025')
    picsou_text = ' '.join(
        paragraph for block in picsou['blocks']
        for paragraph in block['paragraphs']
    )
    assert all(anchor in picsou_text for anchor in (
        'Cross-Cluster Consistent Broadcast',
        'at least one correct replica in the receiving group eventually receives it',
        'It is not the stronger claim that every receiving replica has committed the change',
        'QUACK is a cumulative quorum acknowledgment',
        'If the destination has not yet committed and applied change 17',
        'up to 45 Google Cloud nodes',
        '3.2× over traditional all-to-all broadcast',
        'up to 24× for a 19-node network',
        '2× performance over Kafka',
        'known high-latency Kafka consumer issue',
        'not establish behavior under arbitrary network partitions',
    )), 'Picsou delivery guarantee, evaluation comparison, or evidence boundary changed'
    picsou_exercise = picsou['exercise']['answer']
    assert 'cannot infer that the destination group has committed U' in picsou_exercise
    assert 'client read is required to expose U' in picsou_exercise
    print('Picsou walkthrough: delivery/commit boundary and source-bounded failure and performance claims passed; paper results not reproduced.')
    pmverify = next(paper for paper in PAPERS if paper['id'] == 'pmverify-2025')
    pmverify_text = ' '.join(
        paragraph for block in pmverify['blocks']
        for paragraph in block['paragraphs']
    )
    assert all(anchor in pmverify_text for anchor in (
        'a=1 and then b=1', 'a=0,b=1',
        'If a crash exposes a state that ordinary execution cannot reach',
        'A “robust” verdict requires exhaustive exploration',
        'reports one robust case, 12 robustness violations, and 13 cases the tool could not settle',
        'not estimates of how often arbitrary persistent-memory software fails',
        'The 13 unknown cases are neither safe nor confirmed violations',
    )), 'PMVerify property, verdict categories, or scope boundary changed'
    ordinary_states = {(0, 0), (1, 1)}
    crash_state = (0, 1)
    assert crash_state not in ordinary_states
    assert 'did not settle the case' in pmverify['exercise']['answer']
    assert 'Even a robust program could leave (1,0)' in pmverify['exercise']['answer']
    print('PMVerify walkthrough: crash-state reachability, unknown verdict, and model-scope distinctions passed; paper results not reproduced.')
    exist = next(paper for paper in PAPERS if paper['id'] == 'exist-2025')
    exist_text = ' '.join(
        paragraph for block in exist['blocks']
        for paragraph in block['paragraphs']
    )
    assert all(anchor in exist_text for anchor in (
        '5–10% time overhead', 'worst cases around 18%',
        'from roughly one per scheduling event to roughly one per processor core',
        '90.2% average accuracy', '62.2%',
        '83.7%, 82.6%, and 86.2%',
        'These figures are not directly comparable',
        '0.4% to 1.5%', '1.1% average tracing overhead',
        '2.2% increase in cycles per instruction', '1–3% end-to-end delay',
        'worst-case EXIST overhead can be higher',
    )), 'EXIST efficiency, trace-quality metrics, or evidence boundary changed'
    assert 'CPU use and tail response time are different quantities' in exist['exercise']['answer']
    exist_sources = [href for block in exist['blocks'] for href, _ in block.get('sources', [])]
    exist_pdf = 'https://cs.sjtu.edu.cn/~lichao/publications/EXIST_Enabling_ASPLOS-2025-Wang.pdf'
    exist_doi = 'https://doi.org/10.1145/3676641.3716283'
    assert any(href.startswith(exist_pdf) for href in exist_sources) and exist_doi in exist_sources
    assert 'wang-xinkai.github.io/files/xinkai-asplos2025.pdf' not in exist_sources
    print('EXIST walkthrough: observer overhead, distinct trace-accuracy measures, and whole-request limits passed; paper results not reproduced.')
    afaas = next(paper for paper in PAPERS if paper['id'] == 'afaas-2025')
    afaas_text = ' '.join(paragraph for block in afaas['blocks'] for paragraph in block['paragraphs'])
    assert all(anchor in afaas_text for anchor in (
        'control-path work, resource contention, and user-code initialization',
        'CataOnly', 'CataOPT1', 'CataOPT2', 'AFaaS',
        '24-core Xeon Platinum 8163 server with 512 GB',
        '1.80×–8.14× end-to-end speedup', '5.45–9.41 ms startup latency',
        'peer-call responses mocked', 'not a universal serverless guarantee',
    )), 'AFaaS cost breakdown, staged comparison, production results, or evidence boundary changed'
    assert 'about 1.43×' in afaas['exercise']['answer'] and 'about 1.09×' in afaas['exercise']['answer']
    print('AFaaS walkthrough: three-part cost model, cumulative baselines, production comparison limits, and teaching-model arithmetic passed; paper results not reproduced.')
    emt = next(paper for paper in PAPERS if paper['id'] == 'emt-2025')
    emt_text = ' '.join(paragraph for block in emt['blocks'] for paragraph in block['paragraphs'])
    assert all(anchor in emt_text for anchor in (
        'virtual addresses', 'physical addresses', 'architecture-neutral objects',
        'all 1,208 Linux Test Project checks', '99.9% of the result from Linux without EMT',
        'QEMU itself does not model the exact timing of every processor cycle', 'ECPT reduced total cycles by 2.3%',
        'FPT configuration reduced running-phase total cycles by 6.4%',
        'not measurements on fabricated ECPT or FPT hardware',
    )), 'EMT translation boundary, evaluation evidence, or hardware claim limit changed'
    assert 'about 0.96×' in emt['exercise']['answer']
    print('EMT walkthrough: interface boundary, correctness/overhead evidence, simulation-versus-silicon distinction, and cost model passed; paper results not reproduced.')
    photon = next(paper for paper in PAPERS if paper['id'] == 'photon-2025')
    photon_text = ' '.join(paragraph for block in photon['blocks'] for paragraph in block['paragraphs']) + ' ' + photon['exercise']['answer']
    assert all(anchor in photon_text for anchor in (
        'several local updates before it exchanges model changes',
        'Fewer conversations change the learning process',
        'not by itself a proof that the updates reveal nothing',
        'small batches at each site with high learning rates',
        '95.6 hours for Photon and 147.9 hours for centralized training',
        '10 Gbps connection and Ring-AllReduce',
        'not an independently reproduced result or universal speedup',
    )), 'Photon communication/optimization mechanism or evaluation boundary changed'
    assert 'about 35.4%' in photon['exercise']['answer']
    assert F(1479 - 956, 1479) == F(523, 1479)
    print('Photon walkthrough: local-update tradeoff, separate quality/latency evidence, stated network conditions, and time-reduction arithmetic passed; results not reproduced.')
    past_future = next(paper for paper in PAPERS if paper['id'] == 'past-future-2025')
    past_future_text = ' '.join(paragraph for block in past_future['blocks'] for paragraph in block['paragraphs']) + ' ' + past_future['scope']
    assert all(anchor in past_future_text for anchor in (
        'key–value cache, or KV cache', 'Current free memory answers only the first question',
        'recently completed requests', 'highest predicted memory demand over that timeline',
        'up to two to three times the goodput', 'versions from December 2023',
        'not reconciled every passage with the ACM camera-ready copy',
    )), 'Past-Future memory-prediction mechanism, goodput evidence, baseline boundary, or source-version note changed'
    assert 'the peak is 104' in past_future['exercise']['answer']
    print('Past-Future walkthrough: future-peak admission, service-level goodput, temporal-shift and baseline limits, and timeline arithmetic passed; results not reproduced.')
    def cycles(addresses, banks):
        return max(Counter(a % banks for a in addresses).values(), default=0)
    assert cycles([0, 4, 8, 1, 5, 2, 6, 3], 4) == 3
    for stride, expected in [(1, 1), (2, 2), (4, 4)]:
        assert cycles([stride*i for i in range(4)], 4) == expected
    assert cycles([0, 4, 8, 12], 8) == 2
    assert cycles([0, 4, 8, 12], 16) == 1
    assert cycles([0, 5, 10, 15], 4) == 1
    assert cycles([0, 6, 12, 18], 4) == 2
    assert cycles([0, 6, 12, 18], 8) == 1
    assert 12 + 4 == 4*4 and 12 + 5 < 4*5
    assert 15 == 3*5 and 15 < 3*6
    assert F(20-16, 16) == F(1, 4)
    assert F(8, 200_000_000) == F(40, 1_000_000_000)
    assert F(6, 100_000_000) == F(60, 1_000_000_000)
    print('Banked-memory walkthrough: bank counts, layout break-even, and clock conversion passed.')
    fifo_mean = F(8 + (10 - 1), 2)
    assert fifo_mean == F('8.5')
    for h, expected in [(F(0), F(6)), (F('0.5'), F('6.75')), (F(1), F('7.5')), (F(2), F(9))]:
        short_completion = 1 + h + 2
        long_completion = short_completion + h + 7
        assert F(short_completion - 1 + long_completion, 2) == expected
        assert expected == 6 + F(3, 2)*h
    assert 6 + F(3, 2)*F(5, 3) == fifo_mean
    assert F(8_000_000, 8_000_000_000) == F(1, 1000)
    assert 12//4 == 3
    print('FastServe walkthrough: completion times, switching break-even, and transfer units passed.')
    for values in ((3, 5), (2, 7)):
        table = {(a, b): a*values[0]+b*values[1] for a in (0, 1) for b in (0, 1)}
        for w0 in range(4):
            for w1 in range(4):
                via_table = table[(w0 & 1, w1 & 1)] + 2*table[(w0 >> 1, w1 >> 1)]
                assert via_table == w0*values[0]+w1*values[1]
        for b0 in (0, 1):
            for b1 in (0, 1):
                signed = (2*b0-1)*values[0]+(2*b1-1)*values[1]
                assert F(signed+sum(values), 2) == table[(b0, b1)]
    assert 2**4*2 == 32 and 2**8*2 == 512
    assert 12+4 == 4*4 and 12+5 < 4*5
    assert 15+2*5 == 5*5 and 15+2*6 < 5*6
    assert 8*F('0.01') == F('0.08')
    print('LUT walkthrough: all two-bit weight pairs, signed correction, table sizes, and timing arithmetic passed.')
    disagreement_counts = [0, 4, 2]
    assert [i+1 for i, count in enumerate(disagreement_counts) if count >= 4] == [2]
    assert all(value == 1 for value in [1]*5)
    assert all(value != 0 for value in [1]*5)
    assert 3+2+4+2 == 11
    assert F(76+12, 100) == F('0.88')
    assert F(8, 76+8) == F(2, 21)
    assert F(8, 20) == F('0.4')
    assert F(95+60, 200) == F('0.775')
    assert F(40, 95+40) == F(8, 27)
    assert F(76, 80) == F(95, 100)
    assert F(12, 20) == F(60, 100)
    print('CorrectBench walkthrough: toy disagreement, stopping cost, and classification denominators passed. Paper results not reproduced.')
    sat = next(paper for paper in PAPERS if paper['id'] == 'sat-sampling-2025')
    sat_text = ' '.join(
        paragraph for block in sat['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + sat['exercise']['answer']
    assert sat['route'] == 'date-2025'
    assert all(anchor in sat_text for anchor in (
        'satisfying assignment', 'unique valid solutions generated per second',
        'GPU', 'not a guarantee', '33.6× to 523.6×',
        '0.99^100 ≈ 36.6%', 'not measurements from the paper',
    )), 'SAT sampling validity, throughput, diversity, or evidence boundary changed'
    assert 60 / 0.012 == 5000 and 80 / 0.020 == 4000
    assert 150 / 0.025 == 6000 and 180 / 0.040 == 4500
    assert 'original teaching calculations' in sat['exercise']['answer']
    print('SAT-sampling walkthrough: validity versus uniqueness, probabilistic search, unique-valid throughput, uniformity boundary, and evidence checks passed; paper results not reproduced.')
    pulse = next(paper for paper in PAPERS if paper['id'] == 'pulse-bit-2025')
    pulse_text = ' '.join(
        paragraph for block in pulse['blocks']
        for paragraph in block['paragraphs']
    ) + ' ' + pulse['exercise']['answer']
    assert pulse['route'] == 'vlsid-2025'
    assert all(anchor in pulse_text for anchor in (
        'quantum processor', 'Floating-point storage', 'Total Variation Distance',
        'approaching 200%', 'invalid pulses', 'interpolation',
        'physical fault rate', 'not a pulse-bit paper measurement',
    )), 'Pulse-bit representation, TVD, simulator, or evidence boundary changed'
    assert round((abs(0.75 - 0.55) + abs(0.25 - 0.45)) / 2, 6) == 0.2
    assert 'original teaching calculation' in pulse['exercise']['answer']
    print('Pulse-bit walkthrough: representation-sensitive faults, output-distribution distance, simulator boundary, detector assumptions, and evidence limits passed; paper results not reproduced.')
    assert 3*16 == 48
    assert F(100, 1) == 100 and F(70, F('0.5')) == 140
    assert 100+20 <= 125 < 100+40
    assert 10+2 == 12 and 7+2 == 9
    print('LEGO walkthrough: exercise storage, clock conversion, and fusion arithmetic passed. Paper results not reproduced.')


if __name__ == '__main__':
    main()
