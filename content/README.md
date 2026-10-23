# Notes content

Each post is one Markdown file in `content/notes/`. A small build script turns those files into the homepage feed, the `notes/` pages and the feeds. Nothing else needs editing to publish a post.

```text
content/notes/*.md ──► python tools/build_notes.py ──► notes/<slug>.html     post pages
                                                        notes/index.html      all notes, filter by type
                                                        notes/feed.json       full posts for scripts, LinkedIn, newsletter
                                                        notes/feed.xml        RSS
                                                        index.html            "Latest notes" block (between the notes: markers)
                                                        sitemap.xml           notes entries (between the notes: markers)
```

`notes/` and the marked blocks in `index.html` and `sitemap.xml` are generated. Edit the Markdown, not the output. The output is committed because GitHub Pages serves the repo as it is.

## Writing a post

```bash
python tools/build_notes.py new "FieldHub bring-up"   # creates a draft (add -t engineering-note etc. for other types)
# edit content/notes/YYYY-MM-DD-schematic-review-notes.md, set status: published
python tools/build_notes.py                                                    # rebuild
```

`content/notes/_template.md` shows every field. Files starting with `_` are ignored.

## Content model

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Page title and card title. |
| `type` | yes | `project-update`, `engineering-note`, `research-note` or `article`. Sets the colour of the card, and its label when a feed mixes types. |
| `excerpt` | yes | One or two sentences. Used on cards, as the page intro, in RSS and in link previews. Keep it under 280 characters. |
| `date` | no | `YYYY-MM-DD`. Sets the order and the date shown. It does not schedule anything: a post is live as soon as it is built with `status: published`. Posts without a date sort after all dated ones, and are left out of the RSS feed. |
| `stage` | no | A short status such as `Concept development`, shown on the card and page next to (or instead of) the date. |
| `project` | no | Project or area label such as `FieldMesh`, shown after the date on the card and page. |
| `highlights` | no | Up to four short key results, shown as the entry's detail in the workbench timeline instead of the excerpt, e.g. `- ADS1015 within about 1% of a reference meter`. Quote an item that contains a colon. |
| `date_precision` | no | `day` (default) or `month`. With `month` the card shows `Oct 2026` instead of a day. The full `date` still sets the order, so posts from the same day can be ordered with a time, e.g. `2026-10-23T15:00`. |
| `status` | no | `published` (default) or `draft`. Drafts are not built. |
| `slug` | no | Defaults to the filename without its date prefix. Becomes `notes/<slug>.html`. |
| `tags` | no | `[hardware, firmware]`. Shown on cards and written to the feeds. |
| `image`, `image_alt` | no | Site-root-relative path or an `https` URL. `image_alt` is required when `image` is set. |
| `canonical_url` | no | Set when the original lives elsewhere (LinkedIn article, a newsletter archive). The page then points search engines there and says where it first appeared. |
| `linkedin` | no | LinkedIn-ready text, written as you would post it. Line breaks are kept. |
| `sample` | no | `true` marks placeholder content: `noindex`, left out of the sitemap and RSS, and the build warns about it. |

The body is Markdown: paragraphs, `##`/`###` headings, bold, italic, inline code, links, lists (one level of nesting), block quotes, fenced code, pipe tables, rules and images. Raw HTML is escaped. Links and images that are not full URLs are relative to the site root, for example `projects/fieldmesh.html`. Do not repeat the title or excerpt at the top of the body.

The homepage section and the `notes/` index are currently titled "On the workbench", and every post is a `project-update`, so the type label is hidden on cards. The titles are the `SECTION_*` constants at the top of `tools/build_notes.py`. When other types are published alongside project updates, the labels appear automatically and the index gets a filter by type; rename the section at that point.

A short post and a long article use the same file format. Long articles are just `type: article` with more body text; the card shows a reading time once an article passes about 300 words.

If any post is invalid (unknown type, missing field, missing image, duplicate slug, typo in a key name) the build stops with a message and writes nothing.

## Reusing a post elsewhere

- **LinkedIn:** the `linkedin` field in the post, also available as `linkedin` in `notes/feed.json`. If it is empty, use `title` and `excerpt` plus the `url`.
- **Newsletter:** `notes/feed.xml` carries the full post as HTML (`content:encoded`), so any RSS-to-email tool can pick it up. `notes/feed.json` also has `body_markdown` and `body_html` for a script or a paste.
- **Cross-posted articles:** set `canonical_url` to the original, or leave it empty to make this site the original and link to it from LinkedIn.

## Automating posts (for example from ChatGPT)

The design assumes a post is just one text file, so an automation only has to create a file in `content/notes/`. It never needs to touch HTML.

1. The automation writes `content/notes/YYYY-MM-DD-slug.md` with the front matter above. `_template.md` is a good example to give it, with the instruction to return the file contents and nothing else.
2. It adds the file through the GitHub contents API (`PUT /repos/armsto88/armsto88.github.io/contents/content/notes/<file>.md`) using a fine-grained token limited to this repository with Contents read/write. Opening a pull request instead of committing to `main` gives a review step before anything goes live.
3. `.github/workflows/build-notes.yml` runs the build on every push to `main` that touches `content/notes/`, and commits the regenerated pages. A malformed post fails that run and leaves the site as it was.

Things to know before relying on it:

- **Drafts are not private.** The repository is public and GitHub Pages serves every file in it, so `status: draft` keeps a post off the site's pages and feeds but not out of `content/notes/`. For review, use a branch or pull request, and merge to publish.
- The workflow has not been run yet. After the first automated post, check that the commit appeared and that GitHub Pages redeployed. Commits made with the default workflow token do not always trigger a Pages build; if yours does not, switch Pages to deploy from GitHub Actions or give the workflow a token of your own.
- If `main` is protected, the workflow cannot push to it directly. Run the build locally instead, or allow the bot to bypass protection.
