## Semantic Art Reuse Fix

This pass fixes the issue where visually similar/base artwork was reused across books even when file hashes differed.

User-reported example fixed:

- `alba-atlas-expanded.pdf` no longer uses the lantern/sword/key gear object collage.
- `gear-items-potions.pdf` keeps gear-specific object artwork.
- `mounts-and-pets.pdf` pages are routed to companion-specific artwork rather than atlas/gear/bestiary fallbacks.

Generator/sanitizer changes:

- Removed procedural/different-hash `no-reuse` generation in `tools/build_books.py`.
- Replaced it with semantic final routing in `tools/sanitize_art_refs.py`.
- Added title-level hard overrides for atlas regions, mount/pet pages, and bestiary pages that were being misrouted.
- Added a distinct Alba Atlas Expanded cover/map image at `art/generated/real-context/alba-atlas-expanded/atlas-cover-map-table.png`.

Final hard audit:

```json
{
  "replacements": 216,
  "total_refs": 298,
  "unique_hashes": 298,
  "duplicate_hash_pairs": 0,
  "missing": 0,
  "procedural_svg_backed_refs": 0,
  "derivative_no_reuse_refs": 0,
  "domain_mismatch_refs": 0
}
```

Visual QA:

- `qa/semantic-fix-sheets/reuse-fix-contact-sheet.jpg`
- Confirms atlas/gear/mount sampled pages are no longer using the same base collage.
