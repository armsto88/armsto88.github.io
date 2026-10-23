# Tom Armstrong — personal website

A dependency-free static site for Tom Armstrong, ecologist and environmental technologist, served by GitHub Pages from `main`.

## Structure

- `index.html`, `about.html`, `projects.html`, `cv.html`, `contact.html`, `404.html` — main pages
- `projects/` — project case studies
- `content/notes/` — Markdown source for the workbench notes; `notes/` is generated from it (see `content/README.md`)
- `tools/build_notes.py` — builds the notes pages, feeds, homepage timeline and sitemap entries
- `writing.html`, `writing/` — an earlier writing section, `noindex` and not linked from the navigation
- `assets/css/style.css` — the whole design system; colour tokens at the top come from the brand kit
- `assets/js/main.js` — navigation, filters, lightbox and the on-demand 3D viewer
- `assets/brand/` — logo marks, favicons and the social preview image used by the site
- `assets/fonts/` — Inter v4.1 web fonts, self-hosted, with their licence
- `assets/project_pics/` — project images as WebP at 1600, 800 and 400 px wide
- `assets/partners/` — partner logos (OekoFor, UNE, REWI)
- `assets/models/` — 3D models, loaded only when a visitor asks for them
- `favicon.ico`, `site.webmanifest` — kept at the root, where browsers look for them
- `TA_Sensor_Complete_Brand_Kit/` — the source brand kit (logos, favicons, style guide). Copy files from here into `assets/brand/` rather than linking to the kit directly.

## Local preview

```bash
python3 serve.py
```

Then open `http://localhost:8000/`. `serve.py` is a plain static server that also sends the right MIME type for `.glb` models.

## Changing the site

- **Workbench notes:** add or edit a file in `content/notes/`, then run `python3 tools/build_notes.py`. Pushing to `main` also triggers `.github/workflows/build-notes.yml`, which rebuilds and commits the generated files.
- **Images:** add a 1600 px WebP and smaller `-800` and `-400` versions next to it, and reference them with `srcset`. Keep large originals out of the repo; everything here is published.
- **Brand colours:** change the `--ta-*` tokens at the top of `assets/css/style.css`.

## Validation

```bash
npx --yes html-validate "*.html" "projects/*.html" "writing/*.html" "notes/*.html"
npx --yes csstree-validator assets/css/style.css
node --check assets/js/main.js
git diff --check
```

The notes build is the only generated part. There is no other compile, type-check or bundling step: GitHub Pages serves the checked-in files directly.
