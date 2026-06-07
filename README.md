# Adventures in Alba

D&D-inspired, Scottish fairy mythology, high-fantasy tabletop RPG for Adventurers aged 5–7.

This repo uses an original Adventurer-friendly setting and rules engine. The supplied D&D Player's Handbook reference was used only for broad bookcraft/style principles such as full-bleed chapter art, parchment pages, readable tables, and strong hierarchy. This project does not copy its text, art, logos, mechanics, or trade dress.

## Core rule

Roll one six-sided die only when the answer is exciting. Add the matching classic stat bonus:

- Strength
- Int
- Agility
- Wis
- Luck

Results:

- `1–3`: wobble
- `4–5`: yes, but
- `6+`: bright success

Character creation: choose one best stat at `+2`, two good stats at `+1`, and two normal stats at `+0`.

Currency: `10 copper = 1 silver`, `10 silver = 1 gold`, `100 gold = 1 mythral`.

## Current books

Generated PDFs live in `pdf/` and source HTML lives in `printable-a4/`.

- `player-handbook.pdf` — 56 pages: rules, stats, kindreds, jobs, spells, gear, magic items, potions/poisons, mounts/pets, progression, player choices.
- `guide-book.pdf` — 17 pages: Guide procedures, roll/wobble examples, combat/danger, ready dialogue, boss scenes.
- `guide-extra.pdf` — 3 pages: running young Adventurers, table-play QA checklist.
- `bestiary.pdf` — 28 pages: creature rules and bestiary with individual art/stat blocks.
- `bestiary-vol-2.pdf` — 13 pages: scarier Alba creatures and faction enemies.
- `campaigns.pdf` — 25 pages: ready-to-run campaign arcs and modular scene packets.
- `adventure-module.pdf` — 16 pages: linked one-shots with maps, read-alouds, checks, treasure, and scaling.
- `setting-guide.pdf` — 11 pages: Alba lore, factions, fairy courts, Albion/Dominion, Norse sea-kin, storm-clans.
- `alba-atlas.pdf` — 5 pages: regional atlas, routes, factions, towns, dungeons, legends.
- `treasure-crafting.pdf` — 7 pages: treasure tiers, crafting, fairy bargains, magic item catalogue, enchantments, potions/poisons.
- `table-aids.pdf` — 8 pages: table aids, spell cards, item cards, condition tents, maps.
- `printable-cards.pdf` — 8 pages: cut-out spell, item, potion, companion, monster, quest/reward, and condition cards.
- `quickstart-pack.pdf` — 9 pages: print-this-first starter box pack.
- `character-sheets.pdf` — 8 pages: printable sheets including full-page character drawing page.
- Low-ink variants: `quickstart-pack-low-ink.pdf`, `printable-cards-low-ink.pdf`.
- `style-proof.pdf` — visual style proof retained for reference.

## Build

```bash
python3 tools/build_books.py
uv run --with weasyprint python tools/render_books.py
python3 tools/qa_books.py
```

## QA standard

The project tracks QA contact sheets under `qa/`. Recent QA passes verify:

- every sampled page has visible art/background/marginal art,
- no excessive whitespace on previously sparse pages such as magic item examples,
- no missing repeated-art issue on new kindreds or creatures,
- no forbidden rendered PDF wording such as `child`, `children`, `10 gold = 1 mythral`, or real-world `English` villain labels,
- PDF text includes required new material such as Quickstart, Printable Cards, Alba Atlas, running young Adventurers, progression, player choices, earned companions, and `100 gold = 1 mythral`.

## Release notes



### v0.6 transparent art-layer fix

- Removed the grey full-page/background rectangle treatment.
- Replaced background support art with transparent, feathered-edge PNG wash layers.
- Added dedicated illustrated gear, magic-item, and potion/poison sheets.
- Patched equipment, gear, magic item, potion/poison, and treasure/crafting pages to use visible item illustrations.
- Rebuilt and post-compression QA’d targeted pages for no grey boxes, no square overlays, and readable text.

### v0.5 next-10 expansion

This pass executes the recommended next steps:

- Added universal art/background treatment so every page has visual support.
- Added Starter Box / Quickstart Pack.
- Added standalone Printable Cards deck plus low-ink version.
- Added Guide Extra book for running young Adventurers and table-play QA.
- Added Alba Atlas.
- Added progression beyond level 1.
- Added more player jobs, backgrounds, gifts, and pet/mount hooks.
- Further fleshed campaign scene packets and travel procedures.
- Added print-production aids and low-ink quickstart/card variants.

### v0.4 follow-up polish

- New stranger kindreds use individual portrait art instead of one shared image.
- New bestiary creatures/faction enemies use distinct creature art.
- Sparse Player Handbook examples gained background-layer wash art.
- Character sheets include a full-page “Draw your Adventurer” page.
- Earned mounts and pets became part of the system.
- Tiny Tables alternate table/heading alignment and include background art.
- Example campaigns include concrete ready-to-run session packet material.
