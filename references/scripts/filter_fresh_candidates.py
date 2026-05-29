#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from check_duplicate import check_duplicate, load_index
from paper_key_utils import extract_arxiv_id, normalize_doi, normalize_title, title_hash

ROOT = Path(__file__).resolve().parents[1]


def read_candidates(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "candidates" in data:
        return data["candidates"]
    raise ValueError("Input JSON must be a list or an object with key 'candidates'.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = ROOT / args.input if not Path(args.input).is_absolute() else Path(args.input)
    output_path = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    candidates = read_candidates(input_path)
    index_records = load_index()

    fresh = []
    duplicates = []
    seen_keys = set()

    for cand in candidates:
        title = cand.get("title", "")
        doi = cand.get("doi", "")
        arxiv_id = cand.get("arxiv_id", "") or extract_arxiv_id(cand.get("source_url", "")) or extract_arxiv_id(cand.get("pdf_url", ""))
        source_url = cand.get("source_url", "")
        pdf_url = cand.get("pdf_url", "")

        keys = []
        if normalize_doi(doi):
            keys.append(("doi", normalize_doi(doi)))
        if arxiv_id:
            keys.append(("arxiv_id", arxiv_id))
        if normalize_title(title):
            keys.append(("title_norm", normalize_title(title)))
        if title_hash(title):
            keys.append(("title_hash", title_hash(title)))

        duplicate_within_raw = False
        dup_key = None
        for key in keys:
            if key in seen_keys:
                duplicate_within_raw = True
                dup_key = key
                break

        if duplicate_within_raw:
            duplicates.append({
                "title": title,
                "reason": f"duplicate_within_raw:{dup_key[0]}",
                "matched_title": "",
                "matched_pdf_path": "",
            })
            continue

        duplicate, reason, matched = check_duplicate(
            title=title,
            doi=doi,
            arxiv_id=arxiv_id,
            source_url=source_url,
            pdf_url=pdf_url,
            records=index_records,
        )

        if duplicate:
            duplicates.append({
                "title": title,
                "reason": reason,
                "matched_title": matched.get("title", "") if matched else "",
                "matched_pdf_path": matched.get("pdf_path", "") if matched else "",
                "matched_doi": matched.get("doi", "") if matched else "",
                "matched_arxiv_id": matched.get("arxiv_id", "") if matched else "",
            })
        else:
            fresh.append(cand)
            for key in keys:
                seen_keys.add(key)

    output_path.write_text(json.dumps(fresh, ensure_ascii=False, indent=2), encoding="utf-8")

    stats = {
        "raw_count": len(candidates),
        "duplicate_count": len(duplicates),
        "fresh_count": len(fresh),
        "duplicate_rate": round(len(duplicates) / len(candidates), 4) if candidates else 0,
        "duplicates": duplicates,
    }

    stats_path = output_path.with_suffix(".stats.json")
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "output": str(output_path.relative_to(ROOT)),
        "stats": str(stats_path.relative_to(ROOT)),
        **stats,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
