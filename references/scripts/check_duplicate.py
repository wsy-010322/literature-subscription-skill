#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from paper_key_utils import extract_arxiv_id, normalize_doi, normalize_title, title_hash

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "00_registry" / "paper_index.jsonl"


def load_index():
    records = []
    if INDEX_PATH.exists():
        for line in INDEX_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def check_duplicate(title="", doi="", arxiv_id="", source_url="", pdf_url="", records=None):
    records = records if records is not None else load_index()

    q_doi = normalize_doi(doi)
    q_arxiv = arxiv_id or extract_arxiv_id(source_url) or extract_arxiv_id(pdf_url)
    q_arxiv = extract_arxiv_id(q_arxiv) or q_arxiv
    q_title_norm = normalize_title(title)
    q_title_hash = title_hash(title)

    if q_doi:
        for rec in records:
            if normalize_doi(rec.get("doi", "")) == q_doi:
                return True, "doi_match", rec

    if q_arxiv:
        for rec in records:
            rec_arxiv = rec.get("arxiv_id", "") or extract_arxiv_id(rec.get("source_url", "")) or extract_arxiv_id(rec.get("pdf_url", ""))
            if rec_arxiv == q_arxiv:
                return True, "arxiv_id_match", rec

    if q_title_norm:
        for rec in records:
            if rec.get("title_norm") and rec.get("title_norm") == q_title_norm:
                return True, "normalized_title_match", rec

    if q_title_hash:
        for rec in records:
            if rec.get("title_hash") and rec.get("title_hash") == q_title_hash:
                return True, "title_hash_match", rec

    return False, "no_match", None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", default="")
    parser.add_argument("--doi", default="")
    parser.add_argument("--arxiv-id", default="")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--pdf-url", default="")
    args = parser.parse_args()

    duplicate, reason, matched = check_duplicate(
        title=args.title,
        doi=args.doi,
        arxiv_id=args.arxiv_id,
        source_url=args.source_url,
        pdf_url=args.pdf_url,
    )

    print(json.dumps({
        "duplicate": duplicate,
        "reason": reason,
        "matched_record": matched,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
