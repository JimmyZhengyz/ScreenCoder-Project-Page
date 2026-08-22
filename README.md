# ScreenCoder Project Page

Local, release-neutral first version of the ScreenCoder research project page.
The site uses plain HTML, CSS, and JavaScript, has no runtime dependencies,
and keeps every local asset path relative so it can later move to an approved
GitHub Pages repository without structural changes.

## Preview locally

```bash
./scripts/serve.sh 8000
```

Then open <http://127.0.0.1:8000/>.

## Verify

```bash
python3 -m unittest discover -s tests -v
node --check js/main.js
git diff --check
```

## Source policy

Visible research facts are grounded in the public arXiv v2 paper, canonical
code repository, public Hugging Face Space, and ScreenBench dataset page.
`assets/data/sources.json` records canonical URLs, public asset provenance,
source commits, checksums, and unresolved consistency notes.

The final owner, repository name, canonical URL, and deployment workflow are
deliberately omitted from this local version.
