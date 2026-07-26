#!/usr/bin/env python3
"""Enrich DBLP records with abstract + arXiv id + open-access PDF via OpenAlex.

NOTE ON SOURCES: the brief specified Semantic Scholar, but the unauthenticated S2 Graph
API returns HTTP 429 immediately from this environment (no API key). OpenAlex is the
proven-reachable equivalent (also used by the sibling robotics corpus) and returns the same
signals: abstract (inverted index), open-access PDF, and arXiv id (parsed from locations).

Hardware venues on DBLP often lack DOIs (e.g. MLSys -> OpenReview), so we look up by DOI
when present, else by OpenAlex title search, verifying the match by title similarity.

Usage: python3 scripts/enrich.py --conf mlsys --year 2025 [--limit N]
Reads  metadata/<conf>-<year>-dblp.jsonl
Writes metadata/<conf>-<year>-enriched.jsonl   (resumable: skips keys already present)
"""
import argparse, json, re, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "ai-hw-corpus/1.0 (mailto:mehtama1@gmail.com)"
MAILTO = "mehtama1@gmail.com"
OA = "https://api.openalex.org"


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _sim(a, b):
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _get(url, tries=5):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    delay = 3
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 503) and attempt < tries - 1:
                time.sleep(delay); delay = min(delay * 2, 30); continue
            return None
        except Exception:
            if attempt < tries - 1:
                time.sleep(delay); delay = min(delay * 2, 30); continue
            return None


def _inv_to_text(inv):
    if not inv:
        return None
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def _arxiv_from_work(w):
    """Pull an arXiv id out of any OpenAlex location url or the ids block."""
    ids = w.get("ids") or {}
    for v in ids.values():
        m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", str(v))
        if m:
            return m.group(1)
    for loc in (w.get("locations") or []):
        for k in ("landing_page_url", "pdf_url"):
            m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", str(loc.get(k) or ""))
            if m:
                return m.group(1)
    return None


def _oa_pdf_from_work(w):
    for loc_key in ("best_oa_location", "primary_location"):
        loc = w.get(loc_key) or {}
        if loc.get("pdf_url"):
            return loc["pdf_url"]
    return (w.get("open_access") or {}).get("oa_url")


def oa_by_doi(doi):
    return _get(f"{OA}/works/doi:{urllib.parse.quote(doi)}?mailto={MAILTO}")


def oa_by_title(title):
    q = urllib.parse.quote(title)
    d = _get(f"{OA}/works?search={q}&per-page=3&mailto={MAILTO}")
    if not d or not d.get("results"):
        return None
    best, bestsim = None, 0.0
    for c in d["results"]:
        s = _sim(title, c.get("title") or c.get("display_name"))
        if s > bestsim:
            best, bestsim = c, s
    return best if bestsim >= 0.6 else None


def enrich_one(r):
    w = oa_by_doi(r["doi"]) if r.get("doi") else None
    if not w and r.get("title"):
        w = oa_by_title(r["title"])
    w = w or {}
    r["abstract"] = _inv_to_text(w.get("abstract_inverted_index"))
    r["arxiv_id"] = _arxiv_from_work(w)
    r["oa_pdf"] = _oa_pdf_from_work(w)
    r["cited_by_count"] = w.get("cited_by_count")
    r["openalex_id"] = (w.get("id") or "").split("/")[-1] or None
    r["concepts"] = [c["display_name"] for c in (w.get("concepts") or [])[:6]]
    r["oa_doi"] = (w.get("doi") or "").replace("https://doi.org/", "") or None
    # derive an openreview id from ee if present (fallback PDF source)
    ee = r.get("ee") or ""
    m = re.search(r"openreview\.net/forum\?id=([\w-]+)", ee)
    r["openreview_id"] = m.group(1) if m else None
    r["evidence"] = "abstract" if r.get("abstract") else "title-only"
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    src = ROOT / "metadata" / f"{a.conf}-{a.year}-dblp.jsonl"
    out = ROOT / "metadata" / f"{a.conf}-{a.year}-enriched.jsonl"
    recs = [json.loads(l) for l in src.open()]
    if a.limit:
        recs = recs[: a.limit]
    done = set()
    if out.exists():
        for l in out.open():
            try:
                done.add(json.loads(l)["key"])
            except Exception:
                pass
    n_abs = n_arx = n_pdf = 0
    with out.open("a") as fh:
        for i, r in enumerate(recs):
            if r["key"] in done:
                continue
            r = enrich_one(r)
            n_abs += bool(r.get("abstract"))
            n_arx += bool(r.get("arxiv_id"))
            n_pdf += bool(r.get("oa_pdf"))
            fh.write(json.dumps(r) + "\n")
            if i % 10 == 0:
                print(f"  {i}/{len(recs)}  abs={n_abs} arxiv={n_arx} oa_pdf={n_pdf}")
            time.sleep(0.15)  # OpenAlex polite pool w/ mailto (~10 req/s)
    print(f"done. this run: abstracts={n_abs} arxiv={n_arx} oa_pdf={n_pdf} -> {out}")


if __name__ == "__main__":
    main()
