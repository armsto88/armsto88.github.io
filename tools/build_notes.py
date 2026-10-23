#!/usr/bin/env python3
"""Build the notes feed from Markdown files in content/notes/.

Reads    content/notes/*.md              (front matter + Markdown body)
Writes   notes/<slug>.html               one page per published post
         notes/index.html                all notes, filterable by type
         notes/feed.json                 machine-readable feed (bodies, LinkedIn text)
         notes/feed.xml                  RSS feed (newsletter tools can ingest it)
Updates  index.html                      the block between the notes:start/end markers
         sitemap.xml                     the block between the notes:start/end markers

Standard library only. Nothing is written unless every post validates.

    python tools/build_notes.py                    build everything
    python tools/build_notes.py new "Title" -t engineering-note
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "notes"
OUT_DIR = ROOT / "notes"

SITE_URL = "https://armsto88.github.io"
SITE_NAME = "Tom Armstrong"
AUTHOR = "Tom Armstrong"
DEFAULT_IMAGE = "assets/brand/social-preview-1200x630.png"
HOME_COUNT = 5

# Wording for the feed as a whole. It is currently project updates only; change
# these if other post types are added to the same feed.
SECTION_LABEL = "Project notes"
SECTION_TITLE = "On the workbench"
SECTION_DESC = "A few notes from projects I’m actively developing, testing and learning from."
SECTION_NOUN = "workbench notes"
WORDS_PER_MINUTE = 200

# slug -> label. Order is the order of the filter buttons on the index page.
TYPES = {
    "project-update": "Project update",
    "engineering-note": "Engineering note",
    "research-note": "Research note",
    "article": "Article",
}
STATUSES = ("draft", "published")
KNOWN_KEYS = {
    "title", "slug", "date", "type", "status", "excerpt", "tags",
    "image", "image_alt", "canonical_url", "linkedin", "sample", "stage",
    "project", "date_precision", "highlights",
}
RESERVED_SLUGS = {"index", "feed"}
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August",
               "September", "October", "November", "December")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXCERPT_WARN = 280
EXCERPT_MAX = 400


class BuildError(Exception):
    pass


# --------------------------------------------------------------------------- #
# Front matter
# --------------------------------------------------------------------------- #

def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return re.sub(r'\\(["\\])', r"\1", value[1:-1])
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def _split_inline_list(raw: str) -> list[str]:
    items, buf, quote_char = [], "", ""
    for ch in raw:
        if quote_char:
            buf += ch
            if ch == quote_char:
                quote_char = ""
        elif ch in "\"'":
            buf += ch
            quote_char = ch
        elif ch == ",":
            items.append(buf)
            buf = ""
        else:
            buf += ch
    items.append(buf)
    return [_unquote(i.strip()) for i in items if i.strip()]


def _strip_comment(value: str) -> str:
    """Drop a trailing YAML comment (whitespace then #) outside quotes."""
    quote_char = ""
    n = 0
    while n < len(value):
        ch = value[n]
        if quote_char == "'":
            if ch == "'" and value[n + 1:n + 2] == "'":
                n += 1  # '' is an escaped quote inside single quotes
            elif ch == "'":
                quote_char = ""
        elif quote_char == '"':
            if ch == "\\":
                n += 1
            elif ch == '"':
                quote_char = ""
        elif ch in "\"'" and (n == 0 or value[n - 1] in " [,"):
            quote_char = ch
        elif ch == "#" and n > 0 and value[n - 1] in " \t":
            return value[:n].rstrip()
        n += 1
    return value


def parse_front_matter(text: str, where: str) -> tuple[dict, str]:
    """Parse the small YAML subset the notes use: scalars, [a, b] lists,
    '- item' lists and '|' / '>' block scalars. Flat keys only."""
    text = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    m = re.match(r"---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", text, re.S)
    if not m:
        raise BuildError(f"{where}: missing front matter (file must start with a --- block)")
    lines = m.group(1).split("\n")
    meta: dict = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        km = re.match(r"([A-Za-z_][\w-]*):[ \t]*(.*)$", line)
        if not km:
            raise BuildError(f"{where}: cannot read front matter line: {line!r}")
        key, value = km.group(1), _strip_comment(km.group(2).strip())
        if re.fullmatch(r"[|>][+-]?", value):
            block = []
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in " \t"):
                block.append(lines[i])
                i += 1
            while block and not block[-1].strip():
                block.pop()
            indents = [len(b) - len(b.lstrip()) for b in block if b.strip()]
            cut = min(indents) if indents else 0
            block = [b[cut:] for b in block]
            if value[0] == "|":
                meta[key] = "\n".join(block)
            else:
                paras = "\n".join(block).split("\n\n")
                meta[key] = "\n".join(" ".join(p.split("\n")) for p in paras)
        elif value == "":
            items = []
            while i < len(lines) and re.match(r"\s+-\s+", lines[i]):
                items.append(_unquote(re.sub(r"^\s+-\s+", "", lines[i]).strip()))
                i += 1
            meta[key] = items if items else ""
        elif value.startswith("["):
            if not value.endswith("]"):
                raise BuildError(f"{where}: list for '{key}' must close on the same line")
            meta[key] = _split_inline_list(value[1:-1])
        elif value.lower() in ("true", "false"):
            meta[key] = value.lower() == "true"
        else:
            meta[key] = _unquote(value)
    return meta, m.group(2)


# --------------------------------------------------------------------------- #
# Markdown (the subset the notes need; raw HTML in the body is escaped)
# --------------------------------------------------------------------------- #

def _safe_url(url: str) -> str | None:
    url = re.sub(r"[\x00-\x20]+", "", url)
    scheme = urlsplit(url).scheme.lower()
    if scheme and scheme not in ("http", "https", "mailto"):
        return None
    return url


def _is_external(url: str) -> bool:
    return urlsplit(url).scheme.lower() in ("http", "https")


# A URL may contain one level of balanced parentheses, e.g. photo_(3).webp
_URL = r"((?:[^()\s]|\([^()\s]*\))+)"
_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(' + _URL + r'(?:\s+"([^"]*)")?\)')
_LINK_RE = re.compile(r'\[([^\]]+)\]\(' + _URL + r'(?:\s+"([^"]*)")?\)')


class Resolver:
    """Turns site-root-relative URLs from post bodies into URLs that work
    from the page that will contain them (depth) or in the feeds (absolute)."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, url: str) -> str:
        if _is_external(url) or url.startswith(("mailto:", "#")):
            return url
        path = url.lstrip("/")
        return self.prefix + quote(path, safe="/:#?=&%~+")


def render_inline(text: str, resolve: Resolver) -> str:
    stash: list[str] = []

    def keep(fragment: str) -> str:
        stash.append(fragment)
        return f"\x00{len(stash) - 1}\x00"

    text = text.replace("\x00", "")
    text = re.sub(r"`([^`\n]+)`", lambda m: keep(f"<code>{html.escape(m.group(1))}</code>"), text)

    def image(m):
        src = _safe_url(m.group(2))
        if src is None:
            return ""
        title = f' title="{html.escape(m.group(3))}"' if m.group(3) else ""
        return keep(
            f'<img src="{html.escape(resolve(src))}" alt="{html.escape(m.group(1))}"{title} '
            'loading="lazy" decoding="async" />'
        )

    text = _IMAGE_RE.sub(image, text)

    def link(m):
        href = _safe_url(m.group(2))
        label = render_inline(m.group(1), resolve)
        if href is None:
            return keep(label)
        title = f' title="{html.escape(m.group(3))}"' if m.group(3) else ""
        extra = ' target="_blank" rel="noopener noreferrer"' if _is_external(href) else ""
        return keep(f'<a href="{html.escape(resolve(href))}"{title}{extra}>{label}</a>')

    text = _LINK_RE.sub(link, text)

    text = html.escape(text, quote=False)
    # Keep a value with its unit ("3.3 V", "12 V", "40 mA") on one line.
    text = re.sub(r"(?<=\d) (?=(?:[kMmµu]?(?:V|A|W|Hz|Ah|Wh|Ω|F|g|m)|°C|dB)\b)", "\u00a0", text)

    def bare_url(m):
        url = m.group(1)
        return keep(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
        )

    text = re.sub(r"(?<![\w\"'=>/])(https?://[^\s<]*[^\s<.,;:!?)\]'\"])", bare_url, text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w_])__(?=\S)(.+?)(?<=\S)__(?![\w_])", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![*\w])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_(?=[^\s_])(.+?)(?<=[^\s_])_(?![\w_])", r"<em>\1</em>", text)
    text = re.sub(r" {2,}\n", "<br />\n", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)


def _split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render_list(lines: list[str], i: int, inline) -> tuple[str, int]:
    """Render the list starting at lines[i] (one level of nesting) and return
    the HTML with the index of the first line after the list."""
    marker = re.compile(r"(\s*)([-*+]|\d+[.)])\s+(.*)")
    ordered = lines[i].lstrip()[0].isdigit()
    items: list[dict] = []
    while i < len(lines):
        m = marker.match(lines[i])
        if m and not m.group(1) and m.group(2)[0].isdigit() == ordered:
            items.append({"text": [m.group(3)], "children": [], "child_ordered": False})
        elif m and m.group(1) and items:
            items[-1]["children"].append(m.group(3))
            items[-1]["child_ordered"] = m.group(2)[0].isdigit()
        elif items and lines[i].strip() and lines[i][:1] in " \t":
            items[-1]["text"].append(lines[i].strip())
        else:
            break
        i += 1

    def li(item: dict) -> str:
        nested = ""
        if item["children"]:
            tag = "ol" if item["child_ordered"] else "ul"
            nested = f"<{tag}>" + "".join(f"<li>{inline(c)}</li>" for c in item["children"]) + f"</{tag}>"
        return f"<li>{inline(' '.join(item['text']))}{nested}</li>"

    tag = "ol" if ordered else "ul"
    return f"<{tag}>" + "".join(li(it) for it in items) + f"</{tag}>", i


def render_markdown(source: str, resolve: Resolver) -> str:
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    inline = lambda s: render_inline(s, resolve)  # noqa: E731
    i = 0

    def starts_block(s: str) -> bool:
        return bool(
            re.match(r"(#{1,6}\s|```|>\s?|[-*+]\s+|\d+[.)]\s+|(-{3,}|\*{3,}|_{3,})\s*$)", s)
        )

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        fence = re.match(r"```\s*([\w+-]*)\s*$", line)
        if fence:
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{html.escape(fence.group(1))}"' if fence.group(1) else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(code))}</code></pre>")
            continue

        heading = re.match(r"(#{1,6})\s+(.*?)(?:\s+#+)?\s*$", line)
        if heading:
            # The post title is the page's h1, so body headings start at h2.
            level = min(max(len(heading.group(1)), 2), 4)
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if re.match(r"(-{3,}|\*{3,}|_{3,})\s*$", line):
            out.append("<hr />")
            i += 1
            continue

        if line.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote>{render_markdown(chr(10).join(quote_lines), resolve)}</blockquote>")
            continue

        list_match = re.match(r"([-*+]|\d+[.)])\s+", line)
        if list_match:
            list_html, i = render_list(lines, i, inline)
            out.append(list_html)
            continue

        if (
            "|" in line
            and i + 1 < len(lines)
            and re.match(r"\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", lines[i + 1])
        ):
            head = _split_row(line)
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            thead = "".join(f"<th scope=\"col\">{inline(c)}</th>" for c in head)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in rows
            )
            out.append(
                f'<div class="table-scroll"><table><thead><tr>{thead}</tr></thead>'
                f"<tbody>{tbody}</tbody></table></div>"
            )
            continue

        para = [line.rstrip("\n")]
        i += 1
        while i < len(lines) and lines[i].strip() and not starts_block(lines[i]):
            para.append(lines[i])
            i += 1
        text = "\n".join(para)
        figure = _IMAGE_RE.fullmatch(text.strip())
        if figure:
            caption = f"<figcaption>{html.escape(figure.group(3))}</figcaption>" if figure.group(3) else ""
            out.append(f"<figure>{inline(text.strip())}{caption}</figure>")
        else:
            out.append(f"<p>{inline(text)}</p>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Posts
# --------------------------------------------------------------------------- #

@dataclass
class Post:
    path: Path
    title: str
    slug: str
    when: datetime | None
    type: str
    status: str
    excerpt: str
    body: str
    tags: list[str] = field(default_factory=list)
    image: str = ""
    image_alt: str = ""
    canonical_url: str = ""
    linkedin: str = ""
    sample: bool = False
    stage: str = ""
    project: str = ""
    date_precision: str = "day"
    highlights: list[str] = field(default_factory=list)

    @property
    def iso_date(self) -> str:
        if not self.when:
            return ""
        if self.date_precision == "month":
            return self.when.strftime("%Y-%m")
        return self.when.date().isoformat()

    @property
    def display_date(self) -> str:
        d = self.when
        if not d:
            return ""
        if self.date_precision == "month":
            return f"{MONTHS[d.month - 1]} {d.year}"
        return f"{d.day} {MONTHS[d.month - 1]} {d.year}"

    @property
    def type_label(self) -> str:
        return TYPES[self.type]

    @property
    def url_path(self) -> str:
        return f"notes/{self.slug}.html"

    @property
    def url(self) -> str:
        return f"{SITE_URL}/{self.url_path}"

    @property
    def minutes(self) -> int:
        return max(1, round(len(re.findall(r"\w+", self.body)) / WORDS_PER_MINUTE))

    @property
    def image_url(self) -> str:
        return self.image if _is_external(self.image) else f"{SITE_URL}/{self.image.lstrip('/')}"


def _as_str(meta: dict, key: str, where: str) -> str:
    value = meta.get(key, "")
    if isinstance(value, (list, bool)):
        raise BuildError(f"{where}: '{key}' must be text")
    return str(value).strip()


def load_post(path: Path) -> Post:
    where = path.relative_to(ROOT).as_posix()
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), where)

    unknown = sorted(set(meta) - KNOWN_KEYS)
    if unknown:
        raise BuildError(f"{where}: unknown front matter key(s): {', '.join(unknown)}")

    title = _as_str(meta, "title", where)
    excerpt = " ".join(_as_str(meta, "excerpt", where).split())
    for key, value in (("title", title), ("excerpt", excerpt)):
        if not value:
            raise BuildError(f"{where}: '{key}' is required")

    type_ = _as_str(meta, "type", where)
    if type_ not in TYPES:
        raise BuildError(f"{where}: 'type' must be one of {', '.join(TYPES)} (got {type_!r})")

    status = _as_str(meta, "status", where) or "published"
    if status not in STATUSES:
        raise BuildError(f"{where}: 'status' must be one of {', '.join(STATUSES)}")

    raw_date = _as_str(meta, "date", where)
    when = None
    if raw_date:
        try:
            when = datetime.fromisoformat(raw_date).replace(tzinfo=None)
        except ValueError:
            raise BuildError(f"{where}: 'date' must look like 2026-10-21 (or be left out)") from None

    slug = _as_str(meta, "slug", where) or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    if not SLUG_RE.match(slug) or slug in RESERVED_SLUGS:
        raise BuildError(f"{where}: slug {slug!r} must be lowercase-with-hyphens and not reserved")

    if len(excerpt) > EXCERPT_MAX:
        raise BuildError(f"{where}: excerpt is {len(excerpt)} characters (max {EXCERPT_MAX})")
    if len(excerpt) > EXCERPT_WARN:
        print(f"warning: {where}: excerpt is {len(excerpt)} characters; cards read best under {EXCERPT_WARN}")

    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    image = _as_str(meta, "image", where)
    image_alt = _as_str(meta, "image_alt", where)
    if image:
        if not image_alt:
            raise BuildError(f"{where}: 'image_alt' is required when 'image' is set")
        if not _is_external(image) and not (ROOT / image.lstrip("/")).is_file():
            raise BuildError(f"{where}: image not found: {image}")

    canonical = _as_str(meta, "canonical_url", where)
    if canonical and not _is_external(canonical):
        raise BuildError(f"{where}: 'canonical_url' must be an http(s) URL")

    body = body.strip()
    if not body:
        raise BuildError(f"{where}: the post body is empty")

    highlights = meta.get("highlights", [])
    if isinstance(highlights, str):
        highlights = [highlights] if highlights.strip() else []
    highlights = [" ".join(str(h).split()) for h in highlights if str(h).strip()]
    if len(highlights) > 4:
        raise BuildError(f"{where}: at most 4 'highlights' (got {len(highlights)})")

    precision = _as_str(meta, "date_precision", where) or "day"
    if precision not in ("day", "month"):
        raise BuildError(f"{where}: 'date_precision' must be day or month")
    if precision == "month" and when is None:
        raise BuildError(f"{where}: 'date_precision' needs a 'date'")

    return Post(
        path=path, title=title, slug=slug, when=when, type=type_, status=status,
        excerpt=excerpt, body=body, tags=[str(t) for t in tags], image=image,
        image_alt=image_alt, canonical_url=canonical,
        linkedin=_as_str(meta, "linkedin", where), sample=bool(meta.get("sample", False)),
        stage=_as_str(meta, "stage", where), project=_as_str(meta, "project", where),
        date_precision=precision, highlights=highlights,
    )


def load_posts() -> list[Post]:
    posts, seen = [], {}
    for path in sorted(CONTENT_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        post = load_post(path)
        if post.slug in seen:
            raise BuildError(f"duplicate slug {post.slug!r}: {seen[post.slug].name} and {path.name}")
        seen[post.slug] = path
        posts.append(post)
    published = [p for p in posts if p.status == "published"]
    # Undated posts (a stage instead of a date) sort after every dated one.
    published.sort(key=lambda p: (p.when or datetime.min, p.slug), reverse=True)
    return published


# --------------------------------------------------------------------------- #
# HTML
# --------------------------------------------------------------------------- #

def esc(value: str) -> str:
    return html.escape(value, quote=True)


def asset(path: str, prefix: str) -> str:
    return path if _is_external(path) else prefix + quote(path.lstrip("/"), safe="/:")


ACCENTS = 5  # number of project colours defined in style.css (data-accent 1..5)


def accent_map(posts: list[Post]) -> dict[str, int]:
    """Give each project a colour, in order of first appearance."""
    colours: dict[str, int] = {}
    for post in posts:
        key = post.project or post.type_label
        if key not in colours:
            colours[key] = len(colours) % ACCENTS + 1
    return colours


def log_entry(post: Post, prefix: str, heading: str, show_type: bool, images: bool = True) -> str:
    """One entry in the notebook timeline. prefix is the path back to the site root."""
    meta = []
    if show_type:
        meta.append(f"<span>{esc(post.type_label)}</span>")
    if post.when and post.date_precision == "day":
        meta.append(f'<time datetime="{post.iso_date}">{post.when.day} {MONTHS[post.when.month - 1]}</time>')
    if post.stage:
        meta.append(f"<span>{esc(post.stage)}</span>")
    if post.type == "article" and post.minutes >= 2:
        meta.append(f"<span>{post.minutes} min read</span>")
    meta_html = f'\n                    <p class="log__meta">{"".join(meta)}</p>' if meta else ""
    if post.highlights:
        items = "".join(f"<li>{render_inline(h, Resolver(prefix))}</li>" for h in post.highlights)
        detail = f'<ul class="log__highlights">{items}</ul>'
    else:
        detail = f'<p class="log__summary">{esc(post.excerpt)}</p>'
    thumb = ""
    if post.image and images:
        thumb = (
            f'\n                  <img class="log__thumb" src="{esc(asset(post.image, prefix))}" alt="" '
            f'width="400" height="300" loading="lazy" decoding="async" />'
        )
    classes = "log__entry log__entry--image" if thumb else "log__entry"
    return f"""                <li class="{classes}" data-category="{post.type}">
                  <div class="log__text">{meta_html}
                    <{heading} class="log__title"><a href="{prefix}{post.url_path}">{esc(post.title)}</a></{heading}>
                    {detail}
                  </div>{thumb}
                </li>"""


def _group(posts: list[Post], key) -> list[tuple[str, list[Post]]]:
    """Group posts by key, keeping groups in order of first appearance."""
    groups: dict[str, list[Post]] = {}
    for post in posts:
        groups.setdefault(key(post), []).append(post)
    return list(groups.items())


def log_list(posts: list[Post], prefix: str, month_heading: str, entry_heading: str, images: bool = True) -> str:
    """The notebook timeline: one block per month, and within it one block per
    project, so each project is named once with its own colour."""
    colours = accent_map(posts)
    mixed = len({p.type for p in posts}) > 1
    project = lambda p: p.project or p.type_label  # noqa: E731
    out = []
    for month, members in _group(posts, lambda p: p.when.strftime("%Y-%m") if p.when else "undated"):
        if month == "undated":
            label, datetime_attr = "Undated", ""
        else:
            first = members[0].when
            label, datetime_attr = f"{MONTH_NAMES[first.month - 1]} {first.year}", f' datetime="{month}"'
        blocks = []
        for name, entries in _group(members, project):
            items = "\n".join(log_entry(p, prefix, entry_heading, mixed, images) for p in entries)
            blocks.append(f"""            <li class="log__project-group" data-accent="{colours[name]}">
              <p class="log__project">{esc(name)}</p>
              <ol class="log__entries">
{items}
              </ol>
            </li>""")
        projects_html = "\n".join(blocks)
        out.append(f"""        <div class="log__group">
          <{month_heading} class="log__month"><time{datetime_attr}>{label}</time></{month_heading}>
          <ol class="log__projects">
{projects_html}
          </ol>
        </div>""")
    return '      <div class="log">\n' + "\n".join(out) + "\n      </div>"


def home_block(posts: list[Post]) -> str:
    if not posts:
        return ""
    # No thumbnails here: the project cards just above already show the hardware.
    timeline = textwrap.indent(log_list(posts[:HOME_COUNT], "", "h3", "h4", images=False), "  ")
    return f"""    <section class="section section--notebook" aria-labelledby="notes-title">
      <div class="container notebook">
        <div class="notebook__intro">
          <h2 id="notes-title" class="section-header__label notebook__label">{SECTION_TITLE}</h2>
          <p class="notebook__lede">{SECTION_DESC}</p>
          <a class="text-link notebook__link" href="notes/index.html">View all {SECTION_NOUN}</a>
        </div>
{timeline}
      </div>
    </section>"""


def _fragment(source: str, start: str, end: str) -> str:
    a = source.find(start)
    b = source.find(end, a)
    if a < 0 or b < 0:
        raise BuildError(f"index.html: could not find {start!r} ... {end!r} to reuse the site chrome")
    return source[a:b + len(end)]


def _deepen(fragment: str) -> str:
    """Rewrite root-relative hrefs/srcs so a fragment works from notes/."""
    def fix(m):
        value = m.group(2)
        if re.match(r"([a-z][a-z0-9+.-]*:|#|/)", value, re.I):
            return m.group(0)
        return f'{m.group(1)}="../{value}"'
    return re.sub(r'\b(href|src)="([^"]*)"', fix, fragment)


def site_chrome(index_html: str) -> tuple[str, str]:
    nav = _deepen(_fragment(index_html, '<nav class="nav"', "</nav>"))
    footer = _deepen(_fragment(index_html, '<footer class="footer"', "</footer>"))
    return nav, footer


def head(*, title: str, description: str, canonical: str, og_type: str, image: str,
         image_alt: str, noindex: bool, extra: str = "") -> str:
    robots = '\n  <meta name="robots" content="noindex, nofollow" />' if noindex else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />{robots}
  <meta name="theme-color" content="#556241" />
  <link rel="canonical" href="{esc(canonical)}" />
  <link rel="icon" href="../favicon.ico" sizes="any" />
  <link rel="icon" href="../assets/brand/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="../assets/brand/apple-touch-icon.png" sizes="180x180" />
  <link rel="manifest" href="../site.webmanifest" />
  <link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)} — {SECTION_NOUN}" href="feed.xml" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:url" content="{esc(canonical)}" />
  <meta property="og:site_name" content="{esc(SITE_NAME)}" />
  <meta property="og:image" content="{esc(image)}" />
  <meta property="og:image:alt" content="{esc(image_alt)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="preload" href="../assets/fonts/InterVariable.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="../assets/css/style.css" />{extra}
</head>"""


def page(head_html: str, nav: str, main: str, footer: str) -> str:
    return f"""{head_html}
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>

  {nav}

  <main id="main-content">
{main}
  </main>

  {footer}

  <script src="../assets/js/main.js"></script>
</body>
</html>
"""


def post_page(post: Post, older: Post | None, nav: str, footer: str) -> str:
    social_image = post.image_url if post.image else f"{SITE_URL}/{DEFAULT_IMAGE}"
    social_alt = post.image_alt if post.image else f"{SITE_NAME} — ecologist and environmental technologist"
    canonical = post.canonical_url or post.url
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article" if post.type == "article" else "BlogPosting",
        "headline": post.title,
        "description": post.excerpt,
        "author": {"@type": "Person", "name": AUTHOR, "url": f"{SITE_URL}/"},
        "mainEntityOfPage": canonical,
        "keywords": post.tags,
    }
    if post.when:
        jsonld["datePublished"] = post.iso_date
    if post.image:
        jsonld["image"] = post.image_url
    ld = json.dumps(jsonld, indent=2, ensure_ascii=False).replace("</", "<\\/")
    published = f'\n  <meta property="article:published_time" content="{post.iso_date}" />' if post.when else ""
    extra = (
        f'{published}'
        f'\n  <script type="application/ld+json">\n{textwrap.indent(ld, "  ")}\n  </script>'
    )
    head_html = head(
        title=f"{post.title} | {SITE_NAME}", description=post.excerpt, canonical=canonical,
        og_type="article", image=social_image, image_alt=social_alt, noindex=post.sample, extra=extra,
    )

    meta = []
    if post.when:
        meta.append(f'<time datetime="{post.iso_date}">{post.display_date}</time>')
    if post.stage:
        meta.append(f"<span>{esc(post.stage)}</span>")
    if post.project:
        meta.append(f"<span>{esc(post.project)}</span>")
    if post.minutes >= 2:
        meta.append(f"<span>{post.minutes} min read</span>")
    if post.tags:
        meta.append(f'<span>{esc(", ".join(post.tags))}</span>')

    figure = ""
    if post.image:
        figure = f"""    <figure class="article-figure">
      <div class="article-body"><img src="{esc(asset(post.image, '../'))}" alt="{esc(post.image_alt)}" loading="eager" decoding="async" /></div>
    </figure>
"""
    origin = ""
    if post.canonical_url:
        host = urlsplit(post.canonical_url).netloc.removeprefix("www.")
        origin = (
            f'\n        <p class="article-origin">Originally published at '
            f'<a href="{esc(post.canonical_url)}" target="_blank" rel="noopener noreferrer">{esc(host)}</a>.</p>'
        )
    body_html = render_markdown(post.body, Resolver("../"))
    if older:
        aside_label, aside_title, aside_href, aside_text = (
            "Previous note", older.title, older.slug + ".html", older.excerpt
        )
    else:
        aside_label, aside_title, aside_href, aside_text = (
            "More", f"All {SECTION_NOUN}", "index.html", SECTION_DESC
        )

    main = f"""    <header class="article-header">
      <div class="article-body">
        <a href="index.html" class="back-link">All {SECTION_NOUN}</a>
        <p class="article-kicker"><span class="note-type" data-note-type="{post.type}">{esc(post.type_label)}</span></p>
        <h1>{esc(post.title)}</h1>
        <p class="article-header__intro">{esc(post.excerpt)}</p>
        <div class="article-meta">{"".join(meta)}</div>
      </div>
    </header>
{figure}
    <article class="article-content">
      <div class="article-body">
{body_html}{origin}
      </div>
    </article>

    <aside class="next-item" aria-labelledby="related-title">
      <div class="article-body">
        <p class="next-item__label">{aside_label}</p>
        <h2 id="related-title"><a href="{aside_href}">{esc(aside_title)} →</a></h2>
        <p>{esc(aside_text)}</p>
      </div>
    </aside>"""
    return page(head_html, nav, main, footer)


def index_page(posts: list[Post], nav: str, footer: str) -> str:
    desc = f"{SECTION_DESC} Tom Armstrong's current hardware, software and monitoring projects."
    head_html = head(
        title=f"{SECTION_TITLE} | {SITE_NAME}", description=desc, canonical=f"{SITE_URL}/notes/index.html",
        og_type="website", image=f"{SITE_URL}/{DEFAULT_IMAGE}",
        image_alt=f"{SITE_NAME} — ecologist and environmental technologist", noindex=False,
        extra='\n  <noscript><style>.filter-bar{display:none}</style></noscript>',
    )
    present = [t for t in TYPES if any(p.type == t for p in posts)]
    filters = ""
    if len(present) > 1:
        buttons = ['<button type="button" class="filter-bar__btn" data-filter="all" aria-pressed="true">All</button>']
        buttons += [
            f'<button type="button" class="filter-bar__btn" data-filter="{t}" aria-pressed="false">{esc(TYPES[t])}</button>'
            for t in present
        ]
        filters = (
            '\n        <div class="filter-bar" role="group" aria-label="Filter notes by type" '
            'data-filter-group data-filter-targets=".log__entry">\n          '
            + "\n          ".join(buttons) + "\n        </div>"
        )
    if posts:
        listing = log_list(posts, "../", "h2", "h3").strip()
    else:
        listing = '<p class="note-empty">Nothing published yet.</p>'
    main = f"""    <header class="hero hero--compact">
      <div class="container">
        <p class="hero__eyebrow">{SECTION_LABEL}</p>
        <h1 class="hero__title hero__title--page">{SECTION_TITLE}</h1>
        <p class="hero__subtitle">{SECTION_DESC}</p>
      </div>
    </header>

    <section class="section section--compact notes-index" aria-label="All {SECTION_NOUN}">
      <div class="container">{filters}
        {listing}
        <p class="note-feed-link"><a class="text-link" href="feed.xml">Subscribe via RSS</a></p>
      </div>
    </section>"""
    return page(head_html, nav, main, footer)


# --------------------------------------------------------------------------- #
# Feeds
# --------------------------------------------------------------------------- #

def feed_json(posts: list[Post]) -> str:
    items = []
    for p in posts:
        items.append({
            "title": p.title,
            "slug": p.slug,
            "url": p.url,
            "date": p.iso_date or None,
            "date_precision": p.date_precision,
            "stage": p.stage or None,
            "project": p.project or None,
            "highlights": p.highlights,
            "type": p.type,
            "type_label": p.type_label,
            "tags": p.tags,
            "excerpt": p.excerpt,
            "image": p.image_url if p.image else None,
            "image_alt": p.image_alt or None,
            "canonical_url": p.canonical_url or None,
            "linkedin": p.linkedin or None,
            "reading_minutes": p.minutes,
            "sample": p.sample,
            "body_markdown": p.body,
            "body_html": render_markdown(p.body, Resolver(SITE_URL + "/")),
        })
    return json.dumps({"site": SITE_URL, "generated_from": "content/notes/*.md", "posts": items},
                      indent=2, ensure_ascii=False) + "\n"


def feed_xml(posts: list[Post]) -> str:
    items = []
    for p in [p for p in posts if not p.sample and p.when]:
        pub = format_datetime(p.when.replace(tzinfo=timezone.utc))
        cats = "".join(f"<category>{esc(t)}</category>" for t in [p.type_label, *p.tags])
        body = render_markdown(p.body, Resolver(SITE_URL + "/")).replace("]]>", "]]]]><![CDATA[>")
        items.append(
            f"    <item>\n      <title>{esc(p.title)}</title>\n      <link>{esc(p.url)}</link>\n"
            f'      <guid isPermaLink="true">{esc(p.url)}</guid>\n      <pubDate>{pub}</pubDate>\n'
            f"      {cats}\n      <description>{esc(p.excerpt)}</description>\n"
            f"      <content:encoded><![CDATA[{body}]]></content:encoded>\n    </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
        f"    <title>{esc(SITE_NAME)} — {SECTION_NOUN}</title>\n    <link>{SITE_URL}/notes/index.html</link>\n"
        f'    <atom:link href="{SITE_URL}/notes/feed.xml" rel="self" type="application/rss+xml" />\n'
        f"    <description>{esc(SECTION_DESC)}</description>\n"
        "    <language>en</language>\n" + "".join(f"{item}\n" for item in items) + "  </channel>\n</rss>\n"
    )


def sitemap_block(posts: list[Post]) -> str:
    urls = [f"{SITE_URL}/notes/index.html"] + [p.url for p in posts if not p.sample]
    return "\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in urls)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def replace_between(source: str, name: str, replacement: str, where: str) -> str:
    pattern = re.compile(rf"([ \t]*)<!-- {name}:start -->.*?<!-- {name}:end -->", re.S)
    m = pattern.search(source)
    if not m:
        raise BuildError(f"{where}: missing <!-- {name}:start --> / <!-- {name}:end --> markers")
    indent = m.group(1)
    block = f"{indent}<!-- {name}:start -->\n{replacement}\n{indent}<!-- {name}:end -->" if replacement else \
        f"{indent}<!-- {name}:start -->\n{indent}<!-- {name}:end -->"
    return source[:m.start()] + block + source[m.end():]


def build() -> int:
    posts = load_posts()
    index_src = (ROOT / "index.html").read_text(encoding="utf-8")
    nav, footer = site_chrome(index_src)

    outputs: dict[Path, str] = {}
    for n, post in enumerate(posts):
        older = posts[n + 1] if n + 1 < len(posts) else None
        outputs[OUT_DIR / f"{post.slug}.html"] = post_page(post, older, nav, footer)
    outputs[OUT_DIR / "index.html"] = index_page(posts, nav, footer)
    outputs[OUT_DIR / "feed.json"] = feed_json(posts)
    outputs[OUT_DIR / "feed.xml"] = feed_xml(posts)
    outputs[ROOT / "index.html"] = replace_between(index_src, "notes", home_block(posts), "index.html")
    sitemap = ROOT / "sitemap.xml"
    outputs[sitemap] = replace_between(sitemap.read_text(encoding="utf-8"), "notes", sitemap_block(posts), "sitemap.xml")

    changed = []
    OUT_DIR.mkdir(exist_ok=True)
    for path, content in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8", newline="\n")
            changed.append(path.relative_to(ROOT).as_posix())
    for stale in sorted(OUT_DIR.glob("*.html")):
        if stale not in outputs:
            stale.unlink()
            changed.append(f"{stale.relative_to(ROOT).as_posix()} (removed)")

    for p in posts:
        if p.sample:
            print(f"warning: {p.path.name} is marked sample: true (noindex, left out of the sitemap and RSS)")
    print(f"{len(posts)} published note(s); {len(changed)} file(s) changed")
    for c in changed:
        print(f"  {c}")
    return 0


def new_post(title: str, type_: str, slug: str | None) -> int:
    slug = slug or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not SLUG_RE.match(slug):
        raise BuildError(f"cannot make a slug from {title!r}; pass --slug")
    today = date.today().isoformat()
    path = CONTENT_DIR / f"{today}-{slug}.md"
    if path.exists():
        raise BuildError(f"{path.relative_to(ROOT)} already exists")
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
title: {json.dumps(title, ensure_ascii=False)}
date: {today}
type: {type_}
status: draft
excerpt: One or two sentences for the homepage card.
tags: []
linkedin: |
  Optional LinkedIn-ready text. Delete this key to fall back to the excerpt.
---

Write the post here in Markdown.
""",
        encoding="utf-8",
    )
    print(f"created {path.relative_to(ROOT)} (status: draft)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("build", help="build the notes feed (default)")
    new = sub.add_parser("new", help="create a draft post from a template")
    new.add_argument("title")
    new.add_argument("-t", "--type", choices=list(TYPES), default="project-update")
    new.add_argument("--slug")
    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            return new_post(args.title, args.type, args.slug)
        return build()
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
