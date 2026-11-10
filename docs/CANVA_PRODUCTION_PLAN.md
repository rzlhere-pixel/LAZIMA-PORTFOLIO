# Canva Production Plan — A4 editable master

The HTML book in `site/` is the layout reference. This plan rebuilds it as an editable Canva master. Each page is a separate Canva page with named layers, live text and placed images. Nothing is flattened.

## Document
- **Size:** A4 portrait, 210 × 297 mm (Canva "A4 Document"). 12 pages.
- **Bleed:** turn on *Show print bleed* (3 mm). Extend full-bleed images and colour blocks to the bleed edge.
- **Safe margin:** 12.6 mm (6% of width) for all text and folios.
- **Export:** *PDF Print*, colour profile CMYK where available, crop marks + bleed for the printer. Use *PDF Standard* for email (keep it under 10 MB).
- **Image resolution:** source scans are ≈200 dpi. Do not enlarge any illustration beyond ~70% of page width at A4 print, or it falls below 150 effective dpi.

## Design tokens

| Token | Hex | Role |
|---|---|---|
| Milk ivory | `#F6F2EC` | Default paper (pages 01, 03, 06, 09, 11) |
| Powder rose | `#E9D9D6` | Pages 02, 12; cover colour block |
| Dusty lilac | `#CFC7D7` | Page 05; page 11 side block |
| Muted sage | `#C4CBBE` | Page 04 |
| Misty blue | `#D5DFE5` | Page 07 |
| Deep plum | `#312734` | All headline and body type; page 10 background |
| Cocoa (caption) | `#5A483F` | Secondary captions. Darkened from the approved `#756257` so it reaches ≥ 5:1 contrast on every tint |
| Mulberry | `#840F2F` | Page 08 background (the one bold pivot). Sampled from the original colour board |
| Bougainvillea | `#C72E57` | Swatch chips and colour field only. Sampled from the original fabric board |
| Petal | `#D22D44` | Swatch chips only. Sampled from the original colour board |

Add these as a Canva Brand Kit palette named **LAZIMA — Paper Flower**.

## Type hierarchy

| Role | Typeface (Canva) | Size at A4 | Tracking | Notes |
|---|---|---|---|---|
| Name (cover/closing) | Bodoni Moda Medium | 150–160 pt | −55 | One word, never wraps |
| Display headline | Bodoni Moda Regular | 85–95 pt | −45 | Leading 0.86; 2–3 short lines |
| Section headline | Bodoni Moda Regular | 55–65 pt | −45 | Spec / development / practice |
| Statement / quote | Bodoni Moda Italic | 20–24 pt | 0 | One sentence maximum |
| Data value | Bodoni Moda Regular | 20 pt | 0 | Spec values, facts |
| Caption | Hanken Grotesk Regular | 9–9.5 pt | +5 | Sentence case, 1.45 leading |
| Micro label / folio | Hanken Grotesk Medium | 7.5–8 pt | 0 | Folio: italic Bodoni numeral + sans word |

If Bodoni Moda is unavailable in the Canva account, substitute **Playfair Display** (display) and **DM Sans** (captions), and note the substitution in the export log. Never use the `lazique` script wordmark here unless the approved original file is supplied.

## Layer structure (every page)
Name layers in Canva's *Position → Layers* panel, bottom to top:
1. `BG` — page colour (locked)
2. `BLOCK` — any colour block (locked)
3. `IMG-<asset-id>` — e.g. `IMG-look-01`, matching `site/assets/manifest.js`. Use **Fit** (not Fill) for illustrations and the spec sheet so no artwork is cropped
4. `TITLE`
5. `TEXT-<role>` — caption, quote, data
6. `FOLIO` — page number + section (locked position)
7. `NOTE-review` — hidden rights note; delete before export

## Page-by-page placement (x, y, w as % of page width/height, from the HTML master)

| Pg | Background | Images (layer, x, y, w) | Text |
|---|---|---|---|
| 01 Cover | Ivory + rose block (x44 y0 w56 h61) | IMG-look-05 (36, 6.5, 54) | "Lazima" (x4.5 y62); *Fashion portfolio*; caption bottom-right |
| 02 Identity | Rose | IMG-look-03 detail crop, square (6, 52, 30); IMG-portrait (54, 40, 46) **placeholder** | Statement, 3 lines; name + training bottom-right |
| 03 Moodboard | Ivory | IMG-board-inspiration (46, 0, 54); IMG-board-theme rotated −3.5° (9, 37.5, 34) | "Paper / flower"; quote; 4 swatch squares bottom-left |
| 04 Sketchbook | Sage | IMG-look-01 (25, 5, 69) | "Look 01" rotated −90° along left edge; 3-line caption |
| 05 Silhouettes | Lilac | look-02 (5, 7, 35); look-03 (33, 25, 35, on top, soft shadow); look-04 (61, 4, 34) | One-word notes; "Three / silhouettes" bottom-right |
| 06 Development | Ivory | spec-sheet (4, 30, 46); production-board (54, 4, 42); pattern-board (54, 66, 19) | Headline; numbered stages 1–3 |
| 07 Modest wear | Misty blue | 3 **placeholder** frames (6, 13, 48) (58, 39, 36) (38, 66, 22) | Title; honest pending note |
| 08 Colour & cloth | Mulberry | board-fabric (0, 30, 47); board-colour (50, 6, 37); 3-colour field (90, 9, 10 × 58 h) | Ivory title and caption |
| 09 Specification | Ivory | spec-sheet on white (4, 4, 62); pattern-board (70, 64, 24) | Data list right; "Specification"; quoted description |
| 10 Collection | Deep plum | 5 looks in a row (2–98, 39), alternate looks dropped 7% | "Paper Flower"; numerals 01–05 |
| 11 Practice | Ivory + lilac side block (w38) | IMG-workspace (9, 9, 46) **placeholder** | Facts list; pending line in italic |
| 12 Closing | Rose | look-05 (35, 12, 30) | "Lazima" centred; contact placeholder; credit |

## Asset handling in Canva
- Upload the **PNG masters** from `site/assets/private/` (local only) into a Canva folder named `LAZIMA — private originals`. Do not share that folder.
- Do not apply Canva filters, *Magic Edit*, background removal or enhancement to any illustration or photo. Crop by frame only.
- `production-board` shows identifiable people. Keep it unaltered, and only include it after the wearer's consent is recorded.
- Compiled boards contain third-party photographs. Keep them for private review drafts; replace them before any public or employer-facing export.

## QA before export
- [ ] Every image layer name matches an approved row in `docs/SOURCE_ATTRIBUTION_REGISTER.md`
- [ ] No placeholder frames remain (or they are intentionally removed with their page)
- [ ] Captions ≥ 9 pt; contrast checked against the token table
- [ ] Print one physical A4 proof; check illustration sharpness at 100% zoom
- [ ] View the PDF on a phone at full width
- [ ] Owner sign-off recorded in `docs/STATUS.md`
