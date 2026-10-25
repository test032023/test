#!/usr/bin/env python3
"""Discover academic metadata via OpenAlex and Crossref and export reproducible files."""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"
USER_AGENT = "AcademicResearchToolkit/0.1 (metadata discovery; contact via RESEARCH_MAILTO)"
CSV_FIELDS = [
    "title", "authors", "year", "venue", "doi", "url", "sources",
    "cited_by_count", "open_access", "publication_type", "abstract",
]


def make_session(mailto: str | None = None) -> requests.Session:
    retry = Retry(
        total=3, connect=3, read=3, backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": USER_AGENT})
    if mailto:
        session.params = {"mailto": mailto}
    return session


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = value[0] if value else ""
    text = re.sub(r"<[^>]+>", " ", str(value))
    return re.sub(r"\s+", " ", text).strip()


def normalize_doi(value: Any) -> str:
    doi = clean_text(value).lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.strip().rstrip(".,; ")


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").casefold()
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^\\w]+", " ", value, flags=re.UNICODE).replace("_", " ").strip()


def year_from_crossref(item: dict[str, Any]) -> str:
    for field in ("published-print", "published-online", "published", "issued", "created"):
        date = (item.get(field) or {}).get("date-parts", [])
        if date and date[0]:
            return str(date[0][0])
    return ""


def abstract_from_inverted_index(index: Any) -> str:
    if not isinstance(index, dict) or not index:
        return ""
    positions: dict[int, str] = {}
    for word, indexes in index.items():
        if isinstance(indexes, list):
            for position in indexes:
                if isinstance(position, int):
                    positions[position] = word
    return " ".join(positions[i] for i in sorted(positions))


def normalize_crossref(item: dict[str, Any]) -> dict[str, Any]:
    authors = []
    for author in item.get("author", []) or []:
        name = " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part).strip()
        if not name:
            name = clean_text(author.get("name", ""))
        if name:
            authors.append(name)
    doi = normalize_doi(item.get("DOI"))
    return {
        "title": clean_text(item.get("title")),
        "authors": authors,
        "year": year_from_crossref(item),
        "venue": clean_text(item.get("container-title")),
        "doi": doi,
        "url": clean_text(item.get("URL")) or (f"https://doi.org/{doi}" if doi else ""),
        "sources": ["Crossref"],
        "cited_by_count": item.get("is-referenced-by-count", ""),
        "open_access": "unknown",
        "publication_type": clean_text(item.get("type")),
        "abstract": clean_text(item.get("abstract")),
    }


def normalize_openalex(item: dict[str, Any]) -> dict[str, Any]:
    authors = []
    for authorship in item.get("authorships", []) or []:
        author = authorship.get("author", {}) or {}
        name = clean_text(author.get("display_name"))
        if name:
            authors.append(name)
    doi = normalize_doi(item.get("doi"))
    primary = item.get("primary_location") or {}
    source = primary.get("source") or {}
    oa = item.get("open_access") or {}
    return {
        "title": clean_text(item.get("title")),
        "authors": authors,
        "year": str(item.get("publication_year") or ""),
        "venue": clean_text(source.get("display_name")),
        "doi": doi,
        "url": clean_text(item.get("doi")) or clean_text(item.get("id")),
        "sources": ["OpenAlex"],
        "cited_by_count": item.get("cited_by_count", ""),
        "open_access": "yes" if oa.get("is_oa") is True else ("no" if oa.get("is_oa") is False else "unknown"),
        "publication_type": clean_text(item.get("type")),
        "abstract": abstract_from_inverted_index(item.get("abstract_inverted_index")),
    }


def year_filter(since_year: int | None, until_year: int | None) -> str:
    parts = []
    if since_year is not None:
        parts.append(f"from-pub-date:{since_year}-01-01")
    if until_year is not None:
        parts.append(f"until-pub-date:{until_year}-12-31")
    return ",".join(parts)


def search_crossref(session: requests.Session, query: str, limit: int,
                    since_year: int | None, until_year: int | None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "query.bibliographic": query, "rows": min(limit, 1000), "select": ",".join([
            "DOI", "title", "author", "published-print", "published-online", "published", "issued",
            "created", "container-title", "URL", "is-referenced-by-count", "type", "abstract"
        ])
    }
    date_filter = year_filter(since_year, until_year)
    if date_filter:
        params["filter"] = date_filter
    response = session.get(CROSSREF_URL, params=params, timeout=45)
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])
    return [normalize_crossref(item) for item in items]


def search_openalex(session: requests.Session, query: str, limit: int,
                    since_year: int | None, until_year: int | None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "search": query,
        "per-page": min(limit, 200),
        "sort": "relevance_score:desc",
        "select": "id,doi,title,publication_year,authorships,primary_location,open_access,cited_by_count,type,abstract_inverted_index",
    }
    filters = []
    if since_year is not None:
        filters.append(f"from_publication_date:{since_year}-01-01")
    if until_year is not None:
        filters.append(f"to_publication_date:{until_year}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    response = session.get(OPENALEX_URL, params=params, timeout=45)
    response.raise_for_status()
    items = response.json().get("results", [])
    return [normalize_openalex(item) for item in items]


def merge_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    by_doi: dict[str, dict[str, Any]] = {}
    by_title_year: dict[str, dict[str, Any]] = {}
    for record in records:
        title = clean_text(record.get("title"))
        if not title:
            continue
        doi = normalize_doi(record.get("doi"))
        title_year = f"{normalize_title(title)}|{record.get('year', '')}"
        current = by_doi.get(doi) if doi else None
        if current is None:
            current = by_title_year.get(title_year)
        if current is None:
            current = {**record, "doi": doi, "sources": list(record.get("sources", []))}
            merged.append(current)
        for field in ("title", "venue", "url", "year", "publication_type", "abstract", "cited_by_count"):
            if (current.get(field) in (None, "", []) or current.get(field) == "unknown") and record.get(field) not in (None, "", []):
                current[field] = record[field]
        if not current.get("authors") and record.get("authors"):
            current["authors"] = record["authors"]
        if not current.get("doi") and doi:
            current["doi"] = doi
        if current.get("open_access") in (None, "", "unknown") and record.get("open_access") not in (None, "", "unknown"):
            current["open_access"] = record["open_access"]
        current["sources"] = sorted(set(current.get("sources", []) + record.get("sources", [])))
        if doi:
            by_doi[doi] = current
        by_title_year[title_year] = current
        merged_doi = normalize_doi(current.get("doi"))
        if merged_doi:
            by_doi[merged_doi] = current
        current_title_year = f"{normalize_title(clean_text(current.get('title')))}|{current.get('year', '')}"
        by_title_year[current_title_year] = current
    merged.sort(key=lambda r: (-(int(r["year"]) if str(r.get("year", "")).isdigit() else 0), r.get("title", "").casefold()))
    return merged


def bibtex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    }
    return "".join(replacements.get(ch, ch) for ch in (value or ""))


def bibtex_key(record: dict[str, Any], seen: set[str]) -> str:
    first = (record.get("authors") or ["unknown"])[0]
    surname = re.sub(r"[^A-Za-z0-9]", "", first.split()[-1]).lower() or "unknown"
    title_word = next((w.lower() for w in re.findall(r"[A-Za-z0-9]+", record.get("title", "")) if len(w) > 3), "paper")
    base = f"{surname}{record.get('year') or 'nd'}{title_word}"
    key = base
    counter = 2
    while key in seen:
        key = f"{base}{counter}"
        counter += 1
    seen.add(key)
    return key


def to_bibtex(records: list[dict[str, Any]]) -> str:
    entries = []
    seen: set[str] = set()
    for record in records:
        kind = record.get("publication_type", "").lower()
        entry_type = "article" if ("journal" in kind or kind == "article") else "misc"
        key = bibtex_key(record, seen)
        fields = {
            "title": record.get("title", ""),
            "author": " and ".join(record.get("authors", [])),
            "year": record.get("year", ""),
            "journal": record.get("venue", "") if entry_type == "article" else "",
            "doi": record.get("doi", ""),
            "url": record.get("url", ""),
        }
        lines = [f"@{entry_type}{{{key},"]
        for name, value in fields.items():
            if value:
                lines.append(f"  {name} = {{{bibtex_escape(str(value))}}},")
        lines.append("}")
        entries.append("\n".join(lines))
    return "\n\n".join(entries) + ("\n" if entries else "")


def write_outputs(records: list[dict[str, Any]], output_dir: Path, metadata: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "records.json").open("w", encoding="utf-8") as handle:
        json.dump(records, handle, ensure_ascii=False, indent=2)
    with (output_dir / "records.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["authors"] = "; ".join(row.get("authors", []))
            row["sources"] = "; ".join(row.get("sources", []))
            writer.writerow(row)
    (output_dir / "references.bib").write_text(to_bibtex(records), encoding="utf-8")
    (output_dir / "search_log.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    year_counts = Counter(str(r.get("year") or "Unknown") for r in records)
    source_counts = Counter(source for r in records for source in r.get("sources", []))
    lines = [
        "# Academic literature discovery summary", "",
        f"- Query: {metadata['query']}",
        f"- Run time (UTC): {metadata['run_at_utc']}",
        f"- Year range: {metadata.get('since_year') or 'any'} to {metadata.get('until_year') or 'any'}",
        f"- Requested maximum per source: {metadata['max_records_per_source']}",
        f"- Records retrieved before deduplication: {metadata['records_before_deduplication']}",
        f"- Unique records after deduplication: {len(records)}",
        f"- Records with DOI: {sum(bool(r.get('doi')) for r in records)}", "",
        "## Records by source", "",
    ]
    lines += [f"- {name}: {count}" for name, count in sorted(source_counts.items())] or ["- No records returned"]
    lines += ["", "## Records by publication year", ""]
    lines += [f"- {year}: {count}" for year, count in sorted(year_counts.items(), reverse=True)]
    lines += ["", "## Important limitations", "",
              "This is an automated metadata discovery run, not a completed systematic review. API coverage and ranking differ by source. Missing abstracts or metadata do not imply that a paper is irrelevant. Deduplication is heuristic. Screen titles/abstracts and full texts against predeclared criteria, verify citations, document exclusion reasons, and assess risk of bias before synthesizing evidence.", ""]
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_optional_year(value: str) -> int | None:
    if value is None or not value.strip():
        return None
    year = int(value)
    if year < 1000 or year > 9999:
        raise ValueError("year must be a four-digit year")
    return year


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Research topic or phrase")
    parser.add_argument("--max-records", type=int, default=50, help="Maximum records per API (1-200)")
    parser.add_argument("--since-year", type=parse_optional_year, default=None, help="Earliest publication year, inclusive")
    parser.add_argument("--until-year", type=parse_optional_year, default=None, help="Latest publication year, inclusive")
    parser.add_argument("--output-dir", default="research-workflow/output", help="Output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.query.strip():
        print("Error: --query must not be blank", file=sys.stderr)
        return 2
    if not 1 <= args.max_records <= 200:
        print("Error: --max-records must be between 1 and 200", file=sys.stderr)
        return 2
    if args.since_year and args.until_year and args.since_year > args.until_year:
        print("Error: --since-year must be <= --until-year", file=sys.stderr)
        return 2

    mailto = os.environ.get("RESEARCH_MAILTO") or None
    session = make_session(mailto)
    errors: dict[str, str] = {}
    by_source: dict[str, list[dict[str, Any]]] = {"Crossref": [], "OpenAlex": []}
    for source, search_fn in (("Crossref", search_crossref), ("OpenAlex", search_openalex)):
        try:
            by_source[source] = search_fn(session, args.query.strip(), args.max_records, args.since_year, args.until_year)
            print(f"{source}: retrieved {len(by_source[source])} records")
        except (requests.RequestException, ValueError, KeyError) as exc:
            errors[source] = f"{type(exc).__name__}: {exc}"
            print(f"Warning: {source} search failed: {errors[source]}", file=sys.stderr)
        time.sleep(0.2)

    if not by_source["Crossref"] and not by_source["OpenAlex"]:
        print("Error: no records returned by either API; see warnings above.", file=sys.stderr)
        return 1

    all_records = by_source["Crossref"] + by_source["OpenAlex"]
    records = merge_records(all_records)
    metadata = {
        "query": args.query.strip(),
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "since_year": args.since_year,
        "until_year": args.until_year,
        "max_records_per_source": args.max_records,
        "apis": ["Crossref REST API", "OpenAlex Works API"],
        "records_by_source_before_deduplication": {source: len(items) for source, items in by_source.items()},
        "records_before_deduplication": len(all_records),
        "unique_records_after_deduplication": len(records),
        "errors": errors,
        "mailto_configured": bool(mailto),
    }
    write_outputs(records, Path(args.output_dir), metadata)
    print(f"Wrote {len(records)} unique records to {Path(args.output_dir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
