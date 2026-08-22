import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SOURCES = ROOT / "assets" / "data" / "sources.json"
CSS = ROOT / "css" / "style.css"

REQUIRED_SECTIONS = {
    "overview",
    "motivation",
    "method",
    "demo",
    "results",
    "data",
    "gallery",
    "citation",
}


class SiteParser(HTMLParser):
    def __init__(self, raw_html):
        super().__init__()
        self.raw_html = raw_html
        self.ids = set()
        self.local_urls = []
        self.external_urls = []
        self.images = []
        self.scripts = []
        self.resource_links = []
        self.table_count = 0
        self.has_demo_anchor = False
        self.has_nav_toggle = False
        self.feed(raw_html)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])

        if tag == "table":
            self.table_count += 1

        if tag == "img":
            self.images.append(attributes)

        if tag == "script" and attributes.get("src"):
            self.scripts.append(
                {
                    "src": attributes["src"],
                    "defer": "defer" in attributes,
                }
            )

        if attributes.get("data-nav-toggle") is not None:
            self.has_nav_toggle = True

        if tag == "a" and attributes.get("data-demo-link") is not None:
            self.has_demo_anchor = True

        if tag == "a" and "resource-link" in attributes.get("class", "").split():
            self.resource_links.append(attributes)

        for name in ("href", "src", "poster"):
            url = attributes.get(name)
            if not url or url.startswith(("#", "mailto:", "data:")):
                continue
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https"):
                self.external_urls.append(url)
            elif parsed.scheme == "":
                self.local_urls.append(url)


class SiteContractTests(unittest.TestCase):
    def read_index(self):
        self.assertTrue(INDEX.exists(), "index.html must exist")
        return INDEX.read_text(encoding="utf-8")

    def test_page_is_identified_as_a_paper_project(self):
        html = self.read_index()
        self.assertIn("ScreenCoder: Advancing Visual-to-Code Generation", html)
        self.assertIn("Yilei Jiang", html)
        self.assertIn("Yaozhi Zheng", html)
        self.assertIn("arXiv:2507.22827", html)
        self.assertNotIn("pricing", html.lower())

    def test_required_research_sections_exist(self):
        parser = SiteParser(self.read_index())
        self.assertTrue(REQUIRED_SECTIONS.issubset(parser.ids))

    def test_local_urls_are_deploy_path_agnostic(self):
        parser = SiteParser(self.read_index())
        for url in parser.local_urls:
            self.assertTrue(url.startswith("./"), url)

    def test_public_source_registry_is_complete(self):
        self.assertTrue(SOURCES.exists(), "sources.json must exist")
        sources = json.loads(SOURCES.read_text(encoding="utf-8"))
        self.assertEqual(
            {"paper", "code", "demo", "dataset", "hf_paper"},
            set(sources["canonical_sources"]),
        )
        for source in sources["canonical_sources"].values():
            self.assertTrue(source["url"].startswith("https://"))
            self.assertIsInstance(source["verified"], bool)

    def test_method_pipeline_is_complete(self):
        html = self.read_index()
        for stage in (
            "Grounding Agent",
            "Planning Agent",
            "Generation Agent",
            "Placeholder Mapping",
        ):
            self.assertIn(stage, html)

    def test_results_use_evidence_tables_without_an_unverified_headline(self):
        parser = SiteParser(self.read_index())
        self.assertGreaterEqual(parser.table_count, 2)
        self.assertNotIn('data-metric="screenbench-block"', parser.raw_html)
        self.assertIn("ScreenBench", parser.raw_html)
        self.assertIn("Design2Code", parser.raw_html)

    def test_bibtex_is_present(self):
        html = self.read_index()
        self.assertIn("@article{jiang2025screencoder", html)
        self.assertIn("arXiv:2507.22827", html)

    def test_paper_and_code_are_the_primary_hero_resources(self):
        parser = SiteParser(self.read_index())
        primary_urls = {
            link["href"]
            for link in parser.resource_links
            if "resource-link--primary" in link.get("class", "").split()
        }
        self.assertEqual(
            {
                "https://arxiv.org/abs/2507.22827",
                "https://github.com/leigest519/ScreenCoder",
            },
            primary_urls,
        )


if __name__ == "__main__":
    unittest.main()
