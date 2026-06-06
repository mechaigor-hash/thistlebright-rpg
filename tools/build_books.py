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
    def write(self):
        html = '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(self.title)+'</title><style>'+CSS+'</style></head><body><main class="book">' + '\n'.join(self.pages) + '</main></body></html>'
        (PRINT / f"{self.slug}-a4.html").write_text(html, encoding="utf-8")

def p(text): return f"<p>{text}</p>"
def ul(items): return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
def card(title, body): return f"<div class='option-card'><h3>{title}</h3>{body}</div>"
def rb(text): return f"<div class='rulebox'>{text}</div>"
def qa(text): return f"<div class='questbox'>{text}</div>"
def spot(img, caption=""):
    cap = f"<div class='mini'>{caption}</div>" if caption else ""
    return f"<div class='hero-strip'><img src='{art(img)}' alt='art'>{cap}</div>"

# Player handbook
ph = Book("player-handbook", "Player Handbook", "Character creation, simple rules, kindreds, jobs, spells, gear, and a worked example", "01-cover.png")
ph.cover_page()
ph.text_page("How to use this book", f"""
<ol class='toc'><li>Choose who helps as the Guide.</li><li>Make a hero in five easy steps.</li><li>Use Brave, Kind, and Quick when a roll is exciting.</li><li>Keep the story warm: heroes can be muddy, surprised, or silly, but never shamed.</li></ol>
{spot('02-part-opener.png', '<strong>Table feel:</strong> point at the picture, ask what the hero notices, then roll only when it is exciting.')}
{rb('<strong>For ages 5–7:</strong> read choices aloud, let children point to pictures, and use stars or stickers for stats instead of lots of numbers.')}
<h3>What you need</h3>{ul(['One six-sided die.', 'A pencil, character sheet, and three little counters.', 'A grown-up or older sibling Guide.', 'A promise to listen and take turns.'])}
<h3>What players say</h3>{ul(['“I help.”', '“I try the brave thing.”', '“Can I talk to it?”', '“I have an idea!”'])}
""")
ph.art_page("02-part-opener.png", "Welcome to the glen", "Tiny bells ring beneath the heather. A fairy guide invites the heroes to help a magical place without making the rules too big.")
ph.text_page("The easy dice rule", f"""
<p class='drop'>When the answer is obvious, no roll is needed. When everyone leans forward and wonders what might happen, roll one six-sided die and add the hero's matching stat stars.</p>
<table><tr><th>Total</th><th>Result</th><th>Say it like this</th></tr><tr><td>1–2</td><td>Wobble</td><td>It goes wrong in a funny, safe, or messy way.</td></tr><tr><td>3–4</td><td>Yes, but...</td><td>It works, and there is a tiny cost or choice.</td></tr><tr><td>5+</td><td>Bright success</td><td>It works well, and the hero feels proud.</td></tr></table>
{rb('<strong>No failure spiral:</strong> a wobble changes the scene; it does not stop the adventure.')}
<h3>The three stats</h3>{ul(['<strong>Brave</strong> — standing tall, protecting, climbing, daring, saying “I can try.”', '<strong>Kind</strong> — helping, calming, sharing, talking, understanding feelings.', '<strong>Quick</strong> — sneaking, catching, dodging, spotting, balancing.'])}
""")
ph.text_page("Stat creation", f"""
{card('Step 1: Pick your best stat', p('Put <span class="big-stat">★★</span> in the thing your hero is best at.'))}
{card('Step 2: Pick your okay stat', p('Put <span class="big-stat">★</span> in the thing your hero can usually do.'))}
{card('Step 3: Leave one blank', p('Put <span class="big-stat">—</span> in the thing your hero is still learning. This is not bad; it makes stories fun.'))}
{rb('<strong>Example:</strong> Rowan the Beast Friend has Kind ★★, Quick ★, Brave —. Rowan talks gently to foxes, moves carefully, and is still learning to be bold.')}
{qa('<strong>Helper question:</strong> “Which one sounds most like your hero: brave, kind, or quick?”')}
<div class='card-grid'>
{card('If a child wants all ★★', p('Say: “Every hero is still learning something. Which one will be funny to practise?”'))}
{card('If a child worries about —', p('Say: “Blank means story chance, not bad. Friends can help you.”'))}
</div>
""", columns=False)
ph.art_page("03-race-kindreds.png", "Step 1: Pick your kindred", "Your kindred is where your fairy-tale hero comes from. It gives a picture, a story gift, and a way to join the world.")
ph.text_page("Kindreds", "".join([
card('Glenfolk', p('Croft, cottage, castle, or market-lane children with practical hearts.')+ul(['<strong>Gift:</strong> once per adventure, remember a local clue.', '<strong>Look:</strong> tartan scarf, muddy boots, treasure pockets.'])),
card('Thistle Fairy', p('Small bright folk with manners, shimmer, and secret paths.')+ul(['<strong>Gift:</strong> once per scene, notice nearby fairy magic.', '<strong>Look:</strong> petal cloak, star freckles, tiny crown.'])),
card('Brownie Helper', p('Cozy fixers who tidy, mend, and improve small things.')+ul(['<strong>Gift:</strong> repair or improve one tiny object each scene.', '<strong>Look:</strong> apron, tool pouch, flour on nose.'])),
card('Selkie-Born', p('Gentle loch-hearted heroes with moonlit dreams.')+ul(['<strong>Gift:</strong> understand water, weather, or a sad feeling.', '<strong>Look:</strong> soft seal-cloak, shell button, sea-glass charm.'])),
card('Rowan-Kin', p('Forest children with leaf crowns and careful listening.')+ul(['<strong>Gift:</strong> ask a tree, bird, or breeze for one hint.', '<strong>Look:</strong> red berries, green cloak, bark-pattern gloves.'])),
card('Heather Giantling', p('Small for a giant, huge for a fairy, and very gentle.')+ul(['<strong>Gift:</strong> lift, push, or carry one heavy thing safely.', '<strong>Look:</strong> big knitted jumper, pebble buttons, warm laugh.']))
]))
ph.art_page("04-class-paths.png", "Step 2: Pick your adventure job", "Your job says what you like doing when trouble appears. Each job has one gift that helps the whole table.")
ph.text_page("Adventure jobs", "".join([
card('Thistle Knight', p('Protects friends and stands bravely at the front.')+rb('<strong>Gift:</strong> once per scene, turn a scary moment into a brave one.')),
card('Loch Scout', p('Finds paths, listens for clues, and spots hidden doors.')+rb('<strong>Gift:</strong> ask the Guide one “what do I notice?” question.')),
card('Song-Spark Bard', p('Uses music, jokes, and stories to lift everyone up.')+rb('<strong>Gift:</strong> give another hero +1 after a kind song or cheer.')),
card('Hearth Mage', p('Carries warm, safe magic: sparks, steam, tea, and tiny lights.')+rb('<strong>Gift:</strong> create a small helpful magical effect.')),
card('Beast Friend', p('Understands animals and earns trust with gentle patience.')+rb('<strong>Gift:</strong> ask a friendly creature for a small favor.')),
card('Puzzle Tinker', p('Builds, opens, balances, folds, and wonders how things work.')+rb('<strong>Gift:</strong> make a simple tool from ordinary bits.'))
]))
ph.text_page("Spells, gear, and treasure", f"""
{spot('02-part-opener.png', '<strong>Rule:</strong> magic helps the story; it does not solve every problem alone.')}
<h3>Safe little spells</h3>{ul(['<strong>Glow-pebble:</strong> make a small light.', '<strong>Tea-steam:</strong> warm cold hands or reveal a breeze.', '<strong>Thistle-tickle:</strong> distract a grumpy creature for a moment.', '<strong>Kind whisper:</strong> help someone say what they feel.'])}
<h3>Starting gear</h3>{ul(['A snack wrapped in cloth.', 'One useful tool.', 'One pretty charm.', 'One thing your hero drew themselves.'])}
{rb('<strong>Treasure is story-first:</strong> a shiny button can matter more than a bag of coins if it unlocks a promise.')}
""")
ph.text_page("Making a hero: quick checklist", f"""
<ol><li>Name your hero.</li><li>Pick a kindred.</li><li>Pick an adventure job.</li><li>Choose stats: ★★, ★, and —.</li><li>Pick one gear item and one charm.</li><li>Answer: “Who do I want to help?”</li></ol>
{qa('<strong>Worked example:</strong> Rowan Moonbutton is a Selkie-Born Beast Friend. Stats: Kind ★★, Quick ★, Brave —. Gear: oat pouch. Charm: sea-glass button. Rowan wants to help nervous animals.')}
{rb('<strong>Grown-up tip:</strong> do not quiz a child on rules. Ask what they imagine, then translate that into Brave, Kind, or Quick.')}
<div class='card-grid'>
{card('End of session', p('Ask: “Who did we help?” “What should we draw?” “What promise did we make?”'))}
{card('Tiny advancement', p('After three adventures, add one sticker beside a gift. The sticker is a memory, not a new complicated rule.'))}
</div>
""", columns=False)
ph.write()

# Guide book
gm = Book("guide-book", "Guide Book", "How to run warm high-fantasy adventures for 5–7 year olds", "02-part-opener.png")
gm.cover_page()
gm.text_page("Your job as Guide", f"""
<p class='drop'>The Guide is not the boss of fun. You describe the world, listen to children, ask what they try, and help the dice turn ideas into surprises.</p>
{ul(['Use short scenes: 5 to 12 minutes each.', 'Give choices in twos or threes, not long menus.', 'Name feelings before fights: scared, proud, sleepy, lonely, worried.', 'Let the children succeed often. The fun is in how it happens.'])}
{spot('03-race-kindreds.png', '<strong>Guide stance:</strong> make every scene readable from the art, then support the child’s idea.')}
{rb('<strong>Safety tone:</strong> no gore, no cruelty, no permanent harm. Trouble can be spooky, muddy, noisy, or puzzling.')}
<h3>Useful phrases</h3>{ul(['“Yes, and what does that look like?”', '“Who are you helping?”', '“Which stat fits your idea?”', '“That is a wobble, so something funny changes.”'])}
""")
gm.text_page("Scene recipe", f"""
{card('1. A picture', p('Start with something children can see: misty bridge, silver fox, giant teacup, glowing thistle.'))}
{card('2. A feeling', p('Pick one: worried, excited, lonely, sleepy, proud, grumpy, curious.'))}
{card('3. A choice', p('Offer two helpful directions: follow the bells or talk to the fox.'))}
{card('4. A roll', p('Only roll if the answer is exciting. Use Brave, Kind, or Quick.'))}
{card('5. A change', p('After each scene, something should be different: a clue, friend, promise, opened path, or new question.'))}
{qa('<strong>Read aloud:</strong> “The moon is caught in the loch like a silver coin. The kelpie foal stamps, worried and wet. What do you do?”')}
""", columns=False)
gm.art_page("05-bestiary-catalog.png", "Creatures are characters", "A creature should usually want something before it blocks something. Children can help, trick, soothe, race, sing, or befriend it.")
gm.text_page("Running rolls and wobbles", f"""
<h3>Choosing the stat</h3>{ul(['Use <strong>Brave</strong> when the hero faces pressure.', 'Use <strong>Kind</strong> when feelings, friendship, or care matter.', 'Use <strong>Quick</strong> when speed, balance, noticing, or sneaking matters.'])}
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
be = Book("bestiary", "Bestiary", "Friendly creatures, gentle problems, and encounter ideas", "05-bestiary-catalog.png")
be.cover_page()
be.text_page("How to use creatures", f"""
<p class='drop'>In Thistlebright, a creature is a story moment. It might be scared, proud, hungry, lonely, sleepy, or confused. Heroes are encouraged to notice feelings first.</p>
{rb('<strong>Entry format:</strong> What it feels, what it wants, how it helps, and what makes the scene funny or tricky.')}
{ul(['Use creatures as friends, messengers, puzzles, guardians, or comic interruptions.', 'For this age, avoid “kill it” goals. Use helping, calming, racing, finding, sharing, or promising.', 'If a creature is dangerous, make the danger environmental: slippery bank, loud roar, storm cloud, falling pine cones.'])}
""")
creatures = [
('Moon-Kelpie Foal','Lonely and nervous','Its moon-bell returned','Carries one hero safely across shallow water','Splashes the map when startled'),
('Thistle Sprite','Proud and tiny','Someone to admire its thorn crown','Shows a hidden fairy path','Gets offended by rude pointing'),
('Moss Troll Napper','Sleepy and warm-hearted','A quieter place to nap','Lifts a log bridge','Snores bubbles that float away clues'),
('Silver Fox Familiar','Curious and polite','A riddle answered','Leads heroes to tracks','Only speaks in compliments'),
('Rowan Owl','Wise but forgetful','Help remembering a name','Sees through mist','Calls everyone “young acorn”'),
('Heather Hare','Fast and worried','Its red ribbon untangled','Carries a message','Keeps changing direction'),
('Teacup Dragon','Hot-tempered but small','A biscuit and apology','Boils water for tea or steam clues','Sneezes sparks into puddles'),
('Loch Lantern Jelly','Shy and glowing','A dark pool made less lonely','Lights underwater steps','Floats away if shouted at'),
('Bog-Boot Brownie','Helpful and muddy','A pair of boots to clean','Finds footprints','Cleans the wrong thing first'),
('Cloud Sheep','Dreamy and soft','A shepherd star','Makes a fluffy bridge','Drifts when children giggle')]
body = "".join([f"<div class='creature'><h3>{n}</h3><p><strong>Feels:</strong> {feel}.<br><strong>Wants:</strong> {want}.<br><strong>Helps by:</strong> {help}.<br><strong>Complication:</strong> {comp}.</p><p><span class='badge'>Brave</span><span class='badge'>Kind</span><span class='badge'>Quick</span> Pick one depending on the child’s idea.</p></div>" for n,feel,want,help,comp in creatures[:4]])
be.text_page("Loch and glen creatures", body)
be.art_page("05-bestiary-catalog.png", "Creature scenes", "Use the picture first: what does the child notice, who looks worried, and what helpful thing might the heroes try?")
body2 = "".join([f"<div class='creature'><h3>{n}</h3><p><strong>Feels:</strong> {feel}.<br><strong>Wants:</strong> {want}.<br><strong>Helps by:</strong> {help}.<br><strong>Complication:</strong> {comp}.</p><p><span class='badge'>Best first move</span> ask what the creature feels.</p></div>" for n,feel,want,help,comp in creatures[4:8]])
be.text_page("Forest and sky creatures", body2)
body3 = "".join([f"<div class='creature'><h3>{n}</h3><p><strong>Feels:</strong> {feel}.<br><strong>Wants:</strong> {want}.<br><strong>Helps by:</strong> {help}.<br><strong>Complication:</strong> {comp}.</p></div>" for n,feel,want,help,comp in creatures[8:]])
be.text_page("Tiny odd creatures", body3 + rb('<strong>Make your own:</strong> choose an animal, add a fairy object, then give it one feeling and one wish.'), columns=False)
be.text_page("Creature builder", f"""
<table><tr><th>Roll</th><th>Animal</th><th>Fairy twist</th><th>Feeling</th></tr><tr><td>1</td><td>Fox</td><td>silver whiskers</td><td>worried</td></tr><tr><td>2</td><td>Hare</td><td>bell tail</td><td>excited</td></tr><tr><td>3</td><td>Owl</td><td>moon glasses</td><td>sleepy</td></tr><tr><td>4</td><td>Pony</td><td>kelp mane</td><td>lonely</td></tr><tr><td>5</td><td>Dragon</td><td>teacup size</td><td>proud</td></tr><tr><td>6</td><td>Sheep</td><td>cloud wool</td><td>confused</td></tr></table>
{qa('<strong>Example:</strong> Roll 4, 2, 1: a pony with a bell tail who is worried. It lost the bell that tells the loch when to sleep.')}
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
""")
ca.art_page("02-part-opener.png", "Campaign: The Bells Under the Heather", "Three fairy bells have gone quiet, and the glen is forgetting its bedtime songs.")
ca.text_page("Adventure 1: The Lost Moon-Bell", f"""
{qa('<strong>Read aloud:</strong> “The moon is stuck in the loch like a silver coin. A young kelpie foal stamps at the water and tries not to cry.”')}
<h3>Scenes</h3>{ul(['Meet the nervous kelpie foal.', 'Search reeds, stones, or bubbles for clues.', 'Return the bell by singing, wading, or asking the loch nicely.'])}
<h3>Roll moments</h3><table><tr><th>Idea</th><th>Stat</th></tr><tr><td>Step onto slippery stones</td><td>Quick</td></tr><tr><td>Comfort the foal</td><td>Kind</td></tr><tr><td>Hold the rope in a gust</td><td>Brave</td></tr></table>
""")
ca.text_page("Adventure 2: The Grumpy Bridge", f"""
{qa('<strong>Read aloud:</strong> “The bridge folds its stony arms. ‘No crossing,’ it rumbles, ‘unless someone remembers how to laugh politely.’”')}
{ul(['The bridge is not mean; it is embarrassed because moss covers its carvings.', 'Children can clean, joke, sing, draw, or ask what happened.', 'A wobble makes the bridge sneeze pebbles, not hurt anyone.'])}
{rb('<strong>Reward:</strong> the bridge teaches the party the safe stepping rhythm: clap, step, clap, step.')}
""")
ca.text_page("Adventure 3: The Thistle Crown", f"""
{qa('<strong>Read aloud:</strong> “A tiny sprite wears a crown too big for its head. It declares itself King of All Paths, then whispers, ‘Do I look brave?’”')}
<h3>What is really happening?</h3><p>The sprite is scared of guarding the path alone. It needs help making a promise flag.</p>
<h3>Good solutions</h3>{ul(['Make a tiny flag.', 'Share a brave story.', 'Ask another creature to visit.', 'Let the sprite choose a less lonely job.'])}
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
<div class='sheet-box'><strong>Brave</strong><br><span class='big-stat'>□ □</span></div><div class='sheet-box'><strong>Kind</strong><br><span class='big-stat'>□ □</span></div>
<div class='sheet-box'><strong>Quick</strong><br><span class='big-stat'>□ □</span></div><div class='sheet-box'><strong>My gift</strong><div class='line'></div></div>
<div class='sheet-box big'><strong>Gear and charm</strong><div class='line'></div><div class='line'></div></div><div class='sheet-box big'><strong>I want to help...</strong><div class='line'></div><div class='line'></div></div>
<div class='sheet-box tall'><strong>Draw your hero</strong></div><div class='sheet-box tall'><strong>Adventure notes / stickers</strong></div>
</div>
""", columns=False)
sheet.text_page("Finished example sheet", f"""
<div class='sheet'>
<div class='sheet-box'><strong>Hero name</strong><p>Rowan Moonbutton</p></div><div class='sheet-box'><strong>Player name</strong><p>Example</p></div>
<div class='sheet-box'><strong>Kindred</strong><p>Selkie-Born</p></div><div class='sheet-box'><strong>Adventure job</strong><p>Beast Friend</p></div>
<div class='sheet-box'><strong>Brave</strong><br><span class='big-stat'>—</span></div><div class='sheet-box'><strong>Kind</strong><br><span class='big-stat'>★★</span></div>
<div class='sheet-box'><strong>Quick</strong><br><span class='big-stat'>★</span></div><div class='sheet-box'><strong>My gift</strong><p>Ask a friendly creature for a small favor.</p></div>
<div class='sheet-box big'><strong>Gear and charm</strong><p>Oat pouch, sea-glass button.</p></div><div class='sheet-box big'><strong>I want to help...</strong><p>nervous animals feel safe.</p></div>
<div class='sheet-box tall'><strong>Draw your hero</strong><p class='small'>Soft seal-cloak, muddy boots, kind smile.</p></div><div class='sheet-box tall'><strong>Adventure notes</strong><p>Helped the moon-kelpie foal.</p></div>
</div>
""", columns=False)
sheet.text_page("Quick reference cards", f"""
{card('Roll rule', p('Roll d6 + stat stars. 1–2 wobble. 3–4 yes, but. 5+ bright success.'))}
{card('Stats', p('<strong>Brave</strong> faces pressure. <strong>Kind</strong> helps feelings. <strong>Quick</strong> moves, spots, and sneaks.'))}
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
