# Tom Armstrong — personal website

A dependency-free static site for Tom Armstrong, ecologist and conservation technologist.

## Structure

- `index.html`, `about.html`, `projects.html`, `cv.html`, `writing.html`, `contact.html` — main pages
- `projects/` — project case studies
- `writing/` — published notes
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

The repository has no compile, type-check or production-bundle step. GitHub Pages serves the checked-in HTML, CSS, JavaScript and assets directly.
