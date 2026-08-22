# ScreenCoder Project Page V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete local first version of an English, static ScreenCoder paper project page that can later deploy to any GitHub Pages project path.

**Architecture:** A single semantic `index.html` renders all research content without a build step. `css/style.css` owns the responsive visual system, `js/main.js` adds progressive enhancement, and `assets/data/sources.json` records canonical public sources and claim verification state. Python standard-library contract tests validate content identity, relative paths, accessibility, metadata, and local asset integrity.

**Tech Stack:** HTML5, CSS3, Vanilla JavaScript, Python 3 `unittest`, GitHub Pages-compatible relative paths.

**Spec:** `docs/superpowers/specs/2026-08-22-screencoder-project-page-design.md`

## Global Constraints

- The page is a paper project homepage, not a product landing page.
- The visible site language is English.
- Paper and Code have higher visual priority than Demo and Dataset.
- No framework, backend, API key, analytics SDK, database, or model API.
- No GitHub owner, repository name, `/ScreenCoder/` base path, or final `github.io` URL is hardcoded.
- All local assets use relative paths beginning with `./`.
- Public facts come only from arXiv v2, `leigest519/ScreenCoder`, `Jimmyzheng-10/ScreenCoder`, `Leigest/ScreenCoder`, and the Hugging Face paper page.
- Unresolved metric inconsistencies are disclosed in source metadata and are not promoted as headline cards.
- Core content remains readable when JavaScript is disabled.

---

### Task 1: Static Site Contract and Academic Skeleton

**Files:**
- Create: `tests/test_site.py`
- Create: `index.html`
- Create: `assets/data/sources.json`

**Interfaces:**
- Consumes: Design decisions and canonical URLs from the spec.
- Produces: Semantic section IDs `overview`, `motivation`, `method`, `demo`, `results`, `data`, `gallery`, and `citation`; structured source entries keyed by `paper`, `code`, `demo`, `dataset`, and `hf_paper`.

- [ ] **Step 1: Write failing identity and path tests**

```python
class SiteContractTests(unittest.TestCase):
    def test_page_is_identified_as_a_paper_project(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn("ScreenCoder: Advancing Visual-to-Code Generation", html)
        self.assertIn("Yilei Jiang", html)
        self.assertIn("Yaozhi Zheng", html)
        self.assertIn("arXiv:2507.22827", html)
        self.assertNotIn("pricing", html.lower())

    def test_required_research_sections_exist(self):
        parser = SiteParser(INDEX.read_text(encoding="utf-8"))
        self.assertTrue(REQUIRED_SECTIONS.issubset(parser.ids))

    def test_local_urls_are_deploy_path_agnostic(self):
        parser = SiteParser(INDEX.read_text(encoding="utf-8"))
        for url in parser.local_urls:
            self.assertTrue(url.startswith("./"), url)
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because `index.html` and `assets/data/sources.json` do not exist.

- [ ] **Step 3: Implement the minimal semantic page and source registry**

Create `index.html` with the exact paper title, authors, affiliations, canonical external links, navigation, and empty-but-labeled research sections. Create `sources.json` with canonical URLs and `verified` booleans.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest discover -s tests -v`

Expected: all Task 1 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_site.py index.html assets/data/sources.json
git commit -m "feat: scaffold ScreenCoder paper project page"
```

### Task 2: Research Narrative and Evidence Tables

**Files:**
- Modify: `tests/test_site.py`
- Modify: `index.html`
- Modify: `assets/data/sources.json`

**Interfaces:**
- Consumes: Section IDs and source keys from Task 1.
- Produces: Complete English research narrative, the Grounding/Planning/Generation/Placeholder pipeline, ScreenBench and Design2Code tables, post-training table, human evaluation summary, and BibTeX block.

- [ ] **Step 1: Add failing research-content tests**

```python
def test_method_pipeline_is_complete(self):
    html = INDEX.read_text(encoding="utf-8")
    for stage in ("Grounding Agent", "Planning Agent", "Generation Agent", "Placeholder Mapping"):
        self.assertIn(stage, html)

def test_results_are_tables_not_unverified_headline_claims(self):
    parser = SiteParser(INDEX.read_text(encoding="utf-8"))
    self.assertGreaterEqual(parser.table_count, 2)
    self.assertNotIn('data-metric="screenbench-block"', parser.raw_html)

def test_bibtex_is_present(self):
    html = INDEX.read_text(encoding="utf-8")
    self.assertIn("@article{jiang2025screencoder", html)
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.test_site.SiteContractTests -v`

Expected: FAIL because the method stages, evidence tables, and BibTeX are not yet present.

- [ ] **Step 3: Add paper-grounded content**

Implement concise sections using arXiv v2 facts. Include a visible note that the page reports paper values and avoid converting the Block/Position inconsistency into a hero metric. Add table captions and source links.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest discover -s tests -v`

Expected: all Task 1-2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_site.py index.html assets/data/sources.json
git commit -m "feat: add ScreenCoder research narrative and evidence"
```

### Task 3: Public Assets and Responsive Visual System

**Files:**
- Modify: `tests/test_site.py`
- Create: `assets/images/teaser.jpg`
- Create: `assets/images/comparison-baselines.jpeg`
- Create: `assets/images/comparison-screencoder.jpeg`
- Create: `assets/images/method-pipeline.svg`
- Create: `assets/images/demo-poster.svg`
- Create: `css/style.css`
- Modify: `index.html`

**Interfaces:**
- Consumes: semantic HTML and public asset origins from Tasks 1-2.
- Produces: local, attributed visuals; CSS tokens; responsive layouts at 320px, 768px, and 1440px; reduced-motion and focus-visible support.

- [ ] **Step 1: Add failing asset and accessibility tests**

```python
def test_all_local_assets_exist(self):
    parser = SiteParser(INDEX.read_text(encoding="utf-8"))
    for url in parser.local_urls:
        path = ROOT / url.removeprefix("./").split("#", 1)[0]
        self.assertTrue(path.exists(), url)

def test_informative_images_have_alt_text(self):
    parser = SiteParser(INDEX.read_text(encoding="utf-8"))
    for image in parser.images:
        self.assertTrue(image.get("alt", "").strip(), image)

def test_css_includes_accessible_responsive_contracts(self):
    css = CSS.read_text(encoding="utf-8")
    self.assertIn("@media", css)
    self.assertIn("prefers-reduced-motion", css)
    self.assertIn(":focus-visible", css)
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because visual assets and `css/style.css` are missing.

- [ ] **Step 3: Acquire and record public assets**

Download `teaser.jpg`, `example_others.jpeg`, and `example_ours.jpeg` from the canonical GitHub repository. Record source URLs and repository commit in `sources.json`. Create an original web-native SVG method diagram based on the public paper's four-stage method.

- [ ] **Step 4: Implement responsive styling**

Create a restrained academic visual system: serif display title, sans-serif body, blue-violet accent, max-width reading columns, evidence tables, method cards, gallery panels, responsive stacking, visible focus, and reduced-motion behavior.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python3 -m unittest discover -s tests -v`

Expected: all Task 1-3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_site.py index.html css/style.css assets/images assets/data/sources.json
git commit -m "feat: add academic visual system and public assets"
```

### Task 4: Progressive Enhancement

**Files:**
- Modify: `tests/test_site.py`
- Create: `js/main.js`
- Modify: `index.html`
- Modify: `css/style.css`

**Interfaces:**
- Consumes: gallery, citation block, navigation, and demo poster markup.
- Produces: `copyCitation(button)`, mobile navigation toggling, reveal-on-scroll that respects reduced motion, and progressive demo link behavior.

- [ ] **Step 1: Add failing enhancement-contract tests**

```python
def test_interactive_controls_have_accessible_fallbacks(self):
    parser = SiteParser(INDEX.read_text(encoding="utf-8"))
    self.assertIn("citation-copy", parser.ids)
    self.assertTrue(parser.has_demo_anchor)
    self.assertTrue(parser.has_nav_toggle)

def test_script_is_deferred_and_local(self):
    parser = SiteParser(INDEX.read_text(encoding="utf-8"))
    self.assertIn({"src": "./js/main.js", "defer": True}, parser.scripts)
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because controls and `js/main.js` are absent.

- [ ] **Step 3: Implement minimal JavaScript enhancement**

Add a mobile menu with correct `aria-expanded`, citation copy with success/failure status text, and reveal classes. Do not make core content conditional on JavaScript.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest discover -s tests -v`

Expected: all Task 1-4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_site.py index.html css/style.css js/main.js
git commit -m "feat: add accessible progressive interactions"
```

### Task 5: Metadata, Local Preview, and Release-Neutral Documentation

**Files:**
- Modify: `tests/test_site.py`
- Create: `README.md`
- Create: `404.html`
- Create: `favicon.svg`
- Create: `robots.txt`
- Create: `scripts/serve.sh`
- Modify: `index.html`

**Interfaces:**
- Consumes: completed site files.
- Produces: local preview command, metadata contract, social preview placeholders without a final canonical URL, and documentation for later GitHub Pages deployment.

- [ ] **Step 1: Add failing metadata and documentation tests**

```python
def test_metadata_does_not_hardcode_future_host(self):
    html = INDEX.read_text(encoding="utf-8")
    self.assertIn('name="description"', html)
    self.assertIn('property="og:title"', html)
    self.assertNotIn("github.io", html)

def test_local_preview_files_exist(self):
    self.assertTrue((ROOT / "README.md").exists())
    self.assertTrue((ROOT / "scripts/serve.sh").exists())
    self.assertTrue((ROOT / "404.html").exists())
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because README, preview script, and supporting metadata files are missing.

- [ ] **Step 3: Implement local preview and metadata**

Document `python3 -m http.server 8000` and provide `scripts/serve.sh` as a convenience wrapper. Add description, Open Graph title/description/image, favicon, robots file, and a relative-path-safe 404 page. Do not add canonical URL or sitemap until deployment owner is chosen.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_site.py index.html README.md 404.html favicon.svg robots.txt scripts/serve.sh
git commit -m "docs: add local preview and release-neutral metadata"
```

### Task 6: Full Verification and Visual Review

**Files:**
- Modify only if verification exposes a defect.

**Interfaces:**
- Consumes: complete V1 site.
- Produces: verified local build, screenshots at desktop and mobile sizes, and a clean Git worktree.

- [ ] **Step 1: Run the complete automated test suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS with zero errors and failures.

- [ ] **Step 2: Validate source hygiene**

Run: `git diff --check && rg -n 'api[_-]?key|token|secret|github\.io|/ScreenCoder/' --glob '!docs/**' .`

Expected: no secret-like content, no final host, and no hardcoded project base path in production files.

- [ ] **Step 3: Start the local preview**

Run: `./scripts/serve.sh 8000`

Expected: the site responds at `http://127.0.0.1:8000/`.

- [ ] **Step 4: Perform browser visual review**

Inspect at 1440×1000, 768×1024, and 390×844. Verify title hierarchy, author wrapping, method flow, table scrolling, gallery stacking, focus states, and no clipped content.

- [ ] **Step 5: Re-run tests after visual fixes**

Run: `python3 -m unittest discover -s tests -v && git diff --check`

Expected: all tests PASS and diff check exits 0.

- [ ] **Step 6: Commit final local V1**

```bash
git add .
git commit -m "feat: complete local ScreenCoder project page v1"
```

