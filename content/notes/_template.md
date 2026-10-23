---
# Copy this file to content/notes/YYYY-MM-DD-your-slug.md. Files starting with "_" are ignored by the build.
# Required: title, type, excerpt. Everything else is optional.

title: "A short, specific title"
# slug: custom-slug            # optional; defaults to the filename without its date prefix
date: 2026-01-31               # YYYY-MM-DD. Optional: undated posts sort last and are left out of RSS
# stage: Concept development   # optional short status, shown next to (or instead of) the date
# date_precision: month        # optional; show "Oct 2026" instead of a day
# project: FieldMesh           # optional project label shown after the date
type: project-update           # project-update | engineering-note | research-note | article
status: draft                  # draft (not built) | published
excerpt: One or two sentences for the homepage card, the page intro and the RSS description. Aim for under 280 characters.
tags: [hardware, firmware]
# highlights:                   # optional, up to 4 short key results for the timeline
#   - First result
#   - "Next: what comes after"
# image: assets/notes/example.webp     # site-root-relative path (or an https URL); shown on the card and page
# image_alt: What the image shows      # required when image is set
# canonical_url: https://www.linkedin.com/pulse/...   # set when the original lives elsewhere
# sample: true                 # marks placeholder content: noindex, kept out of the sitemap and RSS
linkedin: |
  Optional LinkedIn-ready text, written the way you would post it.
  Line breaks are kept. Delete this key if the excerpt is enough.
---

Write the post in Markdown. Do not repeat the title or excerpt at the top; the page already shows both.

## Supported formatting

Paragraphs, `##` and `###` headings, **bold**, *italic*, `inline code`, [links](https://example.org),
bullet and numbered lists (one level of nesting), block quotes, fenced code blocks, pipe tables,
horizontal rules and images. Raw HTML is not rendered.

- Links and images that are not full URLs are relative to the site root, for example
  `projects/fieldmesh.html` or `assets/project_pics/ecopi/dashboard_1.webp`.

![Alt text for the image](assets/brand/social-preview-1200x630.png "Optional caption")
