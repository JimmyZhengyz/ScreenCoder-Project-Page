import json
import os
import re
import signal
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SOURCES = ROOT / "assets" / "data" / "sources.json"
CSS = ROOT / "css" / "style.css"
JS = ROOT / "js" / "main.js"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

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

        if "data-nav-toggle" in attributes:
            self.has_nav_toggle = True

        if tag == "a" and "data-demo-link" in attributes:
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

    def test_all_local_assets_exist(self):
        parser = SiteParser(self.read_index())
        self.assertGreaterEqual(len(parser.images), 4)
        for url in parser.local_urls:
            clean_url = url.split("#", 1)[0].split("?", 1)[0]
            path = ROOT / clean_url.removeprefix("./")
            self.assertTrue(path.exists(), url)

    def test_informative_images_have_alt_text(self):
        parser = SiteParser(self.read_index())
        self.assertGreaterEqual(len(parser.images), 4)
        for image in parser.images:
            self.assertTrue(image.get("alt", "").strip(), image)

    def test_css_includes_accessible_responsive_contracts(self):
        self.assertTrue(CSS.exists(), "css/style.css must exist")
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("@media", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn(":focus-visible", css)
        self.assertRegex(css, r"body\s*\{[^}]*overflow-x:\s*clip")
        self.assertRegex(css, r"\.citation-code\s*\{[^}]*min-width:\s*0")

    def test_wide_desktop_hero_places_a_large_teaser_below_the_project_intro(self):
        if not CHROME.exists():
            self.skipTest("Google Chrome is not installed")

        probe = """
<script>
addEventListener("load", () => {
  const title = document.querySelector(".hero h1");
  const content = document.querySelector(".hero__content");
  const visual = document.querySelector(".hero__visual");
  const atmosphere = document.querySelector(".hero-atmosphere");
  document.documentElement.dataset.probeH1Height = String(Math.round(title.getBoundingClientRect().height));
  document.documentElement.dataset.probeContentBottom = String(Math.round(content.getBoundingClientRect().bottom));
  document.documentElement.dataset.probeVisualTop = String(Math.round(visual.getBoundingClientRect().top));
  document.documentElement.dataset.probeVisualWidth = String(Math.round(visual.getBoundingClientRect().width));
  document.documentElement.dataset.probeTextAlign = getComputedStyle(content).textAlign;
  document.documentElement.dataset.probeAtmosphereHidden = String(atmosphere?.getAttribute("aria-hidden") === "true");
  document.documentElement.dataset.probeAtmosphereParts = String(atmosphere?.children.length || 0);
  document.documentElement.dataset.probeAtmosphereAnimation = atmosphere
    ? [...atmosphere.children].map((part) => getComputedStyle(part).animationName).join(",")
    : "none";
});
</script>
"""
        html = self.read_index().replace("</body>", f"{probe}</body>")

        with tempfile.TemporaryDirectory() as profile_dir:
            probe_path = ROOT / ".hero-layout-probe.html"
            try:
                probe_path.write_text(html, encoding="utf-8")
                process = subprocess.Popen(
                    [
                        str(CHROME),
                        "--headless=new",
                        "--disable-gpu",
                        "--disable-background-networking",
                        "--disable-component-update",
                        "--disable-crash-reporter",
                        "--disable-logging",
                        "--disable-breakpad",
                        "--no-sandbox",
                        "--no-first-run",
                        "--no-default-browser-check",
                        f"--user-data-dir={profile_dir}",
                        "--window-size=1512,900",
                        "--dump-dom",
                        probe_path.as_uri(),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    start_new_session=True,
                )
                try:
                    output, _ = process.communicate(timeout=8)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    output, _ = process.communicate(timeout=3)
            finally:
                probe_path.unlink(missing_ok=True)

        match = re.search(r'data-probe-h1-height="(\d+)"', output)
        content_bottom = re.search(r'data-probe-content-bottom="(\d+)"', output)
        visual_top = re.search(r'data-probe-visual-top="(\d+)"', output)
        visual_width = re.search(r'data-probe-visual-width="(\d+)"', output)
        text_align = re.search(r'data-probe-text-align="([^"]*)"', output)
        atmosphere_hidden = re.search(r'data-probe-atmosphere-hidden="(true|false)"', output)
        atmosphere_parts = re.search(r'data-probe-atmosphere-parts="(\d+)"', output)
        atmosphere_animation = re.search(r'data-probe-atmosphere-animation="([^"]*)"', output)
        if match is None and process.returncode:
            self.skipTest("Chrome headless layout probe is unavailable in this sandbox")
        self.assertIsNotNone(match, "Chrome layout probe did not report the title height")
        self.assertIsNotNone(content_bottom, "Chrome layout probe did not report the intro boundary")
        self.assertIsNotNone(visual_top, "Chrome layout probe did not report the teaser position")
        self.assertIsNotNone(visual_width, "Chrome layout probe did not report the teaser width")
        self.assertLessEqual(
            int(match.group(1)),
            285,
            "At 1512px wide, the centered paper title should remain concise and readable",
        )
        self.assertGreaterEqual(
            int(visual_top.group(1)),
            int(content_bottom.group(1)) + 40,
            "The teaser must begin below the complete project introduction, not beside it",
        )
        self.assertGreaterEqual(
            int(visual_width.group(1)),
            1000,
            "The below-title teaser should be a large visual centerpiece",
        )
        self.assertEqual("center", text_align.group(1))
        self.assertEqual("true", atmosphere_hidden.group(1))
        self.assertGreaterEqual(int(atmosphere_parts.group(1)), 3)
        self.assertNotEqual("none", atmosphere_animation.group(1))

    def test_scrolled_results_table_keeps_model_column_above_metric_columns(self):
        if not CHROME.exists():
            self.skipTest("Google Chrome is not installed")

        probe = """
<script>
addEventListener("load", () => {
  const scroll = document.querySelector(".table-scroll");
  document.documentElement.style.scrollBehavior = "auto";
  scroll.scrollIntoView({behavior: "auto", block: "start"});
  scroll.scrollLeft = 220;
  const model = scroll.querySelector("thead th:first-child");
  const rect = model.getBoundingClientRect();
  document.documentElement.dataset.probeModelRect = `${Math.round(rect.left)},${Math.round(rect.top)},${Math.round(rect.right)},${Math.round(rect.bottom)},${innerWidth},${innerHeight}`;
  const topElement = document.elementFromPoint(rect.right - 8, rect.bottom - 12);
  document.documentElement.dataset.probeModelOwnsEdge = String(model.contains(topElement) || model === topElement);
  document.documentElement.dataset.probeTopElement = `${topElement?.tagName || "none"}:${topElement?.textContent?.trim() || ""}`;
});
</script>
"""
        html = self.read_index().replace("</body>", f"{probe}</body>")

        with tempfile.TemporaryDirectory() as profile_dir:
            probe_path = ROOT / ".table-layout-probe.html"
            try:
                probe_path.write_text(html, encoding="utf-8")
                process = subprocess.Popen(
                    [
                        str(CHROME),
                        "--headless=new",
                        "--disable-gpu",
                        "--disable-background-networking",
                        "--disable-component-update",
                        "--disable-crash-reporter",
                        "--disable-logging",
                        "--disable-breakpad",
                        "--no-sandbox",
                        "--no-first-run",
                        "--no-default-browser-check",
                        f"--user-data-dir={profile_dir}",
                        "--window-size=760,900",
                        "--virtual-time-budget=1000",
                        "--dump-dom",
                        probe_path.as_uri(),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    start_new_session=True,
                )
                try:
                    output, _ = process.communicate(timeout=8)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    output, _ = process.communicate(timeout=3)
            finally:
                probe_path.unlink(missing_ok=True)

        match = re.search(r'data-probe-model-owns-edge="(true|false)"', output)
        top_element = re.search(r'data-probe-top-element="([^"]*)"', output)
        model_rect = re.search(r'data-probe-model-rect="([^"]*)"', output)
        if match is None and process.returncode:
            self.skipTest("Chrome headless layout probe is unavailable in this sandbox")
        self.assertIsNotNone(match, "Chrome layout probe did not report the sticky-column owner")
        self.assertEqual(
            "true",
            match.group(1),
            "Horizontally scrolled metric headers must remain behind the sticky Model column; "
            f"top element was {top_element.group(1) if top_element else 'unknown'}, "
            f"rect was {model_rect.group(1) if model_rect else 'unknown'}",
        )

    def test_qualitative_analysis_has_three_aligned_comparison_cases(self):
        html = self.read_index()
        self.assertEqual(
            3,
            len(re.findall(r'class="[^"]*qualitative-case(?:\s|\")', html)),
            "Qualitative analysis should contain exactly three cases",
        )
        self.assertEqual(
            9,
            len(re.findall(r'class="[^"]*qualitative-panel(?:\s|\")', html)),
            "Each qualitative case should contain Source, Baseline, and ScreenCoder panels",
        )
        for case_number in ("01", "02", "03"):
            self.assertIn(f'data-case="{case_number}"', html)

    def test_interactive_controls_have_accessible_fallbacks(self):
        parser = SiteParser(self.read_index())
        self.assertIn("citation-copy", parser.ids)
        self.assertTrue(parser.has_demo_anchor)
        self.assertTrue(parser.has_nav_toggle)

    def test_script_is_deferred_and_local(self):
        self.assertTrue(JS.exists(), "js/main.js must exist")
        parser = SiteParser(self.read_index())
        self.assertIn({"src": "./js/main.js", "defer": True}, parser.scripts)

    def test_metadata_does_not_hardcode_a_future_host(self):
        html = self.read_index()
        self.assertIn('name="description"', html)
        self.assertIn('property="og:title"', html)
        self.assertIn('property="og:description"', html)
        self.assertNotIn("github.io", html)

    def test_local_preview_and_supporting_files_exist(self):
        for relative_path in (
            "README.md",
            "scripts/serve.sh",
            "404.html",
            "favicon.svg",
            "robots.txt",
        ):
            self.assertTrue((ROOT / relative_path).exists(), relative_path)


if __name__ == "__main__":
    unittest.main()
