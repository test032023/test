import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_research import (
    abstract_from_inverted_index,
    merge_records,
    normalize_doi,
    normalize_title,
    to_bibtex,
)


class ResearchHelpersTest(unittest.TestCase):
    def test_normalize_doi_removes_prefix_and_case(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1234/ABC."), "10.1234/abc")

    def test_normalize_title_removes_punctuation_and_accents(self):
        self.assertEqual(normalize_title("Évaluation-based learning!"), "evaluation based learning")

    def test_normalize_title_preserves_non_latin_scripts(self):
        self.assertEqual(normalize_title("人工智能教育研究"), "人工智能教育研究")

    def test_rebuilds_abstract_from_inverted_index(self):
        index = {"research": [1], "careful": [0], "works.": [2]}
        self.assertEqual(abstract_from_inverted_index(index), "careful research works.")

    def test_deduplicates_by_doi_and_merges_sources(self):
        records = [
            {"title": "Example Study", "authors": ["A Author"], "year": "2022", "doi": "10.1/abc", "sources": ["Crossref"], "abstract": "", "venue": "", "url": "", "open_access": "unknown", "publication_type": "", "cited_by_count": ""},
            {"title": "Example Study", "authors": ["A Author"], "year": "2022", "doi": "https://doi.org/10.1/ABC", "sources": ["OpenAlex"], "abstract": "An abstract", "venue": "Journal", "url": "https://doi.org/10.1/abc", "open_access": "yes", "publication_type": "article", "cited_by_count": 5},
        ]
        merged = merge_records(records)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["sources"], ["Crossref", "OpenAlex"])
        self.assertEqual(merged[0]["abstract"], "An abstract")
        self.assertEqual(merged[0]["open_access"], "yes")

    def test_bibtex_contains_doi_and_escapes_ampersand(self):
        bib = to_bibtex([{
            "title": "Research & Learning", "authors": ["Jane Doe"], "year": "2024",
            "venue": "Journal of Research", "doi": "10.1234/example", "url": "https://doi.org/10.1234/example",
            "publication_type": "journal-article"
        }])
        self.assertIn(r"Research \& Learning", bib)
        self.assertIn("doi = {10.1234/example}", bib)


if __name__ == "__main__":
    unittest.main()
