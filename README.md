# MEANWH[x]
Development note: this repository is maintained collaboratively through branches and pull requests.

A lightweight, collaborative static website for MeanwhX: an independent science × art studio and growing community.

## Design idea

The site is one house with different rooms:

- **Home** — a wry *Pocket Guide to the Meantime*: navigator, field notes, slightly unreliable coordinates.
- **Studio** — clean applied-mathematics-center / whiteboard discipline.
- **π + Bear** — graph paper, specimen labels, café table, bear archive, playful equations.
- **Notes** — literary writing table rather than a corporate blog.
- **Community** — a shared table, not a membership dashboard.
- **About / Support / Rights / Contact** — quiet, practical pages.

The implementation is intentionally boring in the best way: **Python + HTML + CSS + tiny JavaScript**. No npm, no React, no CMS, no database, no external fonts, no analytics, and no backend.

## Local preview

Requires Python 3.11+.

```bash
python3 build.py
python3 -m http.server 8000 -d dist
```

Open:

```text
http://localhost:8000
```

## Editing

### Basic identity / email

Edit `site.json`.

Before public launch replace:

```json
"email": "hello@example.org"
```

and add the factual technical-community URL only after the relationship is agreed.

### Add a Note

Create a Markdown file in `src/notes/`. Copy an existing one and change its TOML front matter.

### Add Studio work

For now Studio entries live directly in `src/pages/studio.html`. Replace the three existing **studies** with real work or remove them until ready. Do not upgrade a concept to “Prototype” unless something has actually been made/tested.

### Add π + Bear work

Edit `src/pages/pi-bear.html`. The current `After Seminar` item is explicitly a proposal; no tested recipe or physical venue is claimed.

## Multiple people

Use Git branches + pull requests. Once more than one person edits regularly, protect `main` and require review.

See `CONTRIBUTING.md`.

## Deploy

See `docs/DEPLOY_GITHUB.md`.

## Private-design boundary

**Do not use this public website repository as the private design archive.**

Keep manufacturing-ready CAD, unreleased design families, supplier/manufacturing notes, private collaborator documents, credentials, and sensitive grant paperwork somewhere private.
