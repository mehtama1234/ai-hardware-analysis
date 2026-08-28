#!/usr/bin/env python3
"""Build learner-facing first-principles pages for the AI hardware corpus."""

from __future__ import annotations

import collections
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "analysis" / "explorer_data.json").read_text())
PER_PAPER = ROOT / "analysis" / "per-paper"


TOPICS = [
    {
        "slug": "movement",
        "title": "Data movement is the main cost",
        "tags": ["memory-system", "near-data-processing", "dataflow"],
        "venues": ["ASPLOS", "ISCA", "HPCA", "MICRO"],
        "body": [
            "A chip does not only compute. It has to carry numbers from one place to another. In modern AI systems that trip often costs more than the arithmetic. This is the simplest reason the corpus keeps returning to caches, memory layout, storage paths, chiplet links, network links, and direct device-to-device transfer.",
            "The naive fix is to add more arithmetic units. That helps only when the arithmetic units were the scarce thing. If the machine is waiting for weights, activations, graph neighbors, database rows, or checkpoint data, extra multiply units wait too. The real question becomes: which data can stay close, which data can be reused, and which trip can be removed entirely?",
            "This is why a DPU-to-GPU storage path, a key-value SSD, a GPU graph engine, a processing-in-memory array, and a tensor compiler can all belong to the same idea. They reduce wasted travel. They differ only in the scale where the travel happens.",
        ],
        "check": "Does the paper prove that fewer bytes actually cross the scarce boundary, or only that a local operation is faster?",
    },
    {
        "slug": "kv-cache",
        "title": "The context window becomes a memory system",
        "tags": ["inference-serving", "scheduling", "memory-system", "cache"],
        "venues": ["ASPLOS", "MLSys", "MICRO", "HPCA"],
        "body": [
            "A language model conversation is not just text. During serving it becomes a growing store of intermediate vectors. The system must keep these vectors available because every new token may need to look back at them. The longer the conversation, the more the machine behaves like a memory manager.",
            "The naive fix is to keep every cached vector on the fastest device. That wastes scarce memory. The deeper problem is placement over time: which request will continue, which prefix will be reused, which item can move to slower memory, and when moving it back will cost less than recomputing it?",
            "The first-principles object is not the prompt. It is a live memory allocation whose value changes as the request unfolds. Good serving papers make that object explicit and then prove that their scheduler, cache layout, or eviction rule improves real throughput without breaking answer quality.",
        ],
        "check": "Does the serving method track the cache as a changing allocation with arrival, growth, eviction, and reuse, or treat context as a static input?",
        "include_any": ["kv cache", "kv-cache", "prefix caching", "llm serving", "long-context", "million-token", "serving llm"],
    },
    {
        "slug": "precision",
        "title": "Shorter numbers buy capacity only when error is controlled",
        "tags": ["quantization", "approximation", "reliability"],
        "venues": ["MLSys", "ISCA", "ISSCC", "VLSID"],
        "body": [
            "A number stored with fewer bits is smaller, faster to move, and cheaper to multiply. This makes quantization look like a free win. It is not. The saved bits are useful only if the model, circuit, and workload can absorb the rounding error.",
            "The naive fix is to shrink every number equally. Real systems need a map of sensitivity. Some weights, activations, layers, tokens, or physical circuit states need more care than others. The paper-level question is where detail matters and where it does not.",
            "This connects algorithm papers to circuits. A model-level quantization rule changes bandwidth. Bandwidth changes the memory design. The memory design changes power, heat, area, and timing. The same decision travels from math to silicon.",
        ],
        "check": "Does the evidence say where rounding error is harmless, where it compounds, and which hardware cost is reduced?",
        "include_any": ["quantization", "low-bit", "mixed-precision", "rounding", "fp8", "int4", "fp-int", "numerical data type"],
    },
    {
        "slug": "skipping",
        "title": "Skipping work must be cheaper than finding the skip",
        "tags": ["scheduling", "sparsity", "compiler", "dataflow"],
        "venues": ["ASPLOS", "MLSys", "HPCA", "SC"],
        "body": [
            "Many AI workloads contain work that does not need to happen: zeros, inactive experts, repeated prefixes, finished searches, idle containers, unchanged graph regions, and requests that can share partial results. The best speedup is often avoided work.",
            "The naive fix is to test everything and skip what looks useless. That can lose, because the test itself costs time, memory traffic, and control complexity. A real skipping method has to expose the skip early, represent it compactly, and make hardware or software act on it with low overhead.",
            "The useful proof is therefore not just accuracy. It is saved end-to-end work. A sparse model that still moves dense tensors has not saved the physical bottleneck. A scheduler that predicts well but causes stalls has moved the cost elsewhere.",
        ],
        "check": "Does the system save real end-to-end work after paying the cost of detecting, representing, and scheduling the skipped work?",
        "preferred_ids": ["isca-2025-067", "hpca-2025-035", "hpca-2025-056", "mlsys-2025-017", "mlsys-2025-060", "isca-2025-006"],
    },
    {
        "slug": "compiler",
        "title": "Compilers turn a model into a machine schedule",
        "tags": ["compiler", "kernel-fusion", "dataflow", "scheduling"],
        "venues": ["CGO", "ASPLOS", "DAC", "ICCAD"],
        "body": [
            "A model or circuit description says what result is wanted. It does not say the cheapest way to produce that result on a particular machine. The compiler chooses layouts, loop orders, fusion, tiling, register use, communication, and lowering steps.",
            "The naive fix is to write a custom path for every accelerator. That can be fast but it does not scale. The harder goal is an intermediate representation that keeps enough meaning for optimization while still lowering to the concrete details of CPUs, GPUs, FPGAs, PIM arrays, and circuit tools.",
            "Compiler papers are therefore not peripheral to hardware. They are the place where abstract computation becomes wires, banks, instructions, and queues. A good compiler result names the machine constraint it is exploiting.",
        ],
        "check": "Does the compiler keep enough meaning to choose memory layout, movement, and hardware operations, or does it lower too early?",
        "preferred_ids": ["micro-2025-109", "asplos-2025-020", "asplos-2025-075", "asplos-2025-161", "isca-2025-067", "isca-2025-055"],
    },
    {
        "slug": "many-chips",
        "title": "A cluster is one computer with long internal roads",
        "tags": ["interconnect", "parallelism", "scheduling", "virtualization"],
        "venues": ["SC", "ASPLOS", "HPCA", "Hot Chips"],
        "body": [
            "Large AI jobs exceed one chip. The computer becomes a group of accelerators, CPUs, memory pools, storage systems, switches, power delivery, and cooling. The slow part is often coordination rather than local arithmetic.",
            "The naive fix is to add more chips. More chips also add more messages, more synchronization, more failure points, and more places where one slow participant holds back the rest. Scaling is useful only when communication grows more slowly than useful work.",
            "This is why topology matters. The shape of links decides which data can move together and which flows collide. Scheduling decides when traffic happens. Reliability decides what happens when part of the system falls behind or fails.",
        ],
        "check": "Does scaling add useful work faster than it adds communication, waiting, recovery cost, and shared-resource contention?",
        "preferred_ids": ["isca-2025-032", "isca-2025-027", "hpca-2025-041", "micro-2025-072", "hpca-2025-080", "isca-2025-093"],
    },
    {
        "slug": "physical-design",
        "title": "EDA is search under physical law",
        "tags": ["eda", "compiler", "optimization", "reliability"],
        "venues": ["DAC", "ICCAD", "DATE", "VLSID"],
        "body": [
            "A circuit idea is not yet a chip. It must become placed blocks, routed wires, timing margins, power limits, manufacturable shapes, and tests. EDA papers automate this conversion while respecting physical constraints.",
            "The naive fix is to let a learned model propose designs and trust its score. That is dangerous. A design can look good in an early estimate and fail after routing, timing closure, thermal analysis, or manufacturing checks.",
            "The first-principles issue is delayed truth. Cheap estimates arrive early; reliable measurements arrive late. Good EDA work narrows that gap and says which physical claim is actually validated.",
        ],
        "check": "Does the result survive the later physical checks that matter for a fabricated or deployed design: timing, routing, area, power, heat, and manufacturability?",
        "include_any": ["synthesizable rtl", "layout synthesizer", "design space exploration", "physical design", "floorplan", "routing", "timing closure", "manufacturability", "hardware generation"],
        "exclude_any": ["timing attack", "side channel", "virtual disk placement", "cache replacement"],
        "preferred_ids": ["asplos-2025-164", "hpca-2025-002", "isca-2025-111", "micro-2025-089", "hpca-2025-067", "hpca-2025-076"],
    },
    {
        "slug": "security",
        "title": "Shared hardware leaks through behavior, not only memory reads",
        "tags": ["security", "cache", "virtualization", "reliability"],
        "venues": ["ASPLOS", "HPCA", "MICRO", "DAC"],
        "body": [
            "A program can learn about another program without directly reading its data. Timing, cache occupancy, page faults, contention, power, speculation, and device queues can become signals. AI services make this sharper because many users share expensive accelerators.",
            "The naive fix is to isolate everything fully. That protects more, but it can destroy utilization. The real design problem is choosing which shared resource creates the measurable signal and closing that path with the least damage to useful throughput.",
            "Security claims need an attacker model. Who can run code, what can they observe, what resource is shared, and what secret is protected? Without those boundaries, a defense may only solve a different attack.",
        ],
        "check": "Does the claim name the attacker, the observable signal, the shared resource, the protected secret, and the performance cost of closing the channel?",
    },
    {
        "slug": "evidence",
        "title": "A systems claim is only as strong as its measurement boundary",
        "tags": ["reproducibility", "reliability", "scheduling", "benchmarking"],
        "venues": ["SC", "ASPLOS", "MLSys", "OSDI"],
        "body": [
            "Hardware and systems papers often claim speed, energy, cost, or reliability improvement. Those numbers depend heavily on workload, batch size, memory size, model, simulator fidelity, fabrication node, and cluster shape.",
            "The naive fix is to compare against one convenient baseline. That can hide where the method works. The better habit is to name the boundary: which machine, which workload, which failure mode, which power limit, and which scale.",
            "This makes reproducibility part of the technical contribution. A result that others can rerun is not just more trustworthy; it teaches what condition caused the gain.",
        ],
        "check": "Does the paper state the workload, machine, baseline, metric, and scale where the result holds, plus the case where it may stop holding?",
        "preferred_ids": ["hpca-2025-085", "asplos-2025-019", "mlsys-2025-007", "hpca-2025-025", "isca-2025-018", "micro-2025-043"],
    },
    {
        "slug": "codesign",
        "title": "The field advances when layers change together",
        "tags": ["compiler", "scheduling", "memory-system", "near-data-processing"],
        "venues": ["MLSys", "ISCA", "ASPLOS", "Hot Chips"],
        "body": [
            "A model change can alter memory traffic. A memory change can alter the compiler. A compiler change can alter the chip design. A serving change can alter the right network. AI hardware is hard because no single layer owns the bottleneck.",
            "The naive fix is local optimization: make one kernel faster, one cache larger, one circuit smaller, one scheduler cleverer. Local wins matter, but the largest gains come when the paper changes the right adjacent layers at the same time.",
            "The recurring pattern is full-stack co-design. The phrase is often used loosely, but the first-principles meaning is precise: a constraint is visible at one layer, but the cheapest solution requires another layer to expose, preserve, or exploit information.",
        ],
        "check": "Does the paper change the layer that actually controls the bottleneck, or only optimize the layer where the bottleneck was observed?",
        "preferred_ids": ["isca-2025-074", "asplos-2025-054", "hpca-2025-080", "isca-2025-096", "asplos-2025-015", "hpca-2025-045"],
    },
]


def esc(x: object) -> str:
    return html.escape(str(x or ""), quote=True)


def matching_papers(topic: dict, limit: int = 8) -> list[dict]:
    tags = topic["tags"]
    venues = topic["venues"]
    include_any = [term.lower() for term in topic.get("include_any", [])]
    exclude_any = [term.lower() for term in topic.get("exclude_any", [])]
    preferred_ids = topic.get("preferred_ids", [])
    preferred = []
    if preferred_ids:
        by_id = {p.get("id"): p for p in DATA}
        preferred = [by_id[pid] for pid in preferred_ids if pid in by_id]
        if len(preferred) >= limit:
            return preferred[:limit]
    scored = []
    for p in DATA:
        text = " ".join(str(p.get(k, "")) for k in ["tc", "th", "pb", "me", "nv", "mx"]).lower()
        title_text = str(p.get("t", "")).lower()
        full_text = f"{title_text} {text}"
        if include_any and not any(term in full_text for term in include_any):
            continue
        if exclude_any and any(term in full_text for term in exclude_any):
            continue
        score = sum(2 for tag in tags if tag in text)
        score += sum(1 for venue in venues if p.get("v") == venue)
        score += sum(3 for term in include_any if term in full_text)
        if score:
            scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], x[1].get("id", "")))
    selected = list(preferred)
    seen_titles = {p.get("t") for p in selected}
    venue_counts = collections.Counter()
    for p in selected:
        venue_counts[p.get("v")] += 1
    for _, p in scored:
        title = p.get("t")
        venue = p.get("v")
        if title in seen_titles:
            continue
        if venue_counts[venue] >= 2:
            continue
        selected.append(p)
        seen_titles.add(title)
        venue_counts[venue] += 1
        if len(selected) >= limit:
            return selected
    for _, p in scored:
        title = p.get("t")
        if title in seen_titles:
            continue
        selected.append(p)
        seen_titles.add(title)
        if len(selected) >= limit:
            break
    return selected


def page(title: str, body: str) -> str:
    nav = """
      <a href="hardware-first-principles-articles.html">Articles</a>
      <a href="hardware-stack-map.html">Stack map</a>
      <a href="hardware-synthesis.html">Synthesis</a>
      <a href="hardware-diagrams.html">Diagrams</a>
      <a href="hardware-reader-paths.html">Reader paths</a>
      <a href="hardware-venue-concept-index.html">Venue index</a>
      <a href="hardware-review-guide.html">Review guide</a>
      <a href="index.html">Main site</a>
    """
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · AI Hardware 2025</title>
<style>
:root{{--bg:#101216;--panel:#171b22;--line:#303846;--ink:#ece7dc;--muted:#b9c0ca;--quiet:#87909d;--teal:#44c7b6;--amber:#d59a54;--blue:#7ea6d9;--red:#d56b5f;--serif:Georgia,Charter,serif;--sans:system-ui,-apple-system,Segoe UI,sans-serif;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:18px/1.72 var(--serif)}}a{{color:var(--teal);text-underline-offset:3px}}header{{border-bottom:1px solid var(--line);background:#151922;padding:42px max(24px,calc((100vw - 1080px)/2)) 32px}}h1{{font-size:clamp(2.2rem,5vw,4rem);line-height:1.05;margin:8px 0 12px;max-width:920px}}.dek{{color:var(--muted);max-width:820px;font-style:italic}}.bug,.label{{font:700 .68rem/1 var(--mono);letter-spacing:.17em;text-transform:uppercase;color:var(--amber)}}nav{{position:sticky;top:0;z-index:4;display:flex;gap:8px;overflow:auto;padding:10px max(24px,calc((100vw - 1080px)/2));background:rgba(16,18,22,.97);border-bottom:1px solid var(--line)}}nav a{{white-space:nowrap;text-decoration:none;color:var(--muted);font:.78rem var(--sans);border:1px solid var(--line);border-radius:6px;padding:6px 9px;background:#141820}}main{{max-width:1080px;margin:0 auto;padding:34px 24px 80px}}section{{border-bottom:1px solid var(--line);padding:32px 0}}h2{{font-size:clamp(1.55rem,3vw,2.25rem);line-height:1.12;margin:8px 0 14px}}h3{{font:700 1rem/1.3 var(--sans);margin:18px 0 8px;color:var(--ink)}}p{{color:var(--muted);margin:0 0 14px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.card{{border:1px solid var(--line);background:var(--panel);border-radius:8px;padding:16px}}.card p,.card li{{font:0.95rem/1.55 var(--sans);color:var(--muted)}}ul{{margin:8px 0 0 20px;padding:0}}li{{margin:6px 0;color:var(--muted)}}.paper{{border-left:3px solid var(--blue);padding-left:12px;margin:12px 0}}.paper b{{font-family:var(--sans)}}.small{{font:.78rem/1.4 var(--mono);color:var(--quiet)}}.diagram{{font:0.9rem/1.45 var(--mono);white-space:pre-wrap;background:#0c0f14;border:1px solid var(--line);border-radius:8px;padding:16px;color:#d7dde6;overflow:auto}}.call{{border-left:3px solid var(--amber);background:var(--panel);border-radius:0 8px 8px 0;padding:16px 18px;margin:18px 0}}table{{width:100%;border-collapse:collapse;font:0.92rem/1.45 var(--sans)}}td,th{{border-bottom:1px solid var(--line);padding:10px;text-align:left;vertical-align:top}}th{{color:var(--ink)}}@media(max-width:720px){{body{{font-size:17px}}nav{{position:static}}}}
</style></head><body><header><div class="bug">AI Hardware 2025 · first-principles book layer</div><h1>{esc(title)}</h1><p class="dek">A plain-language layer across 2,412 paper records and 503 deeper analyzed records. Each page starts from the physical constraint, then points back to the paper and venue evidence.</p></header><nav>{nav}</nav><main>{body}</main></body></html>"""


def articles() -> str:
    parts = []
    for i, t in enumerate(TOPICS, 1):
        papers = matching_papers(t, 6)
        ev = "".join(
            f"<div class='paper'><b>{esc(p.get('t'))}</b><div class='small'>{esc(p.get('id'))} · {esc(p.get('v'))} · {esc(p.get('tc'))} · {esc(p.get('hw'))}</div><p><b>Problem:</b> {esc(p.get('pb'))}</p><p><b>Move:</b> {esc(p.get('me'))}</p><p><b>What is new:</b> {esc(p.get('nv'))}</p><p><b>Boundary:</b> {esc(p.get('mx'))}</p></div>"
            for p in papers
        )
        body = "".join(f"<p>{esc(x)}</p>" for x in t["body"])
        parts.append(f"<section id='{esc(t['slug'])}'><div class='label'>Article {i:02d}</div><h2>{esc(t['title'])}</h2>{body}<div class='call'><p><b>Review question:</b> {esc(t['check'])}</p></div><h3>Paper anchors</h3>{ev}</section>")
    return page("AI Hardware From First Principles: The Articles", "".join(parts))


def stack_map() -> str:
    rows = [
        ("Model", "Weights, activations, tokens, graphs, experts", "What can be rounded, reused, skipped, or split?"),
        ("Compiler", "Loops, layouts, kernels, memory movement", "How does intent become an efficient schedule?"),
        ("Runtime", "Batches, queues, cache entries, failures", "Which request runs now and where does its state live?"),
        ("Architecture", "Cores, tensor units, caches, memory controllers", "Where is work placed relative to data?"),
        ("Circuit", "Wires, SRAM, DRAM, analog cells, clocks", "What does the operation cost in energy, timing, and area?"),
        ("Package and cluster", "Chiplets, links, racks, storage, cooling", "Can many parts behave like one useful machine?"),
        ("Evidence", "Benchmarks, simulators, silicon, traces", "What boundary makes the claim true?"),
    ]
    table = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a,b,c in rows)
    body = f"<section><h2>The stack is one chain of constraints</h2><p>AI hardware papers differ in vocabulary, but most are moving the same pressure up or down this stack. A good reader asks which layer exposes the bottleneck and which layer pays to remove it.</p><table><tr><th>Layer</th><th>Concrete object</th><th>First question</th></tr>{table}</table></section>"
    return page("Hardware Stack Map", body)


def synthesis() -> str:
    counts = collections.Counter(p.get("v") for p in DATA)
    body = "<section><h2>The simple shape of the field</h2><p>The corpus says one thing in many forms: AI performance is no longer explained by arithmetic alone. It is explained by where numbers sit, how they move, when work can be skipped, how many chips can cooperate, and how firmly the evidence supports the claim.</p></section>"
    body += "<section><h2>Venue pressure</h2><div class='grid'>" + "".join(f"<div class='card'><h3>{esc(k)}</h3><p>{v} higher-detail records in the explorer layer.</p></div>" for k,v in counts.most_common()) + "</div></section>"
    body += "<section><h2>Reading rule</h2><p>Do not start by asking whether a paper is about hardware, systems, compilers, circuits, or EDA. Start by asking what scarce thing it is protecting: memory bandwidth, chip area, energy, time, correctness, utilization, or trust.</p></section>"
    return page("Cross-Paper Synthesis", body)


def diagrams() -> str:
    diagrams = [
        ("The cost path", "model numbers -> memory -> wires -> compute unit -> wires -> memory\n                 ^ most papers try to shorten, reuse, schedule, or protect this path"),
        ("The serving loop", "request arrives -> scheduler chooses batch -> cache state grows -> next token produced -> memory decision repeats"),
        ("The co-design loop", "model property -> compiler representation -> hardware layout -> runtime policy -> measured bottleneck -> model property"),
        ("Evidence boundary", "claim -> workload -> machine -> baseline -> metric -> scale -> failure case"),
    ]
    body = "".join(f"<section><h2>{esc(t)}</h2><div class='diagram'>{esc(d)}</div></section>" for t,d in diagrams)
    return page("First-Principles Diagrams", body)


def reader_paths() -> str:
    paths = [
        ("New to hardware", ["hardware-stack-map.html", "hardware-first-principles-articles.html#movement", "course.html", "explorer.html"]),
        ("LLM serving and systems", ["hardware-first-principles-articles.html#kv-cache", "hardware-first-principles-articles.html#skipping", "mlsys-2025-bigpicture.html", "asplos-2025-bigpicture.html"]),
        ("Compiler and EDA", ["hardware-first-principles-articles.html#compiler", "hardware-first-principles-articles.html#physical-design", "compiler.html", "dac-2025-bigpicture.html"]),
        ("Security and reliability", ["hardware-first-principles-articles.html#security", "hardware-first-principles-articles.html#evidence", "hpca-2025-bigpicture.html", "micro-2025-bigpicture.html"]),
    ]
    body = "<section><h2>Read by the problem you are trying to understand</h2><div class='grid'>"
    for name, links in paths:
        body += f"<div class='card'><h3>{esc(name)}</h3><ul>" + "".join(f"<li><a href='{esc(x)}'>{esc(x)}</a></li>" for x in links) + "</ul></div>"
    body += "</div></section>"
    return page("Reader Paths", body)


def review_guide() -> str:
    body = "<section><h2>How to review this layer</h2><p>Each article should teach one physical constraint before it names a systems or hardware technique. The paper anchors should then prove that the constraint is real: what was scarce, what moved, what was saved, what broke, and where the claim stops.</p></section>"
    body += "<section><h2>Article checks</h2><table><tr><th>Article</th><th>Hidden object</th><th>Review question</th><th>Open</th></tr>"
    hidden = {
        "movement": "bytes crossing a scarce boundary",
        "kv-cache": "live context memory over time",
        "precision": "error tolerated per saved bit",
        "skipping": "work avoided after detection cost",
        "compiler": "meaning preserved until machine scheduling",
        "many-chips": "communication and waiting across chips",
        "physical-design": "physical design truth after early estimates",
        "security": "observable shared-resource signal",
        "evidence": "measurement boundary for a systems claim",
        "codesign": "the layer that actually controls the bottleneck",
    }
    for topic in TOPICS:
        slug = topic["slug"]
        body += f"<tr><td>{esc(topic['title'])}</td><td>{esc(hidden[slug])}</td><td>{esc(topic['check'])}</td><td><a href='hardware-first-principles-articles.html#{esc(slug)}'>article</a></td></tr>"
    body += "</table></section>"
    body += "<section><h2>Failure signs</h2><div class='grid'>"
    signs = [
        ("Local speedup only", "The paper speeds up one kernel but does not show that the system bottleneck moved."),
        ("No scarce boundary", "The prose never says which memory, link, area, power, queue, or trust boundary is protected."),
        ("Weak evidence", "The metric omits workload, baseline, machine, scale, or failure case."),
        ("Layer mismatch", "The method optimizes software while the real constraint sits in memory, interconnect, circuit, or operations."),
    ]
    for title, text in signs:
        body += f"<div class='card'><h3>{esc(title)}</h3><p>{esc(text)}</p></div>"
    body += "</div></section>"
    body += "<section><h2>Anchor audit</h2><p>This is the next tightening pass. For each article, keep an anchor only if it proves the named object. Replace anchors that only share a tag but do not teach the article's physical idea.</p><table><tr><th>Article</th><th>Anchor test</th><th>Current evidence sample</th><th>Manual decision</th></tr>"
    anchor_tests = {
        "movement": "Keep papers where the saved quantity is actual movement across memory, storage, chip, package, or network distance.",
        "kv-cache": "Keep papers where state is live, grows over time, and forces placement, reuse, eviction, or scheduling choices.",
        "precision": "Keep papers where fewer bits change capacity, bandwidth, circuit cost, or energy and the error path is named.",
        "skipping": "Keep papers where the cost of detecting the skipped work is included in the system result.",
        "compiler": "Keep papers where a representation is preserved long enough to choose layout, memory movement, or machine operations.",
        "many-chips": "Keep papers where added devices also create communication, waiting, contention, recovery, or placement costs.",
        "physical-design": "Keep papers where early search is checked against later timing, routing, power, area, heat, or manufacturing truth.",
        "security": "Keep papers where attacker, observed signal, shared resource, protected object, and isolation cost are all visible.",
        "evidence": "Keep papers where the workload, machine, baseline, scale, metric, and failure case are part of the claim.",
        "codesign": "Keep papers where at least two layers change because the bottleneck cannot be removed inside one layer alone.",
    }
    for topic in TOPICS:
        papers = matching_papers(topic, 6)
        sample = "; ".join(f"{p.get('t')} ({p.get('v')})" for p in papers[:3])
        body += (
            f"<tr><td>{esc(topic['title'])}</td><td>{esc(anchor_tests[topic['slug']])}</td>"
            f"<td>{esc(sample)}</td><td>Review top six anchors for fit, then replace weak tag matches.</td></tr>"
        )
    body += "</table></section>"
    return page("AI Hardware Review Guide", body)


def venue_index() -> str:
    rows = []
    for v, items in collections.defaultdict(list).items():
        pass
    byv: dict[str, list[dict]] = collections.defaultdict(list)
    for p in DATA:
        byv[p.get("v") or "Unknown"].append(p)
    for venue in sorted(byv):
        tags = collections.Counter()
        hw = collections.Counter()
        for p in byv[venue]:
            for tag in (p.get("tc") or "").split(","):
                if tag.strip():
                    tags[tag.strip()] += 1
            if p.get("hw"):
                hw[p.get("hw")] += 1
        rows.append(f"<tr><td>{esc(venue)}</td><td>{len(byv[venue])}</td><td>{esc(', '.join(k for k,_ in tags.most_common(8)))}</td><td>{esc(', '.join(k for k,_ in hw.most_common(5)))}</td></tr>")
    body = "<section><h2>Venue to concept index</h2><p>This page is a regression map: it shows which concepts each venue contributes to the book layer.</p><table><tr><th>Venue</th><th>Explorer records</th><th>Dominant technique tags</th><th>Dominant hardware targets</th></tr>" + "".join(rows) + "</table></section>"
    return page("Venue Concept Index", body)


def what_changed() -> str:
    body = """<section><h2>What changed in this batch</h2><ul>
<li>Added a cross-paper article layer that teaches ten core hardware ideas from physical constraints.</li>
<li>Added a stack map, synthesis page, diagrams, reader paths, and venue-to-concept index.</li>
<li>Grounded paper anchors in the local explorer data instead of writing from memory.</li>
<li>Kept the existing venue pages intact and linked the new book layer from the homepage.</li>
</ul></section>"""
    return page("What Changed", body)


def main() -> None:
    outputs = {
        "hardware-first-principles-articles.html": articles(),
        "hardware-stack-map.html": stack_map(),
        "hardware-synthesis.html": synthesis(),
        "hardware-diagrams.html": diagrams(),
        "hardware-reader-paths.html": reader_paths(),
        "hardware-venue-concept-index.html": venue_index(),
        "hardware-review-guide.html": review_guide(),
        "hardware-what-changed.html": what_changed(),
    }
    for name, text in outputs.items():
        (ROOT / name).write_text(text)
    print(f"wrote {len(outputs)} pages")


if __name__ == "__main__":
    main()
