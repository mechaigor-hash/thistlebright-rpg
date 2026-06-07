# Thistlebright RPG

Fresh start for a D&D-inspired, Scottish fairy mythology, high-fantasy tabletop RPG for children aged 5–7.

This repo uses an original child-friendly setting and rules engine. The supplied D&D Player's Handbook PDF was used only as a broad page-design reference for bookcraft: A4 print layout, full-bleed artwork, strong hierarchy, parchment rules pages, and integrated illustrations. This project does not copy D&D text, art, logos, mechanics, or trade dress.

## Current books

Rendered A4 PDFs live in `pdf/`:

- `pdf/player-handbook.pdf` — 23 pages; character creation, simple dice rule, classic five-stat setup, one full painterly illustrated page per kindred/race, one full painterly illustrated page per adventure job/class, expanded spell list, starter money, equipment shop, and worked example.
- `pdf/guide-book.pdf` — 7 pages; how to guide scenes for 5–7 year olds using Strength, Int, Agility, Wis, and Luck, wobbles, adventure structure, and tiny tables.
- `pdf/bestiary.pdf` — 13 pages; each creature has its own artwork page, classic stat block, moves, wants, complications, and creature builder.
- `pdf/campaigns.pdf` — 7 pages; ready-to-run linked mini campaign.
- `pdf/character-sheets.pdf` — 4 pages; blank sheet, finished example, and quick-reference cards.
- `pdf/style-proof.pdf` — original 10-page style proof.

## Rules summary

- Roll one six-sided die only when the answer is exciting.
- Add the matching classic stat bonus: Strength, Int, Agility, Wis, or Luck.
- Total `1–3`: wobble. Total `4–5`: yes, but. Total `6+`: bright success.
- Character creation: choose one best stat at `+2`, two good stats at `+1`, and two normal stats at `+0`.
- Each hero starts with 10 thistle pennies to buy starter gear.

## Build

```bash
python3 tools/build_books.py
uv run --with weasyprint python tools/render_books.py
python3 tools/qa_books.py
```

Style proof only:

```bash
python3 tools/build_style_proof.py
uv run --with weasyprint python tools/render_style_proof.py
python3 tools/qa_render_pages.py
```

## QA

- `qa/books-contact.jpg` — sampled rendered pages from every book.
- `qa/book-pages/` — rasterized sample pages from each PDF.
- `qa/style-proof-contact.jpg` — style proof contact sheet.
