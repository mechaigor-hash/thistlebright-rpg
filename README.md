# Thistlebright RPG

Fresh start for a D&D-inspired, Scottish fairy mythology, high-fantasy tabletop RPG for children aged 5–7.

This repo uses an original child-friendly setting and rules engine. The supplied D&D Player's Handbook PDF was used only as a broad page-design reference for bookcraft: A4 print layout, full-bleed artwork, strong hierarchy, parchment rules pages, and integrated illustrations. This project does not copy D&D text, art, logos, mechanics, or trade dress.

## Current books

Rendered A4 PDFs live in `pdf/`:

- `pdf/player-handbook.pdf` — 21 pages; character creation, simple dice rule, stats, one illustrated page per kindred/race, one illustrated page per adventure job/class, spells, gear, and worked example.
- `pdf/guide-book.pdf` — 7 pages; how to guide scenes for 5–7 year olds, wobbles, adventure structure, and tiny tables.
- `pdf/bestiary.pdf` — 7 pages; friendly creature entries and creature builder.
- `pdf/campaigns.pdf` — 7 pages; ready-to-run linked mini campaign.
- `pdf/character-sheets.pdf` — 4 pages; blank sheet, finished example, and quick-reference cards.
- `pdf/style-proof.pdf` — original 10-page style proof.

## Rules summary

- Roll one six-sided die only when the answer is exciting.
- Add stat stars: `★★`, `★`, or `—`.
- Total `1–2`: wobble. Total `3–4`: yes, but. Total `5+`: bright success.
- Three stats: Brave, Kind, Quick.
- Character creation stays simple: pick one best stat `★★`, one okay stat `★`, and leave one blank `—`.

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
