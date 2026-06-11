#!/usr/bin/env python3
"""Replace procedural/geometric placeholder image refs in rendered HTML.

The rejected pass produced many PNGs from deterministic SVG source files
(`*.source.svg`).  They are unique by hash but visibly read as abstract
geometric placeholders, not contextual artwork.  This tool rewrites HTML image
references away from those procedural assets to existing non-procedural artwork
PNGs with unique byte hashes.
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

BAD_DIR_PARTS = {
    "true-unique/scenes",
    "true-unique/cards",
    "true-unique/washes",
}

# Prefer actual image-generation outputs and hand-picked/stable generated art.
# Avoid procedural true-unique/scenes/cards/washes, which have .source.svg files.
PREFERRED_PREFIXES = (
    "real/",
    "real/cards/",
    "true-unique/mounts-and-pets/",
    "true-unique/cron-v3/",
    "real-context/",
    "",  # root-level generated art
    "wash/real/",
    "wash/",
)

KEYWORDS = {
    "player": ["dice", "kindred", "job", "spell", "gear", "hero", "table", "rule", "character"],
    "dice": ["dice", "table", "rule", "hero", "gear"],
    "kindred": ["kindred", "fairy", "rowan", "selkie", "brownie", "glenfolk", "moss", "sprite", "myceling"],
    "job": ["job", "knight", "scout", "bard", "mage", "beast", "tinker"],
    "bestiary": ["creature", "beast", "monster", "dragon", "warg", "drake", "redcap", "crow", "wight", "hag"],
    "creature": ["creature", "beast", "monster", "dragon", "warg", "drake", "redcap", "crow", "wight", "hag"],
    "atlas": ["map", "atlas", "loch", "road", "town", "border", "thistlewood", "kettleford"],
    "map": ["map", "atlas", "loch", "road", "town", "border", "thistlewood", "kettleford"],
    "campaign": ["campaign", "adventure", "banner", "fort", "queen", "clan", "oath", "quest"],
    "adventure": ["adventure", "quest", "scene", "road", "crown", "banner", "loch", "longship"],
    "gear": ["gear", "item", "potion", "poison", "lantern", "rope", "tool", "treasure", "magic"],
    "item": ["gear", "item", "potion", "poison", "lantern", "rope", "tool", "treasure", "magic"],
    "card": ["card", "gear", "item", "creature", "companion", "token"],
    "mount": ["mount", "pet", "companion", "pony", "goat", "stag", "owl", "warg", "mouse", "moth", "hedgehog"],
    "pet": ["mount", "pet", "companion", "pony", "goat", "stag", "owl", "warg", "mouse", "moth", "hedgehog"],
    "table": ["table", "aid", "dice", "gear", "rule"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_procedural_png(path: Path) -> bool:
    return path.suffix.lower() == ".png" and Path(str(path).replace(".png", ".source.svg")).exists()


def rel_from_html(html: Path, src: str) -> Path:
    if src.startswith("../"):
        return (html.parent / src).resolve()
    return (ROOT / src).resolve()


def words(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


def context_words(html: Path, old_rel: str, tag: str) -> set[str]:
    w = words(html.stem + " " + old_rel + " " + re.sub(r"<[^>]+>", " ", tag))
    # Pull nearby headings/page title from the document when possible.
    text = html.read_text(encoding="utf-8", errors="ignore")
    pos = text.find(old_rel)
    if pos >= 0:
        window = text[max(0, pos - 1600): pos + 1600]
        w |= words(re.sub(r"<[^>]+>", " ", window))
    expanded = set(w)
    for k, vals in KEYWORDS.items():
        if k in w:
            expanded.update(vals)
    return expanded


def candidate_pool() -> list[dict]:
    pool = []
    seen_hashes = set()
    for p in sorted(ART_ROOT.rglob("*.png")):
        if p.stat().st_size < 50_000:
            continue
        if is_procedural_png(p):
            continue
        rel = p.relative_to(ART_ROOT).as_posix()
        # Avoid generated split source zips/contact artifacts if any ever land here.
        if any(part.startswith("true-unique/scenes") or part.startswith("true-unique/cards") or part.startswith("true-unique/washes") for part in [rel]):
            continue
        h = sha(p)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        pool.append({"path": p, "rel": rel, "hash": h, "words": words(rel)})
    return pool


def score(cand: dict, ctx: set[str]) -> int:
    rel = cand["rel"]
    s = 0
    s += 10 * len(cand["words"] & ctx)
    # Strong contextual boosts.
    for k, vals in KEYWORDS.items():
        if k in ctx and any(v in cand["words"] or v in rel for v in vals):
            s += 15
    if rel.startswith("real-context/"):
        s += 80
    if rel.startswith("real/"):
        s += 50
    if rel.startswith("true-unique/mounts-and-pets/"):
        s += 45
    if "/cards/" in rel or rel.startswith("real/cards/"):
        if "card" in ctx or "print" in ctx or "gear" in ctx or "item" in ctx:
            s += 25
    if rel.startswith("wash/"):
        s -= 12
    return s


def main() -> int:
    pool = candidate_pool()
    if not pool:
        raise SystemExit("No non-procedural artwork candidates found")

    used_hashes: set[str] = set()
    replacements = []
    missing = []

    # Mark already-good image hashes as used so replacements stay unique.
    for html in sorted(HTML_ROOT.glob("*-a4.html")):
        text = html.read_text(encoding="utf-8", errors="ignore")
        for m in IMG_RE.finditer(text):
            src = m.group(2)
            p = rel_from_html(html, src)
            if not p.exists():
                missing.append({"html": html.name, "src": src})
                continue
            if not is_procedural_png(p):
                used_hashes.add(sha(p))

    for html in sorted(HTML_ROOT.glob("*-a4.html")):
        text = html.read_text(encoding="utf-8", errors="ignore")

        def repl(m: re.Match) -> str:
            prefix, src, suffix = m.group(1), m.group(2), m.group(3)
            p = rel_from_html(html, src)
            if not p.exists() or not is_procedural_png(p):
                return m.group(0)
            try:
                old_rel = p.relative_to(ROOT).as_posix()
            except ValueError:
                old_rel = src
            ctx = context_words(html, old_rel, m.group(0))
            ranked = sorted(pool, key=lambda c: (score(c, ctx), -len(c["rel"])), reverse=True)
            chosen = None
            for cand in ranked:
                if cand["hash"] not in used_hashes:
                    chosen = cand
                    break
            if chosen is None:
                # Last resort: allow hash reuse rather than leave procedural art.
                chosen = ranked[0]
            used_hashes.add(chosen["hash"])
            new_src = "../art/generated/" + chosen["rel"]
            replacements.append({"html": html.name, "old": old_rel, "new": "art/generated/" + chosen["rel"], "score": score(chosen, ctx)})
            return prefix + new_src + suffix

        new_text = IMG_RE.sub(repl, text)
        if new_text != text:
            html.write_text(new_text, encoding="utf-8")

    # Final audit.
    final_refs = []
    final_missing = []
    final_proc = []
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
            if is_procedural_png(p):
                final_proc.append({"html": html.name, "src": rel})
            h = sha(p)
            if h in hashes:
                dupes.append({"a": {"html": html.name, "src": rel}, "b": hashes[h]})
            else:
                hashes[h] = {"html": html.name, "src": rel}

    report = {
        "summary": {
            "replacements": len(replacements),
            "total_refs": len(final_refs),
            "unique_hashes": len(hashes),
            "duplicate_hash_pairs": len(dupes),
            "missing": len(final_missing),
            "procedural_svg_backed_refs": len(final_proc),
        },
        "replacements": replacements,
        "missing": final_missing,
        "procedural": final_proc,
        "duplicates": dupes[:50],
    }
    QA_ROOT.mkdir(exist_ok=True)
    (QA_ROOT / "sanitized-art-reference-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 1 if final_missing or final_proc else 0

if __name__ == "__main__":
    raise SystemExit(main())
