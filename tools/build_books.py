#!/usr/bin/env python3
"""Build the first complete Thistlebright RPG book set.

Original child-friendly tabletop content. The D&D PHB reference is used only for
broad bookcraft/style principles; this script does not copy text, art, rules, or
trade dress.
"""
from __future__ import annotations
from pathlib import Path
import textwrap

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
.mini-card { break-inside:avoid-page; page-break-inside:avoid; margin:2mm 0; padding:2.3mm 2.8mm; background:rgba(255,251,239,.72); border:1px solid rgba(184,138,45,.42); }
.columns > .option-card { min-height:62mm; }
.columns > .creature { min-height:58mm; }
.option-card, .rulebox, .readaloud, .questbox, .creature, .sheet-box { break-inside:avoid-page; page-break-inside:avoid; padding:3mm; background:linear-gradient(180deg, rgba(255,251,239,.94), rgba(242,226,187,.78)); border:1px solid rgba(154,116,55,.55); box-shadow:inset 0 0 0 1px rgba(255,255,255,.38); }
.option-card h3, .creature h3 { margin-top:0; }
.rulebox, .readaloud { margin:2.6mm 0; border-left:2.2mm solid rgba(86,51,109,.66); }
.questbox { margin:2.8mm 0; border-left:2.2mm solid rgba(40,87,64,.75); }
.small { font-size:8.8pt; color:var(--muted); }
.big-stat { font-size:20pt; color:#74322d; letter-spacing:.04em; }
table { width:100%; border-collapse:collapse; margin:2.2mm 0 3mm; font-size:8.6pt; break-inside:avoid-page; }
th,td { border:1px solid #c8ac72; padding:2mm 1.8mm; vertical-align:top; } th { background:#dfd0a4; color:#263b2e; } tr:nth-child(even) td { background:rgba(235,222,184,.58); }
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
.feature-box { break-inside:avoid-page; min-height:38mm; padding:3mm; background:rgba(255,251,239,.72); border:1px solid rgba(184,138,45,.42); }
.feature-box h3 { margin-top:0; font-size:12pt; }
.feature-quote { margin-top:3mm; padding:3mm; background:rgba(86,51,109,.10); border-left:2mm solid rgba(86,51,109,.65); font-style:italic; }
.statline { display:grid; grid-template-columns:repeat(5,1fr); gap:1.5mm; margin:2mm 0 3mm; }
.stat { text-align:center; padding:1.7mm 1mm; background:#ead9ad; border:1px solid #b9954d; font-size:8.5pt; }
.stat strong { display:block; color:#6f2d29; font-size:10pt; }
.shop table, .spell-list table { font-size:8.2pt; }
.creature-feature .feature-art { height:142mm; }
.creature-feature .feature-box { min-height:31mm; }
.sheet-page .page { padding:11mm 13mm 18mm; }
.sheet { display:grid; grid-template-columns:1fr 1fr; gap:3.2mm; }
.sheet-box { min-height:17mm; }
.sheet-box.big { min-height:44mm; }
.sheet-box.tall { min-height:62mm; }
.line { border-bottom:1px solid #836a42; min-height:7mm; margin-top:2mm; }
.badge { display:inline-block; padding:.8mm 2mm; margin:.4mm .8mm .4mm 0; background:#ead9ad; border:1px solid #b9954d; border-radius:4mm; font-size:8.5pt; }
.toc li { margin:1.2mm 0; }
'''

def art(name: str) -> str:
    return f"../art/generated/{name}"

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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
        self.pages.append(f'''<section class="page full-bleed"><img class="bg" src="{art(self.cover)}" alt="{esc(self.title)} cover"><div class="scrim"></div><div class="title-panel"><h1>{esc(self.title)}</h1><p>{esc(self.subtitle)}</p></div><div class="overlay"><h3>Thistlebright Adventures</h3><p>Scottish fairy myth, high fantasy, safe wonder, and table rules made for brave young players.</p></div></section>''')
    def art_page(self, image: str, heading: str, text: str):
        p = self.page_no()
        self.pages.append(f'''<section class="page full-bleed"><img class="bg" src="{art(image)}" alt="{esc(heading)}"><div class="scrim"></div><div class="overlay"><h2>{esc(heading)}</h2><p>{esc(text)}</p></div><div class="page-number">{p}</div></section>''')
    def text_page(self, title: str, body: str, columns=True):
        p = self.page_no()
        cls = 'columns' if columns else ''
        self.pages.append(f'''<section class="page"><h2 class="section">{esc(title)}</h2><div class="{cls}">{body}</div><div class="page-number">{p}</div></section>''')
    def feature_page(self, kicker: str, title: str, image: str, intro: str, body: str):
        p = self.page_no()
        self.pages.append(f'''<section class="page feature-page"><div class="feature-top"><figure class="feature-art"><img src="{art(image)}" alt="{esc(title)} illustration"></figure><div class="feature-intro"><div class="feature-kicker">{esc(kicker)}</div><h2>{esc(title)}</h2><p class="drop">{intro}</p></div></div>{body}<div class="page-number">{p}</div></section>''')
    def creature_page(self, title: str, image: str, intro: str, stats: dict, body: str):
        p = self.page_no()
        stat_html = '<div class="statline">' + ''.join(f'<div class="stat"><strong>{k}</strong>{v:+d}</div>' for k,v in stats.items()) + '</div>'
        self.pages.append(f'''<section class="page feature-page creature-feature"><div class="feature-top"><figure class="feature-art"><img src="{art(image)}" alt="{esc(title)} creature art"></figure><div class="feature-intro"><div class="feature-kicker">Creature stat block</div><h2>{esc(title)}</h2><p class="drop">{intro}</p>{stat_html}</div></div>{body}<div class="page-number">{p}</div></section>''')
    def write(self):
        html = '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(self.title)+'</title><style>'+CSS+'</style></head><body><main class="book">' + '\n'.join(self.pages) + '</main></body></html>'
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
ph = Book("player-handbook", "Player Handbook", "Character creation, simple rules, kindreds, jobs, spells, gear, and a worked example", "01-cover.png")
ph.cover_page()
ph.text_page("How to use this book", f"""
{split(
'''<ol class='toc'><li>Choose who helps as the Guide.</li><li>Make a hero in five easy steps.</li><li>Use Strength, Int, Agility, Wis, or Luck when a roll is exciting.</li><li>Keep the story warm: heroes can be muddy, surprised, or silly, but never shamed.</li></ol>''' + spot('02-part-opener.png', '<strong>Table feel:</strong> point at the picture, ask what the hero notices, then roll only when it is exciting.'),
rb('<strong>For ages 5–7:</strong> read choices aloud, let children point to pictures, and use small bonuses (+2, +1, +0) instead of lots of maths.') + '''<h3>What you need</h3>''' + ul(['One six-sided die.', 'A pencil, character sheet, and three little counters.', 'A grown-up or older sibling Guide.', 'A promise to listen and take turns.']) + '''<h3>What players say</h3>''' + ul(['“I help.”', '“I try the brave thing.”', '“Can I talk to it?”', '“I look closer.”', '“Can my friend help?”']) + mini('First table promise', 'Every player gets a turn to say one idea before the dice decide anything.')
)}
""", columns=False)
ph.art_page("02-part-opener.png", "Welcome to the glen", "Tiny bells ring beneath the heather. A fairy guide invites the heroes to help a magical place without making the rules too big.")
ph.text_page("The easy dice rule", f"""
{split(
'''<p class='drop'>When the answer is obvious, no roll is needed. When everyone leans forward and wonders what might happen, roll one six-sided die and add the hero's matching stat bonus.</p><table><tr><th>Total</th><th>Result</th><th>Say it like this</th></tr><tr><td>1–3</td><td>Wobble</td><td>It goes wrong in a funny, safe, or messy way.</td></tr><tr><td>4–5</td><td>Yes, but...</td><td>It works, and there is a tiny cost or choice.</td></tr><tr><td>6+</td><td>Bright success</td><td>It works well, and the hero feels proud.</td></tr></table>''' + rb('<strong>No failure spiral:</strong> a wobble changes the scene; it does not stop the adventure.'),
'''<h3>The five classic stats</h3>''' + ul(['<strong>Strength</strong> — lifting, climbing, holding, pushing, protecting.', '<strong>Int</strong> — puzzles, facts, plans, reading runes, remembering.', '<strong>Agility</strong> — sneaking, dodging, catching, balancing, jumping.', '<strong>Wis</strong> — feelings, animals, nature, noticing, sensible choices.', '<strong>Luck</strong> — charms, surprises, odd magic, last-chance moments.']) + '''<h3>When not to roll</h3>''' + ul(['The action is safe and obvious.', 'A child is only describing how they look or feel.', 'The group already found a kind solution.', 'A roll would slow a warm moment.']) + mini('Helping rule', 'If another hero clearly helps, add +1 or let the child roll again and choose the better die.')
)}
""", columns=False)
ph.text_page("Stat creation: classic five stats", f"""
{card('1. Strength', p('Lifting, climbing, holding, pushing, protecting.'))}
{card('2. Int', p('Puzzles, facts, plans, reading runes, remembering.'))}
{card('3. Agility', p('Sneaking, dodging, catching, balancing, jumping.'))}
{card('4. Wis', p('Feelings, animals, nature, noticing, sensible choices.'))}
{card('5. Luck', p('Charms, surprises, odd magic, last-chance moments.'))}
{rb('<strong>Assign bonuses:</strong> choose one best stat at <span class="big-stat">+2</span>, two good stats at <span class="big-stat">+1</span>, and two normal stats at <span class="big-stat">+0</span>.')}
{qa('<strong>Worked example:</strong> Rowan the Beast Friend has Wis +2, Agility +1, Luck +1, Strength +0, Int +0.')}
""", columns=False)
ph.art_page("03-race-kindreds.png", "Step 1: Pick your kindred", "Each kindred now has its own illustrated page. Let children point at the picture first, then read only the choices they need.")
kindreds = [
    dict(title='Glenfolk', image='kindred-glenfolk.png', intro='Glenfolk are croft, cottage, castle, and market-lane children with practical hearts. They know how to ask neighbours, find a dry path, and make ordinary things feel brave.', gift='Once per adventure, remember a local clue or helpful person.', look=['Tartan scarf, muddy boots, treasure pockets.', 'A wooden badge, snack cloth, or tiny family charm.'], table=['Ask an auntie, shepherd, baker, guard, or gardener for help.', 'Know what a tool is called or where a path should go.', 'Offer practical kindness: a snack, blanket, or fixed latch.'], prompt='“I know someone who might help.”'),
    dict(title='Thistle Fairy', image='kindred-thistle-fairy.png', intro='Thistle Fairies are small bright folk with manners, shimmer, and secret paths. They are excellent at noticing fairy marks that bigger people step over.', gift='Once per scene, notice nearby fairy magic.', look=['Petal cloak, star freckles, tiny crown.', 'Boots that never quite touch the puddles.'], table=['Ask flowers, moths, or beetles for tiny gossip.', 'Spot a hidden ring of mushrooms or a polite fairy door.', 'Remember an old rule of fairy manners.'], prompt='“I bow politely and look for the sparkle.”'),
    dict(title='Brownie Helper', image='kindred-brownie-helper.png', intro='Brownie Helpers are cozy fixers who tidy, mend, and improve small things. They turn a messy room, broken spoon, or squeaky hinge into a clue.', gift='Repair or improve one tiny object each scene.', look=['Apron, tool pouch, flour on nose.', 'Buttons, string, thimble hat, or polished spoon.'], table=['Fix a latch, mend a pouch, clean mud from a clue.', 'Find the important thing hiding in a pile of mess.', 'Make a worried home feel safe again.'], prompt='“I can fix the little thing first.”'),
    dict(title='Selkie-Born', image='kindred-selkie-born.png', intro='Selkie-Born heroes have gentle loch-hearts and moonlit dreams. They understand water, weather, and the soft feelings people hide under their coats.', gift='Understand water, weather, or a sad feeling.', look=['Soft seal-cloak, shell button, sea-glass charm.', 'Wet curls, quiet eyes, and pockets full of smooth stones.'], table=['Hear what rain, waves, or a puddle is trying to say.', 'Comfort a lonely creature without many words.', 'Find a safe way across shallow water.'], prompt='“I listen to the loch before I answer.”'),
    dict(title='Rowan-Kin', image='kindred-rowan-kin.png', intro='Rowan-Kin are forest children with leaf crowns and careful listening. Old trees remember them, birds trust them, and red berries mark their promises.', gift='Ask a tree, bird, or breeze for one hint.', look=['Red berries, green cloak, bark-pattern gloves.', 'Leaf crown, acorn buttons, or a walking twig.'], table=['Read bent grass, scratched bark, or a bird alarm.', 'Ask an old tree who passed this way.', 'Hide gently among leaves without frightening anyone.'], prompt='“I ask the old tree what it remembers.”'),
    dict(title='Heather Giantling', image='kindred-heather-giantling.png', intro='Heather Giantlings are small for giants, huge for fairies, and very gentle. They are best when something heavy, high, or frightening needs a careful friend.', gift='Lift, push, or carry one heavy thing safely.', look=['Big knitted jumper, pebble buttons, warm laugh.', 'Purple heather in hair and boots like little boats.'], table=['Hold a door, carry a tired friend, or move a fallen branch.', 'Stand calmly when a noise is big.', 'Ask hills, stones, or goats about family stories.'], prompt='“I can be big and gentle at the same time.”'),
]
kindred_stats = {'Glenfolk':'Int or Wis', 'Thistle Fairy':'Luck', 'Brownie Helper':'Int', 'Selkie-Born':'Wis', 'Rowan-Kin':'Wis or Agility', 'Heather Giantling':'Strength'}
kindred_scenes = {'Glenfolk':'A village gate is stuck and everyone has an idea.', 'Thistle Fairy':'A secret flower-door opens only after a polite greeting.', 'Brownie Helper':'A kitchen clue is hidden under a very silly mess.', 'Selkie-Born':'A sad loch-creature will only speak to someone gentle.', 'Rowan-Kin':'An old tree remembers the wrong name and needs patient listening.', 'Heather Giantling':'A fallen branch blocks the path, but small animals live underneath.'}
for k in kindreds:
    ph.feature_page('Kindred', k['title'], k['image'], k['intro'], feature_grid([
        ('Story gift', p(k['gift'])),
        ('Look', ul(k['look'])),
        ('Good at the table', ul(k['table'])),
        ('Best first stat', p(kindred_stats[k['title']])),
        ('First scene idea', p(kindred_scenes[k['title']])),
        ('Say this', f"<div class='feature-quote'>{k['prompt']}</div>"),
    ]))
ph.art_page("04-class-paths.png", "Step 2: Pick your adventure job", "Each job now has its own illustrated page. The job says what a hero likes doing when trouble appears.")
jobs = [
    dict(title='Thistle Knight', image='job-thistle-knight.png', intro='Thistle Knights protect friends and stand bravely at the front. They are not rough or bossy; they make scary moments feel safer for everyone.', gift='Once per scene, turn a scary moment into a brave one.', stat='Strength', tryit=['Hold a shield or walking stick like a promise.', 'Stand between danger and a friend.', 'Say a brave sentence out loud.'], kit=['Soft shield', 'Promise ribbon', 'Thistle badge'], prompt='“I stand tall so my friend can try.”'),
    dict(title='Loch Scout', image='job-loch-scout.png', intro='Loch Scouts find paths, listen for clues, and spot hidden doors. They love maps, footprints, bird calls, and the first tiny sign that something changed.', gift='Ask the Guide one “what do I notice?” question.', stat='Agility', tryit=['Follow tracks through reeds or heather.', 'Read a map or remember a landmark.', 'Balance across stepping stones.'], kit=['Chalk', 'String map', 'Tiny lantern'], prompt='“I look closely before we move.”'),
    dict(title='Song-Spark Bard', image='job-song-spark-bard.png', intro='Song-Spark Bards use music, jokes, and stories to lift everyone up. Their magic is cheer, rhythm, and the courage that comes from being heard.', gift='Give another hero +1 after a kind song, rhyme, joke, or cheer.', stat='Wis', tryit=['Cheer a friend who feels unsure.', 'Calm a crowd with a rhyme.', 'Make a grumpy bridge laugh politely.'], kit=['Bell', 'Ribbon drum', 'Story cards'], prompt='“I sing the brave bit for you.”'),
    dict(title='Hearth Mage', image='job-hearth-mage.png', intro='Hearth Mages carry warm, safe magic: sparks, steam, tea, and tiny lights. Their spells help problems; they do not solve the whole story alone.', gift='Create a small helpful magical effect.', stat='Wis or Luck', tryit=['Light a path with a glow-pebble.', 'Warm cold hands with tea-steam.', 'Reveal a hidden breeze or fairy mark.'], kit=['Teacup', 'Glow pebble', 'Little spoon wand'], prompt='“A tiny warm spell might help.”'),
    dict(title='Beast Friend', image='job-beast-friend.png', intro='Beast Friends understand animals and earn trust with gentle patience. They notice tails, ears, paws, feathers, and feelings before they roll dice.', gift='Ask a friendly creature for a small favor.', stat='Wis', tryit=['Offer a snack without grabbing.', 'Copy a small sound politely.', 'Ask what the creature feels.'], kit=['Oat pouch', 'Soft brush', 'Kindness bell'], prompt='“I crouch down and speak gently.”'),
    dict(title='Puzzle Tinker', image='job-puzzle-tinker.png', intro='Puzzle Tinkers build, open, balance, fold, and wonder how things work. They like ordinary bits: string, cups, buttons, chalk, and clever questions.', gift='Make a simple tool from ordinary bits.', stat='Agility', tryit=['Fix a latch or squeaky hinge.', 'Build a tiny bridge from safe pieces.', 'Turn clues into a simple plan.'], kit=['String', 'Chalk', 'Button box'], prompt='“What if this little thing fits here?”'),
]
for j in jobs:
    ph.feature_page('Adventure job', j['title'], j['image'], j['intro'], feature_grid([
        ('Gift', p(j['gift'])),
        ('Best stat', p(f"<span class='big-stat'>{j['stat']}</span>")),
        ('Try this', ul(j['tryit'])),
        ('Starter kit', ul(j['kit'])),
        ('Say this', f"<div class='feature-quote'>{j['prompt']}</div>"),
        ('Team role', p('This job shines most when it helps another hero have a turn.')),
    ]))
ph.text_page("Spells, gear, and treasure", f"""
{split(
spot('02-part-opener.png', '<strong>Rule:</strong> magic helps the story; it does not solve every problem alone.') + '''<h3>Safe little spells</h3>''' + ul(['<strong>Glow-pebble:</strong> make a small light.', '<strong>Tea-steam:</strong> warm cold hands or reveal a breeze.', '<strong>Thistle-tickle:</strong> distract a grumpy creature for a moment.', '<strong>Kind whisper:</strong> help someone say what they feel.', '<strong>Button-bridge:</strong> make a tiny bridge for one small creature.', '<strong>Heather-hush:</strong> quiet a noisy room for one careful question.']) + mini('Spell limit', 'A spell can help one small problem. Big problems still need friends, ideas, and choices.'),
'''<h3>Starting gear</h3>''' + ul(['A snack wrapped in cloth.', 'One useful tool.', 'One pretty charm.', 'One thing your hero drew themselves.', 'A spare ribbon, button, bell, shell, or smooth stone.', 'A tiny notebook for clues or doodles.']) + '''<h3>Useful tools</h3><table><tr><th>Tool</th><th>Use</th></tr><tr><td>Lantern</td><td>See misty paths.</td></tr><tr><td>String</td><td>Tie, measure, or rescue.</td></tr><tr><td>Chalk</td><td>Mark a safe way back.</td></tr><tr><td>Wooden cup</td><td>Offer water, tea, or kindness.</td></tr></table><h3>Treasure prompts</h3><table><tr><th>Find</th><th>Story use</th></tr><tr><td>Silver button</td><td>Opens a promise gate.</td></tr><tr><td>Ribbon</td><td>Marks a safe path.</td></tr><tr><td>Bell</td><td>Calls one fairy friend.</td></tr></table>''' + rb('<strong>Treasure is story-first:</strong> a shiny button can matter more than a bag of coins if it unlocks a promise.')
)}
""", columns=False)
ph.text_page("Spell list", f"""
<div class='spell-list'>
<h3>Cantrips: always small, always safe</h3>
<table><tr><th>Spell</th><th>Roll</th><th>What it does</th></tr>
<tr><td>Glow-Pebble</td><td>Luck</td><td>Make a pebble or charm shine like a candle.</td></tr>
<tr><td>Tea-Steam</td><td>Wis</td><td>Warm cold hands or reveal a hidden breeze.</td></tr>
<tr><td>Button-Bridge</td><td>Int</td><td>Make a tiny bridge for toys, fairies, or clues.</td></tr>
<tr><td>Heather-Hush</td><td>Wis</td><td>Quiet one noisy room long enough for a careful question.</td></tr>
<tr><td>Thistle-Tickle</td><td>Luck</td><td>Distract a grumpy creature for one moment.</td></tr>
<tr><td>Kind Whisper</td><td>Wis</td><td>Help someone say what they feel.</td></tr></table>
<h3>Adventure spells</h3>
<table><tr><th>Spell</th><th>Roll</th><th>Use</th></tr>
<tr><td>Mist Step</td><td>Agility</td><td>Slip past a watcher if a friend describes the mist.</td></tr>
<tr><td>Rune Read</td><td>Int</td><td>Ask the Guide one question about old writing.</td></tr>
<tr><td>Lucky Button</td><td>Luck</td><td>Turn one wobble into “yes, but” once per session.</td></tr>
<tr><td>Shield of Thistles</td><td>Strength</td><td>Hold back wind, rain, or falling branches for a turn.</td></tr>
<tr><td>Foxfire Path</td><td>Wis</td><td>Find the gentlest route through a confusing place.</td></tr>
<tr><td>Tiny Mend</td><td>Int</td><td>Repair a small broken object so it can help the story.</td></tr>
</table>
{rb('<strong>Spell rule:</strong> spells solve one small problem. Big problems still need choices, friends, and consequences.')}
</div>
""", columns=False)
ph.text_page("Equipment shop", f"""
<div class='shop'>
{rb('<strong>Starter money:</strong> each hero starts with 10 thistle pennies. Choose a few useful things before the first adventure. Save at least 1 penny for snacks, tolls, or lucky wishes.')}
<table><tr><th>Item</th><th>Cost</th><th>Use</th></tr>
<tr><td>Lantern</td><td>3p</td><td>See in mist, caves, and under bridges.</td></tr>
<tr><td>Rope</td><td>3p</td><td>Climb, tie, rescue, measure, or make a line.</td></tr>
<tr><td>Chalk</td><td>1p</td><td>Mark a safe path or draw a puzzle answer.</td></tr>
<tr><td>Snack bundle</td><td>1p</td><td>Share with a friend or hungry creature.</td></tr>
<tr><td>Wooden shield</td><td>4p</td><td>Helps Strength rolls to protect or hold steady.</td></tr>
<tr><td>Soft boots</td><td>4p</td><td>Helps Agility rolls to sneak or balance.</td></tr>
<tr><td>Tiny toolkit</td><td>5p</td><td>Helps Int rolls to mend, open, or build.</td></tr>
<tr><td>Oat pouch</td><td>2p</td><td>Helps Wis rolls with animals.</td></tr>
<tr><td>Lucky button</td><td>3p</td><td>Helps one Luck roll per adventure.</td></tr>
<tr><td>Warm cloak</td><td>3p</td><td>Stay cosy in rain, wind, or moonlit cold.</td></tr>
<tr><td>Bell</td><td>2p</td><td>Call a friend, mark a rhythm, or wake a sleepy path.</td></tr>
<tr><td>Blank notebook</td><td>2p</td><td>Draw maps, clues, promises, and creature friends.</td></tr>
</table>
<h3>Starter kits</h3><table><tr><th>Kit</th><th>Cost</th><th>Contains</th></tr>
<tr><td>Knight kit</td><td>8p</td><td>Wooden shield, rope, snack bundle.</td></tr>
<tr><td>Scout kit</td><td>8p</td><td>Lantern, chalk, soft boots.</td></tr>
<tr><td>Mage kit</td><td>8p</td><td>Lucky button, notebook, bell, chalk.</td></tr>
<tr><td>Friend kit</td><td>8p</td><td>Oat pouch, warm cloak, snack bundle, bell.</td></tr>
</table>
</div>
""", columns=False)
ph.text_page("Making a hero: quick checklist", f"""
<ol><li>Name your hero.</li><li>Pick a kindred.</li><li>Pick an adventure job.</li><li>Choose stats: one +2, two +1, two +0.</li><li>Pick one gear item and one charm.</li><li>Answer: “Who do I want to help?”</li></ol>
{qa('<strong>Worked example:</strong> Rowan Moonbutton is a Selkie-Born Beast Friend. Stats: Wis +2, Agility +1, Luck +1, Strength +0, Int +0. Gear: oat pouch. Charm: sea-glass button. Rowan wants to help nervous animals.')}
{rb('<strong>Grown-up tip:</strong> do not quiz a child on rules. Ask what they imagine, then translate that into Strength, Int, Agility, Wis, or Luck.')}
<div class='card-grid'>
{card('End of session', p('Ask: “Who did we help?” “What should we draw?” “What promise did we make?”'))}
{card('Tiny advancement', p('After three adventures, add one sticker beside a gift. The sticker is a memory, not a new complicated rule.'))}
{card('If a player is stuck', p('Offer two choices: “Do you want to talk kindly, move quickly, or do the brave thing?”'))}
{card('If the group gets loud', p('Point to the picture, name one sound in the scene, then ask one child what their hero notices.'))}
</div>
""", columns=False)
ph.write()

# Guide book
gm = Book("guide-book", "Guide Book", "How to run warm high-fantasy adventures for 5–7 year olds", "02-part-opener.png")
gm.cover_page()
gm.text_page("Your job as Guide", f"""
<p class='drop'>The Guide is not the boss of fun. You describe the world, listen to children, ask what they try, and help the dice turn ideas into surprises.</p>
{split(
ul(['Use short scenes: 5 to 12 minutes each.', 'Give choices in twos or threes, not long menus.', 'Name feelings before fights: scared, proud, sleepy, lonely, worried.', 'Let the children succeed often. The fun is in how it happens.']) + spot('03-race-kindreds.png', '<strong>Guide stance:</strong> make every scene readable from the art, then support the child’s idea.'),
rb('<strong>Safety tone:</strong> no gore, no cruelty, no permanent harm. Trouble can be spooky, muddy, noisy, or puzzling.') + '''<h3>Useful phrases</h3>''' + ul(['“Yes, and what does that look like?”', '“Who are you helping?”', '“Which stat fits your idea?”', '“That is a wobble, so something funny changes.”']) + mini('Guide rhythm', 'Picture → feeling → choice → roll only if exciting → warm change.')
)}
""", columns=False)
gm.text_page("Scene recipe", f"""
{card('1. A picture', p('Start with something children can see: misty bridge, silver fox, giant teacup, glowing thistle.'))}
{card('2. A feeling', p('Pick one: worried, excited, lonely, sleepy, proud, grumpy, curious.'))}
{card('3. A choice', p('Offer two helpful directions: follow the bells or talk to the fox.'))}
{card('4. A roll', p('Only roll if the answer is exciting. Use Strength, Int, Agility, Wis, or Luck.'))}
{card('5. A change', p('After each scene, something should be different: a clue, friend, promise, opened path, or new question.'))}
{qa('<strong>Read aloud:</strong> “The moon is caught in the loch like a silver coin. The kelpie foal stamps, worried and wet. What do you do?”')}
""", columns=False)
gm.art_page("05-bestiary-catalog.png", "Creatures are characters", "A creature should usually want something before it blocks something. Children can help, trick, soothe, race, sing, or befriend it.")
gm.text_page("Running rolls and wobbles", f"""
<h3>Choosing the stat</h3>{ul(['Use <strong>Strength</strong> for lifting, climbing, holding, pushing, or protecting.', 'Use <strong>Int</strong> for puzzles, plans, facts, reading runes, or clever tricks.', 'Use <strong>Agility</strong> for speed, balance, dodging, sneaking, or catching.'])}
<h3>Good wobbles</h3>{ul(['A hat blows away.', 'The map gets wet.', 'A bell rings and wakes someone.', 'A helpful creature misunderstands.', 'A path opens, but it is muddy.'])}
{rb('<strong>Never make a wobble mean “you did nothing.”</strong> Always move the story.')}
""")
gm.text_page("Building adventures", f"""
<table><tr><th>Part</th><th>Question</th><th>Example</th></tr><tr><td>Hook</td><td>Who needs help?</td><td>A fairy cannot find the right door.</td></tr><tr><td>Path</td><td>Where must heroes go?</td><td>Across the heather bridge.</td></tr><tr><td>Friend</td><td>Who can help?</td><td>A shy fox with silver whiskers.</td></tr><tr><td>Puzzle</td><td>What needs a clever choice?</td><td>Three bells ring, but only one is kind.</td></tr><tr><td>Ending</td><td>How is the glen warmer now?</td><td>The lost moon-bell is returned.</td></tr></table>
{qa('<strong>Guide promise:</strong> prepare situations, not answers. If the child invents a kind solution, let it matter.')}
""", columns=False)
gm.text_page("Tiny tables", f"""
<h3>What is strange here?</h3><table><tr><td>1</td><td>A thistle glows like a lantern.</td></tr><tr><td>2</td><td>Footprints turn into tiny flowers.</td></tr><tr><td>3</td><td>A crow speaks only in compliments.</td></tr><tr><td>4</td><td>The bridge asks for a joke.</td></tr><tr><td>5</td><td>A teacup storm rains indoors.</td></tr><tr><td>6</td><td>A sleeping troll snores bubbles.</td></tr></table>
<h3>What does the creature want?</h3><table><tr><td>1</td><td>A snack.</td></tr><tr><td>2</td><td>A song.</td></tr><tr><td>3</td><td>Someone to listen.</td></tr><tr><td>4</td><td>A lost button.</td></tr><tr><td>5</td><td>Help being brave.</td></tr><tr><td>6</td><td>A promise kept.</td></tr></table>
<h3>How can it enter a scene?</h3><table><tr><td>1</td><td>It blocks a path by accident.</td></tr><tr><td>2</td><td>It is crying quietly.</td></tr><tr><td>3</td><td>It has the clue but misunderstands it.</td></tr><tr><td>4</td><td>It challenges the heroes to a silly contest.</td></tr><tr><td>5</td><td>It asks for a promise.</td></tr><tr><td>6</td><td>It follows the heroes home.</td></tr></table>
""")
gm.write()

# Bestiary
be = Book("bestiary", "Bestiary", "Friendly creatures, gentle problems, stat blocks, and encounter ideas", "05-bestiary-catalog.png")
be.cover_page()
be.text_page("How to use creature stat blocks", f"""
<p class='drop'>Creatures now have classic fantasy stat blocks, but they are still story-first. Stats help the Guide choose a roll when a creature resists, races, hides, puzzles, or needs calming.</p>
{spot('05-bestiary-catalog.png', '<strong>Creature rule:</strong> every creature has a feeling, a wish, useful stats, and a safe complication.')}
{rb('<strong>Creature rolls:</strong> when a creature acts against a hero, roll d6 + the creature stat. For this age, use results to create funny trouble, not punishment.')}
<table><tr><th>Stat</th><th>Creature use</th></tr><tr><td>Strength</td><td>Push, hold, carry, stomp, protect.</td></tr><tr><td>Int</td><td>Riddles, tricks, memories, old magic.</td></tr><tr><td>Agility</td><td>Race, dodge, fly, swim, sneak.</td></tr><tr><td>Wis</td><td>Feelings, nature, noticing, animal sense.</td></tr><tr><td>Luck</td><td>Fairy weirdness, charm magic, surprises.</td></tr></table>
""", columns=False)
creatures = [
 dict(name='Moon-Kelpie Foal', img='creature-moon-kelpie-foal.png', intro='A nervous water-pony child with a kelp mane and a moon-bell collar. It wants to be brave but splashes when startled.', stats={'STR':1,'INT':0,'AGI':2,'WIS':1,'LUK':1}, wants='Its moon-bell returned.', helps='Carries one hero safely across shallow water.', moves=['Moonlit Splash: makes stepping stones shimmer for one turn.', 'Foal Gallop: races across water if someone sings softly.'], comp='Splashes the map when startled.'),
 dict(name='Thistle Sprite', img='creature-thistle-sprite.png', intro='A tiny proud fairy with a thorn crown too large for its head. It guards paths because it secretly feels lonely.', stats={'STR':-1,'INT':1,'AGI':2,'WIS':0,'LUK':2}, wants='Someone to admire its thorn crown.', helps='Shows a hidden fairy path.', moves=['Prickle Point: blocks a rude shortcut with harmless thistles.', 'Royal Decree: demands a compliment or tiny flag.'], comp='Gets offended by rude pointing.'),
 dict(name='Moss Troll Napper', img='creature-moss-troll-napper.png', intro='A huge mossy troll who only wants a quiet nap. Birds nest in its hair and bubbles puff from its nose.', stats={'STR':3,'INT':0,'AGI':-1,'WIS':1,'LUK':0}, wants='A quieter place to nap.', helps='Lifts a log bridge.', moves=['Gentle Lift: moves something heavy without breaking it.', 'Bubble Snore: floats clues away unless caught.'], comp='Snores bubbles that float away clues.'),
 dict(name='Silver Fox Familiar', img='creature-silver-fox-familiar.png', intro='A polite fox with silver whiskers, clever eyes, and too many compliments. It knows tracks no one else can see.', stats={'STR':0,'INT':2,'AGI':2,'WIS':1,'LUK':1}, wants='A riddle answered.', helps='Leads heroes to tracks.', moves=['Compliment Riddle: gives a clue wrapped in praise.', 'Silver Step: vanishes behind moonlit grass.'], comp='Only speaks in compliments.'),
 dict(name='Rowan Owl', img='creature-rowan-owl.png', intro='An old owl wearing rowan berries like spectacles. It sees through mist but forgets names at the funniest time.', stats={'STR':0,'INT':2,'AGI':1,'WIS':3,'LUK':0}, wants='Help remembering a name.', helps='Sees through mist.', moves=['Mist Sight: spots hidden doors or feelings.', 'Old Acorn Advice: gives wise advice with one wrong noun.'], comp='Calls everyone “young acorn.”'),
 dict(name='Heather Hare', img='creature-heather-hare.png', intro='A fast hare with a red ribbon tangled around one paw. It is worried, quick, and very easy to startle.', stats={'STR':0,'INT':0,'AGI':3,'WIS':1,'LUK':1}, wants='Its red ribbon untangled.', helps='Carries a message.', moves=['Zigzag Dash: outruns almost anything on open heather.', 'Ear Twitch: hears danger before it arrives.'], comp='Keeps changing direction.'),
 dict(name='Teacup Dragon', img='creature-teacup-dragon.png', intro='A biscuit-sized dragon who lives in warm cups and thinks it is enormous. Its sparks are bright but small.', stats={'STR':1,'INT':1,'AGI':1,'WIS':0,'LUK':2}, wants='A biscuit and apology.', helps='Boils water for tea or steam clues.', moves=['Steam Puff: reveals invisible writing.', 'Spark Sneeze: lights a candle or startles a puddle.'], comp='Sneezes sparks into puddles.'),
 dict(name='Loch Lantern Jelly', img='creature-loch-lantern-jelly.png', intro='A shy glowing jelly that floats under dark water like a little lantern. It dims when shouted at.', stats={'STR':-1,'INT':0,'AGI':1,'WIS':2,'LUK':2}, wants='A dark pool made less lonely.', helps='Lights underwater steps.', moves=['Soft Glow: lights a safe route beneath the surface.', 'Drift Away: escapes loud scenes without anger.'], comp='Floats away if shouted at.'),
 dict(name='Bog-Boot Brownie', img='creature-bog-boot-brownie.png', intro='A muddy household fairy who loves cleaning boots, even when boots are not the problem.', stats={'STR':1,'INT':2,'AGI':1,'WIS':1,'LUK':0}, wants='A pair of boots to clean.', helps='Finds footprints.', moves=['Mud Map: reads footprints like a story.', 'Scrub Scrub: cleans one item until it shines.'], comp='Cleans the wrong thing first.'),
 dict(name='Cloud Sheep', img='creature-cloud-sheep.png', intro='A dreamy sheep made of soft cloud wool. It drifts through sky meadows and forgets which star is its shepherd.', stats={'STR':1,'INT':0,'AGI':1,'WIS':1,'LUK':3}, wants='A shepherd star.', helps='Makes a fluffy bridge.', moves=['Cloud Bridge: makes one soft crossing for careful feet.', 'Dream Drift: carries a clue into the sky.'], comp='Drifts when children giggle.'),
]
for c in creatures:
    be.creature_page(c['name'], c['img'], c['intro'], c['stats'], feature_grid([
        ('Wants', p(c['wants'])),
        ('Helps by', p(c['helps'])),
        ('Moves', ul(c['moves'])),
        ('Complication', p(c['comp'])),
        ('Gentle approach', p('Name its feeling, offer one kind idea, then roll only if the moment is exciting.')),
        ('Treasure/friend reward', p('A clue, safe path, charm, drawing prompt, or promise for later.')),
    ]))
be.text_page("Creature builder", f"""
<table><tr><th>Roll</th><th>Animal</th><th>Fairy twist</th><th>Best stat</th></tr><tr><td>1</td><td>Fox</td><td>silver whiskers</td><td>Int</td></tr><tr><td>2</td><td>Hare</td><td>bell tail</td><td>Agility</td></tr><tr><td>3</td><td>Owl</td><td>moon glasses</td><td>Wis</td></tr><tr><td>4</td><td>Pony</td><td>kelp mane</td><td>Strength</td></tr><tr><td>5</td><td>Dragon</td><td>teacup size</td><td>Luck</td></tr><tr><td>6</td><td>Sheep</td><td>cloud wool</td><td>Luck</td></tr></table>
{qa('<strong>Example:</strong> Roll 4, 2, 1: a pony with a bell tail. Give it Strength +1, Agility +2, Wis +1, Int +0, Luck +1. It lost the bell that tells the loch when to sleep.')}
<div class='card-grid'>
{card('Set the stats', p('Pick one +3, one +2, two +1, and one +0. Very tiny creatures may have one -1 and one +3.'))}
{card('Make it child-friendly', p('Replace defeat with help, chase, song, puzzle, promise, snack, or finding a lost thing.'))}
{card('Choose moves', p('Give it two safe moves: one helpful, one troublesome.'))}
{card('Reward idea', p('A friend, clue, safe path, tiny charm, bedtime-song note, or funny drawing prompt.'))}
</div>
""", columns=False)
be.write()

# Campaigns
ca = Book("campaigns", "Example Campaigns", "Ready-to-run adventures and a small linked campaign", "02-part-opener.png")
ca.cover_page()
ca.text_page("How campaigns work", f"""
<p class='drop'>A campaign for this age is a string of friendly episodes. Each session should have a clear helper, a magical place, one puzzle, and one warm ending.</p>
{spot('02-part-opener.png', '<strong>Campaign rhythm:</strong> arrive, discover, help, celebrate.')}
{rb('<strong>Length:</strong> 20–40 minutes per adventure. Stop while children still want more.')}
{ul(['Start with a read-aloud box.', 'Ask one choice at a time.', 'Use three scenes: arrive, discover, help.', 'End with a sticker, drawing, or named promise.'])}
<table><tr><th>Minute</th><th>What to do</th></tr><tr><td>0–5</td><td>Read the hook and ask what the heroes notice.</td></tr><tr><td>5–15</td><td>Meet a creature or obstacle with a feeling.</td></tr><tr><td>15–30</td><td>Try two or three child ideas, rolling only for exciting moments.</td></tr><tr><td>End</td><td>Name the friend helped and draw one treasure.</td></tr></table>
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
{ul(['The bridge is not mean; it is embarrassed because moss covers its carvings.', 'Children can clean, joke, sing, draw, or ask what happened.', 'A wobble makes the bridge sneeze pebbles, not hurt anyone.'])}
{rb('<strong>Reward:</strong> the bridge teaches the party the safe stepping rhythm: clap, step, clap, step.')}
<h3>Extra clues</h3>{ul(['Moss hides a carved smiling face.', 'The bridge remembers children who thanked it long ago.', 'A silver fox waits on the other side with dry socks.'])}
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
{card('If children want more', p('Let them draw the new friend, then turn the drawing into the next adventure hook.'))}
</div>
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
<div class='sheet-box'><strong>Luck</strong><br><span class='big-stat'>+__</span></div><div class='sheet-box'><strong>My gift</strong><div class='line'></div></div>
<div class='sheet-box big'><strong>Gear and charm</strong><div class='line'></div><div class='line'></div></div><div class='sheet-box big'><strong>I want to help...</strong><div class='line'></div><div class='line'></div></div>
<div class='sheet-box tall'><strong>Draw your hero</strong></div><div class='sheet-box tall'><strong>Adventure notes / stickers</strong></div>
</div>
""", columns=False)
sheet.text_page("Finished example sheet", f"""
<div class='sheet'>
<div class='sheet-box'><strong>Hero name</strong><p>Rowan Moonbutton</p></div><div class='sheet-box'><strong>Player name</strong><p>Example</p></div>
<div class='sheet-box'><strong>Kindred</strong><p>Selkie-Born</p></div><div class='sheet-box'><strong>Adventure job</strong><p>Beast Friend</p></div>
<div class='sheet-box'><strong>Strength</strong><br><span class='big-stat'>+0</span></div><div class='sheet-box'><strong>Int</strong><br><span class='big-stat'>+0</span></div>
<div class='sheet-box'><strong>Agility</strong><br><span class='big-stat'>+1</span></div><div class='sheet-box'><strong>Wis</strong><br><span class='big-stat'>+2</span></div>
<div class='sheet-box'><strong>Luck</strong><br><span class='big-stat'>+1</span></div><div class='sheet-box'><strong>My gift</strong><p>Ask a friendly creature for a small favor.</p></div>
<div class='sheet-box big'><strong>Gear and charm</strong><p>Oat pouch, sea-glass button.</p></div><div class='sheet-box big'><strong>I want to help...</strong><p>nervous animals feel safe.</p></div>
<div class='sheet-box tall'><strong>Draw your hero</strong><p class='small'>Soft seal-cloak, muddy boots, kind smile.</p></div><div class='sheet-box tall'><strong>Adventure notes</strong><p>Helped the moon-kelpie foal.</p></div>
</div>
""", columns=False)
sheet.text_page("Quick reference cards", f"""
{card('Roll rule', p('Roll d6 + stat bonus. 1–3 wobble. 4–5 yes, but. 6+ bright success.'))}
{card('Stats', p('<strong>Strength</strong> lifts/protects. <strong>Int</strong> solves/knows. <strong>Agility</strong> moves/sneaks. <strong>Wis</strong> notices/understands. <strong>Luck</strong> handles charms/surprises.'))}
{card('Turn prompt', p('“What do you try?” then “How does your hero do it?”'))}
{card('Kindness rule', p('Heroes can be muddy, surprised, or silly. The story never shames a child for helping.'))}
{card('Wobble ideas', p('Lost hat, wet map, wrong door, sleepy troll, ringing bell, muddied boots.'))}
{card('End of session', p('Name one friend made, one brave choice, and one thing to draw.'))}
""", columns=False)
sheet.write()

# Plain markdown notes for repo browsing
for slug, title in [(ph.slug, ph.title), (gm.slug, gm.title), (be.slug, be.title), (ca.slug, ca.title), (sheet.slug, sheet.title)]:
    (BOOKS / f"{slug}.md").write_text(f"# {title}\n\nSee `printable-a4/{slug}-a4.html` and `pdf/{slug}.pdf`.\n", encoding="utf-8")

print('built book HTML files:', ', '.join(sorted(p.name for p in PRINT.glob('*-a4.html'))))
