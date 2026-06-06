#!/usr/bin/env python3
"""Build the first clean style-proof for Thistlebright RPG.

This intentionally starts from scratch: original child-friendly text, original
layout system, and no copied D&D text/art. The provided PHB is used only as a
high-level reference for bookcraft: parchment, heroic opener pages, strong
hierarchy, integrated art, and readable RPG tables.
"""
from __future__ import annotations
from pathlib import Path
import html
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art" / "generated"
PROMPTS = ROOT / "art" / "prompts"
PRINT = ROOT / "printable-a4"
PDF = ROOT / "pdf"
QA = ROOT / "qa"
for d in [ART, PROMPTS, PRINT, PDF, QA, ROOT/"books", ROOT/"sheets", ROOT/"release"]:
    d.mkdir(parents=True, exist_ok=True)

STYLE_GUIDE = """# Thistlebright RPG visual style guide

Audience: children aged 5–7, with grown-up helper/Guide support.
Mood: Scottish fairy myth + high fantasy, brave but safe, no gore/horror.

Design rules learned from the first attempt:
- Page style comes first. Do not write all content then force it into pages.
- Full-page image pages must be genuinely full-bleed: no white bottom gaps, no picture-frame boxes.
- Step headings that introduce an image page belong inside the overlay panel.
- Text overlays are face-safe lower-third parchment panels; never cover faces.
- Rules pages use parchment, two-column flow, compact tables, and keep-together blocks.
- Instructional art can be medium-height so rules flow below; chapter/race/class/bestiary hero art can be full-page.
- PDFs must be generated and raster-checked with pdftoppm before release.

Reference influence from the supplied PHB is limited to broad layout craft:
full-bleed chapter art, parchment pages, strong display headings, drop caps,
two-column text, decorated rules boxes, and integrated illustration. No text,
logos, art, mechanics, or trade dress are copied.
"""
(ROOT / "STYLE_GUIDE.md").write_text(STYLE_GUIDE, encoding="utf-8")

PROMPT_DATA = {
"01-cover.md": """---
filename: 01-cover.png
aspect: portrait
role: cover
---
A full-bleed portrait fantasy book cover for a child-friendly tabletop RPG called Thistlebright Adventures. Scottish fairy glen at twilight, thistles, heather, standing stones, warm lanterns, a tiny Scottish fairy guide with tartan sash, friendly child heroes, distant gentle castle in mist, high fantasy but safe for ages 5-7. Rich painterly storybook illustration, parchment-gold and thistle-purple palette, no text, no logos, leave safe open space near top for title overlay.
""",
"02-part-opener.md": """---
filename: 02-part-opener.png
aspect: portrait
role: chapter-opener
---
Full-page portrait chapter opener art for a child-friendly Scottish fairy RPG. A group of small brave heroes cross a glowing bridge of mushrooms into an enchanted glen, a friendly fairy with silver wings points toward a moonlit path, thistles and Celtic knot motifs, sweeping high fantasy scale, warm and inviting, no danger, no text. Painterly watercolor and ink, full-bleed composition with safe lower-third for overlay panel.
""",
"03-race-kindreds.md": """---
filename: 03-race-kindreds.png
aspect: portrait
role: step-spread
---
Full-page portrait illustration showing five friendly fantasy kindreds for young children: glenfolk child with tartan scarf, tiny thistle fairy, helpful brownie with tool pouch, selkie-born child with soft seal-cloak, rowan-kin forest child with leaf crown. Scottish fairy mythology, cozy high fantasy, warm expressions, safe lower-third empty area for overlay text, no text, no labels.
""",
"04-class-paths.md": """---
filename: 04-class-paths.png
aspect: portrait
role: step-spread
---
Full-page portrait illustration for choosing an adventure job in a child-friendly Scottish fairy RPG. Friendly young heroes: Thistle Knight with wooden practice sword and shield, Loch Scout with lantern map, Song-Spark Bard with small harp, Hearth Mage with glowing teacup spell, Beast Friend with fox companion. High fantasy, Scottish glen, safe and cheerful, no text, no labels, lower-third safe space for overlay.
""",
"05-bestiary-catalog.md": """---
filename: 05-bestiary-catalog.png
aspect: portrait
role: bestiary
---
Full-page portrait child-friendly fantasy bestiary illustration: a gentle miniature kelpie foal by a moonlit loch, a thistle sprite, a sleepy moss troll, and a silver fox familiar gathered around a glowing storybook. Scottish fairy myth, magical but not scary, rich painterly style, parchment-gold and teal shadows, no text, lower-third safe space for overlay.
""",
}
for name, content in PROMPT_DATA.items():
    (PROMPTS / name).write_text(content, encoding="utf-8")

# Fallback original SVG art converted to PNG if generated art is not present yet.
def svg_art(title: str, slug: str, colors: tuple[str, str, str]) -> str:
    a,b,c = colors
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1980" viewBox="0 0 1400 1980">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{a}"/><stop offset=".55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient>
<radialGradient id="moon" cx="74%" cy="18%" r="34%"><stop stop-color="#fff7c8"/><stop offset=".25" stop-color="#f1cc77" stop-opacity=".72"/><stop offset="1" stop-color="#f1cc77" stop-opacity="0"/></radialGradient>
<filter id="soft"><feGaussianBlur stdDeviation="7"/></filter>
</defs>
<rect width="1400" height="1980" fill="url(#g)"/>
<rect width="1400" height="1980" fill="url(#moon)"/>
<path d="M0 1510 C220 1390 350 1460 520 1370 C780 1235 1020 1450 1400 1300 L1400 1980 L0 1980 Z" fill="#1d3328" opacity=".72"/>
<path d="M0 1650 C260 1530 450 1620 710 1510 C930 1418 1120 1540 1400 1440 L1400 1980 L0 1980 Z" fill="#2e5134" opacity=".62"/>
<g opacity=".42" stroke="#e6c36d" stroke-width="5" fill="none"><path d="M80 95 H1320 V1885 H80 Z"/><path d="M120 135 H1280 V1845 H120 Z"/><path d="M200 170 C350 260 520 265 700 180 C880 265 1050 260 1200 170"/></g>
<g fill="#f4e4b3" opacity=".9">
<circle cx="720" cy="840" r="110"/><circle cx="595" cy="895" r="74"/><circle cx="840" cy="905" r="80"/>
<path d="M540 1010 C630 930 760 930 900 1010 L845 1300 H610 Z"/>
</g>
<g fill="#33271d" opacity=".82"><path d="M620 1320 h250 l45 260 h-360 z"/><path d="M530 1500 h430 v70 h-430z"/></g>
<g fill="#c78cd8" opacity=".5" filter="url(#soft)"><ellipse cx="495" cy="820" rx="135" ry="230" transform="rotate(-24 495 820)"/><ellipse cx="935" cy="820" rx="135" ry="230" transform="rotate(24 935 820)"/></g>
<text x="700" y="250" text-anchor="middle" font-family="Georgia,serif" font-size="82" fill="#fff5d6" font-weight="700" opacity=".92">{html.escape(title)}</text>
<text x="700" y="1740" text-anchor="middle" font-family="Georgia,serif" font-size="40" fill="#fff5d6" opacity=".75">original fallback artwork • {html.escape(slug)}</text>
</svg>'''

fallbacks = [
    ("01-cover.png", "Thistlebright", "cover", ("#37264f", "#726f2d", "#132d2b")),
    ("02-part-opener.png", "Into the Glen", "opener", ("#29536f", "#657d46", "#2b233d")),
    ("03-race-kindreds.png", "Kindreds", "races", ("#4b285f", "#6c8a45", "#183d3a")),
    ("04-class-paths.png", "Adventure Jobs", "classes", ("#233e60", "#925c3a", "#21372c")),
    ("05-bestiary-catalog.png", "Friendly Beasts", "bestiary", ("#1d4d52", "#70485e", "#1c2f24")),
]
for fname, title, slug, colors in fallbacks:
    png = ART / fname
    if not png.exists():
        svg = ART / fname.replace(".png", ".svg")
        svg.write_text(svg_art(title, slug, colors), encoding="utf-8")
        subprocess.run(["convert", str(svg), str(png)], check=True)

CSS = r'''
@page { size:A4 portrait; margin:0; background:#f8efd8; }
* { box-sizing:border-box; }
:root { --ink:#2a2118; --muted:#685943; --red:#8c2f2a; --gold:#b8872d; --green:#285640; --purple:#51306d; --paper:#f8efd8; --paper2:#fff8e8; --line:#c7aa70; }
html, body { margin:0; background:var(--paper); color:var(--ink); font-family: Georgia, 'Times New Roman', serif; }
.book { font-size:10.35pt; line-height:1.31; }
p, li { orphans:3; widows:3; } p { margin:0 0 2.6mm; } ul, ol { margin:1.2mm 0 3mm; padding-left:5.2mm; break-inside:avoid-page; } li { margin:.45mm 0; }
h1,h2,h3,h4 { break-after:avoid-page; text-wrap:balance; }
.page { position:relative; height:297mm; min-height:297mm; padding:13mm 14mm 20mm; background:
 radial-gradient(circle at 10% 6%, rgba(184,138,45,.13), transparent 42mm),
 radial-gradient(circle at 94% 20%, rgba(81,48,109,.08), transparent 50mm),
 linear-gradient(90deg, rgba(91,56,22,.09), transparent 8mm, transparent calc(100% - 8mm), rgba(91,56,22,.08)),
 var(--paper2); page-break-after:always; overflow:hidden; }
.page::before { content:''; position:absolute; left:12mm; right:12mm; bottom:12mm; height:1px; background:linear-gradient(90deg, transparent, rgba(184,138,45,.72), transparent); pointer-events:none; z-index:0; }
.page::after { content:''; position:absolute; inset:5mm; border:1px solid rgba(184,138,45,.45); pointer-events:none; z-index:4; }
.page > * { position:relative; z-index:1; }
.page-number { position:absolute; z-index:5; right:14mm; bottom:5.2mm; min-width:8mm; text-align:center; color:#7b6239; font-size:8pt; line-height:1; letter-spacing:.08em; padding:1.2mm 0; background:rgba(255,248,229,.82); border-top:1px solid rgba(184,138,45,.55); border-bottom:1px solid rgba(184,138,45,.35); }
.full-bleed { padding:0; background:#251b16; }
.full-bleed::before { display:none; }
.full-bleed img.bg { position:relative; z-index:0; display:block; width:100%; height:309mm; margin:-6mm 0; object-fit:cover; object-position:center; transform:scale(1.035); }
.full-bleed::after { inset:6mm; border-color:rgba(255,234,168,.56); }
.scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(18,12,8,.08), rgba(18,12,8,.05) 45%, rgba(18,12,8,.52)); }
.title-panel, .overlay { position:absolute; z-index:2; left:50%; transform:translateX(-50%); background:linear-gradient(180deg, rgba(255,250,238,.96), rgba(244,224,180,.90)); border:1px solid rgba(91,57,22,.55); box-shadow:0 1.5mm 8mm rgba(0,0,0,.30); }
.title-panel { top:20mm; width:166mm; padding:6mm 8mm 5mm; border-top:2.2mm solid var(--red); text-align:center; }
.title-panel h1 { margin:0; color:#6d231f; font-size:34pt; line-height:.95; font-variant:small-caps; letter-spacing:.02em; }
.title-panel p { margin:2.5mm 0 0; color:#3b2a1d; font-size:13pt; }
.overlay { bottom:9mm; width:158mm; padding:4mm 5mm; border-left:2.5mm solid rgba(140,47,42,.78); border-radius:1.4mm 4mm 4mm 1.4mm; }
.overlay h2, .overlay h3 { margin:0 0 1.6mm; padding:0 0 1mm; border-bottom:1px solid rgba(140,47,42,.35); color:#722c28; font-size:18pt; line-height:1.02; font-variant:small-caps; }
.overlay p:last-child { margin-bottom:0; }
.chapter-badge { position:absolute; z-index:3; top:0; left:50%; transform:translateX(-50%); width:112mm; padding:8mm 10mm 5mm; background:rgba(255,246,220,.96); border:1px solid rgba(184,138,45,.7); border-top:0; border-radius:0 0 45mm 45mm; text-align:center; box-shadow:0 1mm 6mm rgba(0,0,0,.18); }
.chapter-badge .part { color:#6d231f; font-size:34pt; font-weight:700; line-height:.9; font-variant:small-caps; }
.chapter-badge .sub { color:#4c3422; font-size:13pt; margin-top:1.5mm; }
.columns { display:grid; grid-template-columns:1fr 1fr; gap:5mm 8mm; align-items:start; }
h2.section { margin:0 0 3mm; color:#6f2d29; font-size:21pt; font-variant:small-caps; letter-spacing:.015em; }
h2.section::first-letter { font-size:1.25em; }
h3 { margin:4mm 0 1.5mm; color:#285640; font-size:13.5pt; border-bottom:1px solid rgba(184,138,45,.55); }
.drop:first-letter { font-size:24pt; line-height:1; color:#8c2f2a; padding-right:1mm; font-weight:700; }
.readaloud, .rulebox, .tablebox { break-inside:avoid-page; margin:3mm 0; padding:3mm 4mm; background:linear-gradient(180deg, rgba(255,251,239,.95), rgba(241,223,181,.78)); border:1px solid rgba(138,104,52,.55); border-left:2.2mm solid rgba(81,48,109,.65); box-shadow:0 .8mm 3mm rgba(68,38,15,.12); }
.rulebox strong { color:#672c28; }
table { width:100%; border-collapse:collapse; margin:2.5mm 0 3mm; font-size:8.8pt; break-inside:avoid-page; }
th,td { border:1px solid #c8ac72; padding:2.2mm 2mm; vertical-align:top; } th { background:#dfd0a4; color:#263b2e; } tr:nth-child(even) td { background:rgba(235,222,184,.58); }
.hero-strip { position:relative; height:92mm; margin:-4mm -5mm 5mm; overflow:hidden; break-inside:avoid-page; background:#271d17; }
.hero-strip img { width:100%; height:100%; object-fit:cover; object-position:center; transform:scale(1.03); }
.hero-strip .mini { position:absolute; left:7mm; bottom:6mm; right:7mm; padding:3mm 4mm; background:rgba(255,248,229,.92); border-left:2mm solid var(--red); box-shadow:0 1mm 5mm rgba(0,0,0,.25); }
.card-grid { display:grid; grid-template-columns:1fr 1fr; gap:4mm; }
.option-card { break-inside:avoid-page; padding:3.2mm; background:rgba(255,250,236,.88); border:1px solid rgba(184,138,45,.52); box-shadow:inset 0 0 0 1px rgba(255,255,255,.4); }
.option-card h3 { margin-top:0; }
.sheet { display:grid; grid-template-columns:1fr 1fr; gap:4mm; }
.box { min-height:20mm; padding:3mm; border:1.4px solid #9d804d; background:rgba(255,252,242,.76); break-inside:avoid-page; }
.box.big { min-height:54mm; }
.no-break { break-inside:avoid-page; page-break-inside:avoid; }
'''

pages = []
def img(name): return f"../art/generated/{name}"

def cover():
    pages.append(f'''<section class="page full-bleed cover"><img class="bg" src="{img('01-cover.png')}" alt="Thistlebright cover art"><div class="scrim"></div><div class="title-panel"><h1>Thistlebright Adventures</h1><p>A fairy-tale tabletop RPG for brave 5–7 year olds</p></div><div class="overlay"><h3>Style proof: clean restart</h3><p>Scottish fairy myth, high fantasy, simple choices, warm artwork, and print-first page design.</p></div></section>''')

def opener():
    pages.append(f'''<section class="page full-bleed"><img class="bg" src="{img('02-part-opener.png')}" alt="Heroes entering the glen"><div class="scrim"></div><div class="chapter-badge"><div class="part">Part 1</div><div class="sub">Making a Hero</div></div><div class="overlay"><h2>Welcome to the glen</h2><p>Every adventure begins with a tiny brave choice. The Guide reads the scene, the players say what they try, and the dice help everyone discover what happens next.</p></div><div class="page-number">2</div></section>''')

def rules_page():
    pages.append('''<section class="page"><h2 class="section">The table rule</h2><div class="columns"><p class="drop">Thistlebright is played by talking together. A grown-up Guide describes a place, then each child says what their hero tries. The rules stay small so the story can stay big.</p><div class="readaloud"><strong>Read aloud:</strong> “You hear bells under the heather. A fox with silver whiskers bows and waits. What do you do?”</div><h3>When to roll</h3><p>Only roll when the answer is exciting. If an idea is safe and simple, it works. If it is tricky, roll one six-sided die.</p><table><tr><th>Roll</th><th>What happens</th></tr><tr><td>1–2</td><td>A wobble: something funny or inconvenient happens.</td></tr><tr><td>3–4</td><td>A yes, but: success with a tiny cost or choice.</td></tr><tr><td>5–6</td><td>A bright success: the hero does it well.</td></tr></table><div class="rulebox"><strong>Kindness rule:</strong> heroes can be scared, surprised, muddy, or silly, but the story never punishes a child for trying to help.</div><h3>The three numbers</h3><ul><li><strong>Brave</strong> for daring, protecting, and standing tall.</li><li><strong>Kind</strong> for helping, calming, and making friends.</li><li><strong>Quick</strong> for sneaking, catching, and balancing.</li></ul></div><div class="page-number">3</div></section>''')

def step_pages():
    pages.append(f'''<section class="page full-bleed"><img class="bg" src="{img('03-race-kindreds.png')}" alt="Five friendly kindreds"><div class="scrim"></div><div class="overlay"><h3>Step 1: Pick your kindred</h3><p>Your kindred is your fairy-tale people. It gives one story gift and a way to picture your hero. Nobody is better or worse because of their kindred.</p></div><div class="page-number">4</div></section>''')
    pages.append('''<section class="page"><h2 class="section">Kindreds of Thistlebright</h2><div class="card-grid"><div class="option-card"><h3>Glenfolk</h3><p>Practical children from cottages, crofts, and market lanes.</p><ul><li><strong>Gift:</strong> once per adventure, remember a useful local clue.</li><li><strong>Look:</strong> tartan scarf, muddy boots, treasure pockets.</li></ul></div><div class="option-card"><h3>Thistle Fairy</h3><p>Small bright folk with shimmer, manners, and secret paths.</p><ul><li><strong>Gift:</strong> once per scene, notice nearby fairy magic.</li><li><strong>Look:</strong> petal cloak, star freckles, tiny crown.</li></ul></div><div class="option-card"><h3>Brownie Helper</h3><p>Cozy fixers who tidy, mend, and improve small things.</p><ul><li><strong>Gift:</strong> repair or improve one tiny object each scene.</li><li><strong>Look:</strong> apron, tool pouch, flour on nose.</li></ul></div><div class="option-card"><h3>Selkie-Born</h3><p>Gentle loch-hearted heroes with moonlit dreams.</p><ul><li><strong>Gift:</strong> understand water, weather, or a sad feeling.</li><li><strong>Look:</strong> soft seal-cloak, shell button, sea-glass charm.</li></ul></div></div><div class="page-number">5</div></section>''')
    pages.append(f'''<section class="page full-bleed"><img class="bg" src="{img('04-class-paths.png')}" alt="Five adventure jobs"><div class="scrim"></div><div class="overlay"><h3>Step 2: Pick your adventure job</h3><p>Your job is what you like doing when adventure starts. It gives one bigger class gift that helps the whole table.</p></div><div class="page-number">6</div></section>''')
    pages.append('''<section class="page"><h2 class="section">Adventure jobs</h2><div class="columns"><div class="no-break"><h3>Thistle Knight</h3><p>Protects friends and stands bravely at the front.</p><div class="rulebox"><strong>Gift:</strong> once per scene, turn a scary moment into a brave one.</div></div><div class="no-break"><h3>Loch Scout</h3><p>Finds paths, listens for clues, and spots hidden doors.</p><div class="rulebox"><strong>Gift:</strong> ask the Guide one “what do I notice?” question.</div></div><div class="no-break"><h3>Song-Spark Bard</h3><p>Uses music, jokes, and stories to lift everyone up.</p><div class="rulebox"><strong>Gift:</strong> give another hero +1 after a kind song or cheer.</div></div><div class="no-break"><h3>Hearth Mage</h3><p>Carries warm, safe magic: sparks, steam, tea, and tiny lights.</p><div class="rulebox"><strong>Gift:</strong> create a small helpful magical effect.</div></div><div class="no-break"><h3>Beast Friend</h3><p>Understands animals and earns trust with gentle patience.</p><div class="rulebox"><strong>Gift:</strong> ask a friendly creature for a small favor.</div></div></div><div class="page-number">7</div></section>''')

def bestiary():
    pages.append(f'''<section class="page full-bleed"><img class="bg" src="{img('05-bestiary-catalog.png')}" alt="Friendly bestiary creatures"><div class="scrim"></div><div class="overlay"><h2>Bestiary style</h2><p>Creatures are encounters, friends, mysteries, or puzzles — not bags of hit points. Every entry keeps a picture, a feeling, and a table action together.</p></div><div class="page-number">8</div></section>''')
    pages.append('''<section class="page"><h2 class="section">Creature entry pattern</h2><div class="columns"><div class="hero-strip"><img src="../art/generated/05-bestiary-catalog.png" alt="Bestiary art"><div class="mini"><strong>Art rule:</strong> image first, overlay second, never a floating framed box.</div></div><h3>Moon-Kelpie Foal</h3><p class="drop">A young water horse with silver mane and shy eyes. It wants someone to find the bell it lost under the reeds.</p><table><tr><th>At the table</th><th>Use this</th></tr><tr><td>Wants</td><td>Its moon-bell returned.</td></tr><tr><td>Helps by</td><td>Carrying one hero safely across shallow water.</td></tr><tr><td>Complication</td><td>It splashes when nervous and soaks the map.</td></tr></table><div class="rulebox"><strong>Kind solution:</strong> sing softly, offer oats, or ask the loch what it remembers.</div><h3>Guide note</h3><p>For this age group, a creature should usually have a feeling before it has a fight. Scared, lonely, proud, sleepy, hungry, confused, or protective gives children something to respond to.</p></div><div class="page-number">9</div></section>''')

def sheet():
    pages.append('''<section class="page"><h2 class="section">Character sheet style</h2><p>This sheet is deliberately large, printable, and chunky. A five-year-old should be able to point at each box and explain it.</p><div class="sheet"><div class="box"><strong>Hero name</strong></div><div class="box"><strong>Player name</strong></div><div class="box"><strong>Kindred</strong></div><div class="box"><strong>Adventure job</strong></div><div class="box"><strong>Brave</strong><br>□ □ □</div><div class="box"><strong>Kind</strong><br>□ □ □</div><div class="box"><strong>Quick</strong><br>□ □ □</div><div class="box"><strong>Treasure</strong></div><div class="box big"><strong>Draw your hero</strong></div><div class="box big"><strong>My helper question</strong><br><br>When I am stuck, I can ask...</div></div><div class="page-number">10</div></section>''')

cover(); opener(); rules_page(); step_pages(); bestiary(); sheet()
HTML = '<!doctype html><html><head><meta charset="utf-8"><title>Thistlebright RPG Style Proof</title><style>'+CSS+'</style></head><body><main class="book">' + '\n'.join(pages) + '</main></body></html>'
(PRINT / "style-proof-a4.html").write_text(HTML, encoding="utf-8")

README = """# Thistlebright RPG

Fresh start for a D&D-inspired, Scottish fairy mythology, high-fantasy tabletop RPG for children aged 5–7.

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
"""
(ROOT / "README.md").write_text(README, encoding="utf-8")

render = """#!/usr/bin/env python3
from pathlib import Path
from weasyprint import HTML
import subprocess
ROOT = Path(__file__).resolve().parents[1]
src = ROOT/'printable-a4/style-proof-a4.html'
out = ROOT/'pdf/style-proof.pdf'
out.parent.mkdir(exist_ok=True)
HTML(filename=str(src), base_url=str(src.parent)).write_pdf(str(out))
print(subprocess.check_output(['pdfinfo', str(out)], text=True))
"""
(ROOT / "tools" / "render_style_proof.py").write_text(render, encoding="utf-8")

qa = """#!/usr/bin/env python3
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
pdf = ROOT/'pdf/style-proof.pdf'
out = ROOT/'qa/style-proof-pages'
out.mkdir(parents=True, exist_ok=True)
for p in range(1, 11):
    prefix = out / f'page-{p:02d}'
    subprocess.run(['pdftoppm','-png','-r','100','-f',str(p),'-singlefile',str(pdf),str(prefix)], check=True)
print('rendered', len(list(out.glob('*.png'))), 'pages to', out)
"""
(ROOT / "tools" / "qa_render_pages.py").write_text(qa, encoding="utf-8")
print('built style proof source at', PRINT / 'style-proof-a4.html')
