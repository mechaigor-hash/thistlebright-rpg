# Adventures in Alba

Fresh start for a D&D-inspired, Scottish fairy mythology, high-fantasy tabletop RPG for children aged 5–7.

This repo uses an original child-friendly setting and rules engine. The supplied D&D Player's Handbook PDF was used only as a broad page-design reference for bookcraft: A4 print layout, full-bleed artwork, strong hierarchy, parchment rules pages, and integrated illustrations. This project does not copy D&D text, art, logos, mechanics, or trade dress.

## Current books

Rendered A4 PDFs live in `pdf/`:

- `pdf/player-handbook.pdf` — 31 pages; character creation, simple dice rule, classic five-stat setup, HP/MP, leveling, feats every 4 levels, class stat blocks, class cantrips/spells, skills/checks, combat, traps, expanded gear/equipment, currency, adventurer-POV example scenarios, and worked example.
- `pdf/guide-book.pdf` — 14 pages; how to guide scenes for 5–7 year olds using Strength, Int, Agility, Wis, and Luck, with wobbles, adventure structure, examples, dialogue prompts, HP/MP/DR guidance, and matching Guide/DM POV scenario pages.
- `pdf/bestiary.pdf` — 20 pages; each creature has its own artwork page, lore above the stat block, HP, MP, Level, calculated Difficulty Rating, classic stats, moves/spells/special attacks, wants, complications, and creature builder.
- `pdf/campaigns.pdf` — 7 pages; ready-to-run linked mini campaign.
- `pdf/character-sheets.pdf` — 4 pages; blank sheet, finished example, HP/MP fields, level, coins/gear, and quick-reference cards.

## Rules summary

- Roll one six-sided die only when the answer is exciting.
- Add the matching classic stat bonus: Strength, Int, Agility, Wis, or Luck.
- Total `1–3`: wobble. Total `4–5`: yes, but. Total `6+`: bright success.
- Character creation: choose one best stat at `+2`, two good stats at `+1`, and two normal stats at `+0`.
- Heroes have HP and MP. Cantrips cost 0 MP; adventure spells usually cost 1 MP.
- Leveling grants HP/MP growth and new choices; feats are chosen every 4 levels.
- Currency: `10 copper = 1 silver`, `10 silver = 1 gold`, `10 gold = 1 mythral`.
- Each hero starts with `1 silver` / `10 copper` to buy starter gear.
- Enemy DR = `round((HP + MP + Level×3 + positive stat bonuses×2) ÷ 10)`, minimum 1.
- Combat is handled as tense, child-safe scenes: protect, dodge, calm, distract, break spells, or tire a creature out; at 0 HP, creatures stop and can be helped, tricked, soothed, or understood.

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
- `qa/player-class-pages-contact.jpg` — class/job pages with stat blocks and spells.
- `qa/player-scenarios-contact.jpg` — player-facing skill/combat/trap/scenario pages.
- `qa/bestiary-contact.jpg` — full bestiary contact sheet.
- `qa/guide-contact.jpg` — full guide book contact sheet.
- `qa/style-proof-contact.jpg` — style proof contact sheet.
