#!/usr/bin/env python3
import hashlib
import re
import string
from pathlib import Path


def normalize_title(title: str) -> str:
    if not title:
        return ""

    title = str(title)
    title = Path(title).stem
    title = title.strip()

    # Remove common leading date prefix: 2026-04-06 - Title
    title = re.sub(r"^\d{4}[-_.]\d{2}[-_.]\d{2}\s*[-–—_:]\s*", "", title)

    # Remove simple LaTeX wrappers
    title = title.replace("{", "").replace("}", "")
    title = title.replace("\\", "")
    title = title.replace("&", " and ")

    # Normalize separators
    title = title.replace("_", " ")
    title = title.replace("-", " ")

    # Lowercase
    title = title.lower()

    # Remove punctuation
    punct = string.punctuation.replace("/", "")
    title = title.translate(str.maketrans("", "", punct))

    # Normalize whitespace
    title = re.sub(r"\s+", " ", title).strip()

    return title


def title_hash(title: str) -> str:
    norm = normalize_title(title)
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16] if norm else ""


def normalize_doi(doi: str) -> str:
    if not doi:
        return ""
    doi = str(doi).strip().lower()
    doi = doi.replace("https://doi.org/", "")
    doi = doi.replace("http://doi.org/", "")
    doi = doi.replace("doi:", "")
    doi = doi.strip()
    m = re.search(r"(10\.\d{4,9}/\S+)", doi)
    return m.group(1).rstrip(".,;") if m else doi.rstrip(".,;")


def extract_arxiv_id(text: str) -> str:
    if not text:
        return ""

    text = str(text).strip()

    # New arXiv IDs: 2401.12345, arXiv:2401.12345, /abs/2401.12345, /pdf/2401.12345
    m = re.search(r"(?:arxiv:|arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?", text, re.IGNORECASE)
    if m:
        return m.group(1)

    # Old arXiv IDs: quant-ph/9705052
    m = re.search(r"([a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?", text, re.IGNORECASE)
    if m:
        return m.group(1).lower()

    return ""


def infer_topic_from_path(path: str) -> str:
    """Infer topic folder name from path. Uses the first pattern like '01_xxx', '02_xxx', etc."""
    path = str(path)
    m = re.search(r'(0\d_[a-zA-Z0-9_]+)', path)
    return m.group(1) if m else "unknown"


def infer_title_from_pdf_name(pdf_name: str) -> str:
    stem = Path(pdf_name).stem.strip()
    stem = re.sub(r"^\d{4}[-_.]\d{2}[-_.]\d{2}\s*[-–—_:]\s*", "", stem)
    return stem.strip()


def infer_date_from_pdf_name(pdf_name: str) -> str:
    stem = Path(pdf_name).stem.strip()
    m = re.match(r"^(\d{4})[-_.](\d{2})[-_.](\d{2})", stem)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return ""
