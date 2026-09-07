# Contributing to MeanwhX

MeanwhX should feel closer to bringing something to a table than submitting to a platform.

## Workflow

1. Create a branch.
2. Make one focused change.
3. Build locally:
   ```bash
   python3 build.py
   ```
4. Preview:
   ```bash
   python3 -m http.server 8000 -d dist
   ```
5. Open a pull request.
6. Another maintainer reviews before merge.

## Notes

Create a Markdown file in `src/notes/`.

Required front matter:

```toml
+++
title = "Title"
author = "Preferred credit"
date = "2026-08-24"
type = "Poetry"
tags = ["Poetry", "After Seminar"]
summary = "Short excerpt."
slug = "title-slug"
+++
```

Contributors keep authorship unless a separate agreement says otherwise. Confirm publication permission before merge.

## Before committing

- Do not add private CAD or fabrication geometry.
- Do not add unpublished personal stories without permission.
- Do not add credentials, private grants, or collaborator contact details.
- Do not invent product status, partners, funders, customers, events, or technical functionality.
- Use **Study / Proposal / Prototype / Edition** literally.

## Visual changes

Keep it light, human, and slightly geeky.

Prefer paper, whiteboard, books, cups, thin rules, mathematical notation, tactile objects, generous space, and jokes that do not need a paragraph of explanation.

Avoid generic AI gradients, glowing brains, robot imagery, fake dashboards, glassmorphism, and every section becoming a rounded card.
