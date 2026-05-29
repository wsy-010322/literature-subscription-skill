#!/usr/bin/env python3
"""
Enrich raw arXiv candidates with journal metadata, citation counts, and impact metrics.

Data sources (in priority order):
1. arXiv API — journal_ref, DOI
2. OpenAlex — cited_by_count, venue (journal name, ISSN), journal h_index, 2yr_mean_citedness
3. Semantic Scholar — citationCount, journal name (fallback)

Strategy: for each candidate, try to find its DOI via arXiv API, then query OpenAlex
by DOI (most reliable). If no DOI, search OpenAlex by title. Batch requests with
rate-limiting (OpenAlex: max 10 req/s politely).

Output: enriched_candidates_YYYY-MM-DD.json with added fields:
  - enriched_journal: str  (validated journal name)
  - enriched_venue_issn: str  (ISSN-L)
  - enriched_cited_by_count: int
  - enriched_h_index: int  (journal-level h_index from OpenAlex)
  - enriched_2yr_mean_citedness: float  (journal-level, proxy for impact factor)
  - enriched_source: str  ("openalex", "semanticscholar", "arxiv_only", "none")
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── helpers ──────────────────────────────────────────────────────────

def http_get(url: str, timeout: int = 20) -> dict | str | None:
    """GET a URL and return parsed JSON, or raw text if not JSON."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={
        "User-Agent": "HermesLiteratureBot/1.0 (mailto:hermesswsy@163.com)",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code == 429:
            print(f"  [WARN] HTTP 429 for {url[:120]}", file=sys.stderr)
        elif e.code == 404:
            pass  # not found, expected
        else:
            print(f"  [WARN] HTTP {e.code} for {url[:120]}: {body[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [WARN] Request failed for {url[:120]}: {e}", file=sys.stderr)
        return None

    # Try JSON first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


# ── arXiv API ────────────────────────────────────────────────────────

def fetch_arxiv_meta(arxiv_id: str) -> dict:
    """Get journal_ref and DOI from arXiv API for a paper."""
    clean_id = arxiv_id.strip()
    # Remove version suffix if present (e.g. "2305.00123v3" -> "2305.00123")
    if 'v' in clean_id and clean_id.split('v')[-1].isdigit():
        clean_id = clean_id.rsplit('v', 1)[0]

    url = f"https://export.arxiv.org/api/query?id_list={clean_id}&max_results=1"
    data = http_get(url)
    if not data or not isinstance(data, str):
        return {}

    try:
        root = ET.fromstring(data)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        entry = root.find("atom:entry", ns)
        if entry is None:
            return {}

        result = {}

        # journal_ref
        jref = entry.find("arxiv:journal_ref", ns)
        if jref is not None and jref.text:
            result["journal_ref"] = jref.text.strip()

        # DOI
        doi_el = entry.find("arxiv:doi", ns)
        if doi_el is not None and doi_el.text:
            result["doi"] = doi_el.text.strip()

        return result
    except Exception as e:
        print(f"  [WARN] arXiv XML parse failed for {arxiv_id}: {e}", file=sys.stderr)
        return {}


# ── OpenAlex API ─────────────────────────────────────────────────────

OPENALEX_BASE = "https://api.openalex.org"

def openalex_work_by_doi(doi: str) -> dict | None:
    """Look up a work in OpenAlex by DOI."""
    url = f"{OPENALEX_BASE}/works/doi:{urllib.parse.quote(doi, safe='')}?select=title,cited_by_count,primary_location,publication_date"
    data = http_get(url)
    if not data or not isinstance(data, dict):
        return None
    return data


def openalex_work_by_title(title: str) -> dict | None:
    """Search OpenAlex by title (exact-ish match)."""
    # Strip version/arXiv noise
    clean = title.strip().rstrip(".")
    q = urllib.parse.quote(clean, safe='')
    url = f"{OPENALEX_BASE}/works?filter=title.search:{q}&per_page=3&select=title,cited_by_count,primary_location,doi,publication_date"
    data = http_get(url)
    if not data or not isinstance(data, dict):
        return None

    results = data.get("results", [])
    if not results:
        return None

    # Return the best match (first result)
    return results[0]


def openalex_source_stats(source_id: str) -> dict | None:
    """Get journal-level stats (h_index, 2yr_mean_citedness) from OpenAlex."""
    if not source_id:
        return None
    url = f"{OPENALEX_BASE}/sources/{source_id}?select=display_name,issn_l,summary_stats"
    data = http_get(url)
    if not data or not isinstance(data, dict):
        return None
    return data


# ── Enrich a single candidate ────────────────────────────────────────

def enrich_one(candidate: dict, idx: int, total: int) -> dict:
    """Enrich a single candidate with journal/citation/impact data."""
    title = candidate.get("title", "")
    arxiv_id = candidate.get("arxiv_id", "")
    doi = candidate.get("doi", "")
    source_url = candidate.get("source_url", "") or candidate.get("url", "")

    # Try to extract arxiv_id from URL if not directly present
    if not arxiv_id and "arxiv.org/abs/" in source_url:
        arxiv_id = source_url.split("arxiv.org/abs/")[-1].split("v")[0].strip("/").strip()

    print(f"  [{idx+1}/{total}] {title[:80]}...", file=sys.stderr)

    result = dict(candidate)  # shallow copy
    result["enriched_journal"] = ""
    result["enriched_venue_issn"] = ""
    result["enriched_cited_by_count"] = -1
    result["enriched_h_index"] = -1
    result["enriched_2yr_mean_citedness"] = -1.0
    result["enriched_source"] = "none"

    # Step 1: Try arXiv API for DOI/journal_ref
    arxiv_meta = {}
    if arxiv_id:
        arxiv_meta = fetch_arxiv_meta(arxiv_id)
        if arxiv_meta.get("doi") and not doi:
            doi = arxiv_meta["doi"]
            result["doi"] = doi

    # Step 2: Query OpenAlex (by DOI, then by title)
    oa_work = None

    if doi:
        oa_work = openalex_work_by_doi(doi)
        time.sleep(0.1)  # polite delay

    if not oa_work and title:
        oa_work = openalex_work_by_title(title)
        time.sleep(0.1)

    if oa_work:
        result["enriched_cited_by_count"] = oa_work.get("cited_by_count", -1)
        result["enriched_source"] = "openalex"

        # Extract venue/journal info
        primary_loc = oa_work.get("primary_location", {}) or {}
        source_info = primary_loc.get("source", {}) or {}

        if source_info:
            journal_name = source_info.get("display_name", "")
            issn = source_info.get("issn_l", "")
            source_id = source_info.get("id", "")

            result["enriched_journal"] = journal_name
            result["enriched_venue_issn"] = issn

            # Get journal-level stats
            if source_id:
                oa_source = openalex_source_stats(source_id)
                time.sleep(0.1)
                if oa_source:
                    stats = oa_source.get("summary_stats", {}) or {}
                    result["enriched_h_index"] = stats.get("h_index", -1)
                    result["enriched_2yr_mean_citedness"] = stats.get("2yr_mean_citedness", -1.0)

    # Step 3: Fallback — if we got journal_ref from arXiv but nothing from OpenAlex
    if not result["enriched_journal"] and arxiv_meta.get("journal_ref"):
        result["enriched_journal"] = arxiv_meta["journal_ref"]
        result["enriched_source"] = "arxiv_only"

    # Step 4: Carry forward any existing journal/citation from original data
    if not result["enriched_journal"] and candidate.get("journal"):
        result["enriched_journal"] = candidate["journal"]
    if result["enriched_cited_by_count"] < 0 and candidate.get("citations", -1) > 0:
        result["enriched_cited_by_count"] = candidate["citations"]

    return result


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Enrich arXiv candidates with journal/citation/impact data"
    )
    parser.add_argument("--input", required=True, help="Path to fresh_candidates JSON")
    parser.add_argument("--output", required=True, help="Path for enriched_candidates JSON")
    parser.add_argument("--delay", type=float, default=0.3,
                        help="Delay between requests in seconds (default: 0.3)")
    args = parser.parse_args()

    input_path = ROOT / args.input if not Path(args.input).is_absolute() else Path(args.input)
    output_path = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    candidates = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(candidates, dict) and "candidates" in candidates:
        candidates = candidates["candidates"]
    if not isinstance(candidates, list):
        raise ValueError("Input must be a JSON array or object with 'candidates' key")

    total = len(candidates)
    print(f"Enriching {total} candidates...", file=sys.stderr)

    enriched = []
    for i, cand in enumerate(candidates):
        result = enrich_one(cand, i, total)
        enriched.append(result)

        # Polite rate limiting
        if i < total - 1:
            time.sleep(args.delay)

    # Stats
    openalex_count = sum(1 for e in enriched if e["enriched_source"] == "openalex")
    arxiv_only_count = sum(1 for e in enriched if e["enriched_source"] == "arxiv_only")
    none_count = sum(1 for e in enriched if e["enriched_source"] == "none")
    has_citations = sum(1 for e in enriched if e["enriched_cited_by_count"] >= 0)
    has_journal = sum(1 for e in enriched if e["enriched_journal"])

    output_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "total": total,
        "openalex_hits": openalex_count,
        "arxiv_only": arxiv_only_count,
        "no_enrichment": none_count,
        "has_citation_data": has_citations,
        "has_journal_data": has_journal,
        "output": str(output_path.relative_to(ROOT)),
    }

    stats_path = output_path.with_suffix(".stats.json")
    stats_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nDone. {openalex_count}/{total} enriched via OpenAlex, "
          f"{arxiv_only_count} via arXiv only, {none_count} without enrichment.",
          file=sys.stderr)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
