#!/usr/bin/env python3
"""Audit the written conference routes without pretending heuristics prove quality."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from course_routes import ROUTES
from course_subtheme_notes import SUBTHEME_NOTES
from course_comparisons import COMPARISONS
from course_paper_qserve import QSERVE
from course_paper_sola import SOLA
from course_paper_picsou import PICSOU
from course_paper_pmverify import PMVERIFY
from course_orientation import render_orientation
from course_capstone import render_capstone
from course_papers import PAPERS
from course_paper_trrip import TRRIP
from course_paper_timefloats import TIMEFLOATS
from course_paper_oaken import OAKEN
from course_paper_lut import LUT
from course_paper_pimba import PIMBA
from course_glossary import GLOSSARY
from html.parser import HTMLParser


class DetailParser(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.details = []
        self.current = None
        self.in_detail = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and 'subtheme-detail' in attrs.get('class', '').split():
            self.in_detail = True
            self.current = {'text': '', 'links': 0}
        elif self.in_detail and tag == 'a':
            self.current['links'] += 1

    def handle_data(self, data):
        if self.in_detail:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_detail:
            self.details.append(self.current)
            self.current = None
            self.in_detail = False


FAILURE_MARKERS = (
    'fail', 'miss', 'los', 'cannot', 'does not', 'not enough', 'only if',
    'depends', 'limit', 'overhead', 'invalid', 'wrong', 'uncertain',
)

# These phrases add praise without telling a reader what changed, how it works,
# or what the evidence establishes. This is a deliberately small guardrail:
# passing it does not prove that prose is clear or free of jargon.
EMPTY_PROMOTION = (
    'cutting-edge', 'game-changing', 'game changing', 'seamless',
    'revolutionary', 'paradigm shift', 'holistic solution', 'leveraging',
    'utilizing',
)

# These are recurring teaching phrases that sound evaluative but do not name
# the result, evidence, or condition. This list is intentionally phrase-level;
# technical uses of words such as "useful" elsewhere are not rejected.
VAGUE_TEACHING_PHRASES = (
    'important idea', 'important limit', 'useful measurement',
    'useful review', 'useful explanation', 'useful follow-up',
    'useful capacity', 'useful fact', 'useful question', 'useful evidence',
    'useful result', 'useful service', 'obvious response',
)

REQUIRED_PLAIN_LANGUAGE_DEFINITIONS = (
    'AICore, its AI calculation cores',
    'HBM (high-bandwidth memory)',
    'AICPU (the processor that handles supporting control work)',
    'SoC, the complete system-on-chip',
    'MWPM)—pairing detected errors while minimizing total correction cost',
    'PEFT (parameter-efficient fine-tuning)',
    'RDMA, or remote direct memory access',
    'GQA (grouped-query attention)',
    'LoRA (low-rank adaptation)',
    'deep-neural-network (DNN)',
    'TPC-C transaction, from a standard database transaction benchmark',
    'YCSB variant, a key-value-store workload',
    'NISQ (noisy intermediate-scale quantum)',
    'acousto-optic deflectors (AODs)',
    'hybrid transactional/analytical processing (HTAP)',
    'multi-version concurrency control (MVCC)',
    'OLAP (online analytical processing)',
    'OLTP (online transaction processing)',
    'processing-in-memory (PIM)',
    'QAOA (quantum approximate optimization algorithm)',
    'ORB-SLAM3, a visual-tracking and mapping system',
    'RTL (register-transfer-level) synthesis',
)


def audit_theme(route_id, number, theme):
    worked = ' '.join(theme.get('worked_example', []))
    practice = theme.get('practice', {})
    combined = ' '.join((theme.get('body', ''), worked,
                         practice.get('answer', ''), theme.get('reading', ''))).lower()
    flags = []
    if not theme.get('body', '').strip():
        flags.append('missing explanation')
    if len(theme.get('worked_example', [])) < 2:
        flags.append('fewer than two worked paragraphs')
    if len(combined) < 900:
        flags.append('short combined teaching text')
    if not any(marker in combined for marker in FAILURE_MARKERS):
        flags.append('no obvious failure/limit marker; read manually')
    if not practice.get('question') or not practice.get('answer'):
        flags.append('missing explained practice')
    if not theme.get('reading', '').strip():
        flags.append('missing evidence/reading boundary')
    for sub_number, (title, explanation) in enumerate(theme.get('subthemes', []), 1):
        if not explanation.strip():
            flags.append(f'subtheme {sub_number} has no explanation')
        # A subtheme is currently a definition entry, not a full mini-lesson.
        if len(explanation.split()) < 12:
            flags.append(f'subtheme {sub_number} definition is short')
    return flags


def main():
    flagged = 0
    total = 0
    subthemes = 0
    print('Conference route editorial audit (heuristic triage; manual review remains required)')
    generated_course = (ROOT / 'course.html').read_text().lower()
    promoted = [phrase for phrase in EMPTY_PROMOTION if phrase in generated_course]
    assert not promoted, (
        'Generated course contains empty promotional phrasing: ' + ', '.join(promoted)
    )
    print('Generated course contains none of the checked empty promotional phrases.')
    vague = [phrase for phrase in VAGUE_TEACHING_PHRASES if phrase in generated_course]
    assert not vague, (
        'Generated course contains vague teaching phrases: ' + ', '.join(vague)
    )
    print('Generated course contains none of the checked vague teaching phrases.')
    missing_definitions = [
        phrase for phrase in REQUIRED_PLAIN_LANGUAGE_DEFINITIONS
        if phrase.lower() not in generated_course
    ]
    assert not missing_definitions, (
        'Generated course lost required plain-language definitions: '
        + ', '.join(missing_definitions)
    )
    print('Required first-use hardware definitions remain present.')
    for route in ROUTES:
        for number, theme in enumerate(route['themes'], 1):
            total += 1
            subthemes += len(theme.get('subthemes', []))
            flags = audit_theme(route['id'], number, theme)
            if flags:
                flagged += 1
                print(f'- {route["id"]} theme {number}: ' + '; '.join(flags))
    print(f'Checked {total} themes and {subthemes} subthemes; {flagged} themes need manual review.')
    route_index = {route['id']: route for route in ROUTES}
    osdi_memory = route_index['osdi-2025']['themes'][1]
    osdi_memory_text = ' '.join(osdi_memory.get('worked_example', []))
    tiered_memory_pdf = 'https://www.usenix.org/system/files/osdi25-liu.pdf#page=3'
    assert all(term in osdi_memory_text for term in (
        '13.6 times as often', '52.4% of the all-fast setup',
        'controlled test', 'not every workload or tiered-memory system',
    )), 'OSDI placement example lost its source-grounded access-frequency comparison'
    assert any(href == tiered_memory_pdf for href, _ in route_index['osdi-2025']['sources'])
    assert tiered_memory_pdf in (ROOT / 'course.html').read_text(), 'Generated course missing Tiered Memory citation'
    emt_paper = 'https://www.usenix.org/conference/osdi25/presentation/chai-siyuan'
    assert all(term in osdi_memory['reading'] for term in (
        'Add EMT', 'without rewriting its general memory code',
        'Faster address translation is not the same claim as faster access to stored data',
        'not fabricated hardware',
    )), 'OSDI memory reading path conflated translation and data placement or lost the simulation boundary'
    assert any(href == emt_paper for href, _ in route_index['osdi-2025']['sources'])
    assert emt_paper in (ROOT / 'course.html').read_text(), 'Generated course missing EMT primary-source link'
    print('OSDI memory-placement example retains the source-backed hotness comparison and scope boundary.')
    mlsys_training = route_index['mlsys-2025']['themes'][4]
    photon_pdf = 'https://proceedings.mlsys.org/paper_files/paper/2025/file/185087ea328b4f03ea8fd0c8aa96f747-Paper-Conference.pdf'
    assert all(term in mlsys_training['reading'] for term in (
        'Use the Photon walkthrough', 'coordinating model updates is not the same as selecting examples',
        'preparing inputs, or storing federated metadata',
    )), 'MLSys training route does not distinguish model coordination from data pipeline work'
    assert any(href == photon_pdf for href, _ in route_index['mlsys-2025']['sources'])
    assert photon_pdf in (ROOT / 'course.html').read_text(), 'Generated course missing Photon primary source'
    mlsys_route_text = route_index['mlsys-2025']['status'] + ' ' + route_index['mlsys-2025']['evidence']
    assert all(term in mlsys_route_text for term in (
        'five focused walkthroughs (FlashInfer, QServe, SOLA, Photon, and MiLo)',
        '61 conference papers with extracted source text',
        '56 full-text entries and five additional text-bearing records',
        'Five papers—FlashInfer, QServe, SOLA, Photon, and MiLo—also have focused learner walkthroughs',
        'No measurements have been independently reproduced',
    )), 'MLSys route must state its five-walkthrough and source-count boundary'
    print('MLSys route notice distinguishes its five walkthroughs from the broader source inventory.')
    osdi_communication = route_index['osdi-2025']['themes'][2]
    osdi_communication_text = ' '.join(osdi_communication.get('worked_example', []))
    picsou_pdf = 'https://www.usenix.org/system/files/osdi25-frank.pdf'
    assert all(term in osdi_communication_text for term in (
        'at least one correct server', 'QUACK', 'not that the receiving service has committed',
    )), 'OSDI communication example blurred Picsou delivery and commit guarantees'
    assert any(href == picsou_pdf for href, _ in route_index['osdi-2025']['sources'])
    assert picsou_pdf in (ROOT / 'course.html').read_text(), 'Generated course missing Picsou primary source'
    print('OSDI communication example separates Picsou group delivery from destination commit and client-visible reads.')
    osdi_allocation = route_index['osdi-2025']['themes'][3]
    osdi_allocation_text = ' '.join(osdi_allocation.get('worked_example', []))
    allocation_sources = {
        'XSched': 'https://www.usenix.org/conference/osdi25/presentation/shen-weihang',
        'BlitzScale': 'https://www.usenix.org/conference/osdi25/presentation/zhang-dingyan',
    }
    assert all(term in osdi_allocation_text for term in (
        'safe unit to move', 'readiness visible', 'separate events',
    )), 'OSDI allocation example lost the distinction between movable work, readiness, and deadline'
    for paper, source_url in allocation_sources.items():
        assert any(href == source_url for href, _ in route_index['osdi-2025']['sources'])
        assert source_url in (ROOT / 'course.html').read_text(), f'Generated course missing {paper} source'
        assert paper in osdi_allocation_text, f'OSDI allocation example no longer explains {paper}'
    print('OSDI allocation example connects XSched and BlitzScale while distinguishing safe movement from readiness and service deadlines.')
    osdi_recovery = route_index['osdi-2025']['themes'][4]
    osdi_recovery_text = ' '.join(osdi_recovery.get('worked_example', []))
    wofs_source = 'https://www.usenix.org/conference/osdi25/presentation/pan'
    assert all(term in osdi_recovery_text for term in (
        'checksum', 'packages', 'states recovery may observe', 'mechanisms are not interchangeable',
    )), 'OSDI recovery example lost the contrast between ordered writes and WOFS metadata packages'
    assert any(href == wofs_source for href, _ in route_index['osdi-2025']['sources'])
    assert wofs_source in (ROOT / 'course.html').read_text(), 'Generated course missing WOFS primary source'
    print('OSDI recovery example distinguishes the teaching write-order protocol from WOFS metadata packages.')
    osdi_trust = route_index['osdi-2025']['themes'][5]
    osdi_trust_text = ' '.join(osdi_trust.get('worked_example', []))
    privacy_sources = {
        'Compass': 'https://www.usenix.org/conference/osdi25/presentation/zhu-jinhao',
        'Weave': 'https://www.usenix.org/conference/osdi25/presentation/soleimani',
    }
    assert all(term in osdi_trust_text for term in (
        'encrypting a record hides its contents', 'which stored pieces a query touches',
        'different workload', 'observer can see',
    )), 'OSDI trust example blurred encrypted contents and access-pattern privacy'
    for paper, source_url in privacy_sources.items():
        assert any(href == source_url for href, _ in route_index['osdi-2025']['sources'])
        assert source_url in (ROOT / 'course.html').read_text(), f'Generated course missing {paper} primary source'
        assert paper in osdi_trust_text, f'OSDI trust example no longer distinguishes {paper}'
    print('OSDI trust example distinguishes encrypted contents from access-pattern privacy across Compass and Weave.')
    osdi_measurement = route_index['osdi-2025']['themes'][6]
    osdi_measurement_text = ' '.join(osdi_measurement.get('worked_example', []))
    tintin_source = 'https://www.usenix.org/conference/osdi25/presentation/li'
    assert all(term in osdi_measurement_text for term in (
        'limited number of counter slots', 'different moments',
        'reports remaining uncertainty', 'change the decision',
    )), 'OSDI measurement example lost the limits of multiplexed counter evidence'
    assert any(href == tintin_source for href, _ in route_index['osdi-2025']['sources'])
    assert tintin_source in (ROOT / 'course.html').read_text(), 'Generated course missing Tintin primary source'
    print('OSDI measurement example distinguishes workload variation from uncertainty introduced by counter multiplexing.')
    osdi_total_cost = route_index['osdi-2025']['themes'][7]
    osdi_total_cost_text = ' '.join(osdi_total_cost.get('worked_example', []))
    fork_source = 'https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu'
    assert all(term in osdi_total_cost_text for term in (
        'control path', 'contention for resources', 'user-code initialization',
        'concurrency', 'readiness definition',
    )), 'OSDI end-to-end example lost the cold-start workflow and comparison boundaries'
    assert any(href == fork_source for href, _ in route_index['osdi-2025']['sources'])
    assert fork_source in (ROOT / 'course.html').read_text(), 'Generated course missing Fork in the Road primary source'
    print('OSDI whole-cost example ties its teaching timeline to production cold-start stages and aligned comparisons.')
    osdi_route_text = route_index['osdi-2025']['status'] + ' ' + route_index['osdi-2025']['evidence']
    assert all(term in osdi_route_text for term in (
        'local primary-source reviews', 'six named walkthroughs',
        'Other named papers are reading leads', 'not independently reproduced',
    )), 'OSDI route must distinguish focused source reviews from the remaining corpus'
    asplos_contract = route_index['asplos-2025']['themes'][0]
    asplos_contract_text = ' '.join(asplos_contract.get('worked_example', []))
    cxl_source = 'https://johnwickerson.github.io/papers/cxl_cache_ASPLOS25.pdf'
    assert all(term in asplos_contract_text for term in (
        'state-transition model', 'messages in flight', 'single-writer/multiple-reader',
        'two devices and one location', 'theorem remains about that model',
    )), 'ASPLOS interface theme lost the guarantee and model boundary from the CXL proof'
    assert any(href == cxl_source for href, _ in route_index['asplos-2025']['sources'])
    assert cxl_source in (ROOT / 'course.html').read_text(), 'Generated course missing CXL primary source'
    print('ASPLOS interface theme connects visible protocol state to the CXL proof’s guarantee and scope.')
    asplos_transform = route_index['asplos-2025']['themes'][1]
    asplos_transform_text = ' '.join(asplos_transform.get('worked_example', []))
    mvq_source = 'https://arxiv.org/abs/2412.10261'
    assert all(term in asplos_transform_text for term in (
        'not lossless compression', 'model accuracy', 'energy efficiency and array size',
        'A result on one axis cannot stand in for another',
    )), 'ASPLOS transformation theme lost the distinct answer-quality and hardware-cost obligations'
    assert any(href == mvq_source for href, _ in route_index['asplos-2025']['sources'])
    assert mvq_source in (ROOT / 'course.html').read_text(), 'Generated course missing MVQ primary source'
    print('ASPLOS transformation theme connects MVQ to separate accuracy and hardware-efficiency tests.')
    asplos_locality = route_index['asplos-2025']['themes'][2]
    asplos_locality_text = ' '.join(asplos_locality.get('worked_example', []))
    tlb_source = 'https://gvavou5.github.io/Documents/Vavouliotis_ASPLOS25.pdf'
    assert all(term in asplos_locality_text for term in (
        'iTP', 'extra page walks', 'xPTP', '18.9%', '11.4%',
        'not a claim that every kind of miss decreases',
    )), 'ASPLOS locality theme lost the cross-level cost and bounded performance evidence'
    assert any(href == tlb_source for href, _ in route_index['asplos-2025']['sources'])
    assert tlb_source in (ROOT / 'course.html').read_text(), 'Generated course missing TLB/cache primary source'
    print('ASPLOS locality theme explains the iTP/xPTP trade and bounds its reported workload results.')
    asplos_mapping = route_index['asplos-2025']['themes'][3]
    asplos_mapping_text = ' '.join(asplos_mapping.get('worked_example', []))
    cent_source = 'https://arxiv.org/abs/2502.07578'
    assert all(term in asplos_mapping_text for term in (
        '2.5 times the throughput in compute-heavy prompt processing',
        '2.5 times the throughput in memory-heavy token decoding',
        'increases time spent exchanging data across CXL',
        'not a universal ranking of GPUs',
    )), 'ASPLOS mapping theme lost CENT’s phase-specific and communication boundaries'
    assert any(href == cent_source for href, _ in route_index['asplos-2025']['sources'])
    assert cent_source in (ROOT / 'course.html').read_text(), 'Generated course missing CENT primary source'
    print('ASPLOS mapping theme distinguishes CENT’s compute-heavy and memory-heavy phases and communication costs.')
    asplos_coordination = route_index['asplos-2025']['themes'][4]
    asplos_coordination_text = ' '.join(asplos_coordination.get('worked_example', []))
    fsmoe_source = 'https://arxiv.org/abs/2501.10714'
    assert all(term in asplos_coordination_text for term in (
        'routing, data exchange between machines, coordination within each machine, and expert computation',
        'cuts a large gradient-reduction into pieces',
        '1.19×–3.01× speedups', 'up to 48 GPUs',
        'does not establish the same result on a much larger cluster',
    )), 'ASPLOS coordination theme lost FSMoE’s overlap mechanism or evaluation boundary'
    assert any(href == fsmoe_source for href, _ in route_index['asplos-2025']['sources'])
    assert fsmoe_source in (ROOT / 'course.html').read_text(), 'Generated course missing FSMoE primary source'
    print('ASPLOS coordination theme connects FSMoE overlap to dependencies and the evaluated cluster boundary.')
    asplos_resource_value = route_index['asplos-2025']['themes'][5]
    asplos_resource_text = ' '.join(asplos_resource_value.get('worked_example', []))
    cent_source = 'https://arxiv.org/abs/2502.07578'
    assert all(term in asplos_resource_text for term in (
        'throughput (tokens per second)', 'energy use for the compared runs',
        'total cost of ownership as tokens per dollar', '2.3× higher throughput',
        '2.9× less energy', '5.2× more tokens per dollar',
        'These are three different questions',
    )), 'ASPLOS resource-value theme blurred throughput, energy, and cost denominators'
    assert any(href == cent_source for href, _ in route_index['asplos-2025']['sources'])
    assert cent_source in (ROOT / 'course.html').read_text(), 'Generated course missing CENT primary source for resource metrics'
    print('ASPLOS resource-value theme distinguishes CENT throughput, energy, and total-cost measures.')
    asplos_safety = route_index['asplos-2025']['themes'][6]
    asplos_safety_text = ' '.join(asplos_safety.get('worked_example', []))
    pmverify_source = 'https://feihe.github.io/materials/asplos25.pdf'
    assert all(term in asplos_safety_text for term in (
        '26 PMDK benchmark programs', 'one robust case, 12 robustness violations, and 13 cases',
        '‘Unknown’ is unresolved, not a softer form of ‘safe.’',
        'Nor does 12 out of 26 estimate how often arbitrary real programs fail',
    )), 'ASPLOS safety theme lost PMVerify’s unknown and benchmark-scope distinctions'
    assert any(href == pmverify_source for href, _ in route_index['asplos-2025']['sources'])
    assert pmverify_source in (ROOT / 'course.html').read_text(), 'Generated course missing PMVerify primary source'
    print('ASPLOS safety theme distinguishes PMVerify’s verified, violating, and unresolved benchmark cases from population risk.')
    asplos_end_to_end = route_index['asplos-2025']['themes'][7]
    asplos_end_to_end_text = ' '.join(asplos_end_to_end.get('worked_example', []))
    past_future_source = 'https://doi.org/10.1145/3676641.3716011'
    assert all(term in asplos_end_to_end_text for term in (
        'Past-Future applies a related idea to admission rather than worker activation',
        'requests that meet the paper’s response-time limits',
        'output-length mix changes abruptly or while the service is warming up',
        'up to 2–3× higher goodput',
        'not a universal multiplier or an independent reproduction',
    )), 'ASPLOS end-to-end theme lost Past-Future’s mechanism, objective, or evidence boundary'
    assert any(href == past_future_source for href, _ in route_index['asplos-2025']['sources'])
    assert past_future_source in (ROOT / 'course.html').read_text(), 'Generated course missing Past-Future primary source'
    print('ASPLOS end-to-end theme links re-evaluation after workload changes to Past-Future admission, SLA goodput, and evidence limits.')
    success_comparison = next(item for item in COMPARISONS if item['id'] == 'compare-what-counts-as-success')
    success_text = ' '.join(success_comparison['paragraphs']) + ' ' + success_comparison['answer']
    assert all(term in success_text for term in (
        'What was counted:', 'What had to happen for one to pass?',
        'QServe', 'SOLA', 'Picsou', 'PMVerify',
        'two results for each request', 'two observed percentages alone do not justify',
        '84 pass both checks',
    )), 'Cross-conference success comparison blurred distinct properties or verdicts'

    qserve_text = ' '.join(' '.join(block['paragraphs']) for block in QSERVE['blocks'])
    assert all(term in qserve_text for term in (
        'one scale for each output channel', 'packs smaller groups', 'rebuilds the codes as eight-bit integers',
        'Weights are values learned during training', 'Activations are intermediate results',
        'safe range', 'not stored in the four-bit cache',
    )), 'QServe must explain its two-step representation and the location of the key adjustment'
    sola_text = ' '.join(' '.join(block['paragraphs']) for block in SOLA['blocks'])
    assert all(term in sola_text for term in (
        'largest incoming request rate', 'still meets both limits',
        'not simply output tokens per second',
    )), 'SOLA must define its paper-specific goodput measure rather than treating it as generic throughput'
    picsou_text = ' '.join(' '.join(block['paragraphs']) for block in PICSOU['blocks'])
    assert all(term in picsou_text for term in (
        'integrity rule', 'only if the sending group transmitted it',
        'does not, by itself, promise an order across separate messages',
    )), 'Picsou must retain both its delivery/integrity distinction and its ordering boundary'
    pmverify_text = ' '.join(' '.join(block['paragraphs']) for block in PMVERIFY['blocks'])
    assert all(term in pmverify_text for term in (
        'most used PMDK operations its frontend did not model',
        'one supported program timed out',
    )), 'PMVerify must preserve the paper’s actual causes of its unresolved benchmark cases'
    orientation_html = render_orientation(lambda value: value)
    assert all(term in orientation_html for term in (
        'What connects the conferences?', '<strong>concept</strong>',
        '<strong>theme</strong>', '<strong>subtheme</strong>',
        'data moved, conversion work, and the result the user receives',
        'not official conference categories',
        'Carry the question between conferences, not the reported speedup',
    )), 'Course entry must explain its reading groups and the limits of cross-paper comparisons'
    assert all(term in orientation_html for term in (
        'Keep three kinds of statements apart', 'label a statement <strong>reported</strong>',
        '<strong>calculated</strong>', '<strong>proposed</strong>',
        'not evidence that the paper already supplied',
    )), 'Course entry point must distinguish paper evidence, reader arithmetic, and proposed tests'
    capstone_html = render_capstone(lambda value: value)
    assert all(term in capstone_html for term in (
        'When only an abstract is available', 'abstract-reported',
        'Label the third as <strong>unknown</strong>',
        'An abstract alone cannot support the full audit',
        'Do not turn a phrase such as “improves performance” into a speedup',
    )), 'Paper challenge must provide a bounded path for abstract-only records'
    flashinfer = next(paper for paper in PAPERS if paper['id'] == 'flashinfer-2025')
    flashinfer_text = ' '.join(' '.join(block['paragraphs']) for block in flashinfer['blocks'])
    assert all(term in flashinfer_text for term in (
        'makes an assignment table', 'recorded GPU command sequence',
        'same launch shape and buffer locations', 'reads a new plan',
        'not part of that recorded GPU sequence',
    )), 'FlashInfer must explain the changing plan versus the fixed CUDA Graph execution structure'
    blitzscale = next(paper for paper in PAPERS if paper['id'] == 'blitzscale-2025')
    blitzscale_text = ' '.join(' '.join(block['paragraphs']) for block in blitzscale['blocks'])
    assert all(term in blitzscale_text for term in (
        'one host-held copy per model', 'one extra host copy for every new serving instance',
        'several new instances', 'zero parameter bytes, zero network traffic, or instant startup',
    )), 'BlitzScale must explain O(1) caching as cache-copy growth, not an absence of transfer work'
    lut = next(paper for paper in PAPERS if paper['id'] == 'lut-tensor-core-2025')
    lut_text = ' '.join(' '.join(block['paragraphs']) for block in lut['blocks'])
    assert all(term in lut_text for term in (
        'separate earlier computation', 'scale and offset',
        'separate one-bit positions', 'multiple lookups and combination work',
        'one activation-dependent table serve more weight columns',
    )), 'LUT Tensor Core must turn its co-design labels into visible preparation, representation, and execution steps'
    dips = next(paper for paper in PAPERS if paper['id'] == 'di-ps-2026')
    dips_text = ' '.join(' '.join(block['paragraphs']) for block in dips['blocks'])
    assert all(term in dips_text for term in (
        'moving history of earlier sizes', 'threshold is excluded',
        'proportion to the amount of training data', 'combined change is clipped',
        'threshold and moving-average settings are choices',
        'two speed ranges use different baselines',
        'less than 6% overhead compared with single-cluster training',
        'about 6% of training time', 'not interchangeable measurements',
    )), 'Di-PS must expose its outlier, weighting, and clipping steps rather than treating correction as a black box'
    fastserve = next(paper for paper in PAPERS if paper['id'] == 'fastserve-2026')
    fastserve_text = ' '.join(' '.join(block['paragraphs']) for block in fastserve['blocks'])
    assert all(term in fastserve_text for term in (
        'first pass through a request is called prefill',
        'Later steps are decoding', 'saved keys and values',
        'output-token iteration boundaries', 'predicted first-iteration time',
        'drop intermediate activations', 'later recomputation',
        'time slice can accommodate that first iteration',
        'P95 latency', 'value below which 95% of the measured jobs fall',
    )), 'FastServe must distinguish a token boundary from an arbitrary mid-prefill interruption'
    nsdi_route_text = route_index['nsdi-2026']['status'] + ' ' + route_index['nsdi-2026']['evidence']
    assert all(term in nsdi_route_text for term in (
        'based on the final USENIX papers', 'inspect their final conference PDFs',
        'have not been independently reproduced',
        'do not turn the wider abstract-based synthesis into a paper-by-paper review',
    )), 'NSDI route must distinguish the focused PDF reviews from its wider synthesis'
    trrip_text = ' '.join(' '.join(block['paragraphs']) for block in TRRIP['blocks'])
    assert all(term in trrip_text for term in (
        'geometric mean combines per-workload time ratios', 'multiplying them and taking the matching root',
        'does not say that every workload became 3.9% faster',
    )), 'TRRIP must explain its aggregate speedup statistic rather than treating it as a universal workload result'
    glossary = {entry[0]: entry[2] for entry in GLOSSARY}
    assert all(key in glossary for key in ('constant-growth', 'cuda-graph', 'geometric-mean', 'goodput', 'quorum', 'service-level-objective')), \
        'Concept lookup must cover the course’s fixed-growth, GPU-recording, aggregate-ratio, accepted-work, group-acknowledgment, and service-promise terms'
    assert 'does not mean free' in glossary['constant-growth']
    assert 'fixed launch shapes' in glossary['cuda-graph']
    assert 'does not say every case had that result' in glossary['geometric-mean']
    assert 'acceptance rule' in glossary['goodput']
    assert 'what state survives failures' in glossary['quorum']
    assert 'does not always mean a majority' in glossary['quorum']
    assert 'share of requests' in glossary['service-level-objective']
    expected_walkthroughs = {
        'paper-qserve-2025', 'paper-sola-2025', 'paper-picsou-2025', 'paper-pmverify-2025',
    }
    assert expected_walkthroughs <= {href for href, label in success_comparison['links']}
    for anchor in expected_walkthroughs:
        assert f'#{anchor}' in (ROOT / 'course.html').read_text(), f'Generated course missing comparison link {anchor}'
    print('Cross-conference synthesis distinguishes answer quality, latency SLOs, message delivery, and crash robustness.')
    fccm = route_index['fccm-2025']
    fccm_reading = ' '.join(theme.get('reading', '') for theme in fccm['themes'])
    assert all(term in fccm_reading for term in (
        'rule for choosing its next waiting request',
        'matrix transpose swaps rows and columns',
        'An FFT is a staged calculation used in signal processing',
    )), 'FCCM route lost its plain-language explanation of arbitration or access patterns'
    print('FCCM route keeps the bank-choice and layout terms connected to actions a reader can count.')
    isscc = route_index['isscc-2025']
    isscc_text = ' '.join(
        theme.get('reading', '') + ' ' + ' '.join(theme.get('worked_example', []))
        for theme in isscc['themes']
    )
    assert all(term in isscc_text for term in (
        'two ways of relating image regions', 'trained mask',
        'stored yes/no choice learned during training',
        'stored lookup data used by its attention calculation',
    )), 'ISSCC route lost its distinction between learned pruning, attention, and exact storage reuse'
    print('ISSCC route keeps learned attention and pruning distinct from exact storage reuse.')
    convformer = next(paper for paper in PAPERS if paper['id'] == 'convformer-2025')
    convformer_text = ' '.join(' '.join(block['paragraphs']) for block in convformer['blocks'])
    assert all(term in convformer['scope'] + ' ' + convformer_text for term in (
        'three-page conference digest', 'Author-reported results were not reproduced',
        'fabricated 28 nm chip', 'not a measurement of every competing system',
        'trained factorization and mask preserve',
    )), 'ConvFormer must preserve the digest, fabricated-chip, and quality-evidence boundaries'
    print('ConvFormer walkthrough keeps digest, fabricated-chip, and answer-quality boundaries explicit.')
    timefloats_text = ' '.join(
        block_text
        for block in TIMEFLOATS['blocks']
        for block_text in block['paragraphs']
    )
    assert all(term in TIMEFLOATS['scope'] + ' ' + timefloats_text for term in (
        'August 2024 preprint', 'not a verified comparison with the final conference text',
        'Digital synthesis estimates', 'HSPICE is a detailed circuit simulator',
        'Table I lists digitization at 21 fJ',
        'section IV-B instead gives 2.421 pJ and 1.32 pJ',
        'These discrepancies remain unresolved here',
    )), 'TimeFloats must preserve its preprint scope and unresolved energy accounting'
    print('TimeFloats walkthrough preserves the preprint boundary and unresolved energy figures.')
    oaken_text = ' '.join(
        block_text
        for block in OAKEN['blocks']
        for block_text in block['paragraphs']
    )
    assert all(term in OAKEN['scope'] + ' ' + oaken_text for term in (
        'author-hosted final conference paper', 'have not been rerun',
        'not measurements of fabricated Oaken silicon',
        '1.58× throughput improvement over an NVIDIA A100',
        '1.79× over vLLM and 1.58× over QServe',
        '0.87% below the original FP16 baseline',
        '0.54% below KVQuant', '0.32% below KIVI',
    )), 'Oaken must preserve its baseline, quality, and modeled-hardware boundaries'
    print('Oaken walkthrough preserves its named baselines, quality references, and simulation boundary.')
    lut_text = ' '.join(
        block_text
        for block in LUT['blocks']
        for block_text in block['paragraphs']
    )
    assert all(term in LUT['scope'] + ' ' + lut_text for term in (
        'author manuscript arXiv:2408.06003v3',
        'Detailed implementation and accuracy review remain outside this focused walkthrough',
        'Accel-Sim', 'tile-based simulator',
        'not measurements of a manufactured LUT-equipped A100',
    )), 'LUT Tensor Core must preserve its source scope and separate simulator evidence'
    print('LUT Tensor Core walkthrough preserves its manuscript scope and distinct simulation stages.')
    trrip_text = ' '.join(
        block_text
        for block in TRRIP['blocks']
        for block_text in block['paragraphs']
    )
    assert all(term in TRRIP['scope'] + ' ' + trrip_text for term in (
        'author manuscript', 'Results are author-reported, not reproduced',
        'hot” is not physical temperature', 'does not permanently lock hot blocks',
        'Sniper', '400 million simulated instructions',
        '3.9% geometric-mean speedup over SRRIP',
        'not measurements of a manufactured TRRIP processor',
    )), 'TRRIP must preserve its prediction, simulation, and evidence boundaries'
    print('TRRIP walkthrough preserves the prediction-versus-reservation distinction and simulator boundary.')
    pimba_text = ' '.join(
        block_text
        for block in PIMBA['blocks']
        for block_text in block['paragraphs']
    )
    assert all(term in PIMBA['scope'] + ' ' + pimba_text for term in (
        'final MICRO paper', 'cycle-level simulation', 'RTL synthesis',
        'No Pimba DRAM device was fabricated or measured by this course',
        'up to 4.1× the generation throughput',
        'up to 2.1× that of a GPU-plus-PIM comparison system',
        'average gains of 1.9× and 1.4×', '2.2× lower energy',
        'Ramulator2', '40 HBM2E processing-in-memory modules',
        'MX8 with stochastic rounding',
    )), 'Pimba must preserve its baselines, quantization choice, and modeled-evidence boundary'
    print('Pimba walkthrough preserves its baseline denominators, MX8 choice, and simulation boundary.')
    micro_route_text = route_index['micro-2025']['status'] + ' ' + route_index['micro-2025']['evidence']
    assert all(term in micro_route_text for term in (
        'two full walkthroughs (TRRIP and Pimba)',
        'Twenty have extracted paper text',
        'two of those records also have full learner walkthroughs here',
        'The other 103 have only abstracts or titles',
        'Results remain author-reported',
    )), 'MICRO route must state the two-walkthrough and twenty-source-backed-record boundary'
    print('MICRO route notice distinguishes its two walkthroughs from the wider twenty-record source-backed synthesis.')
    isca_route_text = route_index['isca-2025']['status'] + ' ' + route_index['isca-2025']['evidence']
    assert all(term in isca_route_text for term in (
        'two full walkthroughs (LUT Tensor Core and Oaken)',
        'Fifteen other source-backed records',
        '17 papers with source text',
        'two of those records also have full learner walkthroughs here',
        'remaining 23 have no source text',
        'Paper results remain author-reported',
    )), 'ISCA route must state its two-walkthrough and bounded source inventory'
    print('ISCA route notice distinguishes its two walkthroughs from the wider source-backed inventory.')
    hpca_route_text = route_index['hpca-2025']['status'] + ' ' + route_index['hpca-2025']['evidence']
    assert all(term in hpca_route_text for term in (
        'seven full walkthroughs (LEGO, DynamoLLM, VQ-LLM, EXION, IRIS, Choco-Q, and MVE)',
        'all seven now have full learner walkthroughs here',
        'remaining 114 records are not equivalent evidence',
        'deliberately non-additive', 'overlap between groups',
        'No independent reproduction is claimed',
    )), 'HPCA route must state its non-additive inventory and seven-walkthrough boundary'
    print('HPCA route notice preserves the non-additive source inventory and seven-walkthrough boundary.')
    sc_route_text = route_index['sc-2025']['status'] + ' ' + route_index['sc-2025']['evidence']
    assert all(term in sc_route_text for term in (
        'one full walkthrough (cuSZ-Hi)', '119 with extracted paper text',
        'one of those records also has a full learner walkthrough here',
        'remaining 314 comprise 312 abstract-only records and two title-only records',
        'The examples below draw on the named reviews',
        'no independent reproduction',
    )), 'SC route must state its one-walkthrough and reconciled evidence inventory'
    print('SC route notice distinguishes the cuSZ-Hi walkthrough from its reconciled source inventory.')
    dac_route_text = route_index['dac-2025']['status'] + ' ' + route_index['dac-2025']['evidence']
    assert all(term in dac_route_text for term in (
        'five full walkthroughs (GSIM, DARIS, CaMDN, Tropical, and VersaSlot)', 'Twenty-seven other source-backed records',
        '32 locally extracted source-backed records',
        'five of those records now have full learner walkthroughs here',
        'remaining 424 are discovery-level records',
        'no cross-paper implementation or independent reproduction is claimed',
    )), 'DAC route must state its one-walkthrough and bounded source inventory'
    print('DAC route notice distinguishes the GSIM, DARIS, CaMDN, Tropical, and VersaSlot walkthroughs from the wider source-backed inventory.')
    date_route_text = route_index['date-2025']['status'] + ' ' + route_index['date-2025']['evidence']
    assert all(term in date_route_text for term in (
        'two full walkthroughs (CorrectBench and High-Throughput SAT Sampling)', 'Thirteen other source-backed records',
        '15 locally extracted source-backed records',
        'two of those records now have full learner walkthroughs here',
        'remaining 410 are discovery-level records',
        'no independent reproduction or composed cross-paper system is claimed',
    )), 'DATE route must state its two-walkthrough and bounded source inventory'
    print('DATE route notice distinguishes the CorrectBench and SAT-sampling walkthroughs from the wider source-backed inventory.')
    vlsid_route_text = route_index['vlsid-2025']['status'] + ' ' + route_index['vlsid-2025']['evidence']
    assert all(term in vlsid_route_text for term in (
        'two full walkthroughs (TimeFloats and the pulse-bit study)', 'One other locally reviewed paper',
        'three papers with locally extracted text',
        'two of those records now have full learner walkthroughs here',
        'other 95 records have only abstracts or titles',
    )), 'VLSID route must state its two-walkthrough and small-sample boundary'
    print('VLSID route notice distinguishes the TimeFloats and pulse-bit walkthroughs from the other reviewed papers and abstract/title sample.')
    isscc_route_text = route_index['isscc-2025']['status'] + ' ' + route_index['isscc-2025']['evidence']
    assert all(term in isscc_route_text for term in (
        'one full ConvFormer accelerator walkthrough', 'other 257 records remain discovery evidence',
        'one PDF with extracted text', 'which also has the full learner walkthrough here',
        'not independently reproduced',
    )), 'ISSCC route must state its one-walkthrough and discovery-only boundary'
    print('ISSCC route notice distinguishes ConvFormer from its discovery-only record population.')
    fccm_route_text = route_index['fccm-2025']['status'] + ' ' + route_index['fccm-2025']['evidence']
    assert all(term in fccm_route_text for term in (
        'one full Banked Memories walkthrough', 'externally inspected manuscript',
        '68 abstract-bearing metadata records', 'no locally validated PDFs',
        'one full learner walkthrough', 'not a retroactive change',
    )), 'FCCM route must preserve the external-manuscript and local-audit boundary'
    print('FCCM route notice distinguishes the externally inspected manuscript from local PDF coverage.')
    iccad_route_text = route_index['iccad-2025']['status'] + ' ' + route_index['iccad-2025']['evidence']
    assert all(term in iccad_route_text for term in (
        'One full RSizing walkthrough', 'not a full-conference synthesis',
        '281 structured-abstract records', 'no usable PDF URL',
        'one full learner walkthrough', 'not independently reproduced',
    )), 'ICCAD route must state its one-walkthrough and local-audit boundary'
    print('ICCAD route notice distinguishes RSizing from the structured-abstract discovery audit.')
    rendered_text = (ROOT / 'course.html').read_text()
    assert all(term in rendered_text for term in (
        'One scenario is one concrete input sequence together with the output observation the checker expects',
        'at least 70% of the candidates disagree on one scenario',
        'more than 25% of the candidates agree with the checker on every scenario',
        'not direct proof that the checker implements the natural-language requirement',
    )), 'CorrectBench walkthrough lost its concrete validator rule or its evidence limit'
    print('CorrectBench walkthrough keeps its concrete agreement rule and no-golden-design limitation.')
    assert all(term in rendered_text for term in (
        'compression-ratio mode (CR)', 'throughput mode (TP)',
        'not the permitted numerical difference set by the earlier conversion',
    )), 'cuSZ-Hi walkthrough lost the distinction between numerical error and lossless-pipeline choice'
    print('cuSZ-Hi walkthrough keeps numerical approximation separate from CR/TP byte-pipeline choice.')
    assert all(term in rendered_text for term in (
        'three levels', 'one shared “needs work” check',
        'wide signal changes only in bits that a later calculation does not read',
    )), 'GSIM walkthrough lost its distinct grouping, expression, and bit-dependency mechanisms'
    print('GSIM walkthrough keeps its three different sources of simulator-work reduction distinct.')
    gsim = next(paper for paper in PAPERS if paper['id'] == 'gsim-2025')
    gsim_text = ' '.join(' '.join(block['paragraphs']) for block in gsim['blocks'])
    assert all(term in gsim_text for term in (
        'GSIM and Verilator successfully simulate XiangShan',
        'ESSENT and Arcilator fail on some designs',
        'not chip-performance gains',
        'bounded to the tested designs and workloads',
    )), 'GSIM must keep simulator correctness, speed, and chip-performance claims separate'
    print('GSIM walkthrough keeps selected correctness results separate from simulator speed and chip claims.')
    assert all(term in rendered_text for term in (
        'learned mathematical stand-in for expensive circuit simulations',
        'does not turn a limited simulation sample into manufactured-chip evidence',
        'requested target, a model prediction, a sample estimate, and the unknown population value',
    )), 'RSizing walkthrough lost its distinction between search estimates, samples, and physical evidence'
    print('RSizing walkthrough keeps model prediction, sampled yield, and manufactured-chip evidence separate.')
    assert all(term in rendered_text for term in (
        'standard 16-bank configuration', 'address’s lowest four binary digits',
        'four-bank remainder rule in this walkthrough is therefore a teaching model',
    )), 'Banked Memories walkthrough blurred the paper mapping with its four-bank teaching model'
    print('Banked Memories walkthrough keeps its paper mapping distinct from the four-bank teaching rule.')
    assert all(term in rendered_text for term in (
        'starts when a server node receives a scaling request',
        'does not automatically include time before that scaling request',
        'client-to-scheduler delay',
    )), 'AFaaS walkthrough broadened the paper’s end-to-end timer without naming the omitted path'
    print('AFaaS walkthrough keeps the paper’s node-scaling-request timing boundary explicit.')
    assert all(term in rendered_text for term in (
        'no predicted overflow', 'neither a reservation of future GPU memory',
        'nor a guarantee of a request’s eventual length',
        'evictions and missed service limits remain outcomes to measure',
    )), 'Past-Future walkthrough presented predicted memory as a physical reservation or guarantee'
    print('Past-Future walkthrough keeps future-memory prediction distinct from a reservation or guarantee.')
    for (route_id, theme_number, subtheme_number), detail in SUBTHEME_NOTES.items():
        route = route_index[route_id]
        assert 1 <= theme_number <= len(route['themes'])
        assert 1 <= subtheme_number <= len(route['themes'][theme_number - 1]['subthemes'])
        assert all(detail.get(key, '').strip() for key in ('example', 'failure', 'evidence', 'source'))
    nsdi_sources = {
        (8, 1): ('PrvTel', 'https://www.usenix.org/system/files/nsdi26-zhou-yajie.pdf'),
        (8, 2): ('Wallet', 'https://www.usenix.org/system/files/nsdi26-sabanic.pdf'),
        (8, 3): ('private-set-intersection', 'https://www.usenix.org/system/files/nsdi26-arpaci.pdf'),
        (10, 1): ('CCEval', 'https://www.usenix.org/system/files/nsdi26-liu-tianfeng.pdf'),
        (10, 2): ('Slowpoke', 'https://www.usenix.org/system/files/nsdi26-xie.pdf'),
        (10, 3): ('CCEval', 'https://www.usenix.org/system/files/nsdi26-liu-tianfeng.pdf'),
    }
    for (theme_number, subtheme_number), (source_name, source_url) in nsdi_sources.items():
        detail = SUBTHEME_NOTES[('nsdi-2026', theme_number, subtheme_number)]
        assert detail['source'] == source_url, f'Wrong NSDI primary source for theme {theme_number}.{subtheme_number}'
        assert source_name.lower() in detail['evidence'].lower(), f'Evidence note does not identify {source_name}'
        assert source_url in (ROOT / 'course.html').read_text(), f'Generated course missing {source_name} citation'
    print(f'NSDI privacy/prediction examples point to {len(set(url for _, url in nsdi_sources.values()))} topic-relevant primary papers, not only the FastServe walkthrough.')
    print(f'Explicit subtheme notes: {len(SUBTHEME_NOTES)}; each has an application, failure boundary, evidence boundary, and source link.')
    rendered = DetailParser(rendered_text)
    assert len(rendered.details) == len(SUBTHEME_NOTES), 'Generated page lost authored subtheme blocks'
    assert all(item['links'] == 1 for item in rendered.details), 'A subtheme block lacks its source link'
    assert all('Apply it' in item['text'] and 'Where it fails:' in item['text'] and
               'Evidence boundary:' in item['text'] for item in rendered.details), 'Incomplete rendered subtheme block'
    print(f'Generated HTML contains {len(rendered.details)}/{len(SUBTHEME_NOTES)} complete subtheme blocks.')
    print('A clean result would still not prove source accuracy, conceptual depth, or that each subtheme has its own example and failure case.')


if __name__ == '__main__':
    main()
