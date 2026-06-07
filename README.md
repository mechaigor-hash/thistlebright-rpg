# Alba RPG

Fresh start for a D&D-inspired, Scottish fairy mythology, high-fantasy tabletop RPG for Adventurers aged 5–7.

This repo begins with the page style system first: A4 print layout, full-bleed artwork, face-safe overlays, two-column parchment rules pages, card grids, bestiary layout, and character sheet style.

## Current artifact

- `printable-a4/style-proof-a4.html` — 10-page style proof
- `pdf/style-proof.pdf` — generated PDF after running `tools/render_style_proof.py`
- `STYLE_GUIDE.md` — layout and art rules
- `art/prompts/` — reproducible art prompts

## Build

```bash
python3 tools/build_style_proof.py
uv run --with weasyprint python tools/render_style_proof.py
python3 tools/qa_render_pages.py
```

The supplied Player's Handbook PDF was used only as a broad page-design reference. This project does not copy its text, art, logos, mechanics, or trade dress.

## v0.4 follow-up polish

This pass addresses layout/art QA notes:
- New stranger kindreds now use individual portrait art instead of the same shared group image.
- New bestiary and Bestiary Vol. 2 creatures/faction enemies now use distinct creature art.
- Sparse Player Handbook examples gain background-layer wash art.
- Character sheets include a full-page “Draw your Adventurer” page.
- Earned mounts and pets are now part of the system; companions are won through story, not bought as starter gear.
- Tiny Tables alternate table/heading alignment and include background art.
- Example campaigns include more concrete ready-to-run session packet material.
