#!/usr/bin/env python3
"""Sanitize rendered HTML art references.

This is a final QA/fix pass for the illustrated Alba book set.  It removes:

* procedural/geometric placeholder PNGs (`*.source.svg` siblings),
* derivative `real/no-reuse-*` assets that are only crops/variants,
* duplicate byte-hash reuse across rendered books,
* obvious cross-domain substitutions (atlas pages getting gear/card/companion art).

The replacement pool is restricted to non-procedural raster art and scored by
book/page domain so atlas pages receive maps/regions, gear pages receive object
art, mounts pages receive companion art, and so on.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART_ROOT = ROOT / "art" / "generated"
HTML_ROOT = ROOT / "printable-a4"
QA_ROOT = ROOT / "qa"

IMG_RE = re.compile(r'(<img\b[^>]*?src=["\'])([^"\']+)(["\'][^>]*>)', re.I)
WORD_RE = re.compile(r"[a-z0-9]+")

DOMAIN_WORDS = {
    "atlas": {"atlas","map","regional","region","area","loch","road","border","thistlewood","kettleford","heatherhigh","heather","cauldron","root","warrens","whale"},
    "gear": {"gear","item","items","potion","potions","poison","poisons","lantern","rope","toolkit","oat","magic","treasure","crafting","shield","cloak","vial","tea","jam"},
    "mount": {"mount","mounts","pet","pets","companion","pony","goat","stag","owl","warg","mouse","moth","hedgehog"},
    "bestiary": {"bestiary","creature","monster","drake","warg","redcap","crow","hag","wight","stag","serpent","imp","goat","giant"},
    "campaign": {"campaign","adventure","quest","scene","banner","fort","clan","oath","road","longship","bell","toll"},
    "player": {"player","handbook","dice","rule","kindred","job","spell","hero","character","trap"},
    "cards": {"printable","cards","card","low","ink","quickstart","table","aid","aids"},
}

# Hard overrides for pages where the title names a specific atlas/map subject.
# These prevent a duplicate-avoidance pass from stealing unrelated gear/card art
# or the wrong region image.
TITLE_OVERRIDES = {
    ("alba-atlas-a4.html", "Atlas map of Alba"): "alba-map.png",
    ("alba-atlas-expanded-a4.html", "Adventures in Alba"): "real-context/alba-atlas-expanded/atlas-cover-map-table.png",
    ("alba-atlas-expanded-a4.html", "Expanded map of Alba"): "alba-frontier-map.png",
    ("alba-atlas-expanded-a4.html", "Heatherhigh Hills"): "real/atlas-area-heatherhigh-hills.png",
    ("alba-atlas-expanded-a4.html", "Glass Loch"): "real/atlas-area-glass-loch.png",
    ("alba-atlas-expanded-a4.html", "Northern Whale-Road"): "real/atlas-area-northern-whale-road.png",
    ("alba-atlas-expanded-a4.html", "Red Banner Border"): "real/atlas-area-red-banner-border.png",
    ("alba-atlas-expanded-a4.html", "Thistlewood"): "real/atlas-area-thistlewood.png",
    ("alba-atlas-expanded-a4.html", "Cauldron Pass"): "real/atlas-area-cauldron-pass.png",
    ("alba-atlas-expanded-a4.html", "Kettleford"): "real/atlas-area-kettleford.png",
    ("alba-atlas-expanded-a4.html", "Root Warrens"): "real/atlas-area-root-warrens.png",
    ("mounts-and-pets-a4.html", "Highland Pony"): "true-unique/mounts-and-pets/mount-pet-highland-pony.png",
    ("mounts-and-pets-a4.html", "Cairn Goat"): "true-unique/mounts-and-pets/mount-pet-cairn-goat.png",
    ("mounts-and-pets-a4.html", "Fairy Stag"): "true-unique/mounts-and-pets/mount-pet-fairy-stag.png",
    ("mounts-and-pets-a4.html", "Kelp-Mane Pony"): "true-unique/mounts-and-pets/mount-pet-kelp-mane-pony.png",
    ("mounts-and-pets-a4.html", "Rowan Owl"): "true-unique/mounts-and-pets/mount-pet-rowan-owl.png",
    ("mounts-and-pets-a4.html", "Border Warg"): "true-unique/mounts-and-pets/mount-pet-border-warg.png",
    ("mounts-and-pets-a4.html", "Rowan Mouse"): "true-unique/mounts-and-pets/mount-pet-rowan-mouse.png",
    ("mounts-and-pets-a4.html", "Cloud Moth"): "true-unique/mounts-and-pets/mount-pet-cloud-moth.png",
    ("mounts-and-pets-a4.html", "Thistle Hedgehog"): "true-unique/mounts-and-pets/mount-pet-thistle-hedgehog.png",
    ("bestiary-a4.html", "How to use creature stat blocks"): "wash/05-bestiary-catalog.png",
    ("bestiary-vol-2-a4.html", "Scary things of war and border"): "wash/scary-bestiary-group.png",
    ("bestiary-vol-2-a4.html", "Adventures in Alba"): "wash/real/wash-bestiary-vol-2-002-86c1.png",
    ("bestiary-vol-2-a4.html", "Mist Stag of Alba"): "creature-mist-stag.png",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_procedural_png(path: Path) -> bool:
    return path.suffix.lower() == ".png" and Path(str(path).replace(".png", ".source.svg")).exists()


def is_derivative_rel(rel: str) -> bool:
    return "/no-reuse-" in rel or rel.startswith("real/no-reuse-") or rel.startswith("real/final-no-reuse-")


def rel_from_html(html: Path, src: str) -> Path:
    if src.startswith("../"):
        return (html.parent / src).resolve()
    return (ROOT / src).resolve()


def words(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


def section_context(html: Path, text: str, pos: int, tag: str, old_rel: str) -> tuple[set[str], str, int]:
    page_no = text[:pos].count('<section class="page')
    sec_start = text.rfind('<section class="page', 0, pos)
    sec_end = text.find('</section>', pos)
    if sec_start < 0:
        sec_start = max(0, pos - 1200)
    if sec_end < 0:
        sec_end = min(len(text), pos + 1200)
    sec = text[sec_start:sec_end]
    title = ""
    tm = re.search(r'<h[12][^>]*>(.*?)</h[12]>', sec, re.S)
    if tm:
        title = re.sub(r"<[^>]+>", " ", tm.group(1)).strip()
    ctx = words(html.stem + " " + old_rel + " " + tag + " " + sec)
    return ctx, title, page_no


def infer_domain(html_name: str, ctx: set[str]) -> str:
    stem = html_name.replace("-a4.html", "")
    # Book identity wins over generic setting words like "Alba" that appear on
    # nearly every page.
    if "gear" in stem or "treasure" in stem:
        return "gear"
    if "mounts" in stem or "pets" in stem:
        return "mount"
    if "bestiary" in stem:
        return "bestiary"
    if "campaign" in stem or "adventure" in stem or "west" in stem:
        return "campaign"
    if "player" in stem or "character" in stem:
        return "player"
    if "cards" in stem or "quickstart" in stem or "table-aids" in stem or "style-proof" in stem or "guide-book" in stem or "guide-extra" in stem:
        return "cards"
    if "atlas" in stem or ("setting-guide" in stem and ("map" in ctx or "frontier" in ctx or "region" in ctx)):
        return "atlas"
    if "companion" in ctx:
        return "mount"
    scores = {d: len(ctx & ws) for d, ws in DOMAIN_WORDS.items()}
    return max(scores.items(), key=lambda kv: kv[1])[0] if max(scores.values()) else "general"


def candidate_pool() -> list[dict]:
    pool: list[dict] = []
    seen_hashes = set()
    for p in sorted(ART_ROOT.rglob("*.png")):
        if p.stat().st_size < 50_000:
            continue
        rel = p.relative_to(ART_ROOT).as_posix()
        if is_procedural_png(p):
            continue
        if rel.startswith("true-unique/scenes/") or rel.startswith("true-unique/cards/") or rel.startswith("true-unique/washes/"):
            continue
        if is_derivative_rel(rel):
            continue
        h = sha(p)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        pool.append({"path": p, "rel": rel, "hash": h, "words": words(rel)})
    return pool


def acceptable(cand: dict, domain: str) -> bool:
    rel = cand["rel"]
    w = cand["words"]
    if domain == "atlas":
        return rel.startswith("real/atlas-area-") or rel in {"alba-regional-map.png","alba-town-dungeon-map.png","alba-frontier-map.png","map-alba-region.png","map-kettleford-village.png","map-moon-loch.png"} or bool(w & DOMAIN_WORDS["atlas"] and "/cards/" not in rel and "mount-pet" not in rel and "gear" not in rel)
    if domain == "gear":
        return rel.startswith("item-") or rel.startswith("true-unique/cron-v3/gear") or ("/cards/" in rel and bool(w & DOMAIN_WORDS["gear"])) or bool(w & DOMAIN_WORDS["gear"])
    if domain == "mount":
        return rel.startswith("true-unique/mounts-and-pets/") or rel.startswith("real/mount-pet-") or bool(w & DOMAIN_WORDS["mount"])
    if domain == "bestiary":
        return rel.startswith("creature-") or "creature" in rel or bool(w & DOMAIN_WORDS["bestiary"])
    if domain == "campaign":
        return rel.startswith("real/west-quest-") or "campaign" in rel or "quest" in rel or "banner" in rel or bool(w & DOMAIN_WORDS["campaign"])
    if domain == "player":
        return rel.startswith("real-context/player-handbook/") or bool(w & DOMAIN_WORDS["player"] | DOMAIN_WORDS["gear"])
    return True


def score(cand: dict, ctx: set[str], domain: str) -> int:
    rel = cand["rel"]
    s = 10 * len(cand["words"] & ctx)
    if acceptable(cand, domain):
        s += 1000
    else:
        s -= 1000
    if rel.startswith("real-context/"):
        s += 80
    if rel.startswith("real/atlas-area-") and domain == "atlas":
        s += 120
    if rel.startswith("true-unique/mounts-and-pets/") and domain == "mount":
        s += 120
    if rel.startswith("item-") and domain == "gear":
        s += 120
    if rel.startswith("real/cards/") and domain == "atlas":
        s -= 500
    if "gear-items-potions" in rel and domain != "gear":
        s -= 500
    if "mount-pet" in rel and domain not in {"mount", "bestiary"}:
        s -= 300
    return s


def main() -> int:
    pool = candidate_pool()
    if not pool:
        raise SystemExit("No non-procedural artwork candidates found")

    used_hashes: set[str] = set()
    replacements = []
    missing = []
    forced_domain = []

    for html in sorted(HTML_ROOT.glob("*-a4.html")):
        text = html.read_text(encoding="utf-8", errors="ignore")

        def repl(m: re.Match) -> str:
            prefix, src, suffix = m.group(1), m.group(2), m.group(3)
            p = rel_from_html(html, src)
            if not p.exists():
                missing.append({"html": html.name, "src": src})
                return m.group(0)
            try:
                old_rel = p.relative_to(ROOT).as_posix()
                art_rel = p.relative_to(ART_ROOT).as_posix()
            except ValueError:
                old_rel = src
                art_rel = src
            h = sha(p)
            ctx, title, page_no = section_context(html, text, m.start(), m.group(0), old_rel)
            domain = infer_domain(html.name, ctx)
            override_rel = TITLE_OVERRIDES.get((html.name, title))
            bad_domain = not acceptable({"rel": art_rel, "words": words(art_rel)}, domain)
            must_replace = is_procedural_png(p) or is_derivative_rel(art_rel) or h in used_hashes or bad_domain or (override_rel is not None and art_rel != override_rel)
            if not must_replace:
                used_hashes.add(h)
                return m.group(0)

            chosen = None
            if override_rel is not None:
                override_path = ART_ROOT / override_rel
                if override_path.exists():
                    chosen = {"path": override_path, "rel": override_rel, "hash": sha(override_path), "words": words(override_rel)}
            if chosen is None:
                ranked = sorted(pool, key=lambda c: (score(c, ctx, domain), len(c["words"] & ctx), -len(c["rel"])), reverse=True)
                for cand in ranked:
                    if cand["hash"] not in used_hashes and acceptable(cand, domain):
                        chosen = cand
                        break
                if chosen is None:
                    for cand in ranked:
                        if cand["hash"] not in used_hashes:
                            chosen = cand
                            break
                if chosen is None:
                    chosen = ranked[0]
            used_hashes.add(chosen["hash"])
            new_src = "../art/generated/" + chosen["rel"]
            reason = []
            if is_procedural_png(p): reason.append("procedural")
            if is_derivative_rel(art_rel): reason.append("derivative")
            if h in used_hashes: reason.append("duplicate")
            if bad_domain: reason.append("domain")
            rec = {"html": html.name, "page": page_no, "title": title, "domain": domain, "old": old_rel, "new": "art/generated/" + chosen["rel"], "score": score(chosen, ctx, domain), "reason": reason}
            replacements.append(rec)
            if bad_domain:
                forced_domain.append(rec)
            return prefix + new_src + suffix

        new_text = IMG_RE.sub(repl, text)
        if new_text != text:
            html.write_text(new_text, encoding="utf-8")

    # Final audit.
    final_refs = []
    final_missing = []
    final_proc = []
    final_derivative = []
    final_domain = []
    hashes = {}
    dupes = []
    for html in sorted(HTML_ROOT.glob("*-a4.html")):
        text = html.read_text(encoding="utf-8", errors="ignore")
        for m in IMG_RE.finditer(text):
            src = m.group(2)
            p = rel_from_html(html, src)
            rel = str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else src
            final_refs.append({"html": html.name, "src": rel})
            if not p.exists():
                final_missing.append({"html": html.name, "src": rel})
                continue
            art_rel = p.relative_to(ART_ROOT).as_posix() if str(p).startswith(str(ART_ROOT)) else rel
            ctx, title, page_no = section_context(html, text, m.start(), m.group(0), rel)
            domain = infer_domain(html.name, ctx)
            if is_procedural_png(p):
                final_proc.append({"html": html.name, "page": page_no, "title": title, "src": rel})
            if is_derivative_rel(art_rel):
                final_derivative.append({"html": html.name, "page": page_no, "title": title, "src": rel})
            if not acceptable({"rel": art_rel, "words": words(art_rel)}, domain):
                final_domain.append({"html": html.name, "page": page_no, "title": title, "domain": domain, "src": rel})
            h = sha(p)
            if h in hashes:
                dupes.append({"a": {"html": html.name, "page": page_no, "title": title, "src": rel}, "b": hashes[h]})
            else:
                hashes[h] = {"html": html.name, "page": page_no, "title": title, "src": rel}

    report = {
        "summary": {
            "replacements": len(replacements),
            "total_refs": len(final_refs),
            "unique_hashes": len(hashes),
            "duplicate_hash_pairs": len(dupes),
            "missing": len(final_missing),
            "procedural_svg_backed_refs": len(final_proc),
            "derivative_no_reuse_refs": len(final_derivative),
            "domain_mismatch_refs": len(final_domain),
        },
        "replacements": replacements,
        "missing": final_missing,
        "procedural": final_proc,
        "derivative": final_derivative,
        "domain_mismatch": final_domain,
        "duplicates": dupes[:100],
    }
    QA_ROOT.mkdir(exist_ok=True)
    (QA_ROOT / "sanitized-art-reference-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 1 if final_missing or final_proc or final_derivative or final_domain or dupes else 0


if __name__ == "__main__":
    raise SystemExit(main())
