# Tom Armstrong — personal website

A dependency-free static site for Tom Armstrong, ecologist and environmental technologist.

## Structure

- `index.html`, `about.html`, `projects.html`, `cv.html`, `writing.html`, `contact.html` — main pages
- `projects/` — project case studies
- `writing/` — published notes
- `content/notes/` — source Markdown for the homepage notes feed; `notes/` is generated from it (see `content/README.md`)
- `tools/build_notes.py` — builds the notes pages, feeds and homepage block (`python tools/build_notes.py`)
- `assets/css/style.css` — shared design system and responsive styles
- `assets/js/main.js` — navigation, accessibility helpers and project lightboxes
- `assets/project_pics/` — source images and optimised WebP derivatives

## Local preview

```powershell
npx --yes http-server . -p 4173 -c-1
```

Then open `http://127.0.0.1:4173/`.

## Validation

```powershell
npx --yes html-validate "*.html" "projects/*.html" "writing/*.html"
npx --yes csstree-validator assets/css/style.css
node --check assets/js/main.js
git diff --check
```

The notes feed is the one generated part: run `python tools/build_notes.py` after changing anything in `content/notes/`, then validate `notes/*.html` as above. The repository has no other compile, type-check or production-bundle step. GitHub Pages serves the checked-in HTML, CSS, JavaScript and assets directly.
