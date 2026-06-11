#!/usr/bin/env python3
"""Build the Adventures in Alba RPG book set.

Original adventurer-friendly tabletop content. The D&D PHB reference is used only for
broad bookcraft/style principles; this script does not copy text, art, rules, or
trade dress.
"""
from __future__ import annotations
from pathlib import Path
import textwrap
import re
import hashlib
import subprocess
import shutil

ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT / "printable-a4"
PDF = ROOT / "pdf"
BOOKS = ROOT / "books"
SHEETS = ROOT / "sheets"
QA = ROOT / "qa"
ART = ROOT / "art" / "generated"
for d in [PRINT, PDF, BOOKS, SHEETS, QA, ART]:
    d.mkdir(parents=True, exist_ok=True)

CSS = r'''
@page { size:A4 portrait; margin:0; background:#f8efd8; }
* { box-sizing:border-box; }
:root { --ink:#2b2118; --muted:#665540; --red:#87312d; --gold:#b9892e; --green:#285740; --purple:#56336d; --paper:#fff8e9; --paper2:#f5e8ca; --line:#c7aa70; --blue:#24516a; }
html, body { margin:0; background:#f8efd8; color:var(--ink); font-family: Georgia, 'Times New Roman', serif; }
.book { font-size:10.25pt; line-height:1.31; }
p { margin:0 0 2.5mm; } p, li { orphans:3; widows:3; }
ul, ol { margin:1mm 0 3mm; padding-left:5.2mm; break-inside:avoid-page; } li { margin:.42mm 0; }
h1,h2,h3,h4 { break-after:avoid-page; text-wrap:balance; }
.page { position:relative; height:297mm; min-height:297mm; padding:12mm 14mm 19mm; background:
  radial-gradient(circle at 9% 5%, rgba(184,138,45,.14), transparent 42mm),
  radial-gradient(circle at 94% 18%, rgba(86,51,109,.08), transparent 48mm),
  linear-gradient(90deg, rgba(91,56,22,.08), transparent 8mm, transparent calc(100% - 8mm), rgba(91,56,22,.07)),
  var(--paper); page-break-after:always; overflow:hidden; }
.page::before { content:''; position:absolute; left:12mm; right:12mm; bottom:12mm; height:1px; background:linear-gradient(90deg, transparent, rgba(184,138,45,.72), transparent); pointer-events:none; z-index:0; }
.page::after { content:''; position:absolute; inset:5mm; border:1px solid rgba(184,138,45,.43); pointer-events:none; z-index:4; }
.page > * { position:relative; z-index:1; }
.page-number { position:absolute; z-index:5; right:14mm; bottom:5.1mm; min-width:8mm; text-align:center; color:#765f37; font-size:8pt; line-height:1; letter-spacing:.08em; padding:1.2mm 0; background:rgba(255,248,229,.84); border-top:1px solid rgba(184,138,45,.55); border-bottom:1px solid rgba(184,138,45,.35); }
.full-bleed { padding:0; background:#251b16; }
.full-bleed::before { display:none; }
.full-bleed::after { inset:6mm; border-color:rgba(255,234,168,.56); }
.full-bleed img.bg { position:relative; z-index:0; display:block; width:100%; height:309mm; margin:-6mm 0; object-fit:cover; object-position:center; transform:scale(1.035); }
.scrim { position:absolute; inset:0; z-index:1; background:linear-gradient(180deg, rgba(15,10,6,.10), rgba(15,10,6,.04) 45%, rgba(15,10,6,.57)); }
.title-panel, .overlay { position:absolute; z-index:2; left:50%; transform:translateX(-50%); background:linear-gradient(180deg, rgba(255,250,238,.96), rgba(244,224,180,.91)); border:1px solid rgba(91,57,22,.55); box-shadow:0 1.5mm 8mm rgba(0,0,0,.30); }
.title-panel { top:19mm; width:166mm; padding:6mm 8mm 5mm; border-top:2.2mm solid var(--red); text-align:center; }
.title-panel h1 { margin:0; color:#692620; font-size:32pt; line-height:.96; font-variant:small-caps; letter-spacing:.015em; }
.title-panel p { margin:2.5mm 0 0; color:#3b2a1d; font-size:12.4pt; }
.overlay { bottom:9mm; width:158mm; padding:4mm 5mm; border-left:2.5mm solid rgba(135,49,45,.78); border-radius:1.4mm 4mm 4mm 1.4mm; }
.overlay h2, .overlay h3 { margin:0 0 1.5mm; padding:0 0 1mm; border-bottom:1px solid rgba(135,49,45,.35); color:#722c28; font-size:17.5pt; line-height:1.04; font-variant:small-caps; }
.overlay p:last-child { margin-bottom:0; }
h2.section { margin:0 0 3mm; color:#6f2d29; font-size:21pt; font-variant:small-caps; letter-spacing:.015em; }
h2.section::first-letter { font-size:1.25em; }
h3 { margin:3.6mm 0 1.3mm; color:#285640; font-size:13pt; border-bottom:1px solid rgba(184,138,45,.55); }
h4 { margin:2.2mm 0 1mm; color:#56336d; font-size:10.8pt; }
.columns { display:grid; grid-template-columns:1fr 1fr; gap:4.5mm 7mm; align-items:start; }
.three { display:grid; grid-template-columns:1fr 1fr 1fr; gap:3.3mm; }
.card-grid { display:grid; grid-template-columns:1fr 1fr; gap:3.6mm; }
.split { display:grid; grid-template-columns:1fr 1fr; gap:5mm 7mm; align-items:start; }
.col { break-inside:avoid-page; page-break-inside:avoid; }
.dense-list li { margin:.25mm 0; }
.mini-card { break-inside:avoid-page; page-break-inside:avoid; margin:2mm 0; padding:2.3mm 2.8mm; background:rgba(255,251,239,.88); border:1px solid rgba(184,138,45,.52); }
.columns > .option-card { min-height:62mm; }
.columns > .creature { min-height:58mm; }
.option-card, .rulebox, .readaloud, .questbox, .creature, .sheet-box { break-inside:avoid-page; page-break-inside:avoid; padding:3mm; background:linear-gradient(180deg, rgba(255,252,244,.975), rgba(244,228,190,.94)); border:1px solid rgba(154,116,55,.72); box-shadow:0 1mm 4mm rgba(0,0,0,.12), inset 0 0 0 1px rgba(255,255,255,.70); }
.option-card h3, .creature h3 { margin-top:0; }
.card-grid .option-card { background:linear-gradient(180deg, rgba(255,252,244,.985), rgba(246,231,196,.965)); box-shadow:0 1.1mm 4.6mm rgba(0,0,0,.16), inset 0 0 0 1px rgba(255,255,255,.72); }
.card-grid .option-card p, .card-grid .option-card li { background:rgba(255,252,244,.55); padding:.7mm 1mm; border-radius:1mm; }
.art-text-strong .wash-content { background:linear-gradient(180deg, rgba(255,252,244,.955), rgba(246,231,196,.91)); border:1px solid rgba(154,116,55,.70); box-shadow:0 1.5mm 7mm rgba(0,0,0,.20); padding:4mm; border-radius:1.4mm; }
.art-text-strong .section { background:rgba(255,252,244,.88); padding:1.5mm 2mm; margin-bottom:3mm; border-bottom:1px solid rgba(184,138,45,.7); }
.art-text-strong .wash-content .split, .art-text-strong .wash-content table, .art-text-strong .wash-content .card-grid { background:rgba(255,252,244,.80); }
.rulebox, .readaloud { margin:2.6mm 0; border-left:2.2mm solid rgba(86,51,109,.66); }
.questbox { margin:2.8mm 0; border-left:2.2mm solid rgba(40,87,64,.75); }
.small { font-size:8.8pt; color:var(--muted); }
.big-stat { font-size:20pt; color:#74322d; letter-spacing:.04em; }
table { width:100%; border-collapse:collapse; margin:2.2mm 0 3mm; font-size:8.6pt; break-inside:avoid-page; }
th,td { border:1px solid #b9934c; padding:2mm 1.8mm; vertical-align:top; } th { background:rgba(217,195,135,.96); color:#263b2e; } td { background:rgba(255,251,239,.78); } tr:nth-child(even) td { background:rgba(242,229,193,.86); }
.keep { break-inside:avoid-page; page-break-inside:avoid; }
.drop:first-letter { font-size:23pt; line-height:1; color:#87312d; padding-right:1mm; font-weight:700; }
.spot { height:54mm; overflow:hidden; margin:0 0 3mm; background:#241a16; border:1px solid rgba(128,92,45,.48); break-inside:avoid-page; }
.spot img { width:100%; height:100%; object-fit:cover; object-position:center; transform:scale(1.025); display:block; }
.hero-strip { position:relative; height:88mm; margin:-3mm -4mm 4mm; overflow:hidden; background:#271d17; break-inside:avoid-page; }
.hero-strip img { width:100%; height:100%; object-fit:cover; transform:scale(1.035); }
.hero-strip .mini { position:absolute; left:6mm; bottom:5mm; right:6mm; padding:2.8mm 3.4mm; background:rgba(255,248,229,.92); border-left:2mm solid var(--red); box-shadow:0 1mm 5mm rgba(0,0,0,.22); }
.feature-page { padding:10mm 12mm 18mm; }
.feature-top { display:grid; grid-template-columns:82mm 1fr; gap:6mm; align-items:stretch; margin-bottom:4mm; }
.feature-art { height:130mm; overflow:hidden; border:1px solid rgba(112,77,35,.55); background:#2b2118; box-shadow:0 1.4mm 5mm rgba(0,0,0,.18); }
.feature-art img { width:100%; height:100%; object-fit:cover; display:block; }
.feature-intro { padding:4mm; background:linear-gradient(180deg, rgba(255,251,239,.92), rgba(242,226,187,.72)); border:1px solid rgba(184,138,45,.46); }
.feature-intro h2 { margin:0 0 2mm; color:#6f2d29; font-size:22pt; line-height:1; font-variant:small-caps; border-bottom:1px solid rgba(184,138,45,.55); padding-bottom:1.5mm; }
.feature-kicker { color:#56336d; text-transform:uppercase; letter-spacing:.08em; font-size:8pt; margin-bottom:1.5mm; }
.feature-grid { display:grid; grid-template-columns:1fr 1fr; gap:3.4mm 5mm; }
.feature-box { break-inside:avoid-page; min-height:38mm; padding:3mm; background:rgba(255,251,239,.88); border:1px solid rgba(184,138,45,.50); }
.feature-box h3 { margin-top:0; font-size:12pt; }
.feature-quote { margin-top:3mm; padding:3mm; background:rgba(86,51,109,.10); border-left:2mm solid rgba(86,51,109,.65); font-style:italic; }
.statline { display:grid; grid-template-columns:repeat(5,1fr); gap:1.2mm; margin:1.7mm 0 2.5mm; }
.vitals { display:grid; grid-template-columns:repeat(4,1fr); gap:1.2mm; margin:1.8mm 0 2.2mm; }
.stat, .vital { text-align:center; padding:1.45mm .8mm; background:#ead9ad; border:1px solid #b9954d; font-size:8pt; }
.stat strong, .vital strong { display:block; color:#6f2d29; font-size:9.4pt; }
.shop table, .spell-list table, .advancement table, .currency table { font-size:8.1pt; }
.creature-feature .feature-top { grid-template-columns:76mm 1fr; align-items:start; }
.creature-feature .feature-art { height:125mm; }
.creature-feature .feature-intro { min-height:125mm; }
.creature-feature .feature-box { min-height:28mm; }
.creature-lore { font-size:9.3pt; line-height:1.25; margin-bottom:1.2mm; }
.stat-note { font-size:8.2pt; color:var(--muted); margin-top:1mm; }
.sheet-page .page { padding:11mm 13mm 18mm; }
.sheet { display:grid; grid-template-columns:1fr 1fr; gap:3.2mm; }
.sheet-box { min-height:17mm; }
.sheet-box.big { min-height:44mm; }
.sheet-box.tall { min-height:62mm; }
.line { border-bottom:1px solid #836a42; min-height:7mm; margin-top:2mm; }
.badge { display:inline-block; padding:.8mm 2mm; margin:.4mm .8mm .4mm 0; background:#ead9ad; border:1px solid #b9954d; border-radius:4mm; font-size:8.5pt; }
.toc li { margin:1.2mm 0; }

.artwash { position:absolute; z-index:0; pointer-events:none; opacity:.82; filter:none; object-fit:cover; object-position:center; }
/* Full-page transparent art wash: big enough to fill A4, with feathered PNG alpha handling the dissolve. */
.artwash.right, .artwash.left, .artwash.auto, .artwash.full {
  left:-10mm; right:auto; top:-8mm; bottom:auto;
  width:230mm; height:315mm;
  object-fit:cover; object-position:center;
}
.artwash.auto.left, .artwash.left { left:-18mm; object-position:left center; }
.artwash.auto.right, .artwash.right { left:-2mm; object-position:right center; }
.artwash.full { left:-10mm; object-position:center center; }
.wash-content { position:relative; z-index:2; }
.page > h2.section, .page > div:not(.page-number), .page > table, .page > p, .page > ol, .page > ul { position:relative; z-index:2; }

.page .columns, .page .split, .page table, .page .card-grid, .page .sheet, .page .draw-frame { position:relative; z-index:2; }
.wash-content .split, .wash-content table, .page > .columns, .page > .split { background:rgba(255,251,239,.76); backdrop-filter:none; border-radius:2mm; padding:1mm; box-shadow:0 0 0 1px rgba(184,138,45,.22); }
.low-ink .page { background:#fffdf6 !important; }
.low-ink .artwash, .low-ink .spot, .low-ink .hero-strip, .low-ink .full-bleed img { opacity:.16 !important; filter:none !important; }
.print-card-grid { display:grid; grid-template-columns:repeat(3, 1fr); gap:2.4mm; }
.print-card { min-height:38mm; padding:2.5mm; border:1.4px dashed rgba(135,49,45,.60); background:rgba(255,251,239,.92); break-inside:avoid; overflow:hidden; }
.print-card .card-illo { float:right; width:22mm; height:20mm; object-fit:cover; object-position:center; margin:0 0 1mm 1.8mm; border-radius:2mm; border:1px solid rgba(135,49,45,.42); display:block; overflow:hidden; box-shadow:0 .7mm 2mm rgba(0,0,0,.16); }
.print-card h3 { margin-top:0; font-size:12pt; }
.quick-grid { display:grid; grid-template-columns:1fr 1fr; gap:4mm; }

.print-card { min-height:38mm !important; padding:2.5mm !important; }
.print-card h3 { font-size:10.8pt !important; margin-bottom:1mm !important; }
.print-card p { font-size:8.4pt !important; line-height:1.18 !important; }
.session-grid .option-card { padding:2mm !important; }
.session-grid .option-card h3 { font-size:10.2pt !important; margin-bottom:.8mm !important; }
.session-grid .option-card p, .session-grid .option-card li { font-size:8pt !important; line-height:1.18 !important; }
.scene-packet { padding:3mm; border:1px solid rgba(184,138,45,.55); background:rgba(255,251,239,.80); margin:2mm 0; break-inside:avoid; }
.scene-packet h3 { margin-top:0; }
.item-art-band { margin:0 0 4mm; height:58mm; overflow:hidden; position:relative; break-inside:avoid; }
.item-art-band img { width:100%; height:100%; object-fit:contain; display:block; }
.item-inline-art { float:right; width:72mm; margin:0 0 3mm 5mm; }
.item-inline-art img { width:100%; display:block; }

'''

def art(name: str) -> str:
    return f"../art/generated/{name}"

def wash_art(name: str) -> str:
    return f"../art/generated/wash/{name}"

ART_CYCLE = [
    '02-part-opener.png','alba-regional-map.png','alba-town-dungeon-map.png','alba-frontier-map.png',
    'item-gear-sheet.png','item-magic-sheet.png','item-potions-poisons-sheet.png','bg-spell-gear.png','bg-tiny-tables.png','bg-mounts-pets.png','bg-campaign-red-banner.png',
    'kindred-cairnling.png','kindred-mosskin.png','kindred-corbie-folk.png','kindred-star-sprite.png','kindred-myceling.png',
    'creature-black-bog-drake.png','creature-border-warg.png','creature-draugr-oath-raider.png','creature-iron-crow-swarm.png',
    'creature-albion-redcloak-captain.png','creature-redcap-warband-boss.png','creature-albion-tax-mage.png','creature-barbarian-storm-berserker.png'
]

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


GLOBAL_IMG_SEEN = {}

def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode('utf-8')).hexdigest()[:8], 16)

def slug_from_title(title: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

def real_art_base(title: str, kind: str = 'scene') -> Path:
    """Pick existing painterly artwork, never vector silhouettes/icons, as the base."""
    lower = title.lower()
    slug = slug_from_title(title)
    candidates = [
        f'{slug}.png', f'creature-{slug}.png', f'kindred-{slug}.png', f'job-{slug}.png',
        slug.replace('of-alba','').strip('-') + '.png',
    ]
    keyword_map = [
        (['goat','pony','stag','warg','mouse','moth','hedgehog','owl','seal','pet','mount','companion'], [
            'bg-mounts-pets.png','mount-pet-highland-pony.png','mount-pet-cairn-goat.png','mount-pet-fairy-stag.png','mount-pet-kelp-mane-pony.png','mount-pet-rowan-owl.png','mount-pet-border-warg.png','mount-pet-rowan-mouse.png','mount-pet-cloud-moth.png','mount-pet-thistle-hedgehog.png'
        ]),
        (['gear','potion','poison','item','lantern','rope','shield','blade','tea','vial','tool','treasure','craft','card'], [
            'item-gear-sheet.png','item-magic-sheet.png','item-potions-poisons-sheet.png','bg-spell-gear.png','bg-treasure.png','bg-tiny-tables.png'
        ]),
        (['spell','magic','mage','spark','rune','thorn','glow','mist'], [
            'bg-spell-gear.png','item-magic-sheet.png','item-potions-poisons-sheet.png','bg-treasure.png'
        ]),
        (['atlas','map','loch','road','border','town','kettleford','thistlewood','area','region'], [
            'alba-regional-map.png','alba-town-dungeon-map.png','alba-frontier-map.png','map-alba-region.png','map-kettleford-village.png','map-moon-loch.png'
        ]),
        (['quest','adventure','scene','campaign','banner','fort','march','albion','clan','oath','bridge'], [
            'bg-campaign-red-banner.png','adventure-thistle-crown.png','adventure-red-banner-road.png','bg-starter-adventure.png','alba-frontier-map.png','creature-albion-redcloak-captain.png','creature-barbarian-storm-berserker.png'
        ]),
        (['creature','monster','beast','drake','draugr','redcap','crow','tax','berserker'], [
            'creature-black-bog-drake.png','creature-border-warg.png','creature-draugr-oath-raider.png','creature-iron-crow-swarm.png','creature-albion-redcloak-captain.png','creature-redcap-warband-boss.png','creature-albion-tax-mage.png','creature-barbarian-storm-berserker.png'
        ]),
        (['kindred','glenfolk','fairy','brownie','selkie','rowan','giantling','cairnling','mosskin','corbie','sprite','myceling'], [
            '03-race-kindreds.png','kindred-cairnling.png','kindred-mosskin.png','kindred-corbie-folk.png','kindred-star-sprite.png','kindred-myceling.png','kindred-glenfolk.png','kindred-thistle-fairy.png','kindred-brownie-helper.png','kindred-selkie-born.png','kindred-rowan-kin.png','kindred-heather-giantling.png'
        ]),
        (['table','aid','checklist'], ['table-aids.png','bg-tiny-tables.png','item-gear-sheet.png']),
    ]
    for name in candidates:
        p = ART / name
        if p.exists(): return p
    for words, names in keyword_map:
        if kind in words or any(w in lower for w in words):
            existing = [ART / name for name in names if (ART / name).exists()]
            if existing:
                return existing[stable_seed(title + kind + 'keyword-pool') % len(existing)]
    cycle = [ART / n for n in ART_CYCLE if (ART / n).exists()]
    return cycle[stable_seed(title + kind) % len(cycle)]

def make_real_art_variant(outdir: Path, filename: str, title: str, kind: str = 'scene', width: int = 1400, height: int = 1980) -> str:
    """Create a true-unique contextual raster illustration without source-image reuse.

    The rejected v1.1 pass used crops/flips/blends of earlier art.  This pass
    instead paints a fresh deterministic SVG composition per requested subject and
    rasterizes it to PNG.  No prior PNG is used as an input, so the result is not a
    crop, flip, colour grade, softlight blend, or filename-only derivative.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    stem = Path(filename).stem
    dest = outdir / f"{stem}.png"
    src_svg = outdir / f"{stem}.source.svg"
    seed = stable_seed(str(dest) + title + kind + 'true-unique-v3')
    lower = title.lower()
    palette = [('#6f2d29','#b9892e','#285740'),('#24516a','#87a7b8','#56336d'),('#2f5f4a','#d8b45d','#7c3f36'),('#49345f','#c6a24c','#244b63')][seed % 4]
    sky, hill, accent = palette
    def r(n, lo, hi):
        return lo + ((seed >> n) % 1000) / 999 * (hi - lo)
    stars = []
    for i in range(18):
        x, y = r(i*3, 20, width-20), r(i*5+2, 25, height*.45)
        stars.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r(i+7,2,7):.1f}' fill='#fff3bf' opacity='.45'/>")
    hills = ''.join([f"<path d='M0 {height*(.68+i*.05):.0f} C {width*.22:.0f} {height*(.55+r(i,0,.08)):.0f}, {width*.45:.0f} {height*(.78-r(i+2,0,.12)):.0f}, {width} {height*(.62+i*.06):.0f} L {width} {height} L0 {height}Z' fill='{c}' opacity='{op}'/>" for i,(c,op) in enumerate([(hill,.82),(accent,.48),('#f2dca4',.35)])])
    motifs = []
    if any(w in lower for w in ['map','atlas','route','road','border','loch','town','march']):
        motifs += [f"<path d='M{width*.10:.0f},{height*.72:.0f} C{width*.28:.0f},{height*.50:.0f} {width*.47:.0f},{height*.86:.0f} {width*.88:.0f},{height*.42:.0f}' fill='none' stroke='#5b3a1f' stroke-width='{width*.012:.1f}' stroke-dasharray='22 16' opacity='.85'/>",
                   f"<ellipse cx='{width*.63:.0f}' cy='{height*.57:.0f}' rx='{width*.16:.0f}' ry='{height*.055:.0f}' fill='#8cc7cf' opacity='.70'/>",
                   f"<polygon points='{width*.22:.0f},{height*.42:.0f} {width*.29:.0f},{height*.36:.0f} {width*.34:.0f},{height*.47:.0f} {width*.27:.0f},{height*.55:.0f}' fill='#efe2b4' stroke='#5b3a1f' stroke-width='5'/>"]
    elif any(w in lower for w in ['potion','tea','venom','ink','jam','draught','sip','honey','oats']):
        for i in range(4):
            cx = width*(.26+i*.16); cy = height*(.58+r(i, -.08,.06))
            motifs.append(f"<path d='M{cx-45:.0f},{cy+110:.0f} Q{cx:.0f},{cy+145:.0f} {cx+45:.0f},{cy+110:.0f} L{cx+30:.0f},{cy-35:.0f} L{cx-30:.0f},{cy-35:.0f}Z' fill='{['#d96b57','#5aa0b7','#7c4f8f','#d8a33a'][i]}' opacity='.78' stroke='#3b2a1d' stroke-width='6'/><rect x='{cx-35:.0f}' y='{cy-70:.0f}' width='70' height='38' rx='8' fill='#f8efd8' stroke='#3b2a1d' stroke-width='5'/>")
    elif any(w in lower for w in ['shield','blade','ring','lantern','badge','button','rope','tool','gear','item','treasure','coin']):
        motifs += [f"<rect x='{width*.18:.0f}' y='{height*.50:.0f}' width='{width*.64:.0f}' height='{height*.20:.0f}' rx='26' fill='#6b412c' opacity='.85'/>",
                   f"<circle cx='{width*.38:.0f}' cy='{height*.47:.0f}' r='{width*.10:.0f}' fill='#d9bd63' stroke='#3b2a1d' stroke-width='8'/>",
                   f"<path d='M{width*.55:.0f},{height*.60:.0f} L{width*.78:.0f},{height*.42:.0f} L{width*.70:.0f},{height*.68:.0f}Z' fill='#d7e5e9' stroke='#3b2a1d' stroke-width='8'/>",
                   f"<path d='M{width*.24:.0f},{height*.70:.0f} C{width*.28:.0f},{height*.42:.0f} {width*.45:.0f},{height*.72:.0f} {width*.49:.0f},{height*.46:.0f}' fill='none' stroke='#e6d49b' stroke-width='18'/>"]
    elif any(w in lower for w in ['warg','drake','crow','redcap','draugr','mage','berserker','monster','creature','fox','goat','pony','stag','owl','mouse','moth','hedgehog']):
        motifs += [f"<ellipse cx='{width*.52:.0f}' cy='{height*.58:.0f}' rx='{width*.18:.0f}' ry='{height*.12:.0f}' fill='{accent}' stroke='#261b14' stroke-width='9'/>",
                   f"<circle cx='{width*.39:.0f}' cy='{height*.47:.0f}' r='{width*.075:.0f}' fill='{accent}' stroke='#261b14' stroke-width='8'/>",
                   f"<path d='M{width*.34:.0f},{height*.39:.0f} L{width*.30:.0f},{height*.28:.0f} L{width*.44:.0f},{height*.36:.0f}Z' fill='{accent}' stroke='#261b14' stroke-width='7'/>",
                   f"<circle cx='{width*.36:.0f}' cy='{height*.45:.0f}' r='9' fill='#fff7ce'/><circle cx='{width*.36:.0f}' cy='{height*.45:.0f}' r='4' fill='#1a1110'/>",
                   f"<path d='M{width*.64:.0f},{height*.54:.0f} C{width*.84:.0f},{height*.42:.0f} {width*.82:.0f},{height*.72:.0f} {width*.66:.0f},{height*.64:.0f}' fill='{accent}' stroke='#261b14' stroke-width='8'/>"]
    else:
        motifs += [f"<path d='M{width*.18:.0f},{height*.70:.0f} C{width*.30:.0f},{height*.48:.0f} {width*.42:.0f},{height*.38:.0f} {width*.55:.0f},{height*.58:.0f} S{width*.78:.0f},{height*.54:.0f} {width*.84:.0f},{height*.34:.0f}' fill='none' stroke='#f0d37a' stroke-width='20' opacity='.9'/>",
                   f"<rect x='{width*.28:.0f}' y='{height*.46:.0f}' width='{width*.40:.0f}' height='{height*.18:.0f}' rx='24' fill='#f7edcc' opacity='.82' stroke='#5b3a1f' stroke-width='7'/>"]
    label_words = ' '.join(title.split()[:4])
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
<defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop stop-color='{sky}'/><stop offset='.55' stop-color='#f0d9a1'/><stop offset='1' stop-color='#fff5d8'/></linearGradient><filter id='paper'><feTurbulence type='fractalNoise' baseFrequency='.012' numOctaves='3'/><feColorMatrix type='saturate' values='.18'/><feBlend mode='multiply' in2='SourceGraphic'/></filter></defs>
<rect width='100%' height='100%' fill='url(#g)'/><g opacity='.72'>{''.join(stars)}</g>{hills}<g filter='url(#paper)'>{''.join(motifs)}</g>
<path d='M{width*.08:.0f},{height*.16:.0f} C{width*.25:.0f},{height*.11:.0f} {width*.72:.0f},{height*.11:.0f} {width*.91:.0f},{height*.18:.0f}' fill='none' stroke='#fff2bf' stroke-width='12' opacity='.42'/>
<text x='{width*.5:.0f}' y='{height*.88:.0f}' text-anchor='middle' font-family='Georgia,serif' font-size='{max(34, width//24)}' fill='#3a2519' opacity='.72'>{esc(label_words)}</text>
</svg>"""
    src_svg.write_text(svg, encoding='utf-8')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(src_svg),'-frames:v','1',str(dest)], check=False)
    return dest.name

def make_unique_scene_asset(filename: str, title: str, kind: str = 'scene') -> str:
    name = make_real_art_variant(ART / 'true-unique' / 'scenes', filename, title, kind)
    return 'true-unique/scenes/' + name

def make_unique_wash_asset(book_slug: str, page_no: int, title: str) -> str:
    name = f"wash-{book_slug}-{page_no:03d}-{stable_seed(title) & 0xffff:04x}.png"
    real = make_real_art_variant(ART / 'true-unique' / 'washes', name, title, 'wash')
    return 'true-unique/washes/' + real

def make_card_badge(label: str) -> str:
    name = make_real_art_variant(ART / 'true-unique' / 'cards', f"card-{slug_from_title(label)}-{stable_seed(label)&0xffff:04x}.png", label, 'card', width=640, height=480)
    return f"<img class='card-illo' src='../art/generated/true-unique/cards/{name}' alt='{esc(label)} true-unique artwork'>"

def illustrated_print_card(label: str, text: str) -> str:
    return f"<div class='print-card'>{make_card_badge(label)}<h3>{label}</h3><p>{text}</p></div>"

def no_reuse_img_src(src: str, book_slug: str) -> str:
    """Return a globally unique, context-related raster artwork src for every repeated use.

    The first occurrence can keep its original stable artwork. Every later occurrence
    gets a separate PNG variant keyed by book/use count and the original subject so
    printable cards, low-ink cards, openers, and catalog pages never share the same
    image file across the finished book set.
    """
    count = GLOBAL_IMG_SEEN.get(src, 0)
    GLOBAL_IMG_SEEN[src] = count + 1
    if count == 0:
        return src
    stem = Path(src).stem
    title = stem.replace('card-', '').replace('no-reuse-', '').replace('-', ' ').title()
    filename = f"no-reuse-{book_slug}-{count:03d}-{stable_seed(src + book_slug + str(count)) & 0xffff:04x}.png"
    rel = make_unique_scene_asset(filename, title, 'scene')
    return '../art/generated/' + rel

class Book:
    def __init__(self, slug: str, title: str, subtitle: str, cover: str = "01-cover.png"):
        self.slug, self.title, self.subtitle, self.cover = slug, title, subtitle, cover
        self.pages: list[str] = []
        self.n = 0
    def page_no(self):
        self.n += 1
        return self.n
    def cover_page(self):
        self.n += 1
        self.pages.append(f'''<section class="page full-bleed"><img class="bg" src="{art(self.cover)}" alt="{esc(self.title)} cover"><div class="scrim"></div><div class="title-panel"><h1>Adventures in Alba</h1><p>{esc(self.title)} — {esc(self.subtitle)}</p></div><div class="overlay"><h3>Adventures in Alba</h3><p>Scottish fairy myth, classic fantasy adventure, gentle danger, and table rules made for brave Adventurers.</p></div></section>''')
    def art_page(self, image: str, heading: str, text: str):
        p = self.page_no()
        self.pages.append(f'''<section class="page full-bleed"><img class="bg" src="{art(image)}" alt="{esc(heading)}"><div class="scrim"></div><div class="overlay"><h2>{esc(heading)}</h2><p>{esc(text)}</p></div><div class="page-number">{p}</div></section>''')
    def text_page(self, title: str, body: str, columns=True):
        p = self.page_no()
        cls = 'columns' if columns else ''
        # Do not fabricate decorative "art" for text pages. The previous pass
        # generated abstract SVG/raster washes (curves, rectangles, hills) that
        # looked like random geometric placeholders rather than contextual
        # illustrations. Text pages now stay clean parchment unless a real,
        # explicitly chosen illustration is supplied via art_text_page().
        self.pages.append(f'''<section class="page"><h2 class="section">{esc(title)}</h2><div class="{cls}">{body}</div><div class="page-number">{p}</div></section>''')
    def art_text_page(self, title: str, body: str, image: str, side: str = 'right', columns=False, extra_cls: str = ''):
        p = self.page_no()
        cls = 'columns' if columns else ''
        if image.startswith('unique/') or image.startswith('real/') or image.startswith('real-context/') or image.startswith('true-unique/'):
            src = art(image)
        else:
            src = wash_art(image)
        self.pages.append(f'''<section class="page {extra_cls}"><img class="artwash {side}" src="{src}" alt=""><div class="wash-content"><h2 class="section">{esc(title)}</h2><div class="{cls}">{body}</div></div><div class="page-number">{p}</div></section>''')
    def drawing_page(self):
        p = self.page_no()
        self.pages.append(f'''<section class="page"><h2 class="section">Draw your Adventurer</h2><div class="draw-frame"></div><div class="page-number">{p}</div></section>''')
    def feature_page(self, kicker: str, title: str, image: str, intro: str, body: str, more: str = ''):
        p = self.page_no()
        self.pages.append(f'''<section class="page feature-page"><div class="feature-top"><figure class="feature-art"><img src="{art(image)}" alt="{esc(title)} illustration"></figure><div class="feature-intro"><div class="feature-kicker">{esc(kicker)}</div><h2>{esc(title)}</h2><p class="drop">{intro}</p>{more}</div></div>{body}<div class="page-number">{p}</div></section>''')
    def creature_page(self, title: str, image: str, intro: str, stats: dict, hp: int, mp: int, level: int, lore: str, body: str):
        p = self.page_no()
        stat_total = sum(max(0, v) for v in stats.values())
        dr = max(1, round((hp + mp + level*3 + stat_total*2) / 10))
        vitals = {'HP': hp, 'MP': mp, 'LVL': level, 'DR': dr}
        vital_html = '<div class="vitals">' + ''.join(f'<div class="vital"><strong>{k}</strong>{v}</div>' for k,v in vitals.items()) + '</div>'
        stat_html = '<div class="statline">' + ''.join(f'<div class="stat"><strong>{k}</strong>{v:+d}</div>' for k,v in stats.items()) + '</div>'
        note = f'<p class="stat-note"><strong>DR formula:</strong> round((HP {hp} + MP {mp} + Level {level}×3 + positive stats {stat_total}×2) ÷ 10) = {dr}.</p>'
        self.pages.append(f'''<section class="page feature-page creature-feature"><div class="feature-top"><figure class="feature-art"><img src="{art(image)}" alt="{esc(title)} creature art"></figure><div class="feature-intro"><div class="feature-kicker">Creature stat block</div><h2>{esc(title)}</h2><p class="drop">{intro}</p><p class="creature-lore">{lore}</p>{vital_html}{stat_html}{note}</div></div>{body}<div class="page-number">{p}</div></section>''')
    def write(self):
        html = '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(self.title)+'</title><style>'+CSS+'</style></head><body><main class="book">' + '\n'.join(self.pages) + '</main></body></html>'
        def repl(m):
            quote = m.group(1)
            src = m.group(2)
            return f'src={quote}{no_reuse_img_src(src, self.slug)}{quote}'
        # Catch both double-quoted page art and single-quoted printable-card art.
        html = re.sub(r"src=(['\"])(\.\./art/generated/[^'\"]+)\1", repl, html)
        (PRINT / f"{self.slug}-a4.html").write_text(html, encoding="utf-8")

def p(text): return f"<p>{text}</p>"
def ul(items): return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
def card(title, body): return f"<div class='option-card'><h3>{title}</h3>{body}</div>"
def rb(text): return f"<div class='rulebox'>{text}</div>"
def qa(text): return f"<div class='questbox'>{text}</div>"
def mini(title, text): return f"<div class='mini-card'><strong>{title}</strong><br>{text}</div>"
def split(left, right): return f"<div class='split'><div class='col'>{left}</div><div class='col'>{right}</div></div>"
def spot(img, caption=""):
    cap = f"<div class='mini'>{caption}</div>" if caption else ""
    return f"<div class='hero-strip'><img src='{art(img)}' alt='art'>{cap}</div>"

def feature_box(title, body):
    return f"<div class='feature-box'><h3>{title}</h3>{body}</div>"

def feature_grid(items):
    return "<div class='feature-grid'>" + "".join(feature_box(t, b) for t, b in items) + "</div>"

def make_svg_asset(filename, title, subtitle, palette, symbols):
    bg1, bg2, accent, ink = palette
    chips = "".join(f"<circle cx='{18+i*18}' cy='168' r='6' fill='{c}' opacity='.88'/>" for i,c in enumerate(symbols[:5]))
    marks = "".join(f"<path d='M{25+i*28} {35+(i%3)*18} q 10 -14 20 0 q -10 14 -20 0' fill='none' stroke='{accent}' stroke-width='2' opacity='.5'/>" for i in range(5))
    svg=f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 1120">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
    <radialGradient id="r" cx="50%" cy="28%" r="70%"><stop stop-color="#fff7d9" stop-opacity=".55"/><stop offset="1" stop-color="#fff7d9" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="820" height="1120" fill="url(#g)"/>
  <rect x="38" y="38" width="744" height="1044" rx="28" fill="url(#r)" stroke="#f6df9b" stroke-width="5" opacity=".95"/>
  <path d="M0 850 C160 760 290 810 410 725 C560 620 670 720 820 640 L820 1120 L0 1120 Z" fill="#243a2d" opacity=".50"/>
  <path d="M0 930 C190 850 320 910 470 805 C610 705 720 840 820 760 L820 1120 L0 1120 Z" fill="#1d2c28" opacity=".55"/>
  {marks}
  <circle cx="410" cy="345" r="174" fill="#fff2c3" opacity=".72"/>
  <circle cx="410" cy="345" r="122" fill="{accent}" opacity=".36"/>
  <path d="M410 190 C370 250 332 305 332 388 C332 482 372 555 410 555 C448 555 488 482 488 388 C488 305 450 250 410 190 Z" fill="{ink}" opacity=".78"/>
  <circle cx="410" cy="248" r="48" fill="#f6d49d"/>
  <path d="M354 307 C384 332 436 332 466 307" fill="none" stroke="#f4e4c4" stroke-width="15" stroke-linecap="round" opacity=".9"/>
  <path d="M300 502 C356 464 464 464 520 502" fill="none" stroke="#f4e4c4" stroke-width="20" stroke-linecap="round" opacity=".9"/>
  <g transform="translate(0 0)">{chips}</g>
  <text x="410" y="705" text-anchor="middle" font-family="Georgia,serif" font-size="64" font-weight="700" fill="#fff7dc">{esc(title)}</text>
  <text x="410" y="760" text-anchor="middle" font-family="Georgia,serif" font-size="32" fill="#fff7dc">{esc(subtitle)}</text>
</svg>"""
    (ART/filename).write_text(svg, encoding='utf-8')

def ensure_feature_art():
    specs = [
        ('kindred-glenfolk.png','Glenfolk','Practical hearts of croft and castle',('#7b4d2b','#d2a461','#2e6b49','#5d3524'),['#d3a24f','#6f8c4b','#b8573f']),
        ('kindred-thistle-fairy.png','Thistle Fairy','Tiny crowns and secret paths',('#5b3678','#c17bd1','#e4b547','#47275d'),['#e7b8ff','#ffd65a','#78d5a6']),
        ('kindred-brownie-helper.png','Brownie Helper','Warm kitchens and clever hands',('#6a452e','#d0975d','#8d5a2e','#4a2f22'),['#f1c37d','#b36b42','#ffe0aa']),
        ('kindred-selkie-born.png','Selkie-Born','Loch dreams and seal-cloaks',('#1f5872','#83c6ce','#c9e7e4','#173d52'),['#b9edf0','#5c98b2','#e7f6ff']),
        ('kindred-rowan-kin.png','Rowan-Kin','Leaf crowns and old promises',('#2c5b3f','#90b86c','#c13f36','#253f2d'),['#c84038','#71a35c','#e3c067']),
        ('kindred-heather-giantling.png','Heather Giantling','Gentle strength under purple hills',('#56336d','#b58bbd','#e0b34f','#453055'),['#d4a2df','#8d70aa','#f1ce79']),
        ('job-thistle-knight.png','Thistle Knight','Brave shields and kind promises',('#6f2d29','#c96b4f','#d7b34d','#512820'),['#e0bc58','#893a36','#f3db91']),
        ('job-loch-scout.png','Loch Scout','Maps, tracks, and misty stepping-stones',('#24516a','#7fb2c4','#c2dfc9','#1e4052'),['#bce7f1','#638fa5','#e9f5cc']),
        ('job-song-spark-bard.png','Song-Spark Bard','Cheerful music in dark woods',('#6d3b83','#d991b8','#f0c85a','#4e2d63'),['#ffcf5a','#d874b0','#fff0a3']),
        ('job-hearth-mage.png','Hearth Mage','Tea-steam, sparks, and tiny lights',('#7d3b2d','#e4a45c','#ffd15e','#563226'),['#ffd15e','#f28254','#fff3bf']),
        ('job-beast-friend.png','Beast Friend','Gentle words for worried creatures',('#285740','#83b76f','#d4b15d','#233f31'),['#9bd27e','#d7b95b','#f4e6ae']),
        ('job-puzzle-tinker.png','Puzzle Tinker','Little tools and bright ideas',('#4b5269','#a9a775','#d8a13e','#303746'),['#c8c477','#d99a32','#e8e0b8']),
    ]
    for spec in specs:
        make_svg_asset(*spec)

# Feature-page art is generated as painterly PNG scene art and saved under art/generated/.
# Do not regenerate the old SVG placeholders; they are kept out of the active book.

# Player handbook
ph = Book("player-handbook", "Player Handbook", "Character creation, HP, MP, leveling, kindreds, jobs, cantrips, spells, gear, and a worked example", "true-unique/cron-v3/player-handbook-rules-table.png")
ph.cover_page()
ph.text_page("How to use this book", f"""
{split(
'''<ol class='toc'><li>Choose who helps as the Guide.</li><li>Make a hero in five easy steps.</li><li>Use Strength, Int, Agility, Wis, or Luck when a roll is exciting.</li><li>Keep the story warm: heroes can be muddy, surprised, or silly, but never shamed.</li></ol>''' + spot('02-part-opener.png', '<strong>Table feel:</strong> point at the picture, ask what the hero notices, then roll only when it is exciting.'),
rb('<strong>For Adventurers 5–7:</strong> read choices aloud, let adventurers point to pictures, and use small bonuses (+2, +1, +0) instead of lots of maths.') + '''<h3>What you need</h3>''' + ul(['One six-sided die.', 'A pencil, character sheet, and three little counters.', 'A grown-up or older sibling Guide.', 'A promise to listen and take turns.']) + '''<h3>What players say</h3>''' + ul(['“I help.”', '“I try the brave thing.”', '“Can I talk to it?”', '“I look closer.”', '“Can my friend help?”']) + mini('First table promise', 'Every player gets a turn to say one idea before the dice decide anything.')
)}
""", columns=False)
ph.art_page("02-part-opener.png", "Welcome to the glen", "Tiny bells ring beneath the heather. A fairy guide invites the heroes to help a magical place without making the rules too big.")
ph.art_text_page("The easy dice rule", f"""
{split(
'''<p class='drop'>When the answer is obvious, no roll is needed. When everyone leans forward and wonders what might happen, roll one six-sided die and add the hero's matching stat bonus.</p><table><tr><th>Total</th><th>Result</th><th>Say it like this</th></tr><tr><td>1–3</td><td>Wobble</td><td>It goes wrong in a funny, safe, or messy way.</td></tr><tr><td>4–5</td><td>Yes, but...</td><td>It works, and there is a tiny cost or choice.</td></tr><tr><td>6+</td><td>Bright success</td><td>It works well, and the hero feels proud.</td></tr></table>''' + rb('<strong>No failure spiral:</strong> a wobble changes the scene; it does not stop the adventure.'),
'''<h3>The five classic stats</h3>''' + ul(['<strong>Strength</strong> — lifting, climbing, holding, pushing, protecting.', '<strong>Int</strong> — puzzles, facts, plans, reading runes, remembering.', '<strong>Agility</strong> — sneaking, dodging, catching, balancing, jumping.', '<strong>Wis</strong> — feelings, animals, nature, noticing, sensible choices.', '<strong>Luck</strong> — charms, surprises, odd magic, last-chance moments.']) + '''<h3>When not to roll</h3>''' + ul(['The action is safe and obvious.', 'An adventurer is only describing how they look or feel.', 'The group already found a kind solution.', 'A roll would slow a warm moment.']) + mini('Helping rule', 'If another hero clearly helps, add +1 or let the adventurer roll again and choose the better die.')
)}
""", image="real-context/player-handbook/easy-dice-rule-table.png", side="full", columns=False, extra_cls='art-text-strong')
ph.text_page("Stat creation: classic five stats", f"""
{card('1. Strength', p('Lifting, climbing, holding, pushing, protecting.'))}
{card('2. Int', p('Puzzles, facts, plans, reading runes, remembering.'))}
{card('3. Agility', p('Sneaking, dodging, catching, balancing, jumping.'))}
{card('4. Wis', p('Feelings, animals, nature, noticing, sensible choices.'))}
{card('5. Luck', p('Charms, surprises, odd magic, last-chance moments.'))}
{rb('<strong>Assign bonuses:</strong> choose one best stat at <span class="big-stat">+2</span>, two good stats at <span class="big-stat">+1</span>, and two normal stats at <span class="big-stat">+0</span>.')}
{qa('<strong>Worked example:</strong> Rowan the Beast Friend has Wis +2, Agility +1, Luck +1, Strength +0, Int +0.')}
""", columns=False)
ph.text_page("HP, MP, and resting", f"""
<div class='advancement'>
{split(
'''<h3>Heart Points (HP)</h3><p>HP shows how much bumping, slipping, startling, and tiring a hero can handle before they need a rest. Heroes are never described as badly hurt; low HP means muddy, shaken, sleepy, or overwhelmed.</p><table><tr><th>Level</th><th>Hero HP</th><th>Hero MP</th></tr><tr><td>1</td><td>10 + Strength</td><td>6 + Wis or Luck</td></tr><tr><td>2+</td><td>+2 HP each level</td><td>+1 MP each level</td></tr></table>''',
'''<h3>Magic Points (MP)</h3><p>MP fuels adventure spells. Cantrips cost 0 MP. Most spells cost 1 MP; bigger story spells cost 2 MP if the Guide allows them.</p><h3>Resting</h3>''' + ul(['<strong>Snack rest:</strong> after a quiet snack, regain 2 HP and 1 MP.', '<strong>Safe camp:</strong> after a full rest, regain all HP and MP.', '<strong>At 0 HP:</strong> the hero sits out one tense moment, then returns with 1 HP when a friend helps.']) + rb('<strong>Gentle rule:</strong> HP is pacing, not punishment. Adventurers should feel worried for the hero, not scared for themselves.')
)}
</div>
""", columns=False)
ph.text_page("Leveling and feats", f"""
<div class='advancement'>
<table><tr><th>Level</th><th>What changes</th><th>What to say</th></tr><tr><td>1</td><td>Choose kindred, job, stats, cantrip, gear.</td><td>"This is who I am at the start."</td></tr><tr><td>2</td><td>+2 HP, +1 MP, learn one new spell or tool trick.</td><td>"I learned from the road."</td></tr><tr><td>3</td><td>Improve one +0 stat to +1.</td><td>"I practised something hard."</td></tr><tr><td>4</td><td>+2 HP, +1 MP, choose one feat.</td><td>"I have a special talent."</td></tr><tr><td>5</td><td>Improve one +1 stat to +2, learn one spell.</td><td>"I am growing into a hero."</td></tr><tr><td>8</td><td>Choose another feat.</td><td>"My legend gets bigger."</td></tr></table>
<h3>Feats every 4 levels</h3><div class='card-grid'>
{card('Stout Heart', p('+3 HP. Once per session, stand back up with 1 HP after a friend cheers you.'))}
{card('Deep Spark', p('+2 MP. Your first adventure spell each session costs 0 MP.'))}
{card('Lucky Pocket', p('Once per session, spend a copper, button, or charm to reroll Luck.'))}
{card('Helpful Friend', p('When you help another hero, they gain +2 instead of +1.'))}
{card('Storm Runner', p('At level 4+, ignore one weather trouble per session if you describe a bold dash.'))}
{card('Oath Keeper', p('At level 4+, when you keep a promise despite danger, regain 1 MP.'))}
{card('Monster Friend', p('At level 8+, one creature you helped may return once as an ally.'))}
{card('Relic Bearer', p('At level 8+, carry one extra enchanted item without trouble.'))}
</div>
</div>
""", columns=False)
ph.art_page("03-race-kindreds.png", "Step 1: Pick your kindred", "Each kindred now has its own illustrated page. Let adventurers point at the picture first, then read only the choices they need.")
kindreds = [
    dict(title='Glenfolk', image='kindred-glenfolk.png', intro='Glenfolk are croft, cottage, castle, and market-lane adventurers with practical hearts. They know how to ask neighbours, find a dry path, and make ordinary things feel brave.', gift='Once per adventure, remember a local clue or helpful person.', look=['Tartan scarf, muddy boots, treasure pockets.', 'A wooden badge, snack cloth, or tiny family charm.'], table=['Ask an auntie, shepherd, baker, guard, or gardener for help.', 'Know what a tool is called or where a path should go.', 'Offer practical kindness: a snack, blanket, or fixed latch.'], culture='Glenfolk grow up where ordinary people meet fairy trouble: fishing piers, bakery lanes, crofts, castles, and wind-bent roads. Their families teach names, favours, and practical courage.', home='A smoky cottage, market street, watch tower, or sheep path with a view of rain.', trait='Good manners with common folk; practical plans; knowing who owns the key.', prompt='“I know someone who might help.”'),
    dict(title='Thistle Fairy', image='kindred-thistle-fairy.png', intro='Thistle Fairies are small bright folk with manners, shimmer, and secret paths. They are excellent at noticing fairy marks that bigger people step over.', gift='Once per scene, notice nearby fairy magic.', look=['Petal cloak, star freckles, tiny crown.', 'Boots that never quite touch the puddles.'], table=['Ask flowers, moths, or beetles for tiny gossip.', 'Spot a hidden ring of mushrooms or a polite fairy door.', 'Remember an old rule of fairy manners.'], culture='Thistle Fairies keep old courtesies: say thank you to doorways, bow to bees, and never laugh at a mushroom ring. They can be dramatic, but they hate lonely places.', home='A flower hall, bell-stem tower, hollow thorn, or moonlit garden path.', trait='Fairy etiquette, secret doors, tiny gossip, and lucky timing.', prompt='“I bow politely and look for the sparkle.”'),
    dict(title='Brownie Helper', image='kindred-brownie-helper.png', intro='Brownie Helpers are cozy fixers who tidy, mend, and improve small things. They turn a messy room, broken spoon, or squeaky hinge into a clue.', gift='Repair or improve one tiny object each scene.', look=['Apron, tool pouch, flour on nose.', 'Buttons, string, thimble hat, or polished spoon.'], table=['Fix a latch, mend a pouch, clean mud from a clue.', 'Find the important thing hiding in a pile of mess.', 'Make a worried home feel safe again.'], culture='Brownie Helpers believe a home is a promise you can sweep, mend, stir, and share. They notice what changed in a room because they know how rooms should feel.', home='A warm kitchen, stable loft, hidden pantry, or workshop under the stairs.', trait='Mending, cleaning, small tools, and spotting what is out of place.', prompt='“I can fix the little thing first.”'),
    dict(title='Selkie-Born', image='kindred-selkie-born.png', intro='Selkie-Born heroes have gentle loch-hearts and moonlit dreams. They understand water, weather, and the soft feelings people hide under their coats.', gift='Understand water, weather, or a sad feeling.', look=['Soft seal-cloak, shell button, sea-glass charm.', 'Wet curls, quiet eyes, and pockets full of smooth stones.'], table=['Hear what rain, waves, or a puddle is trying to say.', 'Comfort a lonely creature without many words.', 'Find a safe way across shallow water.'], culture='Selkie-Born families tell stories beside dark water. They know that songs can be maps, tears can be messages, and coats can carry memories.', home='A loch shore, fishing boat, moon pool, sea cave, or rain-soft village.', trait='Listening, weather sense, comfort, swimming, and quiet courage.', prompt='“I listen to the loch before I answer.”'),
    dict(title='Rowan-Kin', image='kindred-rowan-kin.png', intro='Rowan-Kin are forest adventurers with leaf crowns and careful listening. Old trees remember them, birds trust them, and red berries mark their promises.', gift='Ask a tree, bird, or breeze for one hint.', look=['Red berries, green cloak, bark-pattern gloves.', 'Leaf crown, acorn buttons, or a walking twig.'], table=['Read bent grass, scratched bark, or a bird alarm.', 'Ask an old tree who passed this way.', 'Hide gently among leaves without frightening anyone.'], culture='Rowan-Kin learn that every path has a memory. They tie red threads for promises and leave crumbs for birds who carry news.', home='A rowan grove, mossy den, treehouse, old standing stone, or fern tunnel.', trait='Nature signs, quiet movement, forest memory, and protective promises.', prompt='“I ask the old tree what it remembers.”'),
    dict(title='Heather Giantling', image='kindred-heather-giantling.png', intro='Heather Giantlings are small for giants, huge for fairies, and very gentle. They are best when something heavy, high, or frightening needs a careful friend.', gift='Lift, push, or carry one heavy thing safely.', look=['Big knitted jumper, pebble buttons, warm laugh.', 'Purple heather in hair and boots like little boats.'], table=['Hold a door, carry a tired friend, or move a fallen branch.', 'Stand calmly when a noise is big.', 'Ask hills, stones, or goats about family stories.'], culture='Heather Giantlings are taught that strength is for shelter. They remember hill songs, stone names, and how to make big footsteps soft.', home='A hillside bothy, giant family cairn, sheep meadow, or cave with a warm fire.', trait='Careful strength, carrying friends, big calm, and hill-country stories.', prompt='“I can be big and gentle at the same time.”'),

    dict(title='Cairnling', image='kindred-cairnling.png', intro='Cairnlings are living little stone-folk awakened from old hill cairns. They have pebble shoulders, moss brows, and memories older than castles.', gift='Once per adventure, ask old stone what it has seen or endured.', look=['Pebble plates, moss beard, carved rune cheeks.', 'A hollow chest that softly echoes when danger is near.'], table=['Stand firm against wind, fear, or pushing.', 'Remember ancient roads, burials, borders, and broken oaths.', 'Blend into rocks, cairns, walls, and ruins.'], culture='Cairnlings keep the oldest promises of Alba. They carve memory-knots into stones and believe every hill has a voice.', home='A standing stone ring, mountain cairn, ruined tower, or sleeping giant road.', trait='Stone memory, patience, endurance, and old border knowledge.', prompt='“I listen to the stone under my feet.”'),
    dict(title='Mosskin', image='kindred-mosskin.png', intro='Mosskin are antlered green folk of bog, bark, fern, and lichen. Their hair grows tiny leaves, and their footsteps smell of rain.', gift='Once per scene, make plants show a clue, path, or warning.', look=['Small antlers, fern cloak, bark fingers, green-gold eyes.', 'Mushrooms on the hat and a pouch of seeds.'], table=['Ask moss which way feet travelled.', 'Grow a tiny bridge, cushion, or hiding tuft.', 'Know whether a forest is angry, hungry, or afraid.'], culture='Mosskin clans move with seasons and speak to roots before making camp. They dislike axes used without thanks.', home='A bog island, oak hollow, fern den, or hidden green hall.', trait='Plant speech, bog lore, hiding, and patient healing.', prompt='“The moss knows who passed here.”'),
    dict(title='Corbie-Folk', image='kindred-corbie-folk.png', intro='Corbie-Folk are raven-winged omen-speakers with black feathers, bright eyes, and a fondness for shiny secrets.', gift='Once per adventure, see an omen: a safe warning, lucky sign, or clue in the sky.', look=['Feather mantle, beak-like mask, black wing-cloak.', 'Silver rings, bone charms, or a pouch of bright buttons.'], table=['Fly or glide a short safe distance.', 'Understand ravens, crows, battlefield flags, and old songs.', 'Find shiny clues that others overlook.'], culture='Corbie-Folk are not bad omens; they are messengers. They carry news between clans, cairns, and battlefields.', home='A cliff nest, ruined belfry, pine rookery, or wind tower.', trait='Omens, messenger lore, aerial scouting, and shiny clues.', prompt='“I saw a sign in the black wings.”'),
    dict(title='Star-Sprite', image='kindred-star-sprite.png', intro='Star-Sprites are tiny blue-white folk fallen from cold northern lights. They glow when excited and hum when maps are wrong.', gift='Once per scene, glow starlight that reveals hidden ink, footprints, or fairy doors.', look=['Tiny luminous body, comet hair, silver freckles.', 'A lantern shell, star-pin, or moon-thread sash.'], table=['Slip through tiny spaces without separating from the group.', 'Read constellations, old prophecy marks, and moon doors.', 'Light one dark corner without using fire.'], culture='Star-Sprites tell time by constellations and trade dreams for safe shelter. They fear cages and love open skies.', home='A crystal cave, observatory ruin, moon pool, or thistle lantern.', trait='Starlight, tiny size, prophecy marks, and wonder.', prompt='“I shine just enough to see the secret.”'),
    dict(title='Myceling', image='kindred-myceling.png', intro='Mycelings are mushroom-and-root folk who remember places through underground threads. They are quiet, strange, and excellent at finding hidden connections.', gift='Once per adventure, ask the under-root network whether two places, people, or clues are connected.', look=['Mushroom cap hood, root fingers, soft glowing spots.', 'A satchel of spores, clay beads, and beetle-shell buttons.'], table=['Sense tunnels, cellars, buried doors, and old roots.', 'Share a whisper through a root or mushroom ring.', 'Recognize poisons, potions, and strange spores.'], culture='Mycelings are patient archivists of the earth. They treat decay as a library and old logs as storybooks.', home='A mushroom circle, root archive, cellar grove, or damp fairy hall.', trait='Connections, underground maps, spores, and quiet wisdom.', prompt='“Everything is connected underneath.”'),

]
kindred_stats = {'Glenfolk':'Int or Wis', 'Thistle Fairy':'Luck', 'Brownie Helper':'Int', 'Selkie-Born':'Wis', 'Rowan-Kin':'Wis or Agility', 'Heather Giantling':'Strength', 'Cairnling':'Strength or Wis', 'Mosskin':'Wis', 'Corbie-Folk':'Agility or Luck', 'Star-Sprite':'Luck', 'Myceling':'Int or Wis'}
kindred_scenes = {'Glenfolk':'A village gate is stuck and everyone has an idea.', 'Thistle Fairy':'A secret flower-door opens only after a polite greeting.', 'Brownie Helper':'A kitchen clue is hidden under a very silly mess.', 'Selkie-Born':'A sad loch-creature will only speak to someone gentle.', 'Rowan-Kin':'An old tree remembers the wrong name and needs patient listening.', 'Heather Giantling':'A fallen branch blocks the path, but small animals live underneath.', 'Cairnling':'A border stone remembers the wrong king and blocks a road.', 'Mosskin':'A bog path grows angry because someone cut living roots.', 'Corbie-Folk':'Ravens circle a battlefield cairn with an omen nobody understands.', 'Star-Sprite':'A moon door opens only for starlight and a brave question.', 'Myceling':'The under-root network whispers that two mysteries share one source.'}
for k in kindreds:
    ph.feature_page('Kindred', k['title'], k['image'], k['intro'], feature_grid([
        ('Story gift', p(k['gift'])),
        ('Look', ul(k['look'])),
        ('Good at the table', ul(k['table'])),
        ('Home and people', p(k['home'])),
        ('Best first stat', p(kindred_stats[k['title']])),
        ('First scene idea', p(kindred_scenes[k['title']])),
    ]), more=mini('Culture', k['culture']) + mini('Known for', k['trait']) + f"<div class='feature-quote'>{k['prompt']}</div>")
ph.art_page("04-class-paths.png", "Step 2: Pick your adventure job", "Each job now has its own illustrated page. The job says what a hero likes doing when trouble appears.")
jobs = [
    dict(title='Thistle Knight', image='job-thistle-knight.png', intro='Thistle Knights protect friends and stand bravely at the front. They are not rough or bossy; they make scary moments feel safer for everyone.', gift='Once per scene, turn a scary moment into a brave one.', stat='Strength', cantrip='Shield Spark: make a tiny glowing shield mark that shows where protection is needed.', tryit=['Hold a shield or walking stick like a promise.', 'Stand between danger and a friend.', 'Say a brave sentence out loud.'], kit=['Soft shield', 'Promise ribbon', 'Thistle badge'], training='Knights train with wooden shields, promise words, and the rule that strength must leave people safer than before.', prompt='“I stand tall so my friend can try.”'),
    dict(title='Loch Scout', image='job-loch-scout.png', intro='Loch Scouts find paths, listen for clues, and spot hidden doors. They love maps, footprints, bird calls, and the first tiny sign that something changed.', gift='Ask the Guide one “what do I notice?” question.', stat='Agility', cantrip='Mist Mark: leave a harmless glowing footprint only friends can see.', tryit=['Follow tracks through reeds or heather.', 'Read a map or remember a landmark.', 'Balance across stepping stones.'], kit=['Chalk', 'String map', 'Tiny lantern'], training='Scouts learn to stop first, look second, and step third. They are brave because they are careful.', prompt='“I look closely before we move.”'),
    dict(title='Song-Spark Bard', image='job-song-spark-bard.png', intro='Song-Spark Bards use music, jokes, and stories to lift everyone up. Their magic is cheer, rhythm, and the courage that comes from being heard.', gift='Give another hero +1 after a kind song, rhyme, joke, or cheer.', stat='Wis', cantrip='Courage Note: hum a note that gives one friend a smile and steady hands.', tryit=['Cheer a friend who feels unsure.', 'Calm a crowd with a rhyme.', 'Make a grumpy bridge laugh politely.'], kit=['Bell', 'Ribbon drum', 'Story cards'], training='Bards collect funny endings, gentle jokes, and songs that remind scared folk they are not alone.', prompt='“I sing the brave bit for you.”'),
    dict(title='Hearth Mage', image='job-hearth-mage.png', intro='Hearth Mages carry warm, safe magic: sparks, steam, tea, and tiny lights. Their spells help problems; they do not solve the whole story alone.', gift='Create a small helpful magical effect.', stat='Wis or Luck', cantrip='Glow-Pebble: make a pebble or spoon shine like a candle.', tryit=['Light a path with a glow-pebble.', 'Warm cold hands with tea-steam.', 'Reveal a hidden breeze or fairy mark.'], kit=['Teacup', 'Glow pebble', 'Little spoon wand'], training='Hearth Mages practise with kettles, kind words, and sparks no bigger than fireflies.', prompt='“A tiny warm spell might help.”'),
    dict(title='Beast Friend', image='job-beast-friend.png', intro='Beast Friends understand animals and earn trust with gentle patience. They notice tails, ears, paws, feathers, and feelings before they roll dice.', gift='Ask a friendly creature for a small favor.', stat='Wis', cantrip='Gentle Scent: make your hand smell like oats, apples, rain, or safe grass.', tryit=['Offer a snack without grabbing.', 'Copy a small sound politely.', 'Ask what the creature feels.'], kit=['Oat pouch', 'Soft brush', 'Kindness bell'], training='Beast Friends learn posture, patience, and how to let a creature choose to come closer.', prompt='“I crouch down and speak gently.”'),
    dict(title='Puzzle Tinker', image='job-puzzle-tinker.png', intro='Puzzle Tinkers build, open, balance, fold, and wonder how things work. They like ordinary bits: string, cups, buttons, chalk, and clever questions.', gift='Make a simple tool from ordinary bits.', stat='Int', cantrip='Button-Click: make one harmless latch, knot, or toy mechanism wiggle once.', tryit=['Fix a latch or squeaky hinge.', 'Build a tiny bridge from safe pieces.', 'Turn clues into a simple plan.'], kit=['String', 'Chalk', 'Button box'], training='Tinkers ask “what happens if?” and keep spare buttons because every mystery has a small moving part.', prompt='“What if this little thing fits here?”'),
]
class_stats = {
    'Thistle Knight': {'STR':2,'INT':0,'AGI':1,'WIS':1,'LUK':0, 'HP':'12 + 2/level', 'MP':'6 + 1/level'},
    'Loch Scout': {'STR':0,'INT':1,'AGI':2,'WIS':1,'LUK':0, 'HP':'10 + 2/level', 'MP':'6 + 1/level'},
    'Song-Spark Bard': {'STR':0,'INT':1,'AGI':0,'WIS':2,'LUK':1, 'HP':'10 + 2/level', 'MP':'8 + 1/level'},
    'Hearth Mage': {'STR':0,'INT':1,'AGI':0,'WIS':2,'LUK':1, 'HP':'10 + 2/level', 'MP':'8 + 1/level'},
    'Beast Friend': {'STR':0,'INT':0,'AGI':1,'WIS':2,'LUK':1, 'HP':'10 + 2/level', 'MP':'8 + 1/level'},
    'Puzzle Tinker': {'STR':0,'INT':2,'AGI':1,'WIS':0,'LUK':1, 'HP':'10 + 2/level', 'MP':'7 + 1/level'},
}
class_spells = {
    'Thistle Knight': ['Shield Spark (0 MP): mark the safest square.', 'Shield of Thistles (1 MP): hold back wind, rain, or branches.'],
    'Loch Scout': ['Mist Mark (0 MP): leave friend-only glowing footprints.', 'Mist Step (1 MP): slip past a watcher or trap.'],
    'Song-Spark Bard': ['Courage Note (0 MP): steady a friend.', 'Kind Whisper (0 MP): help someone say a feeling.', 'Brave Chorus (1 MP): give two friends +1 on the same scene.'],
    'Hearth Mage': ['Glow-Pebble (0 MP): candle-sized light.', 'Tea-Steam (0 MP): warm or reveal breeze.', 'Foxfire Path (1 MP): find the gentlest route.'],
    'Beast Friend': ['Gentle Scent (0 MP): smell like oats, apples, or safe grass.', 'Kind Whisper (0 MP): calm a creature.', 'Foxfire Path (1 MP): find a nature route.'],
    'Puzzle Tinker': ['Button-Click (0 MP): wiggle one latch, knot, or toy mechanism.', 'Tiny Mend (1 MP): repair one small object.', 'Rune Read (1 MP): ask one question about old writing.'],
}
def job_stat_block(title):
    st=class_stats[title]
    stats=''.join(f"<div class='stat'><strong>{k}</strong>{v:+d}</div>" for k,v in st.items() if isinstance(v,int))
    vit=f"<div class='vitals'><div class='vital'><strong>HP</strong>{st['HP']}</div><div class='vital'><strong>MP</strong>{st['MP']}</div><div class='vital'><strong>ARM</strong>0</div><div class='vital'><strong>LVL</strong>1</div></div>"
    return vit + "<div class='statline'>" + stats + "</div><p class='stat-note'>Class stat block shows a strong default build. Adventurers may still choose their own +2, +1, +1, +0, +0 spread.</p>"
for j in jobs:
    ph.feature_page('Adventure job', j['title'], j['image'], j['intro'], feature_grid([
        ('Gift', p(j['gift'])),
        ('Class stat block', job_stat_block(j['title'])),
        ('Class cantrip', p(j['cantrip'])),
        ('Class spells', ul(class_spells[j['title']])),
        ('Try this', ul(j['tryit'])),
        ('Starter kit', ul(j['kit'])),
    ]), more=mini('Training', j['training']) + f"<div class='feature-quote'>{j['prompt']}</div>")
ph.text_page("Skills and checks", f"""
{split(
'''<h3>What is a skill?</h3><p>A skill is a thing an adventurer knows how to try. Skills do not add extra numbers. They tell the table which stat makes sense and what tools might help.</p><table><tr><th>Skill</th><th>Usual stat</th><th>Example</th></tr><tr><td>Climb / Hold</td><td>Strength</td><td>Hold a rope while friends cross.</td></tr><tr><td>Riddle / Rune</td><td>Int</td><td>Read fairy marks on a gate.</td></tr><tr><td>Sneak / Dodge</td><td>Agility</td><td>Step around creaky roots.</td></tr><tr><td>Notice / Soothe</td><td>Wis</td><td>Calm a frightened creature.</td></tr><tr><td>Charm / Chance</td><td>Luck</td><td>Trust a lucky button at the last second.</td></tr></table>''',
'''<h3>How checks work</h3>''' + ul(['Say what the adventurer tries.', 'Pick the stat that matches the method, not the problem name.', 'Add +1 if gear or a friend clearly helps.', 'Roll d6 + stat bonus only if the answer is exciting.', 'On a wobble, move the scene forward with a cost, noise, mess, or choice.']) + rb('<strong>Trap example:</strong> A twig-bell trap can be Agility to step over it, Int to disarm it, Wis to notice it, Strength to hold a branch aside, or Luck to bump it in a harmless way.')
)}
""", columns=False)
ph.text_page("Combat and danger", f"""
{split(
'''<h3>Combat is a tense scene</h3><p>Combat in Adventures in Alba is not about hurting enemies. It is about protecting friends, dodging trouble, tiring a creature out, breaking a spell, or helping something stop being scary.</p><ol><li>The Guide describes danger and feeling.</li><li>Each adventurer says one action.</li><li>Roll only for exciting actions.</li><li>Reduce HP when someone is bumped, tired, scared, tangled, or splashed.</li><li>At 0 HP, a hero needs help; a creature stops fighting and can be soothed, tricked, or understood.</li></ol>''',
'''<h3>Combat actions</h3><table><tr><th>Action</th><th>Stat</th><th>On success</th></tr><tr><td>Protect a friend</td><td>Strength</td><td>Friend avoids 2 HP of trouble.</td></tr><tr><td>Dodge claws, roots, or falling stones</td><td>Agility</td><td>You avoid harm and move somewhere useful.</td></tr><tr><td>Spot the weak point in a spell</td><td>Int</td><td>Next hero gets +1.</td></tr><tr><td>Calm or distract</td><td>Wis</td><td>Creature loses 1 MP or changes feeling.</td></tr><tr><td>Use a charm</td><td>Luck</td><td>Turn a bad moment into a funny cost.</td></tr></table>''' + rb('<strong>Damage guide:</strong> small bump 1 HP, scary hit or trap 2 HP, boss special 3 HP. Keep descriptions safe: muddy, tangled, dizzy, startled, sleepy.')
)}
""", columns=False)
ph.art_text_page("Traps, obstacles, and gear", f"""
{split(
'''<h3>Traps are puzzles with a warning</h3><p>Use traps as playful obstacles: bell strings, sleepy roots, sticky jam doors, rune locks, puddle mirrors, or a bridge that sneezes. Always give a clue before a trap matters.</p><table><tr><th>Trap</th><th>Notice</th><th>Checks</th></tr><tr><td>Twig-bell alarm</td><td>Tiny bells in moss</td><td>Wis notice, Agility step, Int untie.</td></tr><tr><td>Sleepy root snare</td><td>Roots yawn quietly</td><td>Agility hop, Strength pull, Wis sing awake.</td></tr><tr><td>Moon-rune lock</td><td>Cold silver letters</td><td>Int read, Luck button, MP Rune Read.</td></tr></table>''',
'''<h3>Equipment matters</h3><table><tr><th>Gear</th><th>Helps with</th><th>Table effect</th></tr><tr><td>Rope</td><td>Climb, rescue, measure.</td><td>+1 when it clearly helps.</td></tr><tr><td>Lantern</td><td>Dark, mist, caves.</td><td>Reveals one clue before a roll.</td></tr><tr><td>Chalk</td><td>Maps and marks.</td><td>Prevents getting lost once.</td></tr><tr><td>Tiny toolkit</td><td>Locks and repairs.</td><td>Allows Int checks on devices.</td></tr><tr><td>Oat pouch</td><td>Animal trust.</td><td>+1 Wis with hungry creatures.</td></tr></table>''' + qa('<strong>Gear question:</strong> “What do you pull from your pack, and how does it help the adventurer?”')
)}
""", image="item-gear-sheet.png", side="right", columns=False)
ph.text_page("Example scenario: adventurer view", f"""
{split(
'''<h3>The Bell-Root Path</h3><p><strong>You see:</strong> a path of soft moss, tiny silver bells tied to roots, and a sleeping fox curled beside a moon-rune door.</p><p><strong>You feel:</strong> the place is quiet, like it is holding its breath.</p><h3>Your choices</h3>''' + ul(['Step carefully between the bells: Agility.', 'Study how the bells are tied: Int.', 'Whisper to the fox and ask what it knows: Wis.', 'Hold the branch up for a friend: Strength.', 'Tap your lucky button and choose the quietest root: Luck.']),
'''<h3>If things go wrong</h3>''' + ul(['Wobble: one bell rings and the fox opens one eye.', 'Yes, but: you pass, but your cloak snags a root.', 'Bright success: you reach the moon-rune door and find a silver acorn key.']) + rb('<strong>Adventurer tip:</strong> describe the idea first. The stat comes after everyone understands what your hero is doing.')
)}
""", columns=False)
ph.text_page("Example scenario: adventurer combat", f"""
{split(
'''<h3>The Bramble Sneak jumps out</h3><p>A red-capped bramble creature shakes thorns and hisses, “No one takes my shiny bell!” It looks more scared than mean.</p><h3>Adventurer turns</h3>''' + ul(['Knight: protect a friend with Strength.', 'Scout: dodge through roots with Agility.', 'Bard: sing a silly rhyme with Wis.', 'Mage: spend 1 MP on Glow-Pebble to show the bell is not stolen.', 'Tinker: use Int to spot the bramble knot holding its cap too tight.']),
'''<h3>How it ends</h3><p>When the Bramble Sneak reaches 0 HP, it is not defeated forever. It is tangled, tired, and ready to listen. If the adventurers offer the bell back or promise a new shiny button, it becomes a grumpy guide.</p>''' + qa('<strong>Reward:</strong> the Bramble Sneak shows a shortcut under the thorn arch and gives one copper it thought was a magic moon.')
)}
""", columns=False)
ph.text_page("Spells, gear, and treasure", f"""
{split(
spot('02-part-opener.png', '<strong>Rule:</strong> magic helps the story; it does not solve every problem alone.') + '''<h3>Safe little spells</h3>''' + ul(['<strong>Glow-pebble:</strong> make a small light.', '<strong>Tea-steam:</strong> warm cold hands or reveal a breeze.', '<strong>Thistle-tickle:</strong> distract a grumpy creature for a moment.', '<strong>Kind whisper:</strong> help someone say what they feel.', '<strong>Button-bridge:</strong> make a tiny bridge for one small creature.', '<strong>Heather-hush:</strong> quiet a noisy room for one careful question.']) + mini('Spell limit', 'A spell can help one small problem. Big problems still need friends, ideas, and choices.'),
'''<h3>Starting gear</h3>''' + ul(['A snack wrapped in cloth.', 'One useful tool.', 'One pretty charm.', 'One thing your hero drew themselves.', 'A spare ribbon, button, bell, shell, or smooth stone.', 'A tiny notebook for clues or doodles.']) + '''<h3>Useful tools</h3><table><tr><th>Tool</th><th>Use</th></tr><tr><td>Lantern</td><td>See misty paths.</td></tr><tr><td>String</td><td>Tie, measure, or rescue.</td></tr><tr><td>Chalk</td><td>Mark a safe way back.</td></tr><tr><td>Wooden cup</td><td>Offer water, tea, or kindness.</td></tr></table><h3>Treasure prompts</h3><table><tr><th>Find</th><th>Story use</th></tr><tr><td>Silver button</td><td>Opens a promise gate.</td></tr><tr><td>Ribbon</td><td>Marks a safe path.</td></tr><tr><td>Bell</td><td>Calls one fairy friend.</td></tr></table>''' + rb('<strong>Treasure is story-first:</strong> a shiny button can matter more than a bag of coins if it unlocks a promise.')
)}
""", columns=False)
ph.text_page("Spell list", f"""
<div class='spell-list'>
<h3>Cantrips: always small, always safe</h3>
<table><tr><th>Spell</th><th>Roll</th><th>Cost</th><th>What it does</th></tr>
<tr><td>Glow-Pebble</td><td>Luck</td><td>0 MP</td><td>Make a pebble or charm shine like a candle.</td></tr>
<tr><td>Tea-Steam</td><td>Wis</td><td>0 MP</td><td>Warm cold hands or reveal a hidden breeze.</td></tr>
<tr><td>Button-Bridge</td><td>Int</td><td>0 MP</td><td>Make a tiny bridge for toys, fairies, or clues.</td></tr>
<tr><td>Heather-Hush</td><td>Wis</td><td>0 MP</td><td>Quiet one noisy room long enough for a careful question.</td></tr>
<tr><td>Thistle-Tickle</td><td>Luck</td><td>0 MP</td><td>Distract a grumpy creature for one moment.</td></tr>
<tr><td>Kind Whisper</td><td>Wis</td><td>0 MP</td><td>Help someone say what they feel.</td></tr></table>
<h3>Adventure spells</h3>
<table><tr><th>Spell</th><th>Roll</th><th>Cost</th><th>Use</th></tr>
<tr><td>Mist Step</td><td>Agility</td><td>1 MP</td><td>Slip past a watcher if a friend describes the mist.</td></tr>
<tr><td>Rune Read</td><td>Int</td><td>1 MP</td><td>Ask the Guide one question about old writing.</td></tr>
<tr><td>Lucky Button</td><td>Luck</td><td>1 MP</td><td>Turn one wobble into “yes, but” once per session.</td></tr>
<tr><td>Shield of Thistles</td><td>Strength</td><td>1 MP</td><td>Hold back wind, rain, or falling branches for a turn.</td></tr>
<tr><td>Foxfire Path</td><td>Wis</td><td>1 MP</td><td>Find the gentlest route through a confusing place.</td></tr>
<tr><td>Tiny Mend</td><td>Int</td><td>1 MP</td><td>Repair a small broken object so it can help the story.</td></tr>
</table>
{rb('<strong>Spell rule:</strong> spells solve one small problem. Big problems still need choices, friends, and consequences.')}
</div>
""", columns=False)
ph.art_text_page("Equipment shop", f"""
<div class='shop'>
{rb('<strong>Starter money:</strong> each hero starts with 1 silver (10 copper). Choose a few useful things before the first adventure. Save at least 1 copper for snacks, tolls, or lucky wishes.')}
<table><tr><th>Item</th><th>Cost</th><th>Use</th></tr>
<tr><td>Lantern</td><td>3 copper</td><td>See in mist, caves, and under bridges.</td></tr>
<tr><td>Rope</td><td>3 copper</td><td>Climb, tie, rescue, measure, or make a line.</td></tr>
<tr><td>Chalk</td><td>1 copper</td><td>Mark a safe path or draw a puzzle answer.</td></tr>
<tr><td>Snack bundle</td><td>1 copper</td><td>Share with a friend or hungry creature.</td></tr>
<tr><td>Wooden shield</td><td>4 copper</td><td>Helps Strength rolls to protect or hold steady.</td></tr>
<tr><td>Soft boots</td><td>4 copper</td><td>Helps Agility rolls to sneak or balance.</td></tr>
<tr><td>Tiny toolkit</td><td>5 copper</td><td>Helps Int rolls to mend, open, or build.</td></tr>
<tr><td>Oat pouch</td><td>2 copper</td><td>Helps Wis rolls with animals.</td></tr>
<tr><td>Lucky button</td><td>3 copper</td><td>Helps one Luck roll per adventure.</td></tr>
<tr><td>Warm cloak</td><td>3 copper</td><td>Stay cosy in rain, wind, or moonlit cold.</td></tr>
<tr><td>Bell</td><td>2 copper</td><td>Call a friend, mark a rhythm, or wake a sleepy path.</td></tr>
<tr><td>Blank notebook</td><td>2 copper</td><td>Draw maps, clues, promises, and creature friends.</td></tr>
</table>
<h3>Coin names</h3><table><tr><th>Coin</th><th>Value</th><th>Use</th></tr><tr><td>Copper</td><td>Basic coin</td><td>Snacks, chalk, rope, simple tools.</td></tr><tr><td>Silver</td><td>10 copper</td><td>Starter purse, good tools, inn beds.</td></tr><tr><td>Gold</td><td>10 silver</td><td>Rare rewards, mounts, special training.</td></tr><tr><td>Mythral</td><td>100 gold</td><td>Legendary fairy metal; a story treasure.</td></tr></table><h3>Starter kits</h3><table><tr><th>Kit</th><th>Cost</th><th>Contains</th></tr>
<tr><td>Knight kit</td><td>8 copper</td><td>Wooden shield, rope, snack bundle.</td></tr>
<tr><td>Scout kit</td><td>8 copper</td><td>Lantern, chalk, soft boots.</td></tr>
<tr><td>Mage kit</td><td>8 copper</td><td>Lucky button, notebook, bell, chalk.</td></tr>
<tr><td>Friend kit</td><td>8 copper</td><td>Oat pouch, warm cloak, snack bundle, bell.</td></tr>
</table>
</div>
""", image="item-gear-sheet.png", side="right", columns=False)
ph.art_text_page("More spell and gear examples", f"""
{split(
'<h3>Class cantrips in play</h3><table><tr><th>Job</th><th>Cantrip scene</th></tr><tr><td>Thistle Knight</td><td>Shield Spark marks the safest place to stand.</td></tr><tr><td>Loch Scout</td><td>Mist Mark leaves friend-only glowing footprints.</td></tr><tr><td>Song-Spark Bard</td><td>Courage Note steadies a worried friend.</td></tr><tr><td>Hearth Mage</td><td>Glow-Pebble lights a cupboard, bridge, or cave.</td></tr><tr><td>Beast Friend</td><td>Gentle Scent makes a hand smell like oats or apples.</td></tr><tr><td>Puzzle Tinker</td><td>Button-Click wiggles one latch or knot.</td></tr></table>',
'<h3>Coin examples</h3><table><tr><th>Reward</th><th>Coins</th><th>Feels like</th></tr><tr><td>Helping a baker</td><td>3 copper</td><td>Snack money.</td></tr><tr><td>Returning a moon-bell</td><td>1 silver</td><td>A real thank-you.</td></tr><tr><td>Saving a village festival</td><td>1 gold</td><td>A rare reward.</td></tr><tr><td>Finding mythral</td><td>1 mythral</td><td>A legendary story treasure.</td></tr></table>' + rb('<strong>Shopping prompt:</strong> ask each player, “What do you buy, and how will it help someone?”')
)}
""", image="bg-spell-gear.png", side="right gear", columns=False)
ph.text_page("Making a hero: quick checklist", f"""
<ol><li>Name your hero.</li><li>Pick a kindred.</li><li>Pick an adventure job.</li><li>Choose stats: one +2, two +1, two +0.</li><li>Pick one gear item and one charm.</li><li>Answer: “Who do I want to help?”</li></ol>
{qa('<strong>Worked example:</strong> Rowan Moonbutton is a Selkie-Born Beast Friend. Stats: Wis +2, Agility +1, Luck +1, Strength +0, Int +0. Gear: oat pouch. Charm: sea-glass button. Rowan wants to help nervous animals.')}
{rb('<strong>Grown-up tip:</strong> do not quiz an Adventurer on rules. Ask what they imagine, then translate that into Strength, Int, Agility, Wis, or Luck.')}
<h3>Common first purchases</h3><table><tr><th>Hero idea</th><th>Good buys</th></tr><tr><td>Protector</td><td>Shield, rope, snack bundle.</td></tr><tr><td>Explorer</td><td>Lantern, chalk, soft boots.</td></tr><tr><td>Mage</td><td>Lucky button, bell, notebook.</td></tr><tr><td>Animal friend</td><td>Oat pouch, warm cloak, snack.</td></tr></table>
<div class='card-grid'>
{card('End of session', p('Ask: “Who did we help?” “What should we draw?” “What promise did we make?”'))}
{card('Track level', p('After a finished adventure, mark one story star. Four story stars usually means the hero gains a level.'))}
{card('If a player is stuck', p('Offer two choices: “Do you want to talk kindly, move quickly, or do the brave thing?”'))}
{card('If the group gets loud', p('Point to the picture, name one sound in the scene, then ask one adventurer what their hero notices.'))}
</div>
""", columns=False)

ph.text_page("More hero options", f"""
{split(
'<h3>Backgrounds</h3><p>Backgrounds give adventurers a first memory, a home tie, and one table reason to ask questions.</p><table><tr><th>Background</th><th>You know</th><th>Starter thing</th></tr><tr><td>Croft Kid</td><td>Animals, weather, chores.</td><td>Oat pouch.</td></tr><tr><td>Castle Page</td><td>Heraldry, manners, maps.</td><td>Ribbon badge.</td></tr><tr><td>Loch Fisher</td><td>Knots, boats, quiet patience.</td><td>Fishing line.</td></tr><tr><td>Market Runner</td><td>Prices, gossip, shortcuts.</td><td>Coin purse.</td></tr><tr><td>Hill Dreamer</td><td>Stars, stories, odd signs.</td><td>Dream pebble.</td></tr></table>',
'<h3>Earned pets</h3><p>Pets are not bought at character creation. They join after an adventure where the party helps, feeds, frees, or understands them.</p><table><tr><th>Pet</th><th>Earn by</th><th>Helps with</th></tr><tr><td>Rowan mouse</td><td>return its stolen crumb-hoard.</td><td>Sneaking and tiny keys.</td></tr><tr><td>Cloud moth</td><td>guide it to safe starlight.</td><td>Finding soft light.</td></tr><tr><td>Thistle hedgehog</td><td>save it from a boot-trap.</td><td>Noticing danger.</td></tr><tr><td>Seal pup</td><td>bring its song back to the loch.</td><td>Water clues.</td></tr></table>' + rb('<strong>Background rule:</strong> once per session, if your background clearly helps, add +1 or ask the Guide for one extra clue. Pets use the companion rules on the next page.')
)}
""", columns=False)

ph.art_text_page("Earned mounts and pets", f"""
{split(
'<h3>Companion rule</h3><p>Mounts and pets are story friends, not shopping items. Earn one by helping it, keeping a promise, or finishing a quest. A companion never replaces a hero; it opens one extra approach.</p>' + ul(['One companion may actively help the party in a scene.', 'If it clearly helps, add +1 or reveal one clue before a roll.', 'If danger targets it, the Guide offers a rescue choice instead of punishment.', 'A companion needs care: food, rest, kindness, and a job it enjoys.']) + rb('<strong>Earned, not bought:</strong> coins can buy tack, feed, or shelter, but trust must be won in play.'),
'<h3>Companions to earn</h3><table><tr><th>Companion</th><th>Earn by</th><th>Helps with</th></tr><tr><td>Highland pony</td><td>free it from a bog rope.</td><td>travel, carrying, courage.</td></tr><tr><td>Cairn goat</td><td>find its lost bell on a cliff.</td><td>climbing paths.</td></tr><tr><td>Fairy stag</td><td>protect its grove from tax-magic.</td><td>fast travel once per adventure.</td></tr><tr><td>Kelp-mane pony</td><td>return a moon-water charm.</td><td>safe loch crossings.</td></tr><tr><td>Rowan owl</td><td>solve an old-name riddle.</td><td>warnings and night clues.</td></tr><tr><td>Border warg</td><td>break the command collar.</td><td>tracking and brave defense.</td></tr></table>'
)}
<h3>Companion bond track</h3><table><tr><th>Bond</th><th>What it means</th><th>Unlock</th></tr><tr><td>1</td><td>Trusts the party.</td><td>+1 once per session.</td></tr><tr><td>2</td><td>Comes when called.</td><td>Can carry a message or small item.</td></tr><tr><td>3</td><td>Chooses the heroes.</td><td>May return dramatically once per campaign.</td></tr></table>
""", image="bg-mounts-pets.png", side="left", columns=False)
ph.text_page("Player choices: more jobs and backgrounds", f"""
<div class='quick-grid'>
{card('New jobs', ul(['Cairn-Warden: protect oaths and stones.', 'Storm-Singer: weather songs and brave speeches.', 'Rune Tinker: locks, maps, clever gadgets.', 'Goat Knight: mountain travel and comic bravery.', 'Loch Herbalist: potions, cures, water lore.', 'Crow Messenger: secrets, scouting, omens.']))}
{card('Backgrounds', ul(['Raised by bridge-keepers.', 'Found in a fairy ring.', 'Apprentice to a kettle witch.', 'Kin to a storm-clan poet.', 'Grew up on a longship market.', 'Escaped a Red Banner border fort.']))}
{card('Starting gift ideas', ul(['Ask one bridge/road question.', 'Know one old hill name.', 'Carry one tiny healing tea.', 'Understand one animal mood.', 'Find one hidden door in mist.', 'Turn a wobble into funny mud once.']))}
{card('Pet/mount hooks', ul(['Find a lost cairn bell.', 'Break a warg collar.', 'Protect a fairy stag grove.', 'Guide a cloud moth home.', 'Share oats with a Highland pony.', 'Solve a rowan owl riddle.']))}
</div>
""", columns=False)
ph.text_page("Progression beyond level 1", f"""
{split('<h3>Level rewards</h3><table><tr><th>Level</th><th>Reward</th></tr><tr><td>2</td><td>+2 HP or +2 MP; learn one spell/card.</td></tr><tr><td>3</td><td>Choose a feat/gift.</td></tr><tr><td>4</td><td>Upgrade one companion bond or home base.</td></tr><tr><td>5</td><td>Earn a named mythral story relic.</td></tr></table>' + rb('<strong>Feat examples:</strong> Brave Helper, Quick Feet, Old Name Knower, Gentle Beast Voice, Red Wax Breaker, Storm-Song.'), '<h3>Campaign tracks</h3><table><tr><th>Track</th><th>How it grows</th></tr><tr><td>Companion bond</td><td>care, rescue, trust scenes.</td></tr><tr><td>Faction reputation</td><td>help clans/courts/towns.</td></tr><tr><td>Home base</td><td>add stable, library, kitchen, map room.</td></tr><tr><td>Spell upgrade</td><td>name, promise, ingredient.</td></tr></table>')}
""", columns=False)
ph.text_page("More magic: schools and rituals", f"""
{split(
'<h3>Four gentle spell schools</h3><p>Schools are story flavors, not homework. Use them to describe how magic looks, sounds, and asks for promises.</p><table><tr><th>School</th><th>Feels like</th><th>Examples</th></tr><tr><td>Hearth</td><td>warmth, light, mending</td><td>Glow-Pebble, Tiny Mend</td></tr><tr><td>Loch</td><td>mist, water, memory</td><td>Mist Step, Moon Reflection</td></tr><tr><td>Thistle</td><td>protection, brambles, courage</td><td>Shield of Thistles, Prickle Path</td></tr><tr><td>Story</td><td>songs, names, promises</td><td>Courage Note, Name Echo</td></tr></table>',
'<h3>Rituals</h3><p>A ritual is a slow spell that takes a scene, a promise, and three ingredients. It usually costs 2 MP from the group instead of one hero.</p>' + ul(['Name what you want: light, bridge, truth, calm, memory.', 'Offer three ingredients: coin, feather, song, button, water, ash, berry.', 'Every adventurer says one helpful line.', 'Roll Wis, Int, or Luck if the answer is exciting.']) + qa('<strong>Ritual mishap:</strong> on a wobble, the ritual works but leaves a funny sign: purple hair, hiccuping bells, sleepy shoes, or talking moss.')
)}
""", columns=False)
ph.text_page("Spell upgrades", f"""
<table><tr><th>Level</th><th>Upgrade choice</th><th>Example</th></tr><tr><td>2</td><td>Longer light</td><td>Glow-Pebble lasts a whole scene.</td></tr><tr><td>3</td><td>Friend boost</td><td>A cantrip can help a nearby friend.</td></tr><tr><td>4</td><td>Feat spell trick</td><td>Choose one spell feat when you gain a feat.</td></tr><tr><td>5</td><td>Big ritual</td><td>Group rituals can affect a bridge, grove, or cottage.</td></tr></table>
<div class='card-grid'>
{card('Spell feat: Careful Magic', p('Once per session, when you spend MP, ignore the first harmless magical mess.'))}
{card('Spell feat: Shared Spark', p('Spend 1 extra MP so a friend also gets +1.'))}
{card('Spell feat: Bright Cantrip', p('Pick one cantrip. It can affect two tiny things instead of one.'))}
{card('Spell feat: Old Words', p('You may ask the Guide what one rune, rhyme, or fairy name means.'))}
{card('Spell feat: Potion Nose', p('You can identify a potion, poison, or enchantment ingredient by smell once per session.'))}
{card('Spell feat: Rune Stitcher', p('You may repair one damaged charm during a safe camp.'))}
</div>
""", columns=False)
ph.text_page("Advanced combat options", f"""
{split(
'<h3>Armor and shields</h3><table><tr><th>Gear</th><th>Cost</th><th>Rule</th></tr><tr><td>Padded cloak</td><td>4 silver</td><td>Once per scene, reduce 1 HP of trouble.</td></tr><tr><td>Wooden shield</td><td>6 silver</td><td>Protect a friend at +1 if you can reach them.</td></tr><tr><td>Thistle charm</td><td>1 gold</td><td>Reduce one bramble/spell trouble by 1 HP.</td></tr></table>',
'<h3>Conditions</h3><table><tr><th>Condition</th><th>Means</th><th>Ends when</th></tr><tr><td>Tangled</td><td>You need help to move far.</td><td>Strength, Agility, or a friend helps.</td></tr><tr><td>Startled</td><td>Next roll is -1 unless soothed.</td><td>Friend says something kind.</td></tr><tr><td>Sleepy</td><td>You can act, but slowly.</td><td>Snack, song, or fresh air.</td></tr><tr><td>Glittered</td><td>Easy to spot.</td><td>Wash, cloak, or scene ends.</td></tr><tr><td>Poisoned</td><td>A venom causes a temporary condition.</td><td>Use the listed cure.</td></tr><tr><td>Cursed</td><td>A spell changes the scene rules.</td><td>Break the rune, oath, or item.</td></tr></table>' + rb('<strong>Boss phases:</strong> at half HP, a boss changes the scene: fog rolls in, bridge wakes, or the creature admits what it truly wants.') + '<h3>Battle complications</h3>' + ul(['Falling stones split the party into two zones.', 'A banner gives enemies +1 until cut down.', 'A poison cloud makes everyone seek clean water.', 'A frightened monster grabs a map instead of a hero.'])
)}
""", columns=False)

ph.art_page("nonhuman-kindreds.png", "Stranger Kindreds of Alba", "Not every adventurer is human-shaped. Alba welcomes stone-born, moss-horned, raven-winged, star-lit, and mushroom-root heroes.")
ph.text_page("Enchantments and magic items", f"""
{split(
'<h3>Enchanting rule</h3>' + ul(['Choose a plain item: blade, cloak, ring, harp, lantern, boots, spoon, shield.', 'Choose one enchantment word: Bright, Thorn, Loch, Cairn, Storm, Rowan, Moon, Ember.', 'Pay the ingredient cost and make a promise about how the item will be used.', 'Enchanted items add +1 only when the story clearly matches their word.']) + rb('<strong>Limit:</strong> carry one active enchanted item per level. Mythral items count as two.'),
'<h3>Enchantment spells</h3><table><tr><th>Spell</th><th>Cost</th><th>Effect</th></tr><tr><td>Wake Charm</td><td>1 MP</td><td>Ask a sleeping magic item what it wants.</td></tr><tr><td>Bind Brightness</td><td>2 MP + silver dust</td><td>Store one cantrip inside an item until next dawn.</td></tr><tr><td>Rune-Lock</td><td>2 MP</td><td>Seal a door, chest, or promise until the right word is spoken.</td></tr><tr><td>Unweave Curse</td><td>3 MP group ritual</td><td>Turn a harmful enchantment into a clue, mark, or choice.</td></tr></table>'
)}
""", columns=False)
ph.art_text_page("Magic item examples", f"""
<div class='card-grid'>
{card('Cairn-Knuckle Ring', p('+1 Strength when holding, bracing, or remembering an oath. If used selfishly, it grows heavy.'))}
{card('Rowan-Bark Shield', p('Once per scene, reduce 2 HP of trouble from thorns, arrows, or frightened beasts.'))}
{card('Loch-Mirror Cloak', p('+1 Agility in mist or moonlight; on a wobble, your reflection gives advice too late.'))}
{card('Star-Moth Lantern', p('Reveals hidden ink, invisible tracks, and fairy doors; moths follow it everywhere.'))}
{card('Storm-Harp String', p('A bard can spend 1 MP to turn thunder, shouting, or battle-noise into a steady rhythm.'))}
{card('Mythral Seed Blade', p('A legendary story weapon. It cuts curses and brambles, not helpless foes. Worth 100 gold or one impossible promise.'))}
</div>
""", image="item-magic-sheet.png", side="right", columns=False)
ph.art_text_page("Potions and poisons", f"""
{split(
'<h3>Potions</h3><table><tr><th>Potion</th><th>Cost</th><th>Effect</th></tr><tr><td>Heatherheart Draught</td><td>2 silver</td><td>Regain 3 HP and ignore Startled once.</td></tr><tr><td>Loch-Breath Sip</td><td>3 silver</td><td>Breathe under calm water for one scene.</td></tr><tr><td>Giant-Step Tonic</td><td>1 gold</td><td>+1 Strength for lifting, pushing, or carrying in one scene.</td></tr><tr><td>Foxwit Tea</td><td>1 gold</td><td>+1 Int for riddles, traps, or runes in one scene.</td></tr></table>',
'<h3>Poisons and venoms</h3><p>Poisons in this game are scary obstacles, not lethal gore. They make adventurers sleepy, confused, glittered, or slowed until treated.</p><table><tr><th>Poison</th><th>Source</th><th>Effect / cure</th></tr><tr><td>Nightshade Jam</td><td>Redcap trick</td><td>Sleepy for one scene; cured by bitter tea.</td></tr><tr><td>Black Bog Venom</td><td>Bog drake bite or thorn</td><td>-1 Agility until washed with clean running water.</td></tr><tr><td>Iron Crow Ink</td><td>Cursed feather</td><td>Cannot speak a lie; cured by confessing one useful truth.</td></tr><tr><td>Frost-Thistle Prickle</td><td>Winter barb</td><td>Startled; cured by warm cloak and a brave song.</td></tr></table>'
)}
""", image="item-potions-poisons-sheet.png", side="right", columns=False)
ph.write()

# Guide book
gm = Book("guide-book", "Guide Book", "How to run warm high-fantasy adventures for Adventurers 5–7, with examples and dialogue", "02-part-opener.png")
gm.cover_page()
gm.text_page("Your job as Guide", f"""
<p class='drop'>The Guide is not the boss of fun. You describe the world, listen to adventurers, ask what they try, and help the dice turn ideas into surprises.</p>
{split(
ul(['Use short scenes: 5 to 12 minutes each.', 'Give choices in twos or threes, not long menus.', 'Name feelings before fights: scared, proud, sleepy, lonely, worried.', 'Let adventurers succeed often. The fun is in how it happens.']) + spot('03-race-kindreds.png', '<strong>Guide stance:</strong> make every scene readable from the art, then support the adventurer’s idea.'),
rb('<strong>Safety tone:</strong> no gore, no cruelty, no permanent harm. Trouble can be spooky, muddy, noisy, or puzzling.') + '''<h3>Useful phrases</h3>''' + ul(['“Yes, and what does that look like?”', '“Who are you helping?”', '“Which stat fits your idea?”', '“That is a wobble, so something funny changes.”']) + mini('Guide rhythm', 'Picture → feeling → choice → roll only if exciting → warm change.')
)}
""", columns=False)
gm.text_page("Scene recipe", f"""
{card('1. A picture', p('Start with something adventurers can see: misty bridge, silver fox, giant teacup, glowing thistle.'))}
{card('2. A feeling', p('Pick one: worried, excited, lonely, sleepy, proud, grumpy, curious.'))}
{card('3. A choice', p('Offer two helpful directions: follow the bells or talk to the fox.'))}
{card('4. A roll', p('Only roll if the answer is exciting. Use Strength, Int, Agility, Wis, or Luck.'))}
{card('5. A change', p('After each scene, something should be different: a clue, friend, promise, opened path, or new question.'))}
{qa('<strong>Read aloud:</strong> “The moon is caught in the loch like a silver coin. The kelpie foal stamps, worried and wet. What do you do?”')}
""", columns=False)
gm.art_page("05-bestiary-catalog.png", "Creatures are characters", "A creature should usually want something before it blocks something. Adventurers can help, trick, soothe, race, sing, or befriend it.")
gm.text_page("Running rolls and wobbles", f"""
<h3>Choosing the stat</h3>{ul(['Use <strong>Strength</strong> for lifting, climbing, holding, pushing, or protecting.', 'Use <strong>Int</strong> for puzzles, plans, facts, reading runes, or clever tricks.', 'Use <strong>Agility</strong> for speed, balance, dodging, sneaking, or catching.', 'Use <strong>Wis</strong> for feelings, nature, animals, and noticing what matters.', 'Use <strong>Luck</strong> for charms, surprises, fairy bargains, and last chances.'])}
<h3>Good wobbles</h3>{ul(['A hat blows away.', 'The map gets wet.', 'A bell rings and wakes someone.', 'A helpful creature misunderstands.', 'A path opens, but it is muddy.'])}
{rb('<strong>Never make a wobble mean “you did nothing.”</strong> Always move the story.')}
""")
gm.text_page("Building adventures", f"""
<table><tr><th>Part</th><th>Question</th><th>Example</th></tr><tr><td>Hook</td><td>Who needs help?</td><td>A fairy cannot find the right door.</td></tr><tr><td>Path</td><td>Where must heroes go?</td><td>Across the heather bridge.</td></tr><tr><td>Friend</td><td>Who can help?</td><td>A shy fox with silver whiskers.</td></tr><tr><td>Puzzle</td><td>What needs a clever choice?</td><td>Three bells ring, but only one is kind.</td></tr><tr><td>Ending</td><td>How is the glen warmer now?</td><td>The lost moon-bell is returned.</td></tr></table>
{qa('<strong>Guide promise:</strong> prepare situations, not answers. If an adventurer invents a kind solution, let it matter.')}
""", columns=False)
gm.art_text_page("Tiny tables", f"""
<div class='tiny-row'><div class='tiny-heading'><h3>What is strange here?</h3><p>Use this when a scene needs one vivid magical detail.</p></div><table><tr><td>1</td><td>A thistle glows like a lantern.</td></tr><tr><td>2</td><td>Footprints turn into tiny flowers.</td></tr><tr><td>3</td><td>A crow speaks only in compliments.</td></tr><tr><td>4</td><td>The bridge asks for a joke.</td></tr><tr><td>5</td><td>A teacup storm rains indoors.</td></tr><tr><td>6</td><td>A sleeping troll snores bubbles.</td></tr></table></div>
<div class='tiny-row alt'><div class='tiny-heading'><h3>What does the creature want?</h3><p>Give every encounter a want before it becomes a fight.</p></div><table><tr><td>1</td><td>A snack.</td></tr><tr><td>2</td><td>A song.</td></tr><tr><td>3</td><td>Someone to listen.</td></tr><tr><td>4</td><td>A lost button.</td></tr><tr><td>5</td><td>Help being brave.</td></tr><tr><td>6</td><td>A promise kept.</td></tr></table></div>
<div class='tiny-row'><div class='tiny-heading'><h3>How can it enter a scene?</h3><p>Drop the creature into the map with one action.</p></div><table><tr><td>1</td><td>It blocks a path by accident.</td></tr><tr><td>2</td><td>It is crying quietly.</td></tr><tr><td>3</td><td>It has the clue but misunderstands it.</td></tr><tr><td>4</td><td>It challenges the heroes to a silly contest.</td></tr><tr><td>5</td><td>It asks for a promise.</td></tr><tr><td>6</td><td>It follows the heroes home.</td></tr></table></div>
""", image="bg-tiny-tables.png", side="full", columns=False, extra_cls="tiny-page")
gm.text_page("Scene dressing examples", f"""
{split(
'<h3>What to put in a scene</h3>' + ul(['<strong>One clear picture:</strong> a bridge with mossy faces, a teacup storm, a silver fox in heather.', '<strong>One sound:</strong> bell, splash, snore, giggle, creak, whisper.', '<strong>One feeling:</strong> lonely, proud, worried, sleepy, curious, embarrassed.', '<strong>One useful object:</strong> rope, button, lantern, map, boot, key, ribbon.', '<strong>One choice:</strong> talk first or look closer; cross now or find a safer path.']) + rb('<strong>Example setup:</strong> “Rain taps the old bridge. A carved face blinks under moss. A red ribbon is tied around the middle stone.”'),
'<h3>Dialogue starters</h3>' + ul(['Bridge: “I will not open for stomping feet. I open for polite ones.”', 'Sprite: “I am not lost. I am doing royal path inspection.”', 'Brownie: “Hold still! Those boots have clues on them!”', 'Fox: “A clever adventurer would notice the quiet puddle, and you look very clever.”', 'Owl: “Young acorn, I remember the path. I forgot the name of remembering.”']) + qa('<strong>Ask the players:</strong> “What do you say back?” “Who helps?” “Which stat fits your idea?”')
)}
""", columns=False)
gm.text_page("Running dialogue with Adventurers", f"""
<div class='card-grid'>
{card('Offer two tones', p('“Do you ask gently, make a joke, or stand tall?” Adventurers often answer faster when the choices are emotional.'))}
{card('Repeat their idea proudly', p('Adventurer: “I give it a biscuit.” Guide: “Excellent. You offer the dragon a biscuit like a peace treaty.”'))}
{card('Make NPCs want something', p('Every speaker wants a snack, a promise, a name remembered, a path cleaned, a song, or help being brave.'))}
{card('Let wobbles talk', p('On a wobble, the creature misunderstands: “You said boot? I thought you said flute!” Then the scene keeps moving.'))}
</div>
{qa('<strong>Mini example:</strong> Guide: “The kelpie foal stamps, but its ears droop.” Player: “I talk quietly.” Guide: “That sounds like Wis. What do you say?” Player: “It is okay.” Guide: “Roll, and your friend may add +1 if they hum softly.”')}
""", columns=False)
gm.text_page("Using HP, MP, and enemy DR", f"""
<table><tr><th>Number</th><th>Guide meaning</th><th>Example</th></tr><tr><td>HP</td><td>How long a creature can stay in a tense scene.</td><td>A troll with high HP can keep holding a log bridge while heroes help.</td></tr><tr><td>MP</td><td>How much fairy weirdness it can use.</td><td>A sprite spends MP to grow thistles or vanish in petals.</td></tr><tr><td>Level</td><td>How experienced or important it is.</td><td>A level 1 hare is a messenger; a level 4 hare might guard a moon gate.</td></tr><tr><td>DR</td><td>Difficulty Rating: a quick “how big is this encounter?” number.</td><td>DR 1–2 easy, DR 3–4 fair, DR 5+ big scene or boss.</td></tr></table>
{rb('<strong>DR formula:</strong> round((HP + MP + Level×3 + positive stat bonuses×2) ÷ 10). Use it to pace scenes, not to punish players.')}
{qa('<strong>Example:</strong> Bog-Boot Brownie has HP 8, MP 3, Level 2, positive stats total 5. DR = round((8+3+6+10)/10) = 3.')}
""", columns=False)
gm.text_page("Ready scene examples", f"""
{split(
'<h3>Scene: The Bootprint Road</h3><p><strong>Read aloud:</strong> “Golden bootprints glow in the mud. They walk in circles around a huge soggy boot. A muddy brownie waves a brush like a sword.”</p>' + ul(['Ask: “Do you let it clean your boots, ask about the prints, or follow them?”', 'Roll Wis to understand the brownie, Int to read the pattern, Agility to hop print to print.', 'Wobble: the brownie cleans the map instead of the boots.']),
'<h3>Scene: The Star Sheep</h3><p><strong>Read aloud:</strong> “A sheep made of cloud wool floats just above the hill. It bleats at a lonely star hiding behind a cloud.”</p>' + ul(['Ask: “Do you sing, climb, shine a light, or ask what it lost?”', 'Roll Luck for star magic, Wis for feelings, Strength to hold the kite-rope.', 'Reward: the sheep makes a cloud bridge for one careful crossing.'])
)}
""", columns=False)
gm.text_page("Scenario from the Guide side: Bell-Root Path", f"""
{split(
'<h3>What the adventurers see</h3><p><strong>Read aloud:</strong> The path is moss-soft. Tiny bells hang from sleepy roots. A fox dreams beside a moon-rune door.</p><h3>What is really happening?</h3>' + ul(['The bells are an alarm, but also a puzzle.', 'The fox is guarding the door because it lost the key.', 'The silver acorn key is under the quietest root.']),
'<h3>Checks to offer</h3><table><tr><th>Idea</th><th>Stat</th><th>Result</th></tr><tr><td>Step around bells</td><td>Agility</td><td>Reach the door quietly.</td></tr><tr><td>Untie bells</td><td>Int</td><td>Learn which root hides the key.</td></tr><tr><td>Talk to fox</td><td>Wis</td><td>Fox admits it is worried.</td></tr><tr><td>Hold branch</td><td>Strength</td><td>Friend gets +1.</td></tr><tr><td>Lucky button</td><td>Luck</td><td>Find the quietest root.</td></tr></table>' + rb('<strong>Wobble:</strong> a bell rings, but it wakes the fox instead of starting a fight. Now dialogue begins.')
)}
""", columns=False)
gm.text_page("Scenario from the Guide side: Bramble combat", f"""
{split(
'<h3>Scene purpose</h3><p>This is a combat scene that teaches danger without cruelty. The Bramble Sneak wants its shiny bell back and uses thorns to look bigger than it feels.</p><h3>Creature plan</h3>' + ul(['Round 1: block the path and shout.', 'Round 2: use Thorn Tangle if adventurers rush.', 'At half HP: admit the bell is important.', 'At 0 HP: tangled, tired, and ready to bargain.']),
'<h3>Guide moves</h3><table><tr><th>Move</th><th>Use when</th><th>Safe result</th></tr><tr><td>Thorn Tangle</td><td>A hero runs straight in.</td><td>2 HP and stuck cloak.</td></tr><tr><td>Shiny Distraction</td><td>Someone shows treasure.</td><td>It pauses; next hero gets +1.</td></tr><tr><td>Cap Snag</td><td>On a wobble.</td><td>Its cap catches and reveals fear.</td></tr></table>' + qa('<strong>End warm:</strong> if adventurers return the bell, trade a button, or promise help, the Bramble Sneak becomes a grumpy shortcut guide.')
)}
""", columns=False)
gm.text_page("More ready dialogue", f"""
<div class='card-grid'>
{card('Gate with a voice', p('Read aloud: “The gate yawns. Password? it asks. Or snack-word. I accept both.” Use Int for clues, Luck for guessing, Wis for asking what it wants.'))}
{card('Proud tiny ruler', p('Sprite: “I decree that all heroes must admire my crown.” Good replies include compliments, jokes, drawing a flag, or asking if the sprite is lonely.'))}
{card('Helpful shopkeeper', p('Shopkeeper: “Copper buys rope, silver buys a kit, gold buys a favour, and mythral buys a legend. Spend kindly.”'))}
{card('Creature at 0 HP', p('Do not narrate harm. Say: “The creature is tired, muddy, and ready to listen.” Then offer help, promise, snack, or rest.'))}
</div>
{qa('<strong>Scene loop example:</strong> picture → feeling → choice → roll → wobble or success → new clue. Keep naming the next useful thing adventurers can touch, ask, follow, or comfort.')}
""", columns=False)

gm.text_page("Guide depth: boss scenes and safety", f"""
{split(
'<h3>Boss scene shape</h3>' + ul(['Show the scary picture safely: shadow, noise, weather, big feelings.', 'Give the creature a want that can be discovered.', 'Use HP to pace attention; use MP for special moves.', 'At half HP, reveal the softer truth.', 'At 0 HP, offer a bargain, apology, nap, or rescue.']),
'<h3>Safety dials</h3><table><tr><th>If players are nervous</th><th>If players want more</th></tr><tr><td>Lower HP by 3.</td><td>Add a second objective.</td></tr><tr><td>Make special attacks cost +1 MP.</td><td>Let the creature change the map.</td></tr><tr><td>Have an NPC friend offer a hint.</td><td>Add a countdown: three bells before fog.</td></tr></table>' + rb('<strong>Rule:</strong> scary is allowed; hopeless is not. Always leave a visible kind choice.')
)}
""", columns=False)
gm.write()

# Bestiary
be = Book("bestiary", "Bestiary", "Friendly creatures, gentle problems, HP, MP, difficulty ratings, and encounter ideas", "05-bestiary-catalog.png")
be.cover_page()
be.text_page("How to use creature stat blocks", f"""
<p class='drop'>Creatures in Adventures in Alba are more than numbers, but the numbers help the Guide pace scenes. Every creature has HP, MP, Level, a Difficulty Rating, classic stats, and plenty of story hooks.</p>
{spot('05-bestiary-catalog.png', '<strong>Creature rule:</strong> every creature has a feeling, a wish, useful stats, and a safe complication.')}
{rb('<strong>Creature rolls:</strong> when a creature acts against a hero, roll d6 + the creature stat. Use results to create funny trouble, not punishment.')}
<table><tr><th>Stat</th><th>Creature use</th></tr><tr><td>Strength</td><td>Push, hold, carry, stomp, protect.</td></tr><tr><td>Int</td><td>Riddles, tricks, memories, old magic.</td></tr><tr><td>Agility</td><td>Race, dodge, fly, swim, sneak.</td></tr><tr><td>Wis</td><td>Feelings, nature, noticing, animal sense.</td></tr><tr><td>Luck</td><td>Fairy weirdness, charm magic, surprises.</td></tr></table>
""", columns=False)
be.text_page("Difficulty Rating", f"""
<div class='advancement'>
{rb('<strong>Formula:</strong> DR = round((HP + MP + Level×3 + positive stat bonuses×2) ÷ 10). Minimum DR is 1.')}
<table><tr><th>DR</th><th>Meaning</th><th>Use at table</th></tr><tr><td>1</td><td>Tiny trouble</td><td>One adventurer can usually solve it with a good idea.</td></tr><tr><td>2</td><td>Small scene</td><td>Good for a warm-up creature or comic obstacle.</td></tr><tr><td>3</td><td>Fair challenge</td><td>Needs teamwork, a spell, or two rolls.</td></tr><tr><td>4</td><td>Big scene</td><td>Use as the main creature for an adventure.</td></tr><tr><td>5+</td><td>Boss or wonder</td><td>Use rarely; make it emotional, not scary.</td></tr></table>
{qa('<strong>Balancing tip:</strong> for Adventurers 5–7, “harder” should mean more choices and more wonder, not harsher consequences.')}
</div>
""", columns=False)
creatures = [
 dict(name='Moon-Kelpie Foal', img='creature-moon-kelpie-foal.png', intro='A nervous water-pony adventurer with a kelp mane and a moon-bell collar. It wants to be brave but splashes when startled.', lore='It circles moonlit shallows where lost songs sink. If heroes speak gently, it lowers its head so the bell-shaped mark on its collar can be seen. It is not trying to block the path; it is afraid the loch will forget bedtime.', stats={'STR':1,'INT':0,'AGI':2,'WIS':1,'LUK':1}, hp=9, mp=4, level=1, wants='Its moon-bell returned.', helps='Carries one hero safely across shallow water.', moves=['Moonlit Splash (1 MP): makes stepping stones shimmer for one turn.', 'Foal Gallop: races across water if someone sings softly.'], comp='Splashes the map when startled.'),
 dict(name='Thistle Sprite', img='creature-thistle-sprite.png', intro='A tiny proud fairy with a thorn crown too large for its head. It guards paths because it secretly feels lonely.', lore='It announces itself with trumpet noises made from a grass stem. The crown keeps sliding over one eye, but the sprite insists this is royal fashion. It wants respect, company, and one job that feels important.', stats={'STR':-1,'INT':1,'AGI':2,'WIS':0,'LUK':2}, hp=6, mp=6, level=2, wants='Someone to admire its thorn crown.', helps='Shows a hidden fairy path.', moves=['Prickle Point (1 MP): blocks a rude shortcut with harmless thistles.', 'Royal Decree: demands a compliment or tiny flag.'], comp='Gets offended by rude pointing.'),
 dict(name='Moss Troll Napper', img='creature-moss-troll-napper.png', intro='A huge mossy troll who only wants a quiet nap. Birds nest in its hair and bubbles puff from its nose.', lore='This troll is older than several bridges and softer than it looks. Adventurers may climb its mossy shoulder if they ask first. It becomes a problem when its snores roll downhill and shake clues loose from the trees.', stats={'STR':3,'INT':0,'AGI':-1,'WIS':1,'LUK':0}, hp=18, mp=2, level=3, wants='A quieter place to nap.', helps='Lifts a log bridge.', moves=['Gentle Lift: moves something heavy without breaking it.', 'Bubble Snore (1 MP): floats clues away unless caught.'], comp='Snores bubbles that float away clues.'),
 dict(name='Silver Fox Familiar', img='creature-silver-fox-familiar.png', intro='A polite fox with silver whiskers, clever eyes, and too many compliments. It knows tracks no one else can see.', lore='The fox belongs to no wizard but knows every wizard worth knowing. It speaks in compliments because a curse once made rude words taste like nettles. It tests heroes with riddles to learn whether they listen.', stats={'STR':0,'INT':2,'AGI':2,'WIS':1,'LUK':1}, hp=10, mp=5, level=3, wants='A riddle answered.', helps='Leads heroes to tracks.', moves=['Compliment Riddle (1 MP): gives a clue wrapped in praise.', 'Silver Step: vanishes behind moonlit grass.'], comp='Only speaks in compliments.'),
 dict(name='Rowan Owl', img='creature-rowan-owl.png', intro='An old owl wearing rowan berries like spectacles. It sees through mist but forgets names at the funniest time.', lore='It remembers storms from before the village had a name, but it may call a lantern a “little sun bucket.” Heroes who are patient receive excellent advice hidden inside silly mistakes.', stats={'STR':0,'INT':2,'AGI':1,'WIS':3,'LUK':0}, hp=11, mp=6, level=4, wants='Help remembering a name.', helps='Sees through mist.', moves=['Mist Sight (1 MP): spots hidden doors or feelings.', 'Old Acorn Advice: gives wise advice with one wrong noun.'], comp='Calls everyone “young acorn.”'),
 dict(name='Heather Hare', img='creature-heather-hare.png', intro='A fast hare with a red ribbon tangled around one paw. It is worried, quick, and very easy to startle.', lore='The hare carries messages between hill paths but cannot sit still long enough to explain them. It thumps warnings in complicated rhythms. A calm hero can turn the thumps into a map.', stats={'STR':0,'INT':0,'AGI':3,'WIS':1,'LUK':1}, hp=8, mp=3, level=2, wants='Its red ribbon untangled.', helps='Carries a message.', moves=['Zigzag Dash: outruns almost anything on open heather.', 'Ear Twitch (1 MP): hears danger before it arrives.'], comp='Keeps changing direction.'),
 dict(name='Teacup Dragon', img='creature-teacup-dragon.png', intro='A biscuit-sized dragon who lives in warm cups and thinks it is enormous. Its sparks are bright but small.', lore='It roars into teaspoons, sleeps on folded napkins, and hoards sugar crystals. It is proud, but a sincere apology and a biscuit can turn it into a tiny furnace for helpful steam.', stats={'STR':1,'INT':1,'AGI':1,'WIS':0,'LUK':2}, hp=9, mp=6, level=3, wants='A biscuit and apology.', helps='Boils water for tea or steam clues.', moves=['Steam Puff (1 MP): reveals invisible writing.', 'Spark Sneeze (1 MP): lights a candle or startles a puddle.'], comp='Sneezes sparks into puddles.'),
 dict(name='Loch Lantern Jelly', img='creature-loch-lantern-jelly.png', intro='A shy glowing jelly that floats under dark water like a little lantern. It dims when shouted at.', lore='It drifts below the surface where moonlight cannot reach. Brave noises frighten it; soft questions brighten it. If befriended, it can show safe stones under black water.', stats={'STR':-1,'INT':0,'AGI':1,'WIS':2,'LUK':2}, hp=7, mp=7, level=3, wants='A dark pool made less lonely.', helps='Lights underwater steps.', moves=['Soft Glow (1 MP): lights a safe route beneath the surface.', 'Drift Away: escapes loud scenes without anger.'], comp='Floats away if shouted at.'),
 dict(name='Bog-Boot Brownie', img='creature-bog-boot-brownie.png', intro='A muddy household fairy who loves cleaning boots, even when boots are not the problem.', lore='It lives where the road becomes mud and treats every bootprint as a personal letter. The brownie can read a trail from one splash mark, but it may scrub away the clue unless heroes ask quickly and kindly.', stats={'STR':1,'INT':2,'AGI':1,'WIS':1,'LUK':0}, hp=8, mp=3, level=2, wants='A pair of boots to clean.', helps='Finds footprints.', moves=['Mud Map: reads footprints like a story.', 'Scrub Scrub (1 MP): cleans one item until it shines.'], comp='Cleans the wrong thing first.'),
 dict(name='Cloud Sheep', img='creature-cloud-sheep.png', intro='A dreamy sheep made of soft cloud wool. It drifts through sky meadows and forgets which star is its shepherd.', lore='Cloud Sheep nibble moon-mist and bump gently into hills. Their wool holds dreams: touch it and you may remember a lullaby. They follow laughter, which is charming until they drift away from home.', stats={'STR':1,'INT':0,'AGI':1,'WIS':1,'LUK':3}, hp=10, mp=8, level=4, wants='A shepherd star.', helps='Makes a fluffy bridge.', moves=['Cloud Bridge (2 MP): makes one soft crossing for careful feet.', 'Dream Drift (1 MP): carries a clue into the sky.'], comp='Drifts when adventurers giggle.'),
 dict(name='Gloaming Bog Hag', img='creature-gloaming-bog-hag.png', intro='A reed-crowned bog witch who looks scary in twilight but mostly wants people to stop dropping rubbish in her marsh.', lore='Her lantern eyes blink through fog and her cloak smells of peat. She mutters old rhymes that make puddles answer. Brave adventurers may discover she is guarding tadpoles and a sunken road sign.', stats={'STR':1,'INT':2,'AGI':0,'WIS':3,'LUK':1}, hp=16, mp=10, level=5, wants='The marsh cleaned and her tadpoles protected.', helps='Reveals safe stepping stones through the bog.', moves=['Bog Fog Spell (2 MP): fills the scene with mist; Agility or Wis avoids getting turned around.', 'Reed Hex (1 MP): sticky reeds grab boots for 2 HP of trouble.', 'Lantern Stare: asks one honest question no one should dodge.'], comp='Sounds frightening even when saying helpful things.'),
 dict(name='Cairn Wight', img='creature-cairn-wight.png', intro='A blue-lit guardian made of old cairn stones and memory. It is spooky, slow, and very serious about promises.', lore='The Cairn Wight rises when someone forgets a vow made on the hill. Stones grind like thunder, but it never chases farther than its cairn circle. It wants the correct name spoken kindly.', stats={'STR':3,'INT':1,'AGI':-1,'WIS':2,'LUK':0}, hp=22, mp=6, level=5, wants='A forgotten promise remembered.', helps='Opens the hill path to an old treasure.', moves=['Stone Sleep (2 MP): heavy drowsiness makes heroes sit unless they sing or move.', 'Cairn Slam: shakes the ground for 3 HP of startling trouble.', 'Memory Riddle (1 MP): asks a name from the past.'], comp='Blocks the path until someone speaks respectfully.'),
 dict(name='Redcap Bramble Sneak', img='creature-redcap-bramble-sneak.png', intro='A thorny little goblin with a red berry cap, sharp giggles, and a habit of stealing shiny bells.', lore='It hides in brambles and pretends to be fierce. The red cap is not blood; it is mashed berries and jam. It steals because it thinks shiny things keep the dark away.', stats={'STR':0,'INT':1,'AGI':3,'WIS':0,'LUK':2}, hp=12, mp=5, level=3, wants='A shiny bell, button, or brave night-light.', helps='Shows a secret thorn tunnel.', moves=['Thorn Tangle (1 MP): vines snag cloaks for 2 HP of trouble.', 'Jam-Cap Vanish: hides in berry brambles after a wobble.', 'Shriek Sneak: startles one hero unless a friend helps.'], comp='Acts mean until someone notices it is afraid of the dark.'),
 dict(name='Night Thistle Dragon', img='creature-night-thistle-dragon.png', intro='A small shadow dragon curled around glowing purple thistles. It puffs lavender smoke and guards dreams too fiercely.', lore='This dragon is not huge, but the dark makes it look larger. It hoards nightmares in thistle pods so villages can sleep, then forgets to let the good dreams out again.', stats={'STR':2,'INT':1,'AGI':2,'WIS':1,'LUK':3}, hp=20, mp=12, level=6, wants='Help sorting good dreams from bad ones.', helps='Burns away nightmare fog with purple starlight.', moves=['Lavender Smoke Spell (2 MP): sleepy smoke; Wis or Luck stays focused.', 'Thistle Breath (2 MP): prickly shadow blast for 3 HP of trouble.', 'Dream Hoard: reveals a clue hidden inside a dream pod.'], comp='Protects the wrong dream and will not listen until praised.'),
 dict(name='Hollow Hill Banshee', img='creature-hollow-hill-banshee.png', intro='A pale wind-spirit whose cry sounds scary because she is trying to warn the hill, not hurt anyone.', lore='Her ribbons flutter through fairy mounds and old doorways. She appears before storms, broken promises, and lost songs. Adventurers who listen hear words inside the wail: names, paths, and warnings.', stats={'STR':-1,'INT':1,'AGI':2,'WIS':3,'LUK':2}, hp=14, mp=14, level=6, wants='A sad song finished and a warning believed.', helps='Warns of danger before it arrives.', moves=['Warning Wail (2 MP): everyone must roll Wis or lose a turn covering ears.', 'Wind Ribbon (1 MP): moves one item across the scene.', 'Ghost Door: opens a fairy mound for one careful promise.'], comp='Her helpful warning sounds like a frightening scream.'),
]
for c in creatures:
    be.creature_page(c['name'], c['img'], c['intro'], c['stats'], c['hp'], c['mp'], c['level'], c['lore'], feature_grid([
        ('Wants', p(c['wants'])),
        ('Helps by', p(c['helps'])),
        ('Moves', ul(c['moves'])),
        ('Complication', p(c['comp'])),
        ('Gentle approach', p('Name its feeling, offer one kind idea, then roll only if the moment is exciting.')),
        ('Treasure/friend reward', p('A clue, safe path, charm, drawing prompt, or promise for later.')),
    ]))
be.text_page("Creature builder", f"""
<table><tr><th>Roll</th><th>Animal</th><th>Fairy twist</th><th>Best stat</th></tr><tr><td>1</td><td>Fox</td><td>silver whiskers</td><td>Int</td></tr><tr><td>2</td><td>Hare</td><td>bell tail</td><td>Agility</td></tr><tr><td>3</td><td>Owl</td><td>moon glasses</td><td>Wis</td></tr><tr><td>4</td><td>Pony</td><td>kelp mane</td><td>Strength</td></tr><tr><td>5</td><td>Dragon</td><td>teacup size</td><td>Luck</td></tr><tr><td>6</td><td>Sheep</td><td>cloud wool</td><td>Luck</td></tr></table>
{qa('<strong>Example:</strong> A kelp-mane pony has HP 9, MP 4, Level 1, Strength +1, Agility +2, Wis +1, Luck +1. DR = round((9+4+3+10)/10) = 3.')}
<div class='card-grid'>
{card('Set HP and MP', p('Tiny: HP 6–8, MP 2–4. Normal: HP 9–12, MP 3–6. Big: HP 15+, MP 2–8.'))}
{card('Set the stats', p('Pick one +3, one +2, two +1, and one +0. Very tiny creatures may have one -1 and one +3.'))}
{card('Calculate DR', p('DR = round((HP + MP + Level×3 + positive stats×2) ÷ 10). Minimum 1.'))}
{card('Make it adventurer-friendly', p('Replace defeat with help, chase, song, puzzle, promise, snack, or finding a lost thing.'))}
</div>
""", columns=False)
be.text_page("Creature tactics without scary combat", f"""
{split(
'<h3>What enemies do</h3>' + ul(['<strong>Guard:</strong> blocks a path until a promise is made.', '<strong>Grab:</strong> takes a hat, map, boot, spoon, or bell.', '<strong>Hide:</strong> runs into mist, reeds, cupboards, or clouds.', '<strong>Challenge:</strong> asks for a race, riddle, song, or brave sentence.', '<strong>Spend MP:</strong> uses one magical move, then gets tired or silly.']) + rb('<strong>At 0 HP:</strong> enemies stop, slump, nap, cry, apologise, or ask for help. No gore, no cruelty.'),
'<h3>Difficulty in scenes</h3><table><tr><th>Party</th><th>Good DR</th><th>Use</th></tr><tr><td>1 new hero</td><td>1–2</td><td>One creature, one clear want.</td></tr><tr><td>2–3 heroes</td><td>2–3</td><td>Teamwork or one spell helps.</td></tr><tr><td>4 heroes</td><td>3–4</td><td>Main scene, multiple approaches.</td></tr><tr><td>Finale</td><td>4–5</td><td>Big wonder, many friends return.</td></tr></table>' + qa('<strong>Guide note:</strong> if a DR feels too high, reduce HP by 2 or MP by 1, or make the creature want help sooner.')
)}
""", columns=False)

be.art_page("scary-bestiary-group.png", "Darker things in Alba", "Alba can be scary: haunted cairns, border wolves, cursed crows, bog drakes, draugr raiders, and redcap warbands.")
extra_creatures = [
 dict(name='Black Bog Drake', img='creature-black-bog-drake.png', intro='A low, tar-black drake with peat smoke nostrils and ember eyes. It coils under rotten bridges and hates bright lanterns.', lore='Bog drakes are born where old battle magic sinks into marsh water. They are dangerous guardians, but they can be tricked by clean fire, honest songs, or offering to drain poisoned pools.', stats={'STR':4,'INT':1,'AGI':1,'WIS':1,'LUK':2}, hp=28, mp=10, level=7, wants='The bog left undisturbed and its poisoned pool cleansed.', helps='Guards a hidden causeway after being respected.', moves=['Peat-Smoke Breath (2 MP): Startled and lost unless Wis resists.', 'Bog Snap: 3 HP trouble and Tangled boots.', 'Sinkhole Coil (2 MP): changes the map by opening black mud.'], comp='Hates lantern-light but follows songs.'),
 dict(name='Border Warg of the Red Wall', img='creature-border-warg.png', intro='An armored grey wolf bred by southern war-mages. It wears broken Albion chain and smells fear through stone.', lore='These wargs are not evil by nature; they were trained by conquerors. A freed warg may become a fierce protector of Alba.', stats={'STR':3,'INT':1,'AGI':3,'WIS':2,'LUK':0}, hp=24, mp=6, level=6, wants='Freedom from a cruel command collar.', helps='Tracks raiders and warns of border patrols.', moves=['Command Howl (1 MP): Startled unless a friend steadies you.', 'Iron Pounce: 3 HP trouble or knocked prone.', 'Scent the Fear: finds a hidden nervous target.'], comp='Obeys the collar until it is broken.'),
 dict(name='Draugr Oath-Raider', img='creature-draugr-oath-raider.png', intro='A sea-dead Norse warrior in barnacled mail who rises when a ship oath is broken. Its eyes burn cold blue.', lore='Draugr remember treasure, feasts, and betrayal. They can be laid to rest by returning a stolen token or finishing the oath carved on their shield.', stats={'STR':3,'INT':1,'AGI':0,'WIS':2,'LUK':1}, hp=26, mp=8, level=7, wants='Its broken ship-oath completed.', helps='Reveals a sea route or buried hoard.', moves=['Cold Oath Grip (2 MP): Sleepy and slowed until warmed.', 'Shield-Rattle: fear noise; Wis to stand firm.', 'Grave Tide (2 MP): water rises across the map.'], comp='Cannot cross a properly spoken guest-right promise.'),
 dict(name='Iron Crow Swarm', img='creature-iron-crow-swarm.png', intro='A murder of black iron-feathered crows that steals secrets, buttons, and battlefield names.', lore='Iron Crows gather where tyrants write false histories. They are terrifying in numbers but love bargains involving true names and shiny lies.', stats={'STR':0,'INT':3,'AGI':4,'WIS':1,'LUK':2}, hp=18, mp=12, level=6, wants='A secret worth carrying.', helps='Delivers a message across enemy lines.', moves=['Secret Peck (1 MP): steals one clue until asked the right question.', 'Wing-Dark (2 MP): makes the scene dim and noisy.', 'False Echo: repeats words in the wrong voice.'], comp='Cannot resist a polished lie or true apology.'),
 dict(name='Albion Redcloak Captain', img='creature-albion-redcloak-captain.png', intro='A stern commander from the southern Dominion of Albion, wearing a red cloak and carrying a banner that tries to make Alba kneel.', lore='The Redcloak Captain represents a fantasy imperial faction, not a real people. Some Albion folk are ordinary traders and neighbors; the Dominion army is the villain.', stats={'STR':2,'INT':2,'AGI':1,'WIS':0,'LUK':1}, hp=22, mp=6, level=6, wants='Taxes, maps, and obedience for the Dominion.', helps='May retreat or bargain if shown the land itself rejects conquest.', moves=['Banner Command (2 MP): nearby minions gain +1 until the banner falls.', 'Shield Wall: blocks a path unless outflanked or persuaded.', 'Orderly Threat: Startled unless someone answers boldly.'], comp='Underestimates fairy law and local clans.'),
]
for c in extra_creatures:
    be.creature_page(c['name'], c['img'], c['intro'], c['stats'], c['hp'], c['mp'], c['level'], c['lore'], feature_grid([('Wants', p(c['wants'])), ('Helps by', p(c['helps'])), ('Moves / spells', ul(c['moves'])), ('Complication', p(c['comp'])), ('Approach', p('Break the oath, collar, curse, banner, or false command that makes this enemy dangerous.')), ('Reward', p('A route, truce, freed ally, map, hoard clue, or faction reputation.'))]))
be.text_page("Monster tactics: scary but playable", f"""
{split(
'<h3>Use real danger</h3>' + ul(['Let monsters hurt plans, gear, courage, position, and resources.', 'Use 2–3 HP trouble for ordinary hits; 3 HP for boss specials.', 'Make fear visible: thunder, banners, howls, cold breath, sinking ground.', 'Always show a counter: oath, light, true name, broken collar, lost token.']),
'<h3>Faction monsters</h3><table><tr><th>Enemy</th><th>What stops it</th></tr><tr><td>Redcloak patrol</td><td>local law, fairy oath, clever terrain.</td></tr><tr><td>Norse draugr</td><td>completed oath or returned ship-token.</td></tr><tr><td>Barbarian raider</td><td>honour challenge, feast-right, or clan bargain.</td></tr><tr><td>Bog horror</td><td>clean water, lantern, song, or drained curse.</td></tr></table>'
)}
""", columns=False)
be.write()

# Campaigns
ca = Book("campaigns", "Example Campaigns", "Ready-to-run adventures and a small linked campaign for Adventures in Alba", "true-unique/cron-v3/campaign-map-table.png")
ca.cover_page()
ca.text_page("How campaigns work", f"""
<p class='drop'>A campaign for this age is a string of friendly episodes. Each session should have a clear helper, a magical place, one puzzle, and one warm ending.</p>
{spot('02-part-opener.png', '<strong>Campaign rhythm:</strong> arrive, discover, help, celebrate.')}
{rb('<strong>Length:</strong> 20–40 minutes per adventure. Stop while adventurers still want more.')}
{ul(['Start with a read-aloud box.', 'Ask one choice at a time.', 'Use three scenes: arrive, discover, help.', 'End with a sticker, drawing, or named promise.'])}
<table><tr><th>Minute</th><th>What to do</th></tr><tr><td>0–5</td><td>Read the hook and ask what the heroes notice.</td></tr><tr><td>5–15</td><td>Meet a creature or obstacle with a feeling.</td></tr><tr><td>15–30</td><td>Try two or three adventurer ideas, rolling only for exciting moments.</td></tr><tr><td>End</td><td>Name the friend helped and draw one treasure.</td></tr></table>
""")
ca.art_page("02-part-opener.png", "Campaign: The Bells Under the Heather", "Three fairy bells have gone quiet, and the glen is forgetting its bedtime songs.")
ca.text_page("Adventure 1: The Lost Moon-Bell", f"""
{qa('<strong>Read aloud:</strong> “The moon is stuck in the loch like a silver coin. A young kelpie foal stamps at the water and tries not to cry.”')}
<h3>Scenes</h3>{ul(['Meet the nervous kelpie foal.', 'Search reeds, stones, or bubbles for clues.', 'Return the bell by singing, wading, or asking the loch nicely.'])}
<h3>Roll moments</h3><table><tr><th>Idea</th><th>Stat</th></tr><tr><td>Step onto slippery stones</td><td>Agility</td></tr><tr><td>Comfort the foal</td><td>Wis</td></tr><tr><td>Hold the rope in a gust</td><td>Strength</td></tr><tr><td>Notice bubbles making an arrow</td><td>Wis</td></tr><tr><td>Promise to bring the bell back</td><td>Luck</td></tr></table>
<h3>Ending choices</h3>{ul(['The kelpie foal carries everyone one careful step across the shallows.', 'The loch hums the first note of the bedtime song.', 'A wet map reveals the next path when it dries.'])}
""")
ca.text_page("Adventure 2: The Grumpy Bridge", f"""
{qa('<strong>Read aloud:</strong> “The bridge folds its stony arms. ‘No crossing,’ it rumbles, ‘unless someone remembers how to laugh politely.’”')}
{ul(['The bridge is not mean; it is embarrassed because moss covers its carvings.', 'Adventurers can clean, joke, sing, draw, or ask what happened.', 'A wobble makes the bridge sneeze pebbles, not hurt anyone.'])}
{rb('<strong>Reward:</strong> the bridge teaches the party the safe stepping rhythm: clap, step, clap, step.')}
<h3>Extra clues</h3>{ul(['Moss hides a carved smiling face.', 'The bridge remembers adventurers who thanked it long ago.', 'A silver fox waits on the other side with dry socks.'])}
""")
ca.text_page("Adventure 3: The Thistle Crown", f"""
{qa('<strong>Read aloud:</strong> “A tiny sprite wears a crown too big for its head. It declares itself King of All Paths, then whispers, ‘Do I look brave?’”')}
<h3>What is really happening?</h3><p>The sprite is scared of guarding the path alone. It needs help making a promise flag.</p>
<h3>Good solutions</h3>{ul(['Make a tiny flag.', 'Share a brave story.', 'Ask another creature to visit.', 'Let the sprite choose a less lonely job.'])}
<h3>If the heroes wobble</h3>{ul(['The crown slips over the sprite’s eyes.', 'The path grows extra thistles, but they smell like jam.', 'The sprite declares a snack break and forgets to be bossy.'])}
""")
ca.text_page("Mini campaign tracker", f"""
<table><tr><th>Session</th><th>Bell or promise</th><th>Friend made</th><th>Drawing space</th></tr><tr><td>1</td><td>Moon-Bell</td><td></td><td></td></tr><tr><td>2</td><td>Bridge rhythm</td><td></td><td></td></tr><tr><td>3</td><td>Thistle Crown promise</td><td></td><td></td></tr><tr><td>Finale</td><td>Bedtime song returns</td><td></td><td></td></tr></table>
{rb('<strong>Finale idea:</strong> every friend returns and adds one sound to the bedtime song: splash, clap, rustle, giggle, bell.')}
<div class='card-grid'>
{card('If time is short', p('Run only the hook, one helpful creature, and the warm ending.'))}
{card('If adventurers want more', p('Let them draw the new friend, then turn the drawing into the next adventure hook.'))}
</div>
""", columns=False)

ca.art_page("alba-regional-map.png", "Campaign map: Alba at war and wonder", "Use the map to choose roads, clan lands, fairy woods, Norse seas, and the southern Dominion border.")
ca.art_page("alba-town-dungeon-map.png", "Town and dungeon map", "Drop this spread into any session: village, keep, harbor, fairy mound, loch shrine, cave, and watchtower.")
ca.art_text_page("Campaign 2: The Red Banner Road", f"""
{qa('<strong>Premise:</strong> Redcloak agents from the Dominion of Albion have crossed the southern road to tax villages, measure fairy hills, and seize mythral relics.')}
<h3>Six-session arc</h3><table><tr><th>Session</th><th>Episode</th><th>Main pressure</th></tr><tr><td>1</td><td>Taxes at Kettleford Bridge</td><td>Redcloak patrol demands coin and maps.</td></tr><tr><td>2</td><td>The Stolen Standing Stone</td><td>Albion surveyors move a fairy boundary marker.</td></tr><tr><td>3</td><td>Warg with the Iron Collar</td><td>Free a border warg from command magic.</td></tr><tr><td>4</td><td>Clan Moot under Rain</td><td>Unite rival clans without starting a feud.</td></tr><tr><td>5</td><td>Raid on the Red Supply Cart</td><td>Rescue prisoners, charms, and stolen maps.</td></tr><tr><td>6</td><td>The Banner That Lied</td><td>Break an enchanted conquest banner.</td></tr></table>
<h3>Villain note</h3><p>The Dominion of Albion is a fantasy imperial faction. Do not say every southerner is evil; make the villains the army, greedy nobles, cursed banners, and officials trying to erase Alba's names.</p><h3>Scene tools</h3><div class='card-grid'>{card('Redcloak patrol', p('2 guards, 1 tax-mage, one nervous local guide.'))}{card('Moral choice', p('Rescue prisoners now, or steal the map that saves three villages later?'))}{card('Magic problem', p('The banner makes locals forget their own hill names.'))}{card('Reward', p('Clan reputation, a freed warg ally, or a red-sealed map.'))}{card('Recurring place', p('Kettleford Bridge changes each visit: tax chain, rumor crowd, warg tracks, then banner shadow.'))}{card('Boss prep', p('Redcloak Captain carries orders, fear, and a banner tassel that points to the final true-name ritual.'))}</div>
""", image="bg-campaign-red-banner.png", side="right", columns=False)
ca.text_page("Red Banner Road: session packets", f"""
<div class='session-grid'>
{card('1. Taxes at Kettleford Bridge', p('Read aloud: Red cloaks block the bridge while a nervous goat chews their map. Goal: protect villagers without starting a battle. Key rolls: Wis to calm the crowd, Int to spot false tax marks, Strength to hold the bridge chain. Reward: bridge oath token.'))}
{card('2. Stolen Standing Stone', p('Surveyors moved a fairy border stone. Goal: learn its true name and roll it home. Wobble: the wrong hill wakes first. Reward: Rowan Compact favour.'))}
{card('3. Iron-Collar Warg', p('A warg attacks because a collar commands it. Goal: break the collar, not the wolf. Clues: red wax seal, rubbed fur, sad eyes. Reward: possible earned mount/ally.'))}
{card('4. Clan Moot in Rain', p('Two clans accuse each other of helping Albion. Goal: prove the tax-mage forged both letters. Use truth-song, guest-right, and one brave speech.'))}
{card('5. Red Supply Cart', p('Sneak, bargain, or distract to free prisoners and stolen charms. Add a three-bell countdown before patrol returns.'))}
{card('6. Banner That Lied', p('Finale: the conquest banner renames hills. Break it with true names gathered from every prior session. Boss phase: Redcloak Captain loses command when locals sing.'))}
{card('Recurring NPC: Nessa Toll-Keeper', p('Starts afraid of Redcloaks; becomes brave if the heroes protect her bridge bell. She can hide messages in toll receipts.'))}
{card('Evidence trail', p('Each session yields one proof: false tax seal, moved boundary chip, broken collar rune, forged clan letter, prisoner list, banner true name.'))}
{card('Escalation clock', p('After every session, mark one red wax dot. At three dots, patrols double. At six, the conquest banner reaches Kettleford.'))}
{card('Finale checklist', p('To beat the banner: gather three true hill names, cut the red wax tassel, and have a local speak the land oath aloud.'))}
</div>
""", columns=False)
ca.art_text_page("Campaign 3: Longships in the Mist", f"""
{qa('<strong>Premise:</strong> Norse-style sea raiders, traders, and oath-ghosts arrive from the northern isles. Some want trade, some want plunder, and some are dead but still rowing.')}
<div class='card-grid'>
{card('Harbor Hook', p('A longship appears with no crew, one blue lantern, and a shield carved with a broken oath.'))}
{card('Friendly Viking', p('Jorunn Wave-Smith wants peace, trade, and help laying her ancestor draugr to rest.'))}
{card('Raider Threat', p('Skull-Sail Rurik steals bells because he thinks they command fairy weather.'))}
{card('Sea Magic', p('Runes, whale-road maps, storm knots, salt charms, oath rings, and ghost anchors.'))}
</div>
<h3>Episodes</h3>{ul(['The Empty Longship', 'Market Day under Axes', 'Draugr in the Sea Cave', 'The Storm-Knot Duel', 'Feast-right at the Clan Hall', 'The Oath-Raiders Rest'])}<h3>Sea encounters</h3><table><tr><td>1</td><td>Fog hides a friendly trader and a hostile raider.</td></tr><tr><td>2</td><td>A seal-spirit demands the party judge an oath.</td></tr><tr><td>3</td><td>Draugr row beneath the boat at midnight.</td></tr><tr><td>4</td><td>A storm knot must be untied with song.</td></tr></table><div class='card-grid'>{card('Harbor clock', p('At three bells, market closes. At six bells, raiders choose a target. At nine, the tide opens the sea cave.'))}{card('Peace route', p('A feast, repaired sail, and returned oath-ring can turn raiders into rivals instead of enemies.'))}{card('Treasure route', p('Each episode gives one ship-token clue: lantern, shield, ring, cup, knot, final oath.'))}{card('Draugr route', p('If ignored, the ghost crew grows louder and colder; if honored, they guide the party through fog.'))}</div>
""", image="bg-campaign-longships.png", side="left", columns=False)
ca.text_page("Longships in the Mist: session packets", f"""
<div class='session-grid'>
{card('1. Empty Longship', p('The ship arrives crewless with one blue lantern. Search cargo, comfort frightened harbor folk, learn the shield oath.'))}
{card('2. Market Day Under Axes', p('Traders and raiders argue. Keep guest-right, separate Skull-Sail Rurik from peaceful Jorunn, and save the bell stall.'))}
{card('3. Draugr Sea Cave', p('Return a stolen ship-token while tide rises. Rolls: Agility on slick rocks, Wis for oath grief, Luck for storm timing.'))}
{card('4. Storm-Knot Duel', p('Untie weather knots by song, riddle, and courage. Wobble: rain falls upward for one scene.'))}
{card('5. Feast-right Hall', p('Win peace through food, story, and one fair challenge. No fighting under the roof once bread is shared.'))}
{card('6. Oath-Raiders Rest', p('Finale: complete the oath carved on the shield so the dead rowers can sleep and the living can trade.'))}
{card('Recurring NPC: Jorunn Wave-Smith', p('Friendly Norse smith-trader. She offers repairs, sea lore, and a moral reminder that not every longship comes to raid.'))}
{card('Oath clues', p('Broken shield, blue lantern, missing ring, drowned map, feast cup, and the final carved promise all point to the same betrayed voyage.'))}
{card('Sea travel rhythm', p('Each voyage scene gets weather, sound, choice: fog + oars + steer toward harbor or cave; storm + gulls + cut sail or sing.'))}
{card('Finale checklist', p('Return the ship-token, feed the living crew under guest-right, speak the shield oath, and let the draugr choose rest.'))}
</div>
""", columns=False)
ca.art_text_page("Campaign 4: The Barbarian Queen of the North", f"""
{qa('<strong>Premise:</strong> The storm-clans beyond the high passes are called barbarians by outsiders, but they have laws, poets, healers, and old reasons to distrust lowland kings.')}
<h3>Key NPCs</h3><table><tr><th>Name</th><th>Role</th><th>What they want</th></tr><tr><td>Queen Maev Stormbraid</td><td>Clan war-leader</td><td>Return of a stolen clan cauldron.</td></tr><tr><td>Old Duthac</td><td>Oath poet</td><td>Someone to remember the true story.</td></tr><tr><td>Bran of the Broken Axe</td><td>Hot-headed champion</td><td>A fair duel, not a massacre.</td></tr><tr><td>Eithne Rowan-Seer</td><td>Seer</td><td>The Thorn Court kept out of clan dreams.</td></tr></table>
<h3>Adventure structure</h3>{ul(['Prove guest-right by sharing food.', 'Solve a stolen-cauldron mystery.', 'Stop a duel using truth, not force.', 'Enter the storm cairn and face an oath monster.', 'Choose whether clans join Alba against the Dominion.'])}<h3>Clan customs</h3><table><tr><td>Guest-right</td><td>Food shared means no one may attack under that roof.</td></tr><tr><td>Truth-song</td><td>A bard may settle disputes by singing the true version.</td></tr><tr><td>Fair challenge</td><td>A duel can be riddle, wrestling, race, poem, or shield-hold.</td></tr></table><div class='card-grid'>{card('Respect scene', p('Before each roll, ask: do you speak as guest, challenger, witness, or helper? The answer changes the stat.'))}{card('Cauldron clues', p('Ash on red wax, wagon tracks, missing feast song, and a frightened page point to Albion theft.'))}{card('Duel variants', p('Run Bran’s duel as race, shield-hold, riddle, wrestling, poem, or carrying water through wind.'))}{card('Alliance reward', p('If won respectfully, the party earns storm-clan shelter and a cairn goat companion hook.'))}</div>
""", image="bg-campaign-barbarian-queen.png", side="right", columns=False)
ca.text_page("Barbarian Queen: session packets", f"""
<div class='session-grid'>
{card('1. Guest-right Test', p('The heroes must share food and answer a challenge without insulting the storm-clans. Reward: safe fire and one honest question.'))}
{card('2. Stolen Cauldron', p('Investigate tracks, lies, and red wax. Twist: Albion agents stole the cauldron to stop clan feasts.'))}
{card('3. Broken Axe Duel', p('Bran demands a duel. Make it race, riddle, shield-hold, poem, or wrestling with non-lethal stakes.'))}
{card('4. Storm Cairn', p("Enter the cairn, face an oath monster, and return the queen's ancestor story. Use thunder as a countdown."))}
{card("5. Queen's Choice", p('Convince Maev Stormbraid to join Alba against the Dominion by proving respect, truth, and returned treasure.'))}
{card('6. Pass of Two Banners', p('Finale: storm-clans and lowland clans stand together while the Red Banner road closes. Earn clan cloak or cairn goat companion.'))}
{card('Recurring NPC: Old Duthac', p('Oath poet who never lies but tells truths in riddles. He can turn a failed argument into a fair challenge.'))}
{card('Clan respect track', p('Gain respect for shared food, fair challenge, returned cauldron, remembered ancestor, and refusing Redcloak lies. Lose it for insults.'))}
{card('Storm signs', p('Thunder answers broken oaths. Lightning points at hidden red wax. Rain stops when someone tells the true story.'))}
{card('Finale checklist', p('Return the cauldron, settle Bran without humiliation, name the ancestor, and ask Maev for alliance as an equal.'))}
</div>
""", columns=False)
ca.text_page("Encounter maps and travel procedures", f"""
{split(
'<h3>Travel turn</h3>' + ul(['Pick route: road, moor, loch, forest, coast, old Roman road, fairy path.', 'Choose pace: careful, normal, urgent.', 'Roll one travel event if the route is dangerous.', 'Mark food, weather, one rumor, and one map change.']) + '<h3>Map symbols</h3><table><tr><td>Castle</td><td>law, soldiers, taxes</td></tr><tr><td>Cairn</td><td>oaths, ghosts, memory</td></tr><tr><td>Loch</td><td>water magic, kelpies, secrets</td></tr><tr><td>Longship</td><td>raids, trade, oaths</td></tr></table>',
'<h3>Travel events</h3><table><tr><td>1</td><td>Redcloak patrol measuring land.</td></tr><tr><td>2</td><td>Norse trader offers a cursed bargain.</td></tr><tr><td>3</td><td>Barbarian scouts test guest-right.</td></tr><tr><td>4</td><td>Fairy ring moves the road.</td></tr><tr><td>5</td><td>Monster sign: claw marks, cold fog, iron feathers.</td></tr><tr><td>6</td><td>Helpful local: shepherd, fisher, brownie, corbie messenger.</td></tr></table><h3>After travel</h3>' + ul(['Ask one player to mark the route on the map.', 'Ask another to name a rumor learned on the road.', 'If a companion helped, advance its bond if the table cared for it.', 'Turn one travel event into tomorrow’s hook.']) + '<h3>Route costs</h3><table><tr><td>Careful</td><td>safe clue, slower clock.</td></tr><tr><td>Normal</td><td>one event.</td></tr><tr><td>Urgent</td><td>arrive fast, start with mud/noise/tired companion.</td></tr></table>'
)}
""", columns=False)
ca.art_text_page("Campaign Workshop: scenes, NPCs, and clues", f"""
<div class='card-grid'>
{card('Scene packet template', p('Every adventure now gets: read-aloud, visible place, helpful NPC, tricky NPC, encounter, clue chain, wobble, reward, and next hook.'))}
{card('NPC voices', p('Give each NPC one tiny stage direction: speaks into a sleeve, counts buttons, whistles before telling truth, or stamps when worried.'))}
{card('Encounter choice', p('Run danger as talk, trick, travel, chase, rescue, puzzle, or careful combat. Young Adventurers should always see a kind or clever route.'))}
{card('Clue chain', p('Use three clues per adventure: one picture clue, one NPC clue, one touchable clue. If one is missed, another still points forward.'))}
</div>
<table><tr><th>Adventure</th><th>New NPCs</th><th>Extra scenes</th><th>Encounter</th></tr><tr><td>Lost Moon-Bell</td><td>Fia the Kelpie Foal, Auntie Reed, Bubble-Nose Trout</td><td>reed maze, moon-stone shelf, underwater humming gate</td><td>comfort frightened foal while water rises</td></tr><tr><td>Grumpy Bridge</td><td>Old Clapperbridge, Nessa Toll-Keeper, Silver Fox in Socks</td><td>moss-cleaning, carving riddle, toll-bell repair</td><td>bridge sneeze sends pebbles rolling toward picnic baskets</td></tr><tr><td>Thistle Crown</td><td>King Pricklecap, Moth Page, Granny Buttonroot</td><td>tiny court parade, lonely guard post, promise-flag craft</td><td>redcaps try to recruit the scared sprite with flattery</td></tr></table>
""", image="bg-campaign-red-banner.png", side="left", columns=False)

ca.text_page("Expanded Adventure 1: The Lost Moon-Bell", f"""
{qa('<strong>Read aloud:</strong> “Cold moonlight trembles on the loch. A tiny foal with a kelp mane whispers, ‘My bell fell where the water remembers every splash.’”')}
<div class='scene-packet'><h3>Scene 1 — Reeds that whisper back</h3>{ul(['NPC: Auntie Reed, an old plant spirit who dislikes rushing.', 'Clues: silver bubbles spell CLAP-SING-STEP; reed scratches show something dragged a bell.', 'Checks: Wis to soothe reeds, Agility to step dry, Luck to notice the moon’s reflection points left.'])}</div>
<div class='scene-packet'><h3>Scene 2 — Moon-stone shelf</h3>{ul(['NPC: Bubble-Nose Trout, very proud of knowing one secret.', 'Encounter: slippery shelf; a hero can tie rope, sing to water, or ask the foal to trust them.', 'Wobble: boots fill with harmless glowing water; everyone can see hidden snail tracks.'])}</div>
<div class='scene-packet'><h3>Scene 3 — Bell under the humming gate</h3>{ul(['The bell is caught in a gate that opens only for a promise.', 'Good solutions: return a lost shell, promise not to ride kelpies without asking, hum the bedtime note.', 'Reward: Moon-Bell token; once, ask water to show the safest stepping stone.'])}</div>
""", columns=False)

ca.text_page("Expanded Adventure 2: The Grumpy Bridge", f"""
{qa('<strong>Read aloud:</strong> “The bridge pulls its stones close like crossed arms. ‘I am not grumpy,’ it grumbles. ‘I am historically underappreciated.’”')}
<div class='scene-packet'><h3>Scene 1 — Toll bells and a scared crowd</h3>{ul(['NPC: Nessa Toll-Keeper hides behind a ledger but wants to help.', 'Challenge: everyone wants to cross before rain; one goat keeps eating the toll rope.', 'Clues: the bridge’s name is partly hidden under moss: Clap-per-bridge.'])}</div>
<div class='scene-packet'><h3>Scene 2 — The carved face</h3>{ul(['Encounter: clean moss without hurting sleepy moss-mice.', 'Checks: Int to read old letters, Wis to move mice kindly, Strength to hold ladder in wind.', 'Wobble: the bridge sneezes; pebbles roll but reveal the missing smile carving.'])}</div>
<div class='scene-packet'><h3>Scene 3 — Laugh politely</h3>{ul(['NPC: Silver Fox in Socks offers terrible jokes and dry socks.', 'Solution: tell a kind joke, clap the stepping rhythm, or thank the bridge by its true name.', 'Reward: Bridge-Friend badge; roads answer one question per adventure.'])}</div>
""", columns=False)

ca.text_page("Expanded Adventure 3: The Thistle Crown", f"""
{qa('<strong>Read aloud:</strong> “A fairy no taller than a teacup wears a crown the size of a soup bowl. ‘Behold my empire!’ it squeaks, then trips over a petal.”')}
<div class='scene-packet'><h3>Scene 1 — Tiny parade of one</h3>{ul(['NPC: King Pricklecap, secretly lonely and trying too hard.', 'NPC: Moth Page, loyal but exhausted from carrying proclamations.', 'Clue: the sprite’s guard post has three empty friend cups.'])}</div>
<div class='scene-packet'><h3>Scene 2 — Redcap flattery</h3>{ul(['Encounter: two redcaps promise Pricklecap a bigger crown if he blocks every path.', 'Solutions: expose the trick, offer a real job, make a promise flag, or invite neighbours to visit.', 'Wobble: thistles grow into a maze, but their flowers point to anyone who tells the truth.'])}</div>
<div class='scene-packet'><h3>Scene 3 — A better royal duty</h3>{ul(['The sprite chooses to be Keeper of Safe Paths rather than King of All Paths.', 'Reward: Thistle Crown ribbon; it untangles one bramble or social misunderstanding.', 'Next hook: Pricklecap saw a red wax seal near the southern road.'])}</div>
""", columns=False)

ca.write()

# Character sheet
sheet = Book("character-sheets", "Character Sheets", "Printable hero sheets, helper cards, and quick reference", "03-race-kindreds.png")
sheet.cover_page()
sheet.text_page("Blank hero sheet", f"""
<div class='sheet'>
<div class='sheet-box'><strong>Hero name</strong><div class='line'></div></div><div class='sheet-box'><strong>Player name</strong><div class='line'></div></div>
<div class='sheet-box'><strong>Kindred</strong><div class='line'></div></div><div class='sheet-box'><strong>Adventure job</strong><div class='line'></div></div>
<div class='sheet-box'><strong>Strength</strong><br><span class='big-stat'>+__</span></div><div class='sheet-box'><strong>Int</strong><br><span class='big-stat'>+__</span></div>
<div class='sheet-box'><strong>Agility</strong><br><span class='big-stat'>+__</span></div><div class='sheet-box'><strong>Wis</strong><br><span class='big-stat'>+__</span></div>
<div class='sheet-box'><strong>Luck</strong><br><span class='big-stat'>+__</span></div><div class='sheet-box'><strong>HP / MP</strong><br><span class='big-stat'>__/__</span></div>
<div class='sheet-box'><strong>Level</strong><div class='line'></div></div><div class='sheet-box'><strong>My gift</strong><div class='line'></div></div>
<div class='sheet-box big'><strong>Coins and gear</strong><div class='line'></div><div class='line'></div></div><div class='sheet-box big'><strong>I want to help...</strong><div class='line'></div><div class='line'></div></div>
<div class='sheet-box tall'><strong>Earned pet / mount</strong><div class='line'></div><div class='line'></div><p class='small'>Bond: □ 1 □ 2 □ 3</p></div><div class='sheet-box tall'><strong>Adventure notes / stickers</strong></div>
</div>
""", columns=False)
sheet.drawing_page()
sheet.text_page("Finished example sheet", f"""
<div class='sheet'>
<div class='sheet-box'><strong>Hero name</strong><p>Rowan Moonbutton</p></div><div class='sheet-box'><strong>Player name</strong><p>Example</p></div>
<div class='sheet-box'><strong>Kindred</strong><p>Selkie-Born</p></div><div class='sheet-box'><strong>Adventure job</strong><p>Beast Friend</p></div>
<div class='sheet-box'><strong>Strength</strong><br><span class='big-stat'>+0</span></div><div class='sheet-box'><strong>Int</strong><br><span class='big-stat'>+0</span></div>
<div class='sheet-box'><strong>Agility</strong><br><span class='big-stat'>+1</span></div><div class='sheet-box'><strong>Wis</strong><br><span class='big-stat'>+2</span></div>
<div class='sheet-box'><strong>Luck</strong><br><span class='big-stat'>+1</span></div><div class='sheet-box'><strong>HP / MP</strong><br><span class='big-stat'>10 / 8</span></div>
<div class='sheet-box'><strong>Level</strong><p>1</p></div><div class='sheet-box'><strong>My gift</strong><p>Ask a friendly creature for a small favor.</p></div>
<div class='sheet-box big'><strong>Coins and gear</strong><p>2 copper, oat pouch, sea-glass button.</p></div><div class='sheet-box big'><strong>I want to help...</strong><p>nervous animals feel safe.</p></div>
<div class='sheet-box tall'><strong>Draw your hero</strong><p class='small'>Soft seal-cloak, muddy boots, kind smile.</p></div><div class='sheet-box tall'><strong>Adventure notes</strong><p>Helped the moon-kelpie foal.</p></div>
</div>
""", columns=False)
sheet.text_page("Quick reference cards", f"""
{card('Roll rule', p('Roll d6 + stat bonus. 1–3 wobble. 4–5 yes, but. 6+ bright success.'))}
{card('HP / MP', p('HP handles bumps and tiredness. MP fuels spells. Cantrips cost 0 MP.'))}
{card('Stats', p('<strong>Strength</strong> lifts/protects. <strong>Int</strong> solves/knows. <strong>Agility</strong> moves/sneaks. <strong>Wis</strong> notices/understands. <strong>Luck</strong> handles charms/surprises.'))}
{card('Turn prompt', p('“What do you try?” then “How does your hero do it?”'))}
{card('Kindness rule', p('Heroes can be muddy, surprised, or silly. The story never shames an Adventurer for helping.'))}
{card('Wobble ideas', p('Lost hat, wet map, wrong door, sleepy troll, ringing bell, muddied boots.'))}
{card('End of session', p('Name one friend made, one brave choice, and one thing to draw.'))}
""", columns=False)
sheet.write()

# Adventure module book
am = Book("adventure-module", "Adventure Module", "Five linked one-shots with maps, read-alouds, encounters, treasure, and scaling", "alba-map.png")
am.cover_page()
am.art_page("alba-map.png", "The Bells of Alba", "A five-part starter campaign across lochs, hills, cottages, fairy mounds, and a stormy thorn crown.")
am.art_page("alba-town-dungeon-map.png", "Adventure map spread", "Use this map for village, keep, loch shrine, fairy mound, cave, and watchtower scenes.")
am.art_page("alba-frontier-map.png", "Border threat map", "Use this map when Redcloak patrols, Norse longships, storm-clans, or monsters enter the campaign.")
am.text_page("How to run these adventures", f"""
{split(
'<h3>Session recipe</h3>' + ul(['Read the boxed opening.', 'Ask what the adventurers notice.', 'Run two scenes and one creature moment.', 'Give treasure that changes the next scene.', 'End with a friend, promise, or map mark.']) + rb('<strong>Length:</strong> each adventure is built for 30–45 minutes.') + '<h3>DM checklist</h3>' + ul(['Circle one feeling: scared, proud, lonely, sleepy, worried.', 'Underline one clue the heroes can touch.', 'Pick one NPC voice: whispery, grand, grumpy, giggly.', 'Choose one safe cost before rolling: noise, mud, delay, lost hat.']),
'<h3>Scaling</h3><table><tr><th>Group</th><th>Change</th></tr><tr><td>1 adventurer</td><td>Reduce enemy HP by 4 and MP by 2.</td></tr><tr><td>2–3 adventurers</td><td>Use listed stats.</td></tr><tr><td>4+ adventurers</td><td>Add one clue objective or +3 HP to the main creature.</td></tr><tr><td>Older Adventurers</td><td>Add a timer, locked door, or rival helper.</td></tr></table>' + '<h3>Quick rewards</h3><table><tr><td>1</td><td>Helpful map mark</td></tr><tr><td>2</td><td>1d6 copper</td></tr><tr><td>3</td><td>Friendly promise</td></tr><tr><td>4</td><td>Consumable charm</td></tr></table>'
)}
""", columns=False)
for title, read, scenes, creature, treasure in [
('1. The Bell-Root Path','Tiny bells hang from sleepy roots. A fox dreams beside a moon-rune door, and the path is holding its breath.',['Notice the bells before they ring.','Find the silver acorn key.','Wake the fox kindly or sneak past.'],'Redcap Bramble Sneak, DR 3, wants its shiny bell back.','Silver acorn key; 6 copper; fox promise.'),
('2. The Glass Loch','The loch is clear as a window. Something long and blue coils below, guarding a bridge made of moon-reflection.',['Gather three dry stones.','Convince the Glass Loch Serpent the party is not stealing moonlight.','Cross without waking the cold current.'],'Glass Loch Serpent, DR 5, uses Mirror Wave.','Moon-water vial; 1 silver; safe crossing song.'),
('3. The Sooty Chimney','A cottage coughs black sparkles. Every spoon is missing, and the chimney giggles.',['Climb or talk to the chimney.','Sort useful soot from imp tricks.','Return the spoon chorus before dinner.'],'Soot Chimney Imp, DR 3, casts Soot Puff.','Warm oatcakes; soot chalk; 8 copper.'),
('4. The Hollow Hill Warning','A ribbon of cold wind circles the mound. The Banshee is crying names no one remembers.',['Listen inside the wail.','Find the forgotten promise stone.','Choose whether to open the fairy door.'],'Hollow Hill Banshee, DR 6, uses Warning Wail.','Promise stone; 1 gold; ghost door favor.'),
('5. The Thorn Crown Storm','The hill giant kneels under thunder. Its crown is too tight, and every thorn points at the village.',['Survive stormy brambles.','Learn the giant is in pain.','Remove the thorn crown using teamwork and ritual magic.'],'Thorn Crown Giant, DR 7, phase change at half HP.','Mythral thorn seed; village feast; level-up feat.')]:
    am.text_page(title, f"""
{qa('<strong>Read aloud:</strong> '+read)}
<h3>Scenes</h3>{ul(scenes)}
<h3>Main creature</h3><p>{creature}</p>
<h3>Checks</h3><table><tr><th>Approach</th><th>Stat</th><th>Wobble</th></tr><tr><td>Careful movement</td><td>Agility</td><td>Noise, snag, or muddy boot.</td></tr><tr><td>Read signs/runes</td><td>Int</td><td>Right answer, awkward timing.</td></tr><tr><td>Comfort or negotiate</td><td>Wis</td><td>Creature asks for proof.</td></tr><tr><td>Hold, lift, protect</td><td>Strength</td><td>You help, but lose 1 HP.</td></tr><tr><td>Fairy chance</td><td>Luck</td><td>Magic works with a funny mark.</td></tr></table>
<h3>Treasure</h3><p>{treasure}</p>
<div class='card-grid'>{card('Read-aloud closer', p('Ask each adventurer what their hero looks like at the end of the scene: muddy boots, proud smile, glowing pocket, or new friend.'))}{card('If they get stuck', p('Show one clue in the art, have an NPC ask a simple question, or let a pet notice the safest path.'))}{card('Optional twist', p('A rival helper arrives, the weather changes, or the treasure points to the next map mark.'))}{card('Level note', p('After a big kindness, mark one star toward the next level.'))}</div>
""", columns=False)
am.text_page("Campaign tracker", f"""
<p>Use this tracker to connect every one-shot to the larger war for Alba. Add map marks, faction reputation, and which monster became an ally.</p><table><tr><th>Adventure</th><th>Friend made</th><th>Treasure</th><th>Promise</th></tr><tr><td>Bell-Root Path</td><td></td><td></td><td></td></tr><tr><td>Glass Loch</td><td></td><td></td><td></td></tr><tr><td>Sooty Chimney</td><td></td><td></td><td></td></tr><tr><td>Hollow Hill</td><td></td><td></td><td></td></tr><tr><td>Thorn Crown Storm</td><td></td><td></td><td></td></tr></table>
{rb('<strong>Leveling suggestion:</strong> level up after adventures 2 and 5. Award a feat after adventure 5 if the party reaches level 4.')}
""", columns=False)
am.write()

# Setting guide
sg = Book("setting-guide", "Setting Guide", "Regions, towns, fairy courts, holidays, factions, and legends of Alba", "alba-map.png")
sg.cover_page()
sg.art_page("alba-map.png", "Map of Alba", "Use this as a soft story map. Add names at the table when adventurers discover them.")
sg.text_page("Regions of Alba", f"""
<table><tr><th>Region</th><th>Look</th><th>Adventure use</th></tr><tr><td>Heatherhigh Hills</td><td>Purple slopes, cairns, windy paths.</td><td>Giants, promises, weather magic.</td></tr><tr><td>Glass Loch</td><td>Still water, moon bridges, kelp bells.</td><td>Kelpies, serpents, reflection riddles.</td></tr><tr><td>Thistlewood</td><td>Brambles, hidden doors, fox tracks.</td><td>Sprites, lost paths, thorn bargains.</td></tr><tr><td>Crofters' Glen</td><td>Warm cottages, markets, oat fields.</td><td>Chores that become quests.</td></tr><tr><td>Hollow Hill</td><td>Fairy mound, ribbons, ghost wind.</td><td>Banshees, old names, warnings.</td></tr></table><div class='card-grid'>{card('Town: Alba-Brae', p('A cozy market village with a crooked clocktower and a shop that sells useful string.'))}{card('Town: Kettleford', p('Bridge town where goats demand manners and tinkers repair enchanted pots.'))}{card('Wild site: Star Cairn', p('Old stones that hum when a promise is almost remembered.'))}{card('Dungeon: Root Warrens', p('Friendly-dark tunnels under Thistlewood, full of bells, mice, and jam doors.'))}</div>
""", columns=False)
sg.text_page("Factions and fairy courts", f"""
{split(
'<h3>Friendly groups</h3>' + ul(['The Rowan Keepers remember promises.', 'The Kettle Guild repairs tiny magical things.', 'The Lantern Jellies guide lost swimmers.', 'The Croft Circle trades gossip, oats, and maps.']),
'<h3>Tricky courts</h3>' + ul(['The Thorn Court loves rules, flags, and compliments.', 'The Moon Court speaks in dreams and reflections.', 'The Soot Court hides useful things in messy places.', 'The Cairn Court guards old names.']) + qa('<strong>Faction question:</strong> who wants this problem solved, and who thinks the problem is useful?')
)}
""", columns=False)
sg.text_page("Holidays, legends, and gods/spirits", f"""
<div class='card-grid'>
{card('First Thistle Day', p('Adventurers tie ribbons to safe paths. Sprites demand tiny speeches.'))}
{card('Loch Lantern Night', p('Families float candle boats and ask the loch to remember kind names.'))}
{card('The Kindly Cailleach', p('An ancient winter spirit who tests manners, then gives warm socks.'))}
{card('The Rowan Stag', p('A spirit of honest paths. Its antlers glow when a promise is true.'))}
</div>
""", columns=False)

sg.art_page("alba-regional-map.png", "Greater Alba", "A high fantasy medieval Scotland of clans, crowns, fairy courts, storm coasts, southern forts, and old mythral roads.")
sg.art_page("alba-frontier-map.png", "Frontiers and enemies", "The coast brings longships; the high passes bring storm-clans; the southern road brings the Dominion of Albion.")
sg.text_page("Alba lore: high fantasy medieval Scotland", f"""
<p class='drop'>Alba is a northern kingdom of rain-dark castles, heather hills, lochs deep enough to remember the moon, fairy roads, clan halls, and mythral seams under ancient cairns.</p>
<div class='card-grid'>
{card('The Crown of Alba', p('The king or queen rules by stone-oath: they must be accepted by clan, kirk, fairy court, and the Stone of Scone-Under-Stars.'))}
{card('Mythral', p('Mythral is moon-silver from old cairns. One mythral coin equals 100 gold; most folk never see one.'))}
{card('Fairy Law', p('Names, guest-right, promises, salt, iron, rowan, and music matter as much as swords.'))}
{card('The Border', p('Southern forts mark the road to the Dominion of Albion, whose nobles want maps, taxes, mythral, and obedience.'))}
</div>
""", columns=False)
sg.text_page("Major factions of Alba", f"""
<p>Factions should pull the party in different directions. Give every faction a useful ally, a dangerous hardliner, and a favor they can offer.</p><table><tr><th>Faction</th><th>Style</th><th>Goal</th><th>Adventure hook</th></tr><tr><td>Clan MacThorn</td><td>Highland oath-warriors</td><td>Keep the old passes free.</td><td>A champion demands guest-right proof.</td></tr><tr><td>The Rowan Compact</td><td>Druids, seers, tree-wardens</td><td>Protect fairy roads and sacred groves.</td><td>A rowan grove accuses a town of oath-breaking.</td></tr><tr><td>The Kettle Guild</td><td>Tinkers, crafters, hearth-mages</td><td>Control enchantment recipes.</td><td>A stolen recipe makes cursed shields.</td></tr><tr><td>The Norse Sea-Kin</td><td>Vikings, traders, skalds, raiders</td><td>Trade, raid, and settle by oath.</td><td>A peaceful jarl needs help against draugr.</td></tr><tr><td>The Storm-Clans</td><td>So-called barbarians of the north</td><td>Defend clan law and old cauldrons.</td><td>They may ally with Alba if respected.</td></tr><tr><td>The Dominion of Albion</td><td>Southern imperial redcloaks</td><td>Tax, map, and conquer Alba.</td><td>Break an enchanted conquest banner.</td></tr></table>
""", columns=False)
sg.text_page("Albion, Vikings, and barbarians", f"""
{split(
'<h3>The Dominion of Albion</h3><p>Albion is a fantasy southern empire inspired by medieval border wars. The villains are imperial nobles, Redcloak officers, tax sorcerers, and conquest banners — not every person from the south.</p>' + ul(['Redcloak patrols measure land with iron chains.', 'Tax-mages try to rename hills so fairy law forgets them.', 'Border captains fear Alba because Alba refuses to kneel.']),
'<h3>Norse and storm-clan neighbors</h3><p>Vikings can be raiders, traders, rivals, oath-keepers, or allies. The northern storm-clans are called barbarians by outsiders, but their own laws are strict: guest-right, fair challenge, clan debt, and truth-song.</p>' + ul(['A Norse jarl may hire the party to end a draugr curse.', 'A raider may become an ally after a feast-right promise.', 'A storm-clan queen may fight Albion if her stolen cauldron is returned.'])
)}
""", columns=False)
sg.text_page("Places to put on maps", f"""
<table><tr><th>Place</th><th>Use</th><th>Secret</th></tr><tr><td>Dun Rowan</td><td>capital hill-fort and oath stone</td><td>the stone speaks in dreams.</td></tr><tr><td>Skerryvik</td><td>Norse harbor town</td><td>half the town wants peace, half wants raids.</td></tr><tr><td>Redwall March</td><td>southern border forts</td><td>an Albion banner is alive and lying.</td></tr><tr><td>Cauldron Pass</td><td>storm-clan mountain road</td><td>barbarian queen guards a mythral spring.</td></tr><tr><td>Saint Brigid's Well</td><td>healing and prophecy</td><td>poison cannot cross it at dawn.</td></tr><tr><td>The Black Bog</td><td>monster lair and ruined battlefield</td><td>a bog drake sleeps on lost redcloak gold.</td></tr></table>
""", columns=False)
sg.write()

# Treasure and crafting book
tc = Book("treasure-crafting", "Treasure and Crafting", "Magic items, potions, mythral gear, fairy bargains, and recipes", "table-aids.png")
tc.cover_page()
tc.text_page("Treasure tiers", f"""
<table><tr><th>Tier</th><th>Coin range</th><th>Examples</th></tr><tr><td>Copper</td><td>1–9 cp</td><td>chalk, snack, candle, ribbon.</td></tr><tr><td>Silver</td><td>1–9 sp</td><td>rope, lantern, padded cloak.</td></tr><tr><td>Gold</td><td>1–9 gp</td><td>spell charm, fine tool, fairy favor.</td></tr><tr><td>Mythral</td><td>1+ mp</td><td>legendary seed, moon key, named blade that refuses cruelty.</td></tr></table><div class='card-grid'>{card('Copper treasure', p('Three blue buttons, a candle stub, and a biscuit wrapped in wax paper.'))}{card('Silver treasure', p('A sturdy rope, a good lantern, or a map drawn by a fox.'))}{card('Gold treasure', p('A named charm, guild favor, or one spell scroll.'))}{card('Mythral treasure', p('A story-changing object that asks for a promise before it works.'))}</div>
{rb('<strong>Conversion:</strong> 10 copper = 1 silver, 10 silver = 1 gold, 100 gold = 1 mythral.')}
""", columns=False)
tc.text_page("Crafting recipes", f"""
<table><tr><th>Item</th><th>Ingredients</th><th>Effect</th></tr><tr><td>Glow-Pebble</td><td>pebble, firefly wink, 1 copper</td><td>Soft light for one scene.</td></tr><tr><td>Bravery Biscuit</td><td>oats, honey, brave word</td><td>Ignore Startled once.</td></tr><tr><td>Mist Ribbon</td><td>ribbon, loch water, song</td><td>+1 Agility in fog.</td></tr><tr><td>Promise Button</td><td>button, thread, true promise</td><td>Ask for one Luck clue.</td></tr><tr><td>Mythral Thorn Seed</td><td>mythral, thorn, giant tear</td><td>Grow a protective hedge in a finale.</td></tr></table>
""", columns=False)
tc.text_page("Fairy bargains", f"""
{split(
'<h3>Good bargain prices</h3>' + ul(['A song sung at sunset.', 'A promise to return a lost thing.', 'A drawing of the creature as a friend.', 'One shiny button, not a memory.', 'A day of helping clean a path.']),
'<h3>Never take</h3>' + ul(["A real adventurer's true name, voice, or memory.", 'Anything that makes a player feel trapped.', 'A choice the adventurer cannot understand.']) + rb('<strong>Safe bargain rule:</strong> bargains are story hooks, not punishments. They should create a future scene, not remove agency.')
)}
""", columns=False)

tc.art_text_page("Magic item catalogue", f"""
<p class='drop'>Magic items in Alba are named, opinionated, and tied to promises. Even simple relics should change a scene or create a hook.</p><table><tr><th>Item</th><th>Cost</th><th>Power</th><th>Quirk</th></tr><tr><td>Rowan-Bark Shield</td><td>8 gold</td><td>Reduce thorn, arrow, or fear trouble by 2 HP once per scene.</td><td>hums near broken promises.</td></tr><tr><td>Loch-Mirror Cloak</td><td>12 gold</td><td>+1 to sneak, dodge, or hide in mist/moonlight.</td><td>reflection sometimes waves first.</td></tr><tr><td>Cairn-Knuckle Ring</td><td>15 gold</td><td>+1 to hold, lift, brace, or remember an oath.</td><td>heavy when the wearer lies.</td></tr><tr><td>Star-Moth Lantern</td><td>20 gold</td><td>Reveals invisible ink, fairy doors, and ghost footprints.</td><td>attracts curious moths.</td></tr><tr><td>Mythral Seed Blade</td><td>1 mythral</td><td>Cuts curses, brambles, and conquest banners; refuses cruelty.</td><td>needs a promise before each quest.</td></tr></table>
""", image="item-magic-sheet.png", side="left", columns=False)
tc.text_page("Enchanting recipes", f"""
{split(
'<h3>Enchanting steps</h3>' + ul(['Choose item and enchantment word.', 'Gather ingredient: rowan berry, loch glass, cairn dust, star moth wing, storm nail, mythral shaving.', 'Spend 2 MP or perform a group ritual.', 'State the promise that limits the item.']) + rb('<strong>Cost:</strong> simple enchantment 5 gold, strong enchantment 20 gold, mythral enchantment 100 gold or one mythral relic.'),
'<h3>Recipe table</h3><table><tr><th>Enchantment</th><th>Ingredient</th><th>Effect</th></tr><tr><td>Bright</td><td>star moth wing</td><td>reveals hidden things.</td></tr><tr><td>Thorn</td><td>red thorn</td><td>protects or tangles.</td></tr><tr><td>Loch</td><td>moon-water</td><td>mist, water, memory.</td></tr><tr><td>Cairn</td><td>oath dust</td><td>stone, memory, endurance.</td></tr><tr><td>Storm</td><td>storm nail</td><td>speed, thunder, courage.</td></tr></table>'
)}
""", columns=False)
tc.art_text_page("Potion and poison recipes", f"""
<p>Potions are bought, brewed, stolen, gifted, or found in monster lairs. Poisons are obstacles with cures, not instant defeat.</p><table><tr><th>Recipe</th><th>Type</th><th>Ingredients</th><th>Effect</th></tr><tr><td>Heatherheart Draught</td><td>Potion</td><td>heather honey, warm oats, rowan berry</td><td>Regain 3 HP; ignore Startled once.</td></tr><tr><td>Loch-Breath Sip</td><td>Potion</td><td>moon-water, shell dust, seal-song</td><td>Breathe underwater for one scene.</td></tr><tr><td>Foxwit Tea</td><td>Potion</td><td>silver mint, foxglove leaf, honest riddle</td><td>+1 Int for riddles/runes/traps.</td></tr><tr><td>Nightshade Jam</td><td>Poison</td><td>dark berry, redcap sugar, sleepy root</td><td>Sleepy until bitter tea is drunk.</td></tr><tr><td>Black Bog Venom</td><td>Poison</td><td>bog drake scale, peat smoke, sour water</td><td>-1 Agility until washed in running water.</td></tr><tr><td>Iron Crow Ink</td><td>Poison/curse</td><td>iron feather, black salt, stolen word</td><td>Cannot speak a lie until one useful truth is told.</td></tr></table>
""", image="item-potions-poisons-sheet.png", side="left", columns=False)
tc.write()

# Bestiary volume 2
b2 = Book("bestiary-vol-2", "Bestiary Volume 2", "More spooky, magical, adventurer-safe creatures with spells and special attacks", "creature-mist-stag.png")
b2.cover_page()
b2.text_page("Using scarier creatures safely", f"""
{split(
'<h3>Scary, not cruel</h3>' + ul(['Use shadow, fog, thunder, strange voices, and big feelings.', 'Avoid gore, helplessness, or hopeless consequences.', 'Give every scary creature a want that can be understood.']) + '<h3>Creature pacing</h3>' + ul(['Round 1: show what is strange.', 'Round 2: use a special attack or spell.', 'Half HP: reveal the true worry.', '0 HP: offer help, bargain, nap, or apology.']),
'<h3>Special attacks</h3>' + ul(['Spend MP when the move changes the scene.', 'Name the safe result: tangled, sleepy, startled, glittered, lost, or muddy.', 'Let clever gear, spells, and kindness reduce danger.']) + '<h3>DR guide</h3><table><tr><th>DR</th><th>Feeling</th><th>Use</th></tr><tr><td>3</td><td>spooky warm-up</td><td>one scene</td></tr><tr><td>5</td><td>main trouble</td><td>teamwork</td></tr><tr><td>7+</td><td>boss wonder</td><td>finale only</td></tr></table>'
)}
""", columns=False)
for c in [
 dict(name='Mist Stag of Alba', img='creature-mist-stag.png', intro='A tall ghostly stag with antlers full of fog-lights. It appears when someone chooses the wrong path for the right reason.', lore='The Mist Stag is majestic and unsettling, but never cruel. Its hooves make no sound, and its breath shows hidden footprints.', stats={'STR':1,'INT':1,'AGI':3,'WIS':3,'LUK':2}, hp=18, mp=12, level=6, wants='A lost traveler guided home.', helps='Reveals the honest path.', moves=['Antler Lantern (2 MP): lights all hidden tracks.', 'Fog Leap: moves anywhere in mist.', 'Wrong-Way Charm (1 MP): turns the path unless Wis resists.'], comp='Only follows honest promises.'),
 dict(name='Glass Loch Serpent', img='creature-glass-loch-serpent.png', intro='A translucent serpent of blue loch water and moonlight. It coils around reflections and dislikes loud splashing.', lore='It guards the boundary between real water and mirror water. If treated politely, it lets heroes cross on moon ripples.', stats={'STR':2,'INT':1,'AGI':2,'WIS':2,'LUK':3}, hp=20, mp=10, level=5, wants='Moonlight returned to the loch.', helps='Creates a reflection bridge.', moves=['Mirror Wave (2 MP): swaps two reflections and confuses directions.', 'Crystal Coil: wraps a boat without crushing it.', 'Moonbite Glimmer (1 MP): 2 HP of cold sparkle trouble.'], comp='Repeats the last words spoken.'),
 dict(name='Soot Chimney Imp', img='creature-soot-chimney-imp.png', intro='A smoky little imp with coal eyes and a grin full of harmless sparks. It steals spoons to make a tiny orchestra.', lore='It lives in chimneys and thinks mess is a language. It can be scary when it pops out, but mostly wants applause.', stats={'STR':0,'INT':2,'AGI':3,'WIS':0,'LUK':1}, hp=10, mp=7, level=3, wants='An audience for its spoon band.', helps='Finds hidden chimney passages.', moves=['Soot Puff (1 MP): makes everyone glitter-black and easy to track.', 'Spoon Clatter: startling noise; Wis to stay calm.', 'Smoke Slip: escapes through cracks.'], comp='Cannot resist applause.'),
 dict(name='Iron-Tooth Granny Goat', img='creature-iron-tooth-granny-goat.png', intro='A stubborn magical goat with one iron tooth charm and a voice like a creaky gate. She guards bridges from rude travelers.', lore='She is scary because she knows when someone has been impolite. Compliments, oats, or a sincere apology soften her quickly.', stats={'STR':3,'INT':1,'AGI':1,'WIS':2,'LUK':0}, hp=17, mp=5, level=4, wants='Manners before crossing.', helps='Knows every bridge toll and secret step.', moves=['Bridge Stomp: 2 HP of wobbling trouble.', 'Iron Chomp (1 MP): bites through rope or bramble, not people.', 'Granny Glare: asks for an apology.'], comp='Headbutts unattended baskets.'),
 dict(name='Thorn Crown Giant', img='creature-thorn-crown-giant.png', intro='A kneeling giant made of heather, bark, and thorn branches. It is huge, frightening, and in pain from a crown that grew too tight.', lore='This is a finale creature. Its storm is not anger; it is hurt feelings and tangled magic. Heroes must survive, listen, and remove the crown.', stats={'STR':4,'INT':0,'AGI':-1,'WIS':2,'LUK':1}, hp=30, mp=12, level=8, wants='The thorn crown loosened safely.', helps='Protects Alba once healed.', moves=['Storm Stomp (2 MP): everyone chooses dodge, hold, or shelter.', 'Thorn Wall (2 MP): divides the map until cut, sung, or soothed.', 'Half-HP Phase: the giant whispers the crown hurts.'], comp='Every movement changes the battlefield.'),
 dict(name='Moon-Mirror Cat', img='creature-moon-mirror-cat.png', intro='A black cat whose eyes reflect stars instead of rooms. It steps through puddles and steals secrets only to keep them safe.', lore='The cat is mysterious, not mean. It tests whether adventurers can ask a careful question rather than grab an answer.', stats={'STR':-1,'INT':3,'AGI':3,'WIS':1,'LUK':3}, hp=9, mp=12, level=5, wants='A secret carried kindly.', helps='Opens a puddle portal.', moves=['Puddle Door (2 MP): creates a shortcut with a strange price.', 'Star-Eye Hint (1 MP): reveals one clue backwards.', 'Secret Swipe: steals a clue until politely asked.'], comp='Answers only one-word questions.'),
 dict(name='Ember Kettle Kobold', img='creature-ember-kettle-kobold.png', intro='A tiny cave kobold with a glowing kettle helmet. Steam whistles when it gets nervous.', lore='It tends dungeon tea boilers and trap kettles. It looks alarming in the dark, but is mostly afraid someone will waste good tea.', stats={'STR':1,'INT':2,'AGI':2,'WIS':0,'LUK':1}, hp=12, mp=8, level=4, wants='A perfect cup of cave tea.', helps='Disarms hot-steam traps.', moves=['Steam Whistle (1 MP): Startled unless someone laughs.', 'Kettle Pop (2 MP): launches harmless sparks for 2 HP trouble.', 'Trap-Tap: points out one device if offered tea.'], comp='Corrects everyone\'s tea manners.'),
]:
    b2.creature_page(c['name'], c['img'], c['intro'], c['stats'], c['hp'], c['mp'], c['level'], c['lore'], feature_grid([('Wants', p(c['wants'])), ('Helps by', p(c['helps'])), ('Spells / special attacks', ul(c['moves'])), ('Complication', p(c['comp'])), ('Gentle approach', p('Ask what it protects, what it fears, or what promise it needs.')), ('Reward', p('A path, charm, recipe, clue, or future ally.'))]))

b2.art_page("scary-bestiary-group.png", "Scary things of war and border", "Use these when the campaign moves from fairy trouble to high fantasy danger: drakes, wargs, draugr, redcloaks, and iron crows.")
for c in [
 dict(name='Redcap Warband Boss', img='creature-redcap-warband-boss.png', intro='A larger redcap with berry-black armor, a stolen horn, and a gang of bramble sneaks.', lore='It wants to turn fear into power. It is scary, bossy, and beatable by bravery, light, and offering its followers a safer home.', stats={'STR':2,'INT':2,'AGI':3,'WIS':0,'LUK':2}, hp=24, mp=10, level=6, wants='A dark hill where nobody laughs at it.', helps='Can reveal redcap tunnels if defeated fairly.', moves=['War Horn (2 MP): summons bramble minions.', 'Jam-Blade Feint: 3 HP trouble but no gore.', 'Bramble Ambush (2 MP): Tangled condition.'], comp='Followers abandon it if shown kindness.'),
 dict(name='Albion Tax-Mage', img='creature-albion-tax-mage.png', intro='A southern Dominion sorcerer with iron measuring chains, red wax seals, and a book that tries to rename Alba.', lore='Tax-mages are dangerous because they erase local names. Break their ink, chain, or authority and their spell collapses.', stats={'STR':0,'INT':4,'AGI':1,'WIS':0,'LUK':1}, hp=18, mp=18, level=7, wants='Names, maps, taxes, and obedience.', helps='Knows secret Redcloak plans if captured or convinced.', moves=['Rename Hill (3 MP): fairy path closes until true name spoken.', 'Iron Chain Map (2 MP): blocks travel routes.', 'Red Wax Seal (1 MP): locks chest, gate, or mouth.'], comp='Cannot control a place whose true name is sung by locals.'),
 dict(name='Barbarian Storm-Berserker', img='creature-barbarian-storm-berserker.png', intro='A northern clan champion painted with storm spirals, fierce but bound by honor and guest-right.', lore='Outsiders call them barbarians; they call themselves the Storm-Clans. They are not monsters, but can be fearsome enemies if insulted.', stats={'STR':4,'INT':0,'AGI':2,'WIS':1,'LUK':1}, hp=26, mp=8, level=7, wants='A fair challenge and respect for clan law.', helps='Can become a mighty ally against Albion.', moves=['Storm Roar (2 MP): Startled unless answered bravely.', 'Axe-Flat Knockdown: 3 HP trouble; no gore.', 'Honor Challenge: one hero may duel with non-lethal stakes.'], comp='Must obey guest-right and cannot refuse a truthful poem.'),
]:
    b2.creature_page(c['name'], c['img'], c['intro'], c['stats'], c['hp'], c['mp'], c['level'], c['lore'], feature_grid([('Wants', p(c['wants'])), ('Helps by', p(c['helps'])), ('Spells / special attacks', ul(c['moves'])), ('Complication', p(c['comp'])), ('Approach', p('Find the law, oath, collar, true name, or respect that changes the fight.')), ('Reward', p('Faction clue, battle map, freed ally, or magic item ingredient.'))]))
b2.write()


# Quickstart / Starter Box pack
qs = Book("quickstart-pack", "Starter Box Quickstart", "Print-this-first pack: rules, hero, adventure, map, monsters, treasure, and table aids", "alba-town-dungeon-map.png")
qs.cover_page()
qs.art_page("alba-town-dungeon-map.png", "Print this first", "A tiny boxed-set version of Adventures in Alba: one map, one adventure, one hero, one sheet, and cards.")
qs.text_page("One-page rules", f"""
{split(
'<h3>Core roll</h3>' + ul(['Say what your Adventurer tries.', 'Choose Strength, Int, Agility, Wis, or Luck.', 'Roll d6 + stat bonus.', '1–3 wobble: it works badly or costs something.', '4–5 yes, but: success with a twist.', '6+ bright success: clean success plus a little advantage.']) + rb('<strong>Only roll when the answer is exciting.</strong> If the idea is kind, clever, and safe, let it work.'),
'<h3>Turn order</h3>' + ul(['Everyone says one idea before dice.', 'One helper may give +1 if they describe how.', 'HP is bumps/tiredness. MP fuels spells.', 'At 0 HP, rest, get rescued, or accept a story cost — no gore.']) + '<h3>Stats</h3><table><tr><td>Strength</td><td>lift, hold, protect</td></tr><tr><td>Int</td><td>runes, plans, puzzles</td></tr><tr><td>Agility</td><td>sneak, dodge, climb</td></tr><tr><td>Wis</td><td>notice, comfort, understand</td></tr><tr><td>Luck</td><td>charms, surprises, fairy chances</td></tr></table>'
)}
""", columns=False)
qs.text_page("Ready Adventurer: Rowan Moonbutton", f"""
{split(
'<h3>Rowan Moonbutton</h3><p><strong>Kindred:</strong> Selkie-Born. <strong>Job:</strong> Beast Friend. <strong>Look:</strong> seal-cloak, muddy boots, kind eyes.</p><table><tr><th>STR</th><th>INT</th><th>AGI</th><th>WIS</th><th>LUK</th></tr><tr><td>+0</td><td>+0</td><td>+1</td><td>+2</td><td>+1</td></tr></table>' + rb('<strong>HP 10 / MP 8.</strong> Gift: once per session, ask a creature what it really wants.'),
'<h3>Gear and spells</h3>' + ul(['Oat pouch: +1 Wis with hungry animals.', 'Sea-glass button: ask for one Luck clue near water.', 'Glow-Pebble: 0 MP soft light.', 'Kind Whisper: 0 MP help a creature name its feeling.', 'Shield of Thistles: 1 MP protect a friend from 2 HP.']) + '<h3>Goal</h3><p>Help nervous animals feel safe, then draw the friend you made.</p>'
)}
""", columns=False)
qs.drawing_page()
qs.text_page("Starter adventure: The Moon-Bell at Kettleford", f"""
<div class='scene-packet'><h3>Read aloud</h3><p>The Kettleford bridge is folded shut like grumpy arms. A moon-bell hangs beneath it, ringing underwater, while a wet fox points at bubbles.</p></div>
<div class='quick-grid'>
{card('What is really happening', p('A red wax tax charm made the bridge forget its name. The moon-bell can wake it if returned to the top stone.'))}
{card('Three clues', ul(['Bubbles spell the bridge name backwards.', 'The fox has red wax on one paw.', 'A cairn goat keeps staring at the loose keystone.']))}
{card('Three solutions', ul(['Sing the bridge name while lifting the bell.', 'Break the red wax seal with clean water.', 'Ask the fox to lead them under the safe arch.']))}
{card('Wobble results', ul(['Muddy boots and -1 Agility until cleaned.', 'The bell rings too loudly and wakes a redcap.', 'The bridge opens halfway, making a silly steep ramp.']))}
{card('Bright success', p('The bridge opens fully, the fox becomes a guide, and the moon-bell marks the map.'))}
{card('Reward', p('1 silver, Bridge-Friend badge, and a companion hook: earn the cairn goat by finding its lost bell.'))}
</div>
""", columns=False)
qs.art_page("alba-town-dungeon-map.png", "Starter map", "Point to village, bridge, fairy mound, loch shrine, cave, and watchtower. Let players choose the route.")
qs.text_page("Six quick monsters and NPCs", f"""
<div class='quick-grid'>
{card('Wet Fox Guide', p('HP 6, DR 1. Wants dry socks. Helps find hidden arches.'))}
{card('Redcap Bramble Sneak', p('HP 10, MP 4, DR 3. Wants shiny bells. Stops if offered a safer joke.'))}
{card('Cairn Goat', p('HP 9, DR 2. Wants lost bell. Earn as companion after a rescue.'))}
{card('Bridge That Forgot', p('HP 18, MP 6, DR 4. Wants its true name sung.'))}
{card('Tax-Mage Echo', p('MP 8, DR 4. A leftover spell, broken by washing red wax away.'))}
{card('Moon-Bell Sprite', p('HP 5, MP 8, DR 2. Wants to be useful, not trapped under stone.'))}
</div>
""", columns=False)
qs.text_page("Twelve treasure cards", f"""
<div class='print-card-grid'>
{''.join([card('Treasure '+str(i+1), p(txt)) for i,txt in enumerate(['Bridge-Friend badge: +1 when asking bridges for help.','Moon-water vial: clean one curse mark.','Fox map: reveals a safe path.','Oat cake: calm one hungry creature.','Glow pebble: soft light for one scene.','Promise button: ask for one Luck clue.','Dry socks: remove Muddy once.','Cairn bell: starts a mount/pet quest.','Rowan twig: keeps fairies polite.','Silver thistle coin: worth 1 silver or one favor.','Red wax scrap: proof of Albion meddling.','Tiny kettle: tea with any friendly NPC.'])])}
</div>
""", columns=False)
qs.write()

# Standalone printable cards deck
pc = Book("printable-cards", "Printable Cards", "Cut-out spell, item, potion, companion, monster, quest, reward, and condition cards", "true-unique/cron-v3/printable-card-table.png")
pc.cover_page()
card_sets = [
('Spell cards', ['Glow-Pebble|0 MP. Make soft light for one scene.','Mist Step|1 MP. Slip past a watcher/root/trap.','Shield of Thistles|1 MP. Block 2 HP trouble.','Kind Whisper|0 MP. Help a creature name its feeling.','Rune Read|1 MP. Ask one question about old writing.','Foxfire Path|1 MP. Find the gentlest route.','Wake Charm|2 MP. Ask a magic item what it wants.','Thorn Thread|1 MP. Tie or tangle gently.','Loch Breath|2 MP. Breathe underwater one scene.']),
('Magic item cards', ['Rowan-Bark Shield|Reduce thorn/arrow/fear trouble by 2 HP.','Loch-Mirror Cloak|+1 to sneak in mist/moonlight.','Cairn-Knuckle Ring|+1 to hold, lift, or remember an oath.','Star-Moth Lantern|Reveals invisible ink and ghost tracks.','Mythral Seed Blade|Cuts curses; refuses cruelty.','Bridge-Friend Badge|+1 when asking bridges or roads for help.','Promise Button|Ask for one Luck clue.','Moon-Water Vial|Clean one curse mark.','Fox Map|Reveal one safe path.']),
('Potion and poison cards', ['Heatherheart Draught|Regain 3 HP; ignore Startled once.','Loch-Breath Sip|Breathe underwater for one calm scene.','Foxwit Tea|+1 Int for riddles/runes/traps.','Nightshade Jam|Sleepy until bitter tea or warm song.','Black Bog Venom|-1 Agility until washed in running water.','Iron Crow Ink|Cannot speak a lie until one useful truth.','Warm Oats|Calm a hungry animal.','Bitter Tea|Cures Sleepy poison.','Storm Honey|+1 Strength in thunder.']),
('Pet and mount cards', ['Highland Pony|Earn by freeing it from a bog rope. Helps travel/carrying.','Cairn Goat|Earn by finding its lost bell. Helps climbing paths.','Fairy Stag|Earn by protecting its grove. Fast travel once/adventure.','Kelp-Mane Pony|Earn by returning moon-water charm. Safe loch crossing.','Rowan Owl|Earn by solving old-name riddle. Night warnings.','Border Warg|Earn by breaking command collar. Tracking/defense.','Rowan Mouse|Earn by returning crumb-hoard. Tiny keys.','Cloud Moth|Earn by guiding to starlight. Soft light.','Thistle Hedgehog|Earn by saving from boot-trap. Danger sense.']),
('Monster/NPC cards', ['Wet Fox Guide|Wants dry socks; knows hidden arches.','Redcap Sneak|Wants shiny bells; stops for safer joke.','Black Bog Drake|Wants poisoned pool cleansed; hates clean lantern-light.','Border Warg|Wants collar broken; can become ally.','Draugr Oath-Raider|Wants broken ship oath finished.','Iron Crow Swarm|Wants a secret; bargains for true names.','Albion Tax-Mage|Wants names/maps/taxes; stopped by true-name song.','Storm-Berserker|Wants fair challenge and respect.','Bridge That Forgot|Wants its true name sung.']),
('Quest and reward cards', ['Find the Moon-Bell|Return it before moonset.','Break Red Wax|Clean a tax charm from a local place.','Guest-Right Feast|Win trust by sharing food and truth.','Storm Cairn Oath|Return an ancestor story.','Longship Lantern|Learn why a ghost crew still rows.','Bridge-Friend|Roads and bridges answer one question.','Clan Respect|+1 with storm-clans after fair action.','Fairy Favor|Ask one small courtly help.','Map Mark|Add a discovered safe route.']),
('Condition cards', ['Muddy|-1 Agility until cleaned or dried.','Startled|-1 until soothed by friend/song/snack.','Tangled|Need help or check to move freely.','Sleepy|Slow; fresh air or tea helps.','Inspired|+1 to next brave/helpful action.','Oathbound|Must keep a clear promise.','Glittered|Easy to track; pretty but inconvenient.','Lost|Need clue, map, or guide.','Boss Phase|Scene changes; reveal true want.'])
]
for title, cards in card_sets:
    pc.text_page(title, "<div class='print-card-grid'>" + ''.join([illustrated_print_card(c.split('|')[0], c.split('|')[1]) for c in cards]) + "</div>", columns=False)
pc.write()

# Extra guide section, atlas, progression, and choices inserted as small companion books/pages.
gx = Book("guide-extra", "Guide Extra", "Running young Adventurers, safety, pacing, page flipping, and table-play QA notes", "bg-tiny-tables.png")
gx.cover_page()
gx.text_page("Running young Adventurers", f"""
{split('<h3>Keep turns short</h3>'+ul(['Ask one concrete question at a time.','Let pointing at art count as an answer.','Rotate spotlight after one idea and one roll.','Offer two choices when players freeze.'])+rb('<strong>Best prompt:</strong> “What do you try, and who helps?”'), '<h3>Scary but safe</h3>'+ul(['Describe sound, weather, shadow, and size before danger.','Never trap a player in hopelessness.','Show a counter: true name, light, oath, kindness, broken collar.','At 0 HP use rescue, rest, bargain, or lost gear.']))}
""", columns=False)
gx.text_page("Table-play QA checklist", f"""
<div class='quick-grid'>{card('Before play', ul(['Print quickstart, map, character, cards.','Pick one adventure and three monsters.','Read boxed text once.']))}{card('During play', ul(['Mark where page flipping slows you.','Circle unclear rules.','Star pages that need more art.']))}{card('After play', ul(['Ask each Adventurer their favourite picture.','Ask which rule was confusing.','Write one new pet/mount hook.']))}{card('Fix pass', ul(['Simplify wording.','Move repeated rules to cards.','Add art to blank zones.','Turn dead prose into table tools.']))}</div>
""", columns=False)
gx.write()

atlas = Book("alba-atlas", "Alba Atlas", "Regions, clan lands, fairy courts, Norse sea routes, Dominion border, towns, dungeons, and legends", "alba-regional-map.png")
atlas.cover_page()
atlas.art_page("alba-regional-map.png", "Atlas map of Alba", "Use as a living map; name places when Adventurers discover them.")
atlas.text_page("Regions, roads, and routes", f"""
<table><tr><th>Place</th><th>Look</th><th>Hooks</th></tr><tr><td>Heatherhigh Hills</td><td>purple slopes, cairns, storm goats</td><td>oath ghosts, giant crowns, clan challenges</td></tr><tr><td>Glass Loch</td><td>moon water, kelp paths, seal songs</td><td>selkie bargains, serpent bridges, drowned bells</td></tr><tr><td>Northern Whale-Road</td><td>mist, longships, black rocks</td><td>trade, raids, draugr oaths</td></tr><tr><td>Red Banner Border</td><td>forts, roads, tax chains</td><td>Albion patrols, false maps, freed wargs</td></tr><tr><td>Thistlewood</td><td>brambles, fairy doors, fox tracks</td><td>redcaps, lost paths, court bargains</td></tr></table>
""", columns=False)
atlas.text_page("Factions and reputation", f"""
<table><tr><th>Faction</th><th>Wants</th><th>Reputation reward</th></tr><tr><td>Rowan Compact</td><td>promises remembered</td><td>safe fairy passage</td></tr><tr><td>Storm-Clans</td><td>respect, guest-right, returned cauldron</td><td>shelter and cairn goat hook</td></tr><tr><td>Norse Sea-Kin</td><td>trade, honor, settled oaths</td><td>ship passage and rune repairs</td></tr><tr><td>Dominion of Albion</td><td>taxes, maps, obedience</td><td>villain faction; defectors can help</td></tr><tr><td>Thorn Court</td><td>pranks, bargains, old laws</td><td>charms with exact promises</td></tr></table>
""", columns=False)
atlas.text_page("Towns, dungeons, and legends", f"""
<div class='quick-grid'>{card('Kettleford', p('Bridge town with toll bells, goat laws, and a market that moves in rain.'))}{card('Alba-Brae', p('Warm village with crooked clocktower and a guild of useful string.'))}{card('Root Warrens', p('Dungeon under Thistlewood: jam doors, mice, bells, redcap tunnels.'))}{card('Storm Cairn', p('Old burial hill where thunder answers broken promises.'))}{card('Loch Shrine', p('Moon-water shrine watched by selkies and glass serpents.'))}{card('Red Wall Fort', p('Dominion border fort with tax-magic and nervous local guides.'))}</div>
""", columns=False)
atlas.write()

# Printable table aids
ta = Book("table-aids", "Printable Table Aids", "Cards, tokens, trackers, and quick references for the table", "table-aids.png")
ta.cover_page()
ta.art_page("table-aids.png", "Table tools", "Print, cut, and use these at the table for faster play.")
ta.text_page("Spell cards", f"""
<div class='card-grid'>
{card('Glow-Pebble', p('0 MP. Make candlelight for one scene.'))}
{card('Mist Step', p('1 MP. Slip past a watcher, root, or trap.'))}
{card('Shield of Thistles', p('1 MP. Protect a friend from 2 HP of trouble.'))}
{card('Kind Whisper', p('0 MP. Help a creature name its feeling.'))}
{card('Rune Read', p('1 MP. Ask one question about old writing.'))}
{card('Foxfire Path', p('1 MP. Find the gentlest route.'))}
</div>
""", columns=False)
ta.text_page("Item and coin cards", f"""
<div class='card-grid'>
{card('Rope', p('+1 when climbing, tying, or rescuing.'))}
{card('Lantern', p('Reveal one clue before a dark-scene roll.'))}
{card('Tiny toolkit', p('Allows Int checks on small devices.'))}
{card('Oat pouch', p('+1 Wis with hungry animals.'))}
{card('Copper / Silver / Gold / Mythral', p('10 copper = 1 silver. 10 silver = 1 gold. 100 gold = 1 mythral.'))}
{card('Promise Button', p('Ask for one Luck clue when a promise matters.'))}
</div>
""", columns=False)
ta.text_page("Condition and initiative tents", f"""
<table><tr><th>Tent</th><th>Front</th><th>Back note</th></tr><tr><td>Hero turn</td><td>What do you try?</td><td>Pick stat after idea.</td></tr><tr><td>Tangled</td><td>Need help to move.</td><td>Ends with help/check.</td></tr><tr><td>Startled</td><td>-1 until soothed.</td><td>Kind words end it.</td></tr><tr><td>Sleepy</td><td>Slow but okay.</td><td>Snack/song/fresh air.</td></tr><tr><td>Boss phase</td><td>Scene changes.</td><td>Reveal true want.</td></tr></table>
""", columns=False)

ta.text_page("Potion, poison, and enchantment cards", f"""
<div class='card-grid'>
{card('Heatherheart Draught', p('Potion. Regain 3 HP and ignore Startled once.'))}
{card('Loch-Breath Sip', p('Potion. Breathe underwater for one calm scene.'))}
{card('Foxwit Tea', p('Potion. +1 Int for riddles, runes, and traps.'))}
{card('Nightshade Jam', p('Poison. Sleepy until bitter tea or warm song.'))}
{card('Black Bog Venom', p('Poison. -1 Agility until washed in running water.'))}
{card('Wake Charm', p('Enchanting spell. Ask a magic item what it wants.'))}
</div>
""", columns=False)
ta.art_page("alba-regional-map.png", "Printable regional map", "Use for routes, factions, borders, and campaign travel.")
ta.art_page("alba-town-dungeon-map.png", "Printable town/dungeon map", "Use for village, keep, cave, loch shrine, tower, and fairy mound encounters.")
ta.write()



# West Marches setting and quest notice board
wm = Book("west-marches", "West Marches of Alba", "Open-table frontier adventures, safe exploration turns, printable notice board, and quest cards", "true-unique/cron-v3/west-marches-notice-board.png")
wm.cover_page()
wm.art_page("alba-frontier-map.png", "The West Marches", "A frontier sandbox: choose a notice, mark a route, explore one place, and return home with a story.")
wm.text_page("How West Marches play works", f"""
{split('<h3>One safe home base</h3>'+p('The hearth-town of Kettleford is where each session starts and ends. The notice board gives choices, but the Guide only needs one chosen quest ready.')+ul(['Pick one notice from the board.', 'Ask the party which route they take.', 'Run three exploration turns.', 'Bring everyone home before bedtime.']), '<h3>Exploration turn</h3>'+table if False else '<table><tr><th>Step</th><th>Question</th></tr><tr><td>1. Look</td><td>What do the Adventurers notice in the art or map?</td></tr><tr><td>2. Choose</td><td>Careful, normal, or brave shortcut?</td></tr><tr><td>3. Meet</td><td>Creature, clue, weather, or local helper?</td></tr><tr><td>4. Mark</td><td>Add a sticker, path, friend, danger, or treasure to the map.</td></tr></table>'+rb('<strong>West Marches rule:</strong> no quest is mandatory; players choose the next notice.'))}
""", columns=False)
wm.text_page("Printable quest notice board", f"""
<h3>Cut out or pin this page</h3>
<div class='print-card-grid'>
{illustrated_print_card('Lost Bell at Moon Loch','Reward: Moon-water vial. Route: reeds and stepping stones. Danger: worried kelpie foal.')}
{illustrated_print_card('Red Wax on the Toll Gate','Reward: Bridge-Friend badge. Route: south road. Danger: tax-mage echo.')}
{illustrated_print_card('Goat Bell in Storm Cairn','Reward: cairn goat bond. Route: high path. Danger: oath thunder.')}
{illustrated_print_card('Longship Lantern','Reward: sea-token map. Route: north coast. Danger: draugr oath.')}
{illustrated_print_card('Fox Map in Thistlewood','Reward: safe route mark. Route: bramble path. Danger: redcap bargain.')}
{illustrated_print_card('Potion Garden Rescue','Reward: heatherheart draught recipe. Route: bog edge. Danger: sleepy nightshade jam.')}
</div>
""", columns=False)
for title, body in [
('Quest: Lost Bell at Moon Loch', '<h3>Scenes</h3>'+ul(['Meet Fia the kelpie foal at the wet stones.','Follow silver bubbles through a reed maze.','Open the humming gate with a promise.'])+'<h3>NPCs</h3>'+ul(['Fia: scared but brave if praised.','Auntie Reed: slow, formal, hates grabbing.','Bubble-Nose Trout: wants to be paid in compliments.'])+'<h3>Encounter</h3><p>Rising water makes choices urgent. Rope, song, stepping stones, or animal friendship all work.</p>'),
('Quest: Red Wax on the Toll Gate', '<h3>Scenes</h3>'+ul(['Spot red wax on Kettleford gate.','Question villagers without scaring them.','Wash the false-tax charm while the echo complains.'])+'<h3>NPCs</h3>'+ul(['Nessa Toll-Keeper: nervous ledger keeper.','Tax-Mage Echo: bossy spell that repeats old orders.','Goat Mungo: chewing evidence.'])+'<h3>Encounter</h3><p>The echo tries to rename the bridge. True names, water, songs, and proof break it.</p>'),
('Quest: Goat Bell in Storm Cairn', '<h3>Scenes</h3>'+ul(['Climb heather hills in wind.','Hear thunder answer wrong promises.','Return the bell to a cairn goat without waking the wight.'])+'<h3>NPCs</h3>'+ul(['Pebblehorn Goat: stubborn, hungry, honorable.','Old Duthac: poet guide.','Cairn Wight: scary but fair.'])+'<h3>Encounter</h3><p>Hold a cloak rope, speak an oath, and choose whether to bargain or sneak.</p>'),
('Quest: Longship Lantern', '<h3>Scenes</h3>'+ul(['Find a blue lantern on an empty longship.','Trade clues at the harbor market.','Carry the lantern to the sea cave before tide turns.'])+'<h3>NPCs</h3>'+ul(['Jorunn Wave-Smith: friendly trader.','Skull-Sail Rurik: loud rival.','Draugr Rowers: want oath finished.'])+'<h3>Encounter</h3><p>Fog, rowing sounds, and a rising tide. Peace, trade, and oath-work beat fighting.</p>')]:
    img = make_unique_scene_asset('west-quest-'+title.lower().replace(':','').replace(' ','-')+'.svg', title, 'quest')
    wm.art_text_page(title, body, image=img, side='right', columns=False)
wm.write()

# Dedicated gear/items/potions/poisons book
gear = Book("gear-items-potions", "Gear, Items, Potions and Poisons", "Dedicated equipment catalogue with illustrated object cards, prices, recipes, and table use", "true-unique/cron-v3/gear-potions-still-life.png")
gear.cover_page()
gear.art_text_page("Gear that changes scenes", f"""
{split('<h3>Starter gear shelves</h3><table><tr><th>Item</th><th>Cost</th><th>Use</th></tr><tr><td>Rope with ribbon knots</td><td>5 copper</td><td>+1 climbing/rescue when someone holds the end.</td></tr><tr><td>Lantern with beetle glass</td><td>8 copper</td><td>Reveal one clue before a dark roll.</td></tr><tr><td>Tiny toolkit</td><td>1 silver</td><td>Try Int checks on locks, carts, toys, traps.</td></tr><tr><td>Oat pouch</td><td>2 copper</td><td>+1 Wis with hungry animals.</td></tr></table>', '<h3>Gear scenes</h3>'+ul(['Rope makes teamwork visible: one climbs, one holds, one watches.','Lanterns should show clues, not just remove darkness.','Tools let small hands fix things instead of smash them.','Food is social magic: it starts conversations.'])+rb('<strong>Rule:</strong> gear gives +1 only when the player describes how it helps.'))}
""", image="item-gear-sheet.png", side="right", columns=False)
gear.art_text_page("Magic items", f"""
<div class='card-grid'>
{card('Rowan-Bark Shield', p('Reduces thorn, arrow, or fear trouble by 2 HP. Wants to protect someone smaller.'))}
{card('Loch-Mirror Cloak', p('+1 to sneak in mist or moonlight. Shows the wearer one honest reflection.'))}
{card('Cairn-Knuckle Ring', p('+1 to hold, lift, or remember an oath. Heavy when lies are near.'))}
{card('Star-Moth Lantern', p('Reveals invisible ink, ghost tracks, and shy fairies if spoken to politely.'))}
{card('Mythral Seed Blade', p('Cuts curses and refuses cruelty. It becomes dull if used to bully.'))}
{card('Bridge-Friend Badge', p('Roads and bridges answer one practical question per adventure.'))}
</div>
""", image="item-magic-sheet.png", side="left", columns=False)
gear.art_text_page("Potions and poisons", f"""
<table><tr><th>Name</th><th>Kind</th><th>Effect</th><th>Cure/cost</th></tr><tr><td>Heatherheart Draught</td><td>Potion</td><td>Regain 3 HP; ignore Startled once.</td><td>Needs heather honey and kind words.</td></tr><tr><td>Loch-Breath Sip</td><td>Potion</td><td>Breathe underwater for one calm scene.</td><td>Cannot shout until dry.</td></tr><tr><td>Foxwit Tea</td><td>Potion</td><td>+1 Int for riddles, runes, traps.</td><td>Must answer one question honestly.</td></tr><tr><td>Nightshade Jam</td><td>Poison</td><td>Sleepy until bitter tea or warm song.</td><td>Bitter tea, fresh air, friend song.</td></tr><tr><td>Black Bog Venom</td><td>Poison</td><td>-1 Agility until washed in running water.</td><td>Clean stream or moon-water vial.</td></tr><tr><td>Iron Crow Ink</td><td>Poison</td><td>Cannot speak a lie until one useful truth.</td><td>Tell the truth that helps someone.</td></tr></table>
""", image="item-potions-poisons-sheet.png", side="right", columns=False)
gear.text_page("Illustrated item cards", "<div class='print-card-grid'>" + ''.join([illustrated_print_card(n,t) for n,t in [('Rope with ribbon knots','+1 to climb/rescue when a friend holds the end.'),('Beetle-glass lantern','Reveal one clue before a dark roll.'),('Tiny toolkit','Allows Int checks on small devices.'),('Oat pouch','+1 Wis with hungry animals.'),('Rowan-Bark Shield','Reduce one thorn/arrow/fear trouble by 2 HP.'),('Star-Moth Lantern','See invisible ink or ghost tracks.'),('Heatherheart Draught','Regain 3 HP; ignore Startled once.'),('Black Bog Venom','Poison: -1 Agility until washed.'),('Promise Button','Ask for one Luck clue.')]]) + "</div>", columns=False)
gear.write()

# Dedicated mounts and pets book
mp = Book("mounts-and-pets", "Mounts and Pets", "Story-earned companions, bond tracks, quests, care scenes, and printable companion cards", "true-unique/mounts-and-pets/companion-opener.png")
mp.cover_page()
mp.art_text_page("Companions are earned friends", f"""
{split('<h3>Bond rule</h3><table><tr><th>Bond</th><th>Trust</th><th>Unlock</th></tr><tr><td>1</td><td>Trusts the party.</td><td>+1 once per session when cared for.</td></tr><tr><td>2</td><td>Comes when called.</td><td>Carry message/small item.</td></tr><tr><td>3</td><td>Chooses the heroes.</td><td>Return dramatically once per campaign.</td></tr></table>', '<h3>Care scenes</h3>'+ul(['Feed: oats, berries, warm milk, moon-water, or story.','Rest: companions need safe sleep too.','Respect: ask before riding magical creatures.','Job: every companion wants a useful role.'])+rb('<strong>No punishment:</strong> if a pet is threatened, offer a rescue choice, not a cruel scene.'))}
""", image="true-unique/mounts-and-pets/companion-bond-care.png", side="right", columns=False, extra_cls='art-text-strong')
for title, txt, img in [
('Highland Pony', 'Earn by freeing it from bog rope. Helps travel, carrying, and brave parade entrances. Likes oat cakes and steady voices.', 'true-unique/mounts-and-pets/mount-pet-highland-pony.png'),
('Cairn Goat', 'Earn by finding its lost bell. Helps climbing, stubborn pushing, and storm-path warnings. Likes hill songs.', 'true-unique/mounts-and-pets/mount-pet-cairn-goat.png'),
('Fairy Stag', 'Earn by protecting its grove. Fast travel once per adventure. Will not carry anyone who breaks a promise.', 'true-unique/mounts-and-pets/mount-pet-fairy-stag.png'),
('Kelp-Mane Pony', 'Earn by returning a moon-water charm. Carries careful riders across lochs. Needs polite asking.', 'true-unique/mounts-and-pets/mount-pet-kelp-mane-pony.png'),
('Rowan Owl', 'Earn by solving its old-name riddle. Gives night warnings and sees red wax in the dark.', 'true-unique/mounts-and-pets/mount-pet-rowan-owl.png'),
('Border Warg', 'Earn by breaking its command collar. Tracks danger and protects friends. Needs trust after fear.', 'true-unique/mounts-and-pets/mount-pet-border-warg.png'),
('Rowan Mouse', 'Earn by returning crumb-hoard. Helps tiny keys, hiding, and finding snack-sized clues.', 'true-unique/mounts-and-pets/mount-pet-rowan-mouse.png'),
('Cloud Moth', 'Earn by guiding it to starlight. Gives soft light and gentle weather hints.', 'true-unique/mounts-and-pets/mount-pet-cloud-moth.png'),
('Thistle Hedgehog', 'Earn by saving it from a boot-trap. Notices danger and curls into a tiny shield.', 'true-unique/mounts-and-pets/mount-pet-thistle-hedgehog.png')]:
    mp.art_text_page(title, '<div class="card-grid">'+card('How to earn', p(txt))+card('Care promise', p('Name one food, one comfort, and one job this companion enjoys.'))+card('Adventure hook', p('Someone else wants the companion for the wrong reason; prove kindness works better.'))+card('Table help', p('+1 only when the companion’s special talent clearly matters and the party cared for it.'))+'</div>', image=img, side='right', columns=False, extra_cls='art-text-strong')
def companion_card(label: str, text: str, img: str) -> str:
    return f"<div class='print-card'><img class='card-illo' src='../art/generated/true-unique/mounts-and-pets/cards/{img}' alt='{esc(label)} unique card art'><h3>{label}</h3><p>{text}</p></div>"
mp.art_text_page("Printable companion cards", "<div class='print-card-grid'>" + ''.join([companion_card(n,t,i) for n,t,i in [
    ('Highland Pony','Travel/carrying. Earn: free from bog rope.','highland-pony-card.png'),
    ('Cairn Goat','Climbing. Earn: find lost bell.','cairn-goat-card.png'),
    ('Fairy Stag','Fast travel. Earn: protect grove.','fairy-stag-card.png'),
    ('Kelp-Mane Pony','Loch crossing. Earn: return moon charm.','kelp-mane-pony-card.png'),
    ('Rowan Owl','Night warning. Earn: old-name riddle.','rowan-owl-card.png'),
    ('Border Warg','Tracking/defense. Earn: break collar.','border-warg-card.png'),
    ('Rowan Mouse','Tiny keys. Earn: return crumbs.','rowan-mouse-card.png'),
    ('Cloud Moth','Soft light. Earn: guide to stars.','cloud-moth-card.png'),
    ('Thistle Hedgehog','Danger sense. Earn: save from trap.','thistle-hedgehog-card.png')]]) + "</div>", image='true-unique/mounts-and-pets/companion-card-table-bg.png', side='full', columns=False, extra_cls='art-text-strong')
mp.write()

# Expanded atlas with area-specific art and lore
atlas2 = Book("alba-atlas-expanded", "Alba Atlas Expanded", "Every major area with location, unique art, factions, history, folklore, and adventure hooks", "alba-regional-map.png")
atlas2.cover_page()
atlas2.art_page("alba-regional-map.png", "Expanded map of Alba", "Each region below has its own page, art, factions, folklore, and play hooks.")
for name, location, factions, folklore, hooks in [
('Heatherhigh Hills','West-central Alba above Kettleford, between Storm Cairn and the old goat roads.','Storm-Clans, cairn goats, oath poets, hidden Rowan Compact messengers.','Thunder is said to be old chiefs arguing until someone remembers the exact promise.','lost goat bell; oath ghost; storm-clan fair challenge; mythral spring rumor'),
('Glass Loch','Northern lowlands where moon-water gathers beneath seal roads and kelp paths.','Selkie families, kelpie foals, loch herbalists, glass serpent guardians.','The loch reflects not faces but promises; a liar sees an empty sky.','moon-bell rescue; underwater shrine; serpent bridge; stolen seal-cloak'),
('Northern Whale-Road','Cold sea lanes and skerries north of Skerryvik harbor.','Norse Sea-Kin, draugr oath-raiders, whale singers, harbor traders.','Blue lanterns mark ships whose crews still owe one last kindness.','empty longship; ghost oars; feast-right bargain; storm-knot duel'),
('Red Banner Border','Southern forts, tax roads, and measured fields where Albion pushes north.','Dominion officials, defecting guides, Redcloak patrols, freed border wargs.','The red banner steals place-names first; people vanish only after maps are changed.','tax charm; false map; iron collar; banner true-name ritual'),
('Thistlewood','Eastern fairy wood between Alba-Brae and the hidden Thorn Court gates.','Thorn Court, redcaps, fox guides, brownie helpers, myceling scouts.','Every bramble has a door, but only polite knockers learn which door is theirs.','redcap bargain; moving road; fox map; tiny court trial'),
('Cauldron Pass','High northern pass from lowland farms to Queen Maev’s storm-clan halls.','Storm-clans, Queen Maev, Albion spies, cairn wights.','A stolen feast cauldron can make a whole valley forget guest-right.','returned cauldron; fair duel; ancestor story; pass of two banners'),
('Kettleford','Home-base bridge town on the road between loch, hills, woods, and border.','Toll-keepers, market aunties, bridge spirits, young adventurers.','The bridge was built by a giant child who wanted everyone to get home dry.','notice board; toll bell; market mystery; grumpy bridge'),
('Root Warrens','Dungeon tangle under Thistlewood, full of jam doors, mouse paths, and bell roots.','Redcaps, rowan mice, root goblins, Buttonroot elders.','Roots remember every footstep and repeat rude words until someone apologises.','lost crumbs; jam lock; redcap tunnel; bedtime song root')]:
    body = '<div class="card-grid">'+card('Location in wider Alba', p(location))+card('Factions', p(factions))+card('History or folklore', p(folklore))+card('Adventure hooks', p(hooks))+'</div><h3>Local table</h3><table><tr><th>d6</th><th>Discovery</th></tr><tr><td>1</td><td>A friendly local asks for help before danger appears.</td></tr><tr><td>2</td><td>A faction mark points to a secret path.</td></tr><tr><td>3</td><td>Old folklore explains a safe solution.</td></tr><tr><td>4</td><td>Weather changes the route.</td></tr><tr><td>5</td><td>A pet or mount notices the real clue.</td></tr><tr><td>6</td><td>A reward becomes tomorrow’s notice-board quest.</td></tr></table>'
    img = make_unique_scene_asset('atlas-area-'+name.lower().replace(' ','-')+'.svg', name, 'atlas')
    atlas2.art_text_page(name, body, image=img, side='right', columns=False)
atlas2.write()

# Plain markdown notes for repo browsing
for slug, title in [(ph.slug, ph.title), (gm.slug, gm.title), (be.slug, be.title), (ca.slug, ca.title), (sheet.slug, sheet.title), (am.slug, am.title), (sg.slug, sg.title), (tc.slug, tc.title), (b2.slug, b2.title), (ta.slug, ta.title), (qs.slug, qs.title), (pc.slug, pc.title), (gx.slug, gx.title), (atlas.slug, atlas.title), (wm.slug, wm.title), (gear.slug, gear.title), (mp.slug, mp.title), (atlas2.slug, atlas2.title)]:
    (BOOKS / f"{slug}.md").write_text(f"# {title}\n\nSee `printable-a4/{slug}-a4.html` and `pdf/{slug}.pdf`.\n", encoding="utf-8")

# low-ink quickstart/cards variants
for slug in ['quickstart-pack','printable-cards']:
    src = PRINT / f'{slug}-a4.html'
    if src.exists():
        txt = src.read_text(encoding='utf-8')
        txt = txt.replace('<main class="book">', '<main class="book low-ink">')
        (PRINT / f'{slug}-low-ink-a4.html').write_text(txt, encoding='utf-8')

# Final artwork pass across every generated HTML, including low-ink variants
# and style-proof HTML that may pre-exist in printable-a4/. Exact src reuse and
# any legacy SVG/shape placeholder source are replaced with real raster artwork.
seen_final = {}
seen_final_serial = 0
for html_path in sorted(PRINT.glob('*-a4.html')):
    txt = html_path.read_text(encoding='utf-8')
    def repl_final(m):
        global seen_final_serial
        quote = m.group(1)
        src = m.group(2)
        n = seen_final.get(src, 0)
        seen_final[src] = n + 1
        seen_final_serial += 1
        derivative_src = any(flag in src for flag in ['/real/no-reuse-', '/real/final-no-reuse-', '/wash/real/', '/real/cards/card-', '/wash/bg-', '/wash/item-', '/wash/kindred-'])
        legacy_shape_src = src.endswith('.svg') or '/unique/' in src or derivative_src
        if n == 0 and not legacy_shape_src:
            return f'src={quote}{src}{quote}'
        title = Path(src).stem.replace('card-', '').replace('final-no-reuse-', '').replace('no-reuse-', '').replace('-', ' ').title()
        filename = f"true-unique-{html_path.stem}-{seen_final_serial:03d}-{stable_seed(src+html_path.name+str(n)) & 0xffff:04x}.png"
        rel = make_unique_scene_asset(filename, title, 'scene')
        return f'src={quote}../art/generated/{rel}{quote}'
    txt = re.sub(r"src=(['\"])(\.\./art/generated/[^'\"]+)\1", repl_final, txt)
    html_path.write_text(txt, encoding='utf-8')

print('built book HTML files:', ', '.join(sorted(p.name for p in PRINT.glob('*-a4.html'))))
