#!/usr/bin/env python3
'''
Tiny dependency-free static site builder for MeanwhX.

Why this exists:
- shared header/footer without a JavaScript framework
- Markdown-ish notes that are easy to edit in GitHub
- no package manager, database, CMS, or external build dependency
- GitHub Pages can build it with Python already available on the runner

Supported note Markdown:
- paragraphs
- ## and ### headings
- unordered lists beginning with "- "
- blockquotes beginning with "> "
- **bold**, *italic*, `code`, and [links](https://...)
- --- horizontal rules

HTML in note files is escaped intentionally.
'''
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import shutil
import tomllib
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

with (ROOT / "site.json").open("r", encoding="utf-8") as f:
    SITE = json.load(f)

BASE_PATH = os.environ.get("SITE_BASE_PATH", SITE.get("base_path", "")).strip()
if BASE_PATH and not BASE_PATH.startswith("/"):
    BASE_PATH = "/" + BASE_PATH
BASE_PATH = BASE_PATH.rstrip("/")

SITE_URL = os.environ.get("SITE_URL", SITE.get("site_url", "")).strip().rstrip("/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def replace_tokens(value: str, mapping: dict[str, object]) -> str:
    merged = {**SITE, **mapping}
    for key, raw in merged.items():
        if isinstance(raw, (str, int, float)):
            value = value.replace("{{" + key + "}}", str(raw))
    return value


def with_base(value: str) -> str:
    '''Prefix root-relative href/src/action attributes for project GitHub Pages.'''
    if not BASE_PATH:
        return value
    pattern = re.compile(r'(?P<attr>\b(?:href|src|action))="/(?!/)')
    return pattern.sub(lambda m: f'{m.group("attr")}="{BASE_PATH}/', value)


def absolute_url(path: str) -> str:
    if not SITE_URL:
        return ""
    if not path.startswith("/"):
        path = "/" + path
    if BASE_PATH and not path.startswith(BASE_PATH + "/"):
        path = BASE_PATH + path
    return SITE_URL + path


def header(active: str | None) -> str:
    items = [
        ("Home", "/"),
        ("Studio", "/studio/"),
        ("π + Bear", "/pi-bear/"),
        ("Notes", "/notes/"),
        ("Community", "/community/"),
        ("About", "/about/"),
    ]
    desktop = []
    mobile = []
    for label, href in items:
        current = ' aria-current="page"' if active == label else ""
        desktop.append(f'<a href="{href}"{current}>{esc(label)}</a>')
        mobile.append(f'<a href="{href}"{current}>{esc(label)}</a>')
    return f'''
<header class="site-header">
  <div class="shell header-inner">
    <a class="brand" href="/" aria-label="{esc(SITE["name"])} home">
      <span class="meanwh-word">MEANWH<span>[x]</span></span>
    </a>
    <nav class="desktop-nav" aria-label="Primary navigation">
      {"".join(desktop)}
    </nav>
    <a class="header-write" href="/contact/">Write to us</a>
    <details class="mobile-menu" data-mobile-menu>
      <summary>Menu</summary>
      <div class="mobile-panel">
        <nav aria-label="Mobile navigation">
          {"".join(mobile)}
          <a href="/support/">Support &amp; collaborate</a>
          <a href="/contact/">Contact</a>
        </nav>
      </div>
    </details>
  </div>
</header>
'''.strip()


def footer() -> str:
    return f'''
<footer class="site-footer">
  <div class="shell footer-main">
    <div class="footer-intro">
      <a class="brand" href="/">
        <span class="meanwh-word">MEANWH<span>[x]</span></span>
      </a>
      <p>{esc(SITE["tagline"])}</p>
    </div>
    <div class="footer-group">
      <p>Rooms</p>
      <a href="/studio/">{esc(SITE["studio_name"])}</a>
      <a href="/pi-bear/">{esc(SITE["cafe_name"])}</a>
      <a href="/notes/">Notes</a>
      <a href="/community/">Community</a>
    </div>
    <div class="footer-group">
      <p>Practical</p>
      <a href="/support/">Support &amp; collaborate</a>
      <a href="/rights/">Rights &amp; use</a>
      <a href="/contact/">Contact</a>
    </div>
  </div>
  <div class="shell footer-bottom">
    <p>© <span data-year>{dt.datetime.now().year}</span> {esc(SITE["name"])}. {esc(SITE["status"])}.</p>
    <p>Built as a lightweight static site. No tracking by default.</p>
  </div>
</footer>
'''.strip()


def safe_link(url: str) -> str:
    raw = url.strip()
    parsed = urlparse(raw)
    if parsed.scheme and parsed.scheme not in {"http", "https", "mailto"}:
        return "#"
    if raw.startswith("//"):
        return "#"
    return html.escape(raw, quote=True)


def inline_markdown(text: str) -> str:
    value = html.escape(text, quote=False)

    code_chunks: list[str] = []

    def hold_code(match: re.Match[str]) -> str:
        code_chunks.append(f"<code>{match.group(1)}</code>")
        return f"\x00CODE{len(code_chunks)-1}\x00"

    value = re.sub(r"`([^`]+)`", hold_code, value)

    def repl_link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = safe_link(html.unescape(match.group(2)))
        external = url.startswith("http://") or url.startswith("https://")
        attrs = ' rel="noreferrer"' if external else ""
        return f'<a href="{url}"{attrs}>{label}</a>'

    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl_link, value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)

    for i, chunk in enumerate(code_chunks):
        value = value.replace(f"\x00CODE{i}\x00", chunk)

    return value


def markdown_to_html(markdown: str, preserve_linebreaks: bool = False) -> str:
    lines = markdown.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    quote_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            sep = "<br>\n" if preserve_linebreaks else " "
            text = sep.join(inline_markdown(line.strip()) for line in paragraph)
            out.append(f"<p>{text}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            items = "".join(f"<li>{inline_markdown(item)}</li>" for item in list_items)
            out.append(f"<ul>{items}</ul>")
            list_items = []

    def flush_quote() -> None:
        nonlocal quote_lines
        if quote_lines:
            text = " ".join(inline_markdown(x) for x in quote_lines)
            out.append(f"<blockquote><p>{text}</p></blockquote>")
            quote_lines = []

    def flush_all() -> None:
        flush_paragraph()
        flush_list()
        flush_quote()

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_all()
            continue

        if stripped == "---":
            flush_all()
            out.append("<hr>")
            continue

        if stripped.startswith("### "):
            flush_all()
            out.append(f"<h3>{inline_markdown(stripped[4:])}</h3>")
            continue

        if stripped.startswith("## "):
            flush_all()
            out.append(f"<h2>{inline_markdown(stripped[3:])}</h2>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            flush_quote()
            list_items.append(stripped[2:].strip())
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            quote_lines.append(stripped[2:].strip())
            continue

        flush_list()
        flush_quote()
        paragraph.append(stripped)

    flush_all()
    return "\n".join(out)


def parse_note(path: Path) -> dict:
    raw = read(path)
    if not raw.startswith("+++\n"):
        raise ValueError(f"{path}: note must start with TOML front matter delimited by +++")
    try:
        _, front, body = raw.split("+++", 2)
    except ValueError as exc:
        raise ValueError(f"{path}: invalid front matter") from exc

    data = tomllib.loads(front)
    required = ["title", "author", "date", "type", "tags", "summary", "slug"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{path}: missing front matter: {', '.join(missing)}")

    data["body_markdown"] = body.strip()
    data["source"] = path.name
    return data


def human_date(value: str) -> str:
    parsed = dt.date.fromisoformat(value)
    # Cross-platform day without a leading zero.
    return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def render_notes_list(notes: list[dict]) -> str:
    rows = []
    for note in notes:
        url = f'/notes/{note["slug"]}/'
        rows.append(f'''
<a class="note-teaser" href="{url}">
  <div class="note-teaser-meta">{esc(note["type"])}<br>{esc(human_date(note["date"]))}</div>
  <div>
    <h3>{esc(note["title"])}</h3>
    <p>{esc(note["summary"])}</p>
  </div>
  <span class="note-teaser-arrow" aria-hidden="true">↗</span>
</a>
'''.strip())
    return "\n".join(rows)


def render_note(note: dict, base_template: str, note_template: str) -> tuple[str, str]:
    preserve = str(note["type"]).lower() == "poetry"
    body = markdown_to_html(note["body_markdown"], preserve_linebreaks=preserve)
    tags = " ".join(f'<span class="tag">{esc(tag)}</span>' for tag in note["tags"])

    content = note_template
    values = {
        "title": esc(note["title"]),
        "author": esc(note["author"]),
        "date": esc(human_date(note["date"])),
        "type": esc(note["type"]),
        "tags": tags,
        "body": body,
    }
    for key, val in values.items():
        content = content.replace("{{" + key + "}}", val)

    path = f'notes/{note["slug"]}/index.html'
    title = f'{note["title"]} · {SITE["name"]}'
    canonical = ""
    abs_url = absolute_url(f'/notes/{note["slug"]}/')
    if abs_url:
        canonical = f'<link rel="canonical" href="{esc(abs_url)}">'

    page = base_template
    mapping = {
        "page_title": esc(title),
        "description": esc(note["summary"]),
        "page_key": "notes",
        "canonical": canonical,
        "header": header("Notes"),
        "content": content,
        "footer": footer(),
    }
    for key, val in mapping.items():
        page = page.replace("{{" + key + "}}", val)

    page = replace_tokens(page, {})
    page = with_base(page)
    return path, page


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    if (ROOT / "public").exists():
        shutil.copytree(ROOT / "public", DIST, dirs_exist_ok=True)

    shutil.copytree(SRC / "assets", DIST / "assets", dirs_exist_ok=True)

    base_template = read(SRC / "templates" / "base.html")
    note_template = read(SRC / "templates" / "note.html")
    pages = json.loads(read(SRC / "pages" / "pages.json"))

    notes = [parse_note(path) for path in sorted((SRC / "notes").glob("*.md"))]
    notes.sort(key=lambda n: (n["date"], n["title"]), reverse=True)
    notes_list = render_notes_list(notes)

    nav_names = {key: meta.get("nav") for key, meta in pages.items()}

    for key, meta in pages.items():
        content = read(SRC / "pages" / meta["source"])
        content = content.replace("{{notes_list}}", notes_list)
        content = replace_tokens(content, {})

        title = (
            f'{SITE["name"]} · {SITE["tagline"]}'
            if key == "index"
            else f'{meta["title"]} · {SITE["name"]}'
        )

        route = "/" if meta["path"] == "index.html" else "/" + meta["path"].replace("index.html", "")
        abs_url = absolute_url(route)
        canonical = f'<link rel="canonical" href="{esc(abs_url)}">' if abs_url else ""

        page = base_template
        mapping = {
            "page_title": esc(title),
            "description": esc(meta["description"]),
            "page_key": key,
            "canonical": canonical,
            "header": header(nav_names.get(key)),
            "content": content,
            "footer": footer(),
        }
        for token, val in mapping.items():
            page = page.replace("{{" + token + "}}", val)

        page = replace_tokens(page, {})
        page = with_base(page)
        write(DIST / meta["path"], page)

    for note in notes:
        path, page = render_note(note, base_template, note_template)
        write(DIST / path, page)

    write(DIST / ".nojekyll", "")

    if SITE_URL:
        urls = []
        for key, meta in pages.items():
            if key == "404":
                continue
            route = "/" if meta["path"] == "index.html" else "/" + meta["path"].replace("index.html", "")
            urls.append(absolute_url(route))
        for note in notes:
            urls.append(absolute_url(f'/notes/{note["slug"]}/'))

        sitemap = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        sitemap.extend(f"  <url><loc>{esc(url)}</loc></url>" for url in urls if url)
        sitemap.append("</urlset>")
        write(DIST / "sitemap.xml", "\n".join(sitemap) + "\n")

    print(f"Built {len(pages) + len(notes)} pages into {DIST}")


if __name__ == "__main__":
    main()
