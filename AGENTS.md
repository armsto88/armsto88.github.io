# Notes for AI assistants working in this repo

This is Tom Armstrong's personal static website, served by GitHub Pages from `main`. Read `README.md` and `content/README.md` first: they describe the structure, the notes pipeline and the validation commands.

## Adding notes from the weekly summary

Weekly notes arrive as finished Markdown files in `content/notes/` with `status: draft`. Their content has already been fact-checked and cleared before it reached this repo. **Your job is to add them to the site, not to review, edit or re-verify the text.**

When asked to add notes:

1. Check each file's front matter and images against the content model in `content/README.md`. Fix format errors only (front matter fields, image paths, missing alt text) and tell the owner what you changed.
2. Set `status: published` on the notes you were asked to add.
3. Run `python3 tools/build_notes.py`, then the validation commands in `README.md`. Fix build errors that are about format. If a failure is about the wording of the content, stop and tell the owner.
4. Preview with `python3 serve.py` if asked.
5. Commit the notes, their images and the generated files together. Push to `main` only after the owner confirms in this session.

Do not rewrite, shorten, add or remove claims. If something looks wrong or unsafe (for example a credential or key), leave the text as it is and tell the owner. Do not edit generated files by hand (`notes/`, and the marked blocks in `index.html` and `sitemap.xml`).

## Figures

- Images live in `assets/project_pics/<project>/` as WebP at 1600 px, with `-800` and `-400` versions.
- A figure in a note body is written `![alt](path "caption")`; the title becomes the figcaption.
- The `image` front matter field becomes the timeline thumbnail and the social preview, so a chart isn't used there.
