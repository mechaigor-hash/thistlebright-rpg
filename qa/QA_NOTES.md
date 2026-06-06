# QA notes — v0.1 style proof

Rendered with WeasyPrint and checked with `pdfinfo` + `pdftoppm`.

Verified:
- A4 portrait PDF: 10 pages, 595.276 x 841.89 pts.
- Full-bleed cover/chapter/step/bestiary art pages render with no white bottom gaps.
- Step 1 and Step 2 headings are inside image overlay panels.
- Overlay panels sit in lower safe areas and do not cover faces.
- Rules, kindred cards, adventure jobs, bestiary pattern, and character sheet pages use parchment background rather than pure white dead bands.
- WeasyPrint column-count bug avoided by using grid columns.

Contact sheet: `qa/style-proof-contact.jpg`.
