#!/usr/bin/env python3
import argparse
import json
from datetime import date
from pathlib import Path
from paper_key_utils import (
    extract_arxiv_id,
    infer_topic_from_path,
    normalize_doi,
    normalize_title,
    title_hash,
)

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


def write_index(records):
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def read_input(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "candidates" in data:
        return data["candidates"]
    if isinstance(data, dict):
        return [data]
    raise ValueError("Input JSON must be one object, a list, or an object with key 'candidates'.")


def canonicalize_record(raw):
    title = raw.get("title", "")
    doi = normalize_doi(raw.get("doi", ""))
    arxiv_id = raw.get("arxiv_id", "") or extract_arxiv_id(raw.get("source_url", "")) or extract_arxiv_id(raw.get("pdf_url", ""))
    pdf_path = raw.get("pdf_path", "")
    topic = raw.get("topic", "") or infer_topic_from_path(pdf_path)

    return {
        "candidate_id": raw.get("candidate_id", ""),
        "title": title,
        "title_norm": normalize_title(title),
        "title_hash": title_hash(title),
        "authors": raw.get("authors", []),
        "year": raw.get("year", ""),
        "venue": raw.get("venue", ""),
        "doi": doi,
        "arxiv_id": arxiv_id,
        "source_url": raw.get("source_url", ""),
        "pdf_url": raw.get("pdf_url", ""),
        "topic": topic,
        "subtopic": raw.get("subtopic", ""),
        "status": raw.get("status", "candidate_sent"),
        "pdf_path": pdf_path,
        "text_path": raw.get("text_path", ""),
        "deep_report_path": raw.get("deep_report_path", ""),
        "date_added": raw.get("date_added", date.today().isoformat()),
        "last_seen": date.today().isoformat(),
    }


def find_match(records, rec):
    doi = normalize_doi(rec.get("doi", ""))
    arxiv_id = rec.get("arxiv_id", "")
    thash = rec.get("title_hash", "")

    if doi:
        for i, r in enumerate(records):
            if normalize_doi(r.get("doi", "")) == doi:
                return i

    if arxiv_id:
        for i, r in enumerate(records):
            r_arxiv = r.get("arxiv_id", "") or extract_arxiv_id(r.get("source_url", "")) or extract_arxiv_id(r.get("pdf_url", ""))
            if r_arxiv == arxiv_id:
                return i

    if thash:
        for i, r in enumerate(records):
            if r.get("title_hash") == thash:
                return i

    return None


def merge_record(old, new):
    preserve_date = old.get("date_added") or new.get("date_added")
    for key, value in new.items():
        if key == "date_added":
            continue
        if key == "status":
            if value:
                old[key] = value
            continue
        if isinstance(value, list):
            if value and not old.get(key):
                old[key] = value
        else:
            if value and not old.get(key):
                old[key] = value
    old["date_added"] = preserve_date
    old["last_seen"] = date.today().isoformat()
    return old


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    input_path = ROOT / args.input if not Path(args.input).is_absolute() else Path(args.input)
    incoming = [canonicalize_record(x) for x in read_input(input_path)]
    records = load_index()

    added = 0
    updated = 0
    skipped = 0

    for rec in incoming:
        if not rec.get("title") and not rec.get("doi") and not rec.get("arxiv_id"):
            skipped += 1
            continue

        idx = find_match(records, rec)
        if idx is None:
            records.append(rec)
            added += 1
        else:
            records[idx] = merge_record(records[idx], rec)
            updated += 1

    write_index(records)

    print(json.dumps({
        "input_count": len(incoming),
        "added_count": added,
        "updated_count": updated,
        "skipped_count": skipped,
        "total_index_records": len(records),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
